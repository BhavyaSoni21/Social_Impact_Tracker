"""
Quick Start Script for Social Impact Tracker
Run this script to quickly start both backend API and frontend dashboard
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("   SOCIAL IMPACT TRACKER - Quick Start")
    print("=" * 60)
    print()

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import streamlit
        import sqlalchemy
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required packages: {e}")
        print("\nPlease install requirements first:")
        print("  pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("\n📡 Starting Backend API...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)  # Wait for backend to start
    return backend_process

def start_frontend():
    """Start the Streamlit frontend"""
    print("\n🎨 Starting Frontend Dashboard...")
    print("   URL: http://localhost:8501")
    
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)  # Wait for frontend to start
    
    # Open browser
    webbrowser.open("http://localhost:8501")
    
    return frontend_process

def main():
    """Main execution"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Start backend
        backend = start_backend()
        
        # Start frontend
        frontend = start_frontend()
        
        print("\n" + "=" * 60)
        print("✓ Social Impact Tracker is running!")
        print("=" * 60)
        print("\nPress Ctrl+C to stop both services")
        print()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        
        try:
            backend.terminate()
            frontend.terminate()
            print("✓ Services stopped successfully")
        except:
            pass
        
        sys.exit(0)

if __name__ == "__main__":
    main()
