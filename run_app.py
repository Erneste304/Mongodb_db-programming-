"""
Unified entry point for Petroleum Station Management System
Runs both FastAPI backend and NiceGUI frontend together
"""
import sys
import os
import asyncio
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app as fastapi_app
import uvicorn
from frontend.nicegui_app import create_nicegui_app


def run_backend():
    """Run FastAPI backend"""
    uvicorn.run(
        "backend.main:app",
        host="localhost",
        port=8000,
        reload=False
    )


if __name__ == "__main__":
    # Run backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    import time
    time.sleep(3)
    
    # Run NiceGUI frontend
    create_nicegui_app()
