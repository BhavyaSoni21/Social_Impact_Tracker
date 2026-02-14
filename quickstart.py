import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("   SOCIAL IMPACT TRACKER - Quick Start")
    print("=" * 60)
    print()

def check_requirements():
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
    print("\n📡 Starting Backend API...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    return backend_process

def start_frontend():
    print("\n🎨 Starting Frontend Dashboard...")
    print("   URL: http://localhost:8501")
    
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    
    # Open browser
    webbrowser.open("http://localhost:8501")
    
    return frontend_process

def main():
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    try:
        backend = start_backend()
        
        frontend = start_frontend()
        
        print("\n" + "=" * 60)
        print("✓ Social Impact Tracker is running!")
        print("=" * 60)
        print("\nPress Ctrl+C to stop both services")
        print()
        
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
