"""
ChromaDB Client for Retrieval Augmented Generation.
RAG module for retrieving cybersecurity knowledge.
"""

# ## CLIENTE RAG (Retrieval Augmented Generation)
# Componente encargado de la búsqueda semántica y exacta en la base de datos de conocimiento.


import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import re

# Chroma imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Chroma no disponible. Instalar: pip install chromadb")

# Sentence Transformers para embeddings
try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    print("sentence-transformers no disponible. Instalar: pip install sentence-transformers")


# ## PLAYBOOKS DE EMERGENCIA (Offline Fallback)
# Estos playbooks se utilizan si la base de datos vectorial (ChromaDB) no está disponible.
EMERGENCY_PLAYBOOKS = {
    "malware": "Standard Containment: Isolate infected host immediately. Perform full scan. Block malicious IPs/Domains in EDR/Firewall.",
    "phishing": "Phishing Response: Reset user credentials. Identify and delete malicious emails. Check logs for unauthorized access/forwarding.",
    "denial_of_service": "DoS Mitigation: Identify source IPs. Apply rate limiting. Enable DDoS protection service (Cloudflare/AWS Shield).",
    "unauthorized_access": "Breach Response: Revoke all active sessions. Review audit logs. Isolate compromised assets. Change administrative passwords.",
    "default": "Incident Handling: Follow NIST 800-61 Rev 2. Identify, Contain, Eradicate, and Recover. Log all findings for forensic analysis."
}


