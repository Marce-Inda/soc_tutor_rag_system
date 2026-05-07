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
                        'id': hashlib.sha256(f"{mitre_id}:{name}".encode()).hexdigest(),
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
                
            chunk_id = hashlib.sha256(section[:200].encode()).hexdigest()
            
            chunks.append({
                'id': chunk_id,
                'text': section[:1000],  # Limitar a 1000 chars
                'source': source_name,
                'type': 'guideline'
            })
        
        print(f"  → {len(chunks)} chunks extraídos")
        return chunks
    
    def process_all(self):
        """Procesa todos los documentos, priorizando las fuentes globales y en inglés."""
        all_chunks = []
        
        # 1. Procesar nuevas fuentes Globales (Estructura mejorada)
        global_categories = ["frameworks", "forensics", "compliance", "techniques", "cisa", "nist", "owasp"]
        for cat in global_categories:
            cat_dir = DOCS_DIR / cat
            if cat_dir.exists():
                print(f"Buscando fuentes globales en: {cat_dir}")
                for md_file in cat_dir.glob("*.md"):
                    all_chunks.extend(self.process_markdown(md_file, f"{cat.upper()} (Global)"))

        # 2. Procesar fuentes en inglés (Fase 2 Legacy structure)
        target_docs_en = DOCS_DIR / "en"
        if target_docs_en.exists():
            print(f"Buscando fuentes oficiales en: {target_docs_en}")
            
            # MITRE (Directorio 'en/mitre')
            mitre_en = target_docs_en / "mitre" / "enterprise-attack.json"
            if mitre_en.exists():
                all_chunks.extend(self.process_mitre(mitre_en))
            
            # Otros archivos MD en 'en/'
            for md_file in target_docs_en.glob("**/*.md"):
                # Evitar procesar dos veces si ya se procesó en las categorías globales
                if any(cat in str(md_file) for cat in global_categories):
                    continue
                source_name = md_file.parent.name.upper()
                all_chunks.extend(self.process_markdown(md_file, f"{source_name} (EN)"))

        # 3. Mantener compatibilidad con fuentes originales (ES/Legacy)
        # MITRE
        mitre_legacy = DOCS_DIR / "mitre" / "enterprise-attack.json"
        if mitre_legacy.exists() and not (target_docs_en / "mitre").exists():
            all_chunks.extend(self.process_mitre(mitre_legacy))
        
        # OWASP
        owasp_file = DOCS_DIR / "owasp" / "owasp-top-10-2021.md"
        if owasp_file.exists():
            all_chunks.extend(self.process_markdown(owasp_file, 'OWASP Top 10'))
        
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
    
    chroma_host = os.environ.get("CHROMA_HOST")
    if chroma_host:
        print(f"Conectando a ChromaDB Server en {chroma_host}:8000")
        client = chromadb.HttpClient(host=chroma_host, port=8000)
    else:
        # Inicializar Chroma local
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
    
    # Agregar documentos (usar upsert para evitar errores de duplicados)
    collection.upsert(
        ids=[c['id'] for c in chunks],
        documents=[c['text'] for c in chunks],
        metadatas=[{'source': c['source'], 'type': c.get('type', 'unknown')} for c in chunks]
    )
    
    print(f"✓ Índice Chroma creado con {len(chunks)} documentos")


def generate_integrity_manifest():
    """Genera un manifiesto SHA-256 de todos los archivos fuente para verificación post-ingesta."""
    manifest = {}
    
    # Recorrer todos los archivos en data/docs y data/sample_scenarios
    for search_dir in [DOCS_DIR, BASE_DIR / "sample_scenarios"]:
        if not search_dir.exists():
            continue
        for filepath in search_dir.rglob("*"):
            if filepath.is_file():
                with open(filepath, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                rel_path = str(filepath.relative_to(BASE_DIR))
                manifest[rel_path] = {
                    "sha256": file_hash,
                    "size_bytes": filepath.stat().st_size
                }
    
    manifest_path = INDICES_DIR / "integrity_manifest.json"
    INDICES_DIR.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    
    print(f"✓ Manifiesto de integridad generado: {len(manifest)} archivos → {manifest_path}")
    return manifest


def main():
    print("=" * 60)
    print("INGESTIÓN DE DOCUMENTOS PARA RAG")
    print("=" * 60)
    
    processor = DocumentProcessor()
    chunks = processor.process_all()
    
    # Deduplicar chunks por ID antes de indexar
    unique_chunks = {}
    for c in chunks:
        unique_chunks[c['id']] = c
    
    final_chunks = list(unique_chunks.values())
    print(f"\nTotal chunks (original): {len(chunks)}")
    print(f"Total chunks (unique): {len(final_chunks)}")
    
    # Crear índice
    create_chroma_index(final_chunks)
    
    # Generar manifiesto de integridad de archivos fuente
    generate_integrity_manifest()
    
    print("\n✓ Ingestión completada")


if __name__ == "__main__":
    main()