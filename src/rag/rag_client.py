"""
Cliente de Chroma para Retrieval Augmented Generation.
Módulo de RAG para recuperar conocimiento de ciberseguridad.
"""

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
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i]['source'],
                'type': results['metadatas'][0][i].get('type', 'unknown'),
                'distance': results['distances'][0][i]
            })
        
        return retrieved

    def _translate_query(self, query: str) -> str:
        """Traduce una consulta técnica al inglés para mejorar el 'match' en el RAG."""
        if not self.llm_client:
            return query
            
        system_prompt = "You are a specialized translator for cybersecurity technical terms."
        prompt = f"Translate the following technical incident response query to English. Keep technical IDs (IPs, MITRE) as they are. Return ONLY the translation:\n\n{query}"
        
        try:
            translation = self.llm_client.generate(prompt, system_prompt=system_prompt)
            return translation.strip()
        except Exception as e:
            print(f"  [RAG] Error translating query: {e}")
            return query

    def retrieve_hybrid(
        self, 
        query: str, 
        k: int = 5,
        filter_source: Optional[str] = None,
        filter_scenario_id: Optional[str] = None,
        translate: bool = False
    ) -> List[Dict[str, Any]]:
        """Realiza una búsqueda híbrida (Exacta + Semántica)."""
        
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
    
    def retrieve_with_context(
        self,
        decision: Dict[str, Any],
        contexto: Dict[str, Any],
        k: int = 5
    ) -> Dict[str, Any]:
        """Recupera conocimiento contextual para una decisión usando búsqueda híbrida."""
        # Construir query
        query = f"{decision.get('accion', '')} {contexto.get('tipo_incidente', '')}"
        
        # Intentar extraer ID de técnica si existe en la decisión
        if 'tecnica_id' in decision:
            query += f" {decision['tecnica_id']}"
        
        # Recuperar usando modo Híbrido con traducción automática
        docs = self.retrieve_hybrid(query, k=k, translate=True)
        
        # Formatear contexto para los agentes
        context_parts = []
        for i, d in enumerate(docs):
            prefix = "[MATCH EXACTO]" if d.get('is_exact') else f"[RELEVANCIA {i+1}]"
            context_parts.append(f"{prefix} ({d['source']}): {d['text']}")
            
        contexto_rag = "\n\n".join(context_parts)
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


def create_rag_client(persist_directory: Optional[str] = None, llm_client: Optional[Any] = None) -> RAGClient:
    """Factory function para crear cliente RAG."""
    return RAGClient(persist_directory=persist_directory, llm_client=llm_client)
