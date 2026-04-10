"""
Script de ingestión de documentos para Chroma.
Procesa los documentos bajados y crea el índice vectorial.

Ejecutar: python ingest_docs.py
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import hashlib

# Intentar importar chroma - si no está, usar fallback
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Chroma no instalado. Install: pip install chromadb")

# Imports adicionales
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("sentence-transformers no instalado. Install: pip install sentence-transformers")


# Rutas
BASE_DIR = Path(__file__).parent.parent / "data"
DOCS_DIR = BASE_DIR / "docs"
INDICES_DIR = BASE_DIR / "indices"


class DocumentProcessor:
    """Procesador de documentos para RAG."""
    
    def __init__(self):
        self.docs_chunks = []
        
    def process_mitre(self, filepath: Path) -> List[Dict]:
        """Procesa el JSON de MITRE ATT&CK."""
        print(f"Procesando MITRE: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = []
        
        # Extraer objetos del bundle STIX
        objects = data.get('objects', [])
        
        for obj in objects:
            # Solo técnicas (attack-pattern)
            if obj.get('type') == 'attack-pattern':
                name = obj.get('name', '')
                description = obj.get('description', '')[:500]  # Limitar descripción
                external_ids = obj.get('external_references', [])
                
                # Buscar ID de MITRE
                mitre_id = None
                for ref in external_ids:
                    if 'attack.mitre.org' in ref.get('source_name', ''):
                        mitre_id = ref.get('external_id', '')
                        break
                
                if name:
                    chunks.append({
                        'id': hashlib.md5(name.encode()).hexdigest(),
                        'text': f"Técnica MITRE {mitre_id}: {name}. {description}",
                        'source': 'MITRE ATT&CK',
                        'type': 'technique',
                        'mitre_id': mitre_id,
                        'name': name
                    })
        
        print(f"  → {len(chunks)} técnicas extraídas")
        return chunks
    
    def process_markdown(self, filepath: Path, source_name: str) -> List[Dict]:
        """Procesa documentos Markdown."""
        print(f"Procesando {source_name}: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split por encabezados o líneas en blanco
        chunks = []
        sections = content.split('\n## ')
        
        for i, section in enumerate(sections):
            if len(section) < 50:
                continue
                
            chunk_id = hashlib.md5(section[:100].encode()).hexdigest()
            
            chunks.append({
                'id': chunk_id,
                'text': section[:1000],  # Limitar a 1000 chars
                'source': source_name,
                'type': 'guideline'
            })
        
        print(f"  → {len(chunks)} chunks extraídos")
        return chunks
    
    def process_all(self):
        """Procesa todos los documentos."""
        all_chunks = []
        
        # MITRE
        mitre_file = DOCS_DIR / "mitre" / "enterprise-attack.json"
        if mitre_file.exists():
            all_chunks.extend(self.process_mitre(mitre_file))
        
        # OWASP
        owasp_file = DOCS_DIR / "owasp" / "owasp-top-10-2021.md"
        if owasp_file.exists():
            all_chunks.extend(self.process_markdown(owasp_file, 'OWASP Top 10'))
        
        # NIST (PDF no se procesa fácilmente, saltamos)
        nist_file = DOCS_DIR / "nist" / "nist-800-61r3.pdf"
        if nist_file.exists():
            print(f"Nota: NIST PDF no procesado automáticamente (requiere OCR)")
        
        self.docs_chunks = all_chunks
        return all_chunks


def create_chroma_index(chunks: List[Dict]):
    """Crea el índice vectorial con Chroma."""
    if not CHROMA_AVAILABLE:
        print("Chroma no disponible. Guardando chunks como JSON.")
        output_file = INDICES_DIR / "chunks.json"
        with open(output_file, 'w') as f:
            json.dump(chunks, f, indent=2)
        print(f"Guardado en: {output_file}")
        return
    
    # Inicializar Chroma
    INDICES_DIR.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(INDICES_DIR))
    
    # Crear u obtener colección
    collection = client.get_or_create_collection(
        name="cybersec-knowledge",
        metadata={"description": "Conocimiento de ciberseguridad para RAG"}
    )
    
    # Embeddings
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode([c['text'] for c in chunks])
    else:
        # Fallback: Chroma tiene embeddings por defecto
        embeddings = None
    
    # Agregar documentos
    collection.add(
        ids=[c['id'] for c in chunks],
        documents=[c['text'] for c in chunks],
        metadatas=[{'source': c['source'], 'type': c.get('type', 'unknown')} for c in chunks]
    )
    
    print(f"✓ Índice Chroma creado con {len(chunks)} documentos")


def main():
    print("=" * 60)
    print("INGESTIÓN DE DOCUMENTOS PARA RAG")
    print("=" * 60)
    
    processor = DocumentProcessor()
    chunks = processor.process_all()
    
    print(f"\nTotal chunks: {len(chunks)}")
    
    # Crear índice
    create_chroma_index(chunks)
    
    print("\n✓ Ingestión completada")


if __name__ == "__main__":
    main()