# Ingeniería de Datos - RAG

## Contenido

Esta carpeta contiene los scripts para descargar e ingestar documentos para el RAG.

### Estructura

```
02-ingestion-datos/
├── download_docs.py    # Descarga documentos de fuentes oficiales
├── ingest_docs.py      # Procesa y crea índice vectorial
└── README.md           # Este archivo
```

## Documentos fuente

| Documento | Fuente | Tamaño |
|-----------|--------|--------|
| MITRE ATT&CK Enterprise | github.com/mitre/cti | ~8MB |
| NIST SP 800-61r3 | nist.gov | ~1MB |
| OWASP Top 10 2021 | owasp.org | ~10KB |
| CISA Playbook | cisa.gov | ~2MB |

## Uso

### Paso 1: Descargar documentos

```bash
cd 02-ingestion-datos
python download_docs.py
```

Esto descargará los documentos a `../data/docs/`

### Paso 2: Crear índice vectorial

```bash
python ingest_docs.py
```

Esto creará el índice en `../data/indices/`

### Requisitos

```bash
pip install chromadb sentence-transformers
```

## Notas

- El JSON de MITRE ATT&CK contiene ~600+ técnicas
- El PDF de NIST requiere procesamiento adicional (OCR) si se necesita texto
- El índice Chroma ocupa ~10-20MB en disco

## Costo

- **Descarga**: $0 (documentos públicos)
- **Embeddings locales**: $0 (sentence-transformers)
- **Almacenamiento**: ~20MB total