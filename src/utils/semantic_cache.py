import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import hashlib

# Configuración de logging
logger = logging.getLogger(__name__)

# Intentar importar chroma y sentence_transformers
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False
    logger.warning("Bibliotecas chromadb o sentence-transformers no encontradas. La caché semántica estará desactivada.")

class SemanticCache:
    """
    Manejador de caché semántica para respuestas del tutor.
    Utiliza embeddings vectoriales para encontrar respuestas previas a situaciones similares,
    incluso si la redacción no es idéntica.
    """
    
    def __init__(
        self, 
        persist_dir: Optional[str] = None,
        collection_name: str = "tutor-feedback-cache",
        threshold: float = 0.95,
        ttl_days: int = 7,
        llm_client: Optional[Any] = None,
        model_name: str = 'all-MiniLM-L6-v2'
    ):
        """
        Inicializa la caché semántica.
        
        Args:
            persist_dir: Directorio para persistir la base de datos Chroma.
            collection_name: Nombre de la colección en Chroma.
            threshold: Umbral de similitud (0.0 a 1.0). Por defecto 0.95.
            ttl_days: Días de vida de una entrada en caché.
            llm_client: Cliente LLM para traducciones (opcional).
            model_name: Nombre del modelo de embeddings a utilizar.
        """
        self.collection_name = collection_name
        self.threshold = threshold
        self.ttl_days = ttl_days
        self.llm_client = llm_client
        self.model_name = model_name
        
        # Caché interna de traducciones para evitar llamadas redundantes al LLM en la misma sesión
        self._translation_cache = {}
        
        if not persist_dir:
            # Por defecto, guardar en la carpeta data/indices del proyecto
            base_dir = Path(__file__).parent.parent.parent
            persist_dir = str(base_dir / "data" / "indices")
            
        self.persist_dir = persist_dir
        self._client = None
        self._collection = None
        self._model = None

    def _init_resources(self):
        """Inicializa los recursos pesados (Chroma y Modelo de Embeddings) solo cuando se necesitan."""
        if not LIBS_AVAILABLE:
            return
            
        if not self._client:
            try:
                chroma_host = os.environ.get("CHROMA_HOST")
                if chroma_host:
                    logger.info(f"Conectando a ChromaDB remoto en {chroma_host}")
                    self._client = chromadb.HttpClient(host=chroma_host, port=8000)
                else:
                    os.makedirs(self.persist_dir, exist_ok=True)
                    logger.info(f"Usando ChromaDB local en {self.persist_dir}")
                    self._client = chromadb.PersistentClient(path=self.persist_dir)
                
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Caché semántica de respuestas del SOC Tutor"}
                )
            except Exception as e:
                logger.error(f"Error inicializando ChromaDB: {e}")
                return
            
        if not self._model:
            try:
                logger.info(f"Cargando modelo de embeddings: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error(f"Error cargando modelo de embeddings {self.model_name}: {e}")

    def _translate_intent(self, text: str) -> str:
        """
        Traduce la intención del jugador al inglés para permitir aciertos de caché entre idiomas.
        Utiliza una caché interna para no llamar al LLM si el texto ya se tradujo antes.
        """
        if not self.llm_client or not text or text.strip() == "":
            return text
            
        # Verificar caché de sesión
        if text in self._translation_cache:
            return self._translation_cache[text]
            
        # Traducción rápida para propósitos de indexación semántica
        system_prompt = "You are a translation microservice. Translate the following SOC analyst action/justification to English concisely."
        try:
            translation = self.llm_client.generate(f"Translate to English: {text}", system_prompt=system_prompt)
            result = translation.strip()
            self._translation_cache[text] = result
            return result
        except Exception as e:
            logger.warning(f"Error en traducción semántica: {e}")
            return text

    def _generate_fingerprint(
        self, 
        decision: Dict[str, Any], 
        context: Dict[str, Any], 
        player_profile: Dict[str, Any]
    ) -> str:
        """Crea una representación textual única (fingerprint) normalizada para la búsqueda vectorial."""
        scenario = context.get('scenario_id', 'unknown')
        incident = context.get('tipo_incidente', 'unknown')
        fase = context.get('fase', 'unknown')
        
        # Intentamos unificar la acción en inglés para mejorar hits multilingües
        action_raw = decision.get('accion', '')
        action_en = self._translate_intent(action_raw)
        
        parts = [
            f"SCENARIO: {scenario}",
            f"INCIDENT: {incident}",
            f"PHASE: {fase}",
            f"ACTION: {action_en}",
            f"TARGET: {decision.get('target', '')}",
            f"LEVEL: {player_profile.get('level', '1')}",
            f"ROLE: {player_profile.get('rol', 'analyst')}"
        ]
        return " | ".join(parts)

    def _similarity_to_distance(self, similarity: float) -> float:
        """
        Convierte un score de similitud (0.0-1.0) a distancia L2 (Chroma default).
        Para embeddings normalizados: d = 2 * (1 - s)
        """
        return 2.0 * (1.0 - similarity)

    def lookup(
        self, 
        decision: Dict[str, Any], 
        context: Dict[str, Any], 
        player_profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Busca en el caché una respuesta similar a la decisión actual."""
        self._init_resources()
        if not self._collection or not self._model:
            return None
            
        fingerprint = self._generate_fingerprint(decision, context, player_profile)
        
        try:
            embedding = self._model.encode([fingerprint]).tolist()
            
            results = self._collection.query(
                query_embeddings=embedding,
                n_results=1,
                include=['metadatas', 'distances']
            )
            
            if not results['metadatas'] or not results['metadatas'][0]:
                return None
                
            distance = results['distances'][0][0]
            
            # Cálculo dinámico del umbral basado en el parámetro threshold
            max_distance = self._similarity_to_distance(self.threshold)
            
            if distance > max_distance: 
                logger.debug(f"Cache miss por distancia: {distance:.4f} > {max_distance:.4f}")
                return None
                
            # Verificar TTL
            metadata = results['metadatas'][0][0]
            created_at = datetime.fromisoformat(metadata['created_at'])
            if datetime.now() > created_at + timedelta(days=self.ttl_days):
                logger.info("Cache entry expired by TTL")
                return None
                
            logger.info(f"Cache HIT semántico! Distancia: {distance:.4f}")
            return json.loads(metadata['feedback_json'])
            
        except Exception as e:
            logger.error(f"Error durante lookup en caché: {e}")
            return None

    def store(
        self, 
        decision: Dict[str, Any], 
        context: Dict[str, Any], 
        player_profile: Dict[str, Any], 
        feedback: Union[Dict[str, Any], Any]
    ):
        """Guarda una respuesta en el caché para uso futuro."""
        self._init_resources()
        if not self._collection or not self._model:
            return
            
        fingerprint = self._generate_fingerprint(decision, context, player_profile)
        entry_id = hashlib.sha256(fingerprint.encode()).hexdigest()
        
        try:
            # Generar embedding manualmente
            embedding = self._model.encode([fingerprint]).tolist()
            
            # Convertir feedback a JSON string (maneja objetos Pydantic o Dicts)
            feedback_data = feedback if isinstance(feedback, dict) else feedback.model_dump()
            feedback_json = json.dumps(feedback_data, default=str)
            
            # Upsert para mantener la versión más fresca
            self._collection.upsert(
                ids=[entry_id],
                embeddings=embedding,
                documents=[fingerprint],
                metadatas=[{
                    "created_at": datetime.now().isoformat(),
                    "scenario_id": context.get("scenario_id", "unknown"),
                    "tipo_incidente": context.get("tipo_incidente", "unknown"),
                    "fase": context.get("fase", "unknown"),
                    "feedback_json": feedback_json
                }]
            )
            logger.debug(f"Guardado en caché semántica: {entry_id}")
        except Exception as e:
            logger.error(f"Error guardando en caché: {e}")

def get_cache_client(llm_client: Optional[Any] = None, threshold: float = 0.95) -> SemanticCache:
    """Factory para obtener el cliente de caché configurado."""
    return SemanticCache(llm_client=llm_client, threshold=threshold)
