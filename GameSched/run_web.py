#!/usr/bin/env python3
"""
Launch script for the web-based CPU Scheduling Game
Run this to start the modern web interface
"""

import subprocess
import sys
import webbrowser
import time
import threading

def install_requirements():
    """Install required packages"""
    try:
        # Install only web dependencies (skip pygame for web version)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==2.3.3", "flask-socketio==5.3.6", "python-socketio==5.8.0"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        sys.exit(1)

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:5000')

def main():
    print("GameSched: CPU Scheduling Visualizer")
    print("=" * 50)
    
    # Install dependencies
    print("Installing dependencies...")
    install_requirements()
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start web server
    print("Starting web server...")
    print("Opening browser at http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    try:
        from web_server import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nGame server stopped")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all game files are present")

if __name__ == "__main__":
    main()