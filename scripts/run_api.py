#!/usr/bin/env python3
"""
Run the FastAPI backend
Usage: python scripts/run_api.py
Or from project root: uvicorn backend.main:app --reload
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    # Disable reload on Windows due to multiprocessing issues
    reload = sys.platform != "win32"
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload,
        reload_dirs=["backend"] if reload else None,
    )
