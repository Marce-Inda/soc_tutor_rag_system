"""
Módulo de Caché Semántica para el SOC Tutor.
Permite recordar y reutilizar feedbacks para decisiones similares,
optimizando costos y reduciendo latencia.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib

# Intentar importar chroma y sentence_transformers (asumimos disponibles vía .venv)
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False

class SemanticCache:
    """Manejador de caché semántica para respuestas del tutor."""
    
    def __init__(
        self, 
        persist_dir: Optional[str] = None,
        collection_name: str = "tutor-feedback-cache",
        threshold: float = 0.98,
        ttl_days: int = 7,
        llm_client: Optional[Any] = None
    ):
        self.collection_name = collection_name
        self.threshold = threshold
        self.ttl_days = ttl_days
        self.llm_client = llm_client
        
        if not persist_dir:
            base_dir = Path(__file__).parent.parent.parent
            persist_dir = str(base_dir / "data" / "indices")
            
        self.persist_dir = persist_dir
        self._client = None
        self._collection = None
        self._model = None
        
    def _init_resources(self):
        """Inicializa Chroma y el modelo de embeddings."""
        if not LIBS_AVAILABLE:
            return
            
        if not self._client:
            os.makedirs(self.persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Caché semántica de respuestas del SOC Tutor"}
            )
            
        if not self._model:
            self._model = SentenceTransformer('all-MiniLM-L6-v2')

    def _translate_intent(self, text: str) -> str:
        """Traduce la intención del jugador al inglés para permitir aciertos de caché entre idiomas."""
        if not self.llm_client or not text or text.strip() == "":
            return text
            
        # We use a very fast and loose translation for semantic indexing
        system_prompt = "You are a translation microservice. Translate the following SOC analyst action/justification to English concisely."
        try:
            translation = self.llm_client.generate(f"Translate to English: {text}", system_prompt=system_prompt)
            return translation.strip()
        except Exception:
            return text

    def _generate_fingerprint(
        self, 
        decision: Dict[str, Any], 
        context: Dict[str, Any], 
        player_profile: Dict[str, Any]
    ) -> str:
        """Crea una representación textual única (fingerprint) en inglés para normalizar la búsqueda."""
        # Translate core intent to English to unify the cache across ES, PT, EN
        action_en = self._translate_intent(decision.get('accion', ''))
        justification_en = self._translate_intent(decision.get('justificacion', ''))
        
        parts = [
            f"SCENARIO: {context.get('scenario_id', 'unknown')}",
            f"ACTION: {action_en}",
            f"TARGET: {decision.get('target', '')}",
            f"JUSTIFICATION: {justification_en}",
            f"LEVEL: {player_profile.get('level', '1')}"
        ]
        return " | ".join(parts)

    def lookup(
        self, 
        decision: Dict[str, Any], 
        context: Dict[str, Any], 
        player_profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Busca en el caché una respuesta similar."""
        self._init_resources()
        if not self._collection:
            return None
            
        fingerprint = self._generate_fingerprint(decision, context, player_profile)
        embedding = self._model.encode([fingerprint]).tolist()
        
        results = self._collection.query(
            query_embeddings=embedding,
            n_results=1,
            include=['metadatas', 'distances']
        )
        
        if not results['metadatas'] or not results['metadatas'][0]:
            return None
            
        distance = results['distances'][0][0]
        
        # Con embeddings normalizados de all-MiniLM-L6-v2:
        # 0.0 es exacto, < 0.08 es muy similar (~98%).
        if distance > 0.08: 
            return None
            
        # Verificar TTL
        metadata = results['metadatas'][0][0]
        created_at = datetime.fromisoformat(metadata['created_at'])
        if datetime.now() > created_at + timedelta(days=self.ttl_days):
            return None
            
        # El feedback está guardado como string JSON en la metadata
        return json.loads(metadata['feedback_json'])

    def store(
        self, 
        decision: Dict[str, Any], 
        context: Dict[str, Any], 
        player_profile: Dict[str, Any], 
        feedback: Any # FeedbackFinal
    ):
        """Guarda una respuesta en el caché."""
        self._init_resources()
        if not self._collection:
            return
            
        fingerprint = self._generate_fingerprint(decision, context, player_profile)
        entry_id = hashlib.md5(fingerprint.encode()).hexdigest()
        
        # Generar embedding manualmente
        embedding = self._model.encode([fingerprint]).tolist()
        
        # Convertir feedback a JSON string
        feedback_data = feedback if isinstance(feedback, dict) else feedback.model_dump()
        feedback_json = json.dumps(feedback_data, default=str)
        
        # IMPORTANTE: Guardamos el fingerprint como DOCUMENTO y pasamos su EMBEDDING explícito
        # Usamos upsert para asegurar que si el ID existe, se actualice con la versión más fresca
        self._collection.upsert(
            ids=[entry_id],
            embeddings=embedding,
            documents=[fingerprint],
            metadatas=[{
                "created_at": datetime.now().isoformat(),
                "scenario_id": context.get("scenario_id", "unknown"),
                "feedback_json": feedback_json
            }]
        )

def get_cache_client(llm_client: Optional[Any] = None) -> SemanticCache:
    """Factory para obtener el cliente de caché."""
    return SemanticCache(llm_client=llm_client)
