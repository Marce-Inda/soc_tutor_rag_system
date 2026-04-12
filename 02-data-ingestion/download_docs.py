"""
Script de descarga de documentos para RAG.
Ejecutar: python download_docs.py
"""

import os
import urllib.request
import json
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent.parent / "data" / "docs"
BASE_DIR.mkdir(parents=True, exist_ok=True)

DOCS_CONFIG = {
    "mitre": {
        "url": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
        "filename": "enterprise-attack.json",
        "description": "MITRE ATT&CK Enterprise Matrix (STIX format)",
        "size_mb": "~8MB"
    },
    "nist": {
        "url": "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf",
        "filename": "nist-800-61r3.pdf",
        "description": "NIST SP 800-61r3 - Incident Response Recommendations",
        "size_mb": "~1MB"
    },
    "owasp": {
        "url": "https://raw.githubusercontent.com/OWASP/www-project-top-10/master/2021/OWASP-Top-10-2021.md",
        "filename": "owasp-top-10-2021.md",
        "description": "OWASP Top 10 2021",
        "size_mb": "~10KB"
    },
    "cisa": {
        "url": "https://www.cisa.gov/sites/default/files/2023-11/cisa-csrm-playbook-508c.pdf",
        "filename": "cisa-cyber-safety-response-playbook.pdf",
        "description": "CISA Cyber Safety Response Playbook",
        "size_mb": "~2MB"
    }
}


def download_file(url: str, filepath: Path) -> bool:
    """Descarga un archivo de una URL."""
    try:
        print(f"Descargando: {url[:60]}...")
        urllib.request.urlretrieve(url, filepath)
        size = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ Descargado: {filepath.name} ({size:.2f} MB)")
        return True
    except Exception as e:
        print(f"✗ Error descargando {url}: {e}")
        return False


def download_mitre_subset():
    """Descarga solo las técnicas relevantes de MITRE (JSON más pequeño)."""
    # URL alternativa con técnicas filtradas (si existe)
    # Por ahora usamos el enterprise-attack completo
    mitre_dir = BASE_DIR / "mitre"
    mitre_dir.mkdir(exist_ok=True)
    
    config = DOCS_CONFIG["mitre"]
    filepath = mitre_dir / config["filename"]
    
    return download_file(config["url"], filepath)


def main():
    print("=" * 60)
    print("DESCARGA DE DOCUMENTOS PARA RAG")
    print("=" * 60)
    
    results = {}
    
    # MITRE ATT&CK
    print("\n[1/4] Descargando MITRE ATT&CK...")
    results["mitre"] = download_mitre_subset()
    
    # NIST 800-61
    print("\n[2/4] Descargando NIST 800-61r3...")
    nist_dir = BASE_DIR / "nist"
    nist_dir.mkdir(exist_ok=True)
    results["nist"] = download_file(DOCS_CONFIG["nist"]["url"], nist_dir / DOCS_CONFIG["nist"]["filename"])
    
    # OWASP
    print("\n[3/4] Descargando OWASP Top 10...")
    owasp_dir = BASE_DIR / "owasp"
    owasp_dir.mkdir(exist_ok=True)
    results["owasp"] = download_file(DOCS_CONFIG["owasp"]["url"], owasp_dir / DOCS_CONFIG["owasp"]["filename"])
    
    # CISA
    print("\n[4/4] Descargando CISA Playbook...")
    cisa_dir = BASE_DIR / "cisa"
    cisa_dir.mkdir(exist_ok=True)
    results["cisa"] = download_file(DOCS_CONFIG["cisa"]["url"], cisa_dir / DOCS_CONFIG["cisa"]["filename"])
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for name, success in results.items():
        status = "✓ OK" if success else "✗ FALLO"
        print(f"{name}: {status}")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)