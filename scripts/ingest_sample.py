#!/usr/bin/env python3
"""
Index sample documents into the vector store.
Run from project root: python scripts/ingest_sample.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.app.rag.ingestion import ingest_directory


def main():
    sample_dir = project_root / "data" / "sample"
    if not sample_dir.exists():
        print("Erreur: data/sample introuvable")
        sys.exit(1)

    print("Indexation des documents dans data/sample...")
    stats = ingest_directory(sample_dir)
    print(f"Terminé: {stats['files']} fichiers, {stats['chunks']} chunks indexés")


if __name__ == "__main__":
    main()
