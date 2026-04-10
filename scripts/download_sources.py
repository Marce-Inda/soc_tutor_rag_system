"""
Script to download official English cybersecurity sources for SOC Tutor RAG.
Downloads MITRE ATT&CK, NIST, and CISA documents.
"""

import os
import requests
from pathlib import Path

# URLs for official sources
SOURCES = {
    "mitre": {
        "url": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json",
        "filename": "enterprise-attack.json",
        "description": "MITRE ATT&CK Enterprise Matrix (STIX 2.1)"
    },
    "nist": {
        "url": "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf",
        "filename": "NIST.SP.800-61r2.pdf",
        "description": "NIST Computer Security Incident Handling Guide"
    },
    "cisa": {
        "url": "https://www.cisa.gov/sites/default/files/publications/Federal_Government_Cybersecurity_Incident_and_Vulnerability_Response_Playbooks_508C.pdf",
        "filename": "CISA_Incident_Response_Playbook.pdf",
        "description": "CISA Federal Incident Response Playbook"
    }
}

def download_file(url, target_path):
    """Downloads a file from a URL to a target path."""
    print(f"  Downloading {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  ✓ Saved to {target_path}")
        return True
    except Exception as e:
        print(f"  ✗ Error downloading: {e}")
        return False

def main():
    print("=" * 60)
    print("SOC TUTOR - DATA DOWNLOADER (English Sources)")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    docs_dir = base_dir / "data" / "docs" / "en"
    
    # Create directories
    for source_name in SOURCES.keys():
        source_dir = docs_dir / source_name
        source_dir.mkdir(parents=True, exist_ok=True)
        
        source_info = SOURCES[source_name]
        target_path = source_dir / source_info["filename"]
        
        print(f"\nProcessing {source_info['description']}...")
        download_file(source_info["url"], target_path)

    print("\n" + "=" * 60)
    print("Download process completed.")
    print(f"Data stored in: {docs_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
