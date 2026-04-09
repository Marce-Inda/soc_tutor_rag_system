"""
Cliente de Chroma para Retrieval Augmented Generation.
Módulo de RAG para recuperar conocimiento de ciberseguridad.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Chroma imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Chroma no disponible. Instalar: pip install chromadb")

# Sentence Transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    print("sentence-transformers no disponible. Instalar: pip install sentence-transformers")


class RAGClient:
    """Cliente de Retrieval Augmented Generation."""
    
    def __init__(
        self, 
        persist_directory: Optional[str] = None,
        collection_name: str = "cybersec-knowledge"
    ):
        self.collection_name = collection_name
        
        # Default path relative to project root
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
                hashlib.md5(d['text'].encode()).hexdigest() 
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
    
    def retrieve(
        self, 
        query: str, 
        k: int = 5,
        filter_source: Optional[str] = None,
        filter_scenario_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recupera documentos relevantes para una query."""
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
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i]['source'],
                'type': results['metadatas'][0][i].get('type', 'unknown'),
                'distance': results['distances'][0][i]
            })
        
        return retrieved
    
    def retrieve_with_context(
        self,
        decision: Dict[str, Any],
        contexto: Dict[str, Any],
        k: int = 5
    ) -> Dict[str, Any]:
        """Recupera conocimiento contextual para una decisión."""
        # Construir query
        query = f"{decision.get('accion', '')} {contexto.get('tipo_incidente', '')}"
        
        # Recuperar
        docs = self.retrieve(query, k=k)
        
        # Formatear contexto para los agentes
        contexto_rag = "\n\n".join([
            f"[{d['source']}] {d['text']}" 
            for d in docs
        ])
        
        fuentes = list(set([d['source'] for d in docs]))
        
        return {
            'contexto_rag': contexto_rag,
            'documentos_recuperados': docs,
            'fuentes': fuentes
        }
    
    def count_documents(self) -> int:
        """Cuenta documentos en el índice."""
        if not self._client:
            self._init_client()
        return self._collection.count()


def create_rag_client(persist_directory: Optional[str] = None) -> RAGClient:
    """Factory function para crear cliente RAG."""
    return RAGClient(persist_directory=persist_directory)