class RAGClient:
    """Cliente de Retrieval Augmented Generation."""
    
    def __init__(
        self, 
        persist_directory: Optional[str] = None,
        collection_name: str = "cybersec-knowledge",
        llm_client: Optional[Any] = None
    ):
        self.collection_name = collection_name
        self.llm_client = llm_client
        
        # Ruta por defecto relativa a la raíz del proyecto
        if not persist_directory:
            base_dir = Path(__file__).parent.parent.parent
            persist_directory = str(base_dir / "data" / "indices")
        
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None
        self._embeddings = None
    
    def _init_client(self):
        """Inicializa el cliente Chroma."""
        if not CHROMA_AVAILABLE:
            raise RuntimeError("Chroma no disponible")
        
        chroma_host = os.environ.get("CHROMA_HOST")
        if chroma_host:
            print(f"  [RAG] Conectando a ChromaDB Server en {chroma_host}:8000")
            self._client = chromadb.HttpClient(host=chroma_host, port=8000)
        else:
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.persist_directory
            )
        
        # Obtener o crear colección
        try:
            self._collection = self._client.get_collection(self.collection_name)
        except Exception:
            # Crear nueva colección
            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"description": "Conocimiento de ciberseguridad para RAG"}
            )
    
    def _init_embeddings(self):
        """Inicializa el modelo de embeddings."""
        if not ST_AVAILABLE:
            raise RuntimeError("sentence-transformers no disponible")
        
        # Modelo ligero para embeddings
        self._embeddings = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        ids: Optional[List[str]] = None,
        batch_size: int = 500
    ):
        """Agrega documentos al índice con soporte para batching."""
        if not self._client:
            self._init_client()
        if not self._embeddings:
            self._init_embeddings()
        
        # Generar IDs si no se proporcionan
        if not ids:
            import hashlib
            ids = [
                hashlib.sha256(d['text'].encode()).hexdigest() 
                for d in documents
            ]
        
        # Procesar por batches
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            batch_docs = documents[i:end_idx]
            batch_ids = ids[i:end_idx]
            
            # Generar embeddings para el batch
            texts = [d['text'] for d in batch_docs]
            embeddings = self._embeddings.encode(texts).tolist()
            
            # Agregar a colección
            self._collection.add(
                ids=batch_ids,
                documents=texts,
                metadatas=[
                    {
                        'source': d.get('source', 'unknown'),
                        'type': d.get('type', 'unknown'),
                        'scenario_id': d.get('scenario_id', 'none')
                    } 
                    for d in batch_docs
                ]
            )
            print(f"  → Procesado batch {i // batch_size + 1} ({len(batch_docs)} documentos)")
        
        print(f"✓ Indexación completada: {len(documents)} documentos.")
    
    def _extract_technical_tokens(self, query: str) -> List[str]:
        """Extrae identificadores técnicos (IPs, IDs MITRE, Hashes) de la query."""
        patterns = [
            r'T\d{4}(?:\.\d{3})?',  # MITRE IDs (T1059, T1059.001)
            r'CVE-\d{4}-\d{4,7}',   # CVEs
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IPv4
            r'[a-fA-F0-9]{32,64}'   # Hashes (MD5, SHA)
        ]
        
        tokens = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            tokens.extend(matches)
            
        # Limpieza y normalización (mantener original + uppercase para IDs)
        results = set()
        for t in tokens:
            t_clean = t.strip()
            results.add(t_clean)
            if t_clean.startswith('t') or t_clean.startswith('T'):
                results.add(t_clean.upper()) # Asegurar que T1059 sea buscado como tal
        
        return list(results)

    def retrieve_exact(
        self, 
        query: str, 
        k: int = 3,
        filter_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recupera documentos que contienen términos exactos de la query."""
        if not self._client:
            self._init_client()
            
        tokens = self._extract_technical_tokens(query)
        if not tokens:
            return []
            
        # Búsqueda por cada token técnico
        all_results = []
        seen_ids = set()
        
        for token in tokens:
            # Usamos where_document con $contains para búsqueda exacta en Chroma
            results = self._collection.query(
                query_texts=[token], # Chroma usará esto para filtrar si no pasamos embeddings
                n_results=k,
                where_document={"$contains": token}
            )
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    doc_id = results['ids'][0][i]
                    if doc_id not in seen_ids:
                        all_results.append({
                            'text': results['documents'][0][i],
                            'source': results['metadatas'][0][i]['source'],
                            'type': results['metadatas'][0][i].get('type', 'unknown'),
                            'distance': 0.0, # Distancia 0 para match exacto
                            'is_exact': True
                        })
                        seen_ids.add(doc_id)
        
        return all_results[:k]

    def retrieve(
        self, 
        query: str, 
        k: int = 5,
        filter_source: Optional[str] = None,
        filter_scenario_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recupera documentos relevantes para una query usando búsqueda semántica."""
        if not self._client:
            self._init_client()
        if not self._embeddings:
            self._init_embeddings()
        
        # Generar embedding de la query
        query_embedding = self._embeddings.encode([query]).tolist()
        
        # Construir filtro Chroma
        where_filter = {}
        if filter_source:
            where_filter['source'] = filter_source
        if filter_scenario_id:
            where_filter['scenario_id'] = filter_scenario_id
            
        if not where_filter:
            where_filter = None
            
        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=where_filter
        )
        
        # Formatear resultados
        retrieved = []
        if not results['documents'] or not results['documents'][0]:
            return []
            
        for i in range(len(results['documents'][0])):
            retrieved.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i]['source'],
                'type': results['metadatas'][0][i].get('type', 'unknown'),
                'distance': results['distances'][0][i]
            })
        
        return retrieved

    def _translate_query(self, query: str) -> str:
        """
        [OPTIMIZED] No longer calls LLM for translation.
        Calculates search terms based on technical tokens and original query.
        """
        return query

    def retrieve_hybrid(
        self, 
        query: str, 
        k: int = 5,
        filter_source: Optional[str] = None,
        filter_scenario_id: Optional[str] = None,
        translate: bool = False
    ) -> List[Dict[str, Any]]:
        """Realiza una búsqueda híbrida (Exacta + Semántica) con fallback resiliente."""
        
        try:
            search_query = query
            if translate:
                search_query = self._translate_query(query)
                if search_query != query:
                    print(f"  [RAG] Translated query: '{query}' -> '{search_query}'")

            # 1. Búsqueda Exacta (Prioritaria para IDs técnicos)
            exact_results = self.retrieve_exact(search_query, k=3, filter_source=filter_source)
            
            # 2. Búsqueda Semántica
            semantic_results = self.retrieve(
                search_query, 
                k=k, 
                filter_source=filter_source, 
                filter_scenario_id=filter_scenario_id
            )
            
            # 3. Fusión y De-duplicación
            seen_texts = set()
            hybrid_results = []
            
            # Primero agregamos los exactos (prioridad)
            for res in exact_results:
                hybrid_results.append(res)
                seen_texts.add(res['text'])
                
            # Agregamos los semánticos si no están ya
            for res in semantic_results:
                if res['text'] not in seen_texts:
                    res['is_exact'] = False
                    hybrid_results.append(res)
                    seen_texts.add(res['text'])
                    
            return hybrid_results[:k]
            
        except Exception as e:
            print(f"  [RAG] ⚠️ Retrieval failed (falling back to emergency playbooks): {e}")
            # Fallback dinámico basado en palabras clave en la query
            query_lower = query.lower()
            pb_type = "default"
            for key in EMERGENCY_PLAYBOOKS.keys():
                if key in query_lower:
                    pb_type = key
                    break
            
            return [{
                'id': 'emergency-pb-001',
                'text': f"[EMERGENCY FALLBACK] {EMERGENCY_PLAYBOOKS[pb_type]}",
                'source': 'OFFLINE_PLAYBOOK',
                'type': 'procedural',
                'distance': 0.0,
                'is_exact': True
            }]
    
    def retrieve_with_context(
        self,
        decision: Dict[str, Any],
        contexto: Dict[str, Any],
        k: int = 5,
        knowledge_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recupera conocimiento contextual adaptado al tipo de conocimiento pedido.
        - technical: Busca MITRE y Evidencias.
        - strategic: Busca NIST, GDPR y leyes.
        """
        # Construir query base
        query = f"{decision.get('accion', '')} {contexto.get('tipo_incidente', '')}"
        
        # Filtro de fuente dinámico basado en el tipo de conocimiento
        filter_source = None
        if knowledge_type == "technical":
            # Nota: En un sistema real, Chroma soportaría $in para múltiples fuentes.
            # Por ahora simplificamos la query para buscar MITRE o Evidencia si es técnico.
            query += " mitre tactics techniques evidence logs"
        elif knowledge_type == "strategic":
            query += " nist guidelines gdpr compliance legal"
        
        # Intentar extraer ID de técnica si existe en la decisión
        if 'tecnica_id' in decision:
            query += f" {decision['tecnica_id']}"
        
        # Recuperar usando modo Híbrido con traducción automática
        docs = self.retrieve_hybrid(query, k=k, translate=True)
        
        # Formatear contexto en Silos (RAG Cognitivo Avanzado / OpenMemory)
        semantic_parts = []
        procedural_parts = []
        
        for i, d in enumerate(docs):
            prefix = "[MATCH EXACTO]" if d.get('is_exact') else f"[RELEVANCIA {i+1}]"
            doc_id = d.get('id', 'no-id')[:16]
            source_lower = str(d.get('source', '')).lower()
            
            # Clasificador de Silos
            if any(kw in source_lower for kw in ['playbook', 'procedimiento', 'pasos', 'response', 'containment']):
                silo = procedural_parts
            else:
                silo = semantic_parts
                
            silo.append(f"{prefix} (Source: {d['source']} | Hash: {doc_id}): {d['text']}")
            
        # Unir silos
        context_parts = []
        if semantic_parts:
            context_parts.append("### SECTOR SEMÁNTICO (Conocimiento Teórico y Normativo)\n" + "\n\n".join(semantic_parts))
        if procedural_parts:
            context_parts.append("### SECTOR PROCEDURAL (Playbooks y Guías de Acción)\n" + "\n\n".join(procedural_parts))
            
        contexto_rag = "\n\n---\n\n".join(context_parts)
        fuentes = list(set([d['source'] for d in docs]))
        
        return {
            'contexto_rag': contexto_rag,
            'documentos_recuperados': docs,
            'sources': fuentes
        }
    
    def count_documents(self) -> int:
        """Cuenta documentos en el índice."""
        if not self._client:
            self._init_client()
        return self._collection.count()


def create_rag_client(persist_directory: Optional[str] = None, llm_client: Optional[Any] = None) -> RAGClient:
    """Factory function para crear cliente RAG."""
    return RAGClient(persist_directory=persist_directory, llm_client=llm_client)
