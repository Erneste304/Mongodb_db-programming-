"""
Unified entry point for Petroleum Station Management System
Runs both FastAPI backend and NiceGUI frontend together
"""
from frontend.nicegui_app import create_nicegui_app
import uvicorn
from backend.main import app as fastapi_app
import sys
import os
import asyncio
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    # Run NiceGUI frontend
    create_nicegui_app(fastapi_app)
