#!/usr/bin/env python3
"""
Run the FastAPI backend
Usage: python scripts/run_api.py
Or from project root: uvicorn backend.main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
