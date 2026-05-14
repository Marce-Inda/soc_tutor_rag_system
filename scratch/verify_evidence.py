
import hashlib
import json
import os
from pathlib import Path

BASE_DIR = Path("/home/marce-i/Documentos/proyectos/proyecto_final_especializacion/soc-tutor-rag-system/data")
MANIFEST_PATH = BASE_DIR / "indices" / "integrity_manifest.json"

def verify():
    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    mismatches = []
    missing = []
    
    for rel_path, info in manifest.items():
        full_path = BASE_DIR / rel_path
        if not full_path.exists():
            missing.append(rel_path)
            continue
            
        with open(full_path, "rb") as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()
            
        if current_hash != info["sha256"]:
            mismatches.append(rel_path)

    print(f"Verified {len(manifest)} files.")
    if missing:
        print(f"Missing files ({len(missing)}):")
        for m in missing: print(f"  - {m}")
    if mismatches:
        print(f"Hash mismatches ({len(mismatches)}):")
        for m in mismatches: print(f"  - {m}")
    
    if not missing and not mismatches:
        print("✓ All files match the manifest integrity.")
    else:
        print("✗ Integrity check failed. Re-run ingestion recommended.")

if __name__ == "__main__":
    verify()
