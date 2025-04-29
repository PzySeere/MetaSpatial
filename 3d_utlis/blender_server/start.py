#!/usr/bin/env python
"""
Blender Server Launcher
This script launches Blender with the server script.
"""

import subprocess
import os
import sys
import time
import platform

def find_blender_executable():
    """Find the Blender executable on the system"""
    # Common locations for Blender on macOS
    blender_paths = [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "/Applications/Blender/Blender.app/Contents/MacOS/Blender"
    ]
    
    for path in blender_paths:
        if os.path.exists(path):
            return path
    
    # If not found in common locations, try to find it in PATH
    try:
        result = subprocess.run(["which", "blender"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def kill_existing_processes():
    """Kill any existing processes using the server port"""
    try:
        # Try to kill any processes using port 65432
        if platform.system() == "Darwin":  # macOS
            os.system("lsof -i:65432 -t | xargs kill -9 2>/dev/null || true")
        elif platform.system() == "Linux":
            os.system("fuser -k 65432/tcp 2>/dev/null || true")
        elif platform.system() == "Windows":
            os.system("FOR /F \"tokens=5\" %P IN ('netstat -ano | findstr :65432') DO taskkill /F /PID %P 2>NUL")
    except Exception as e:
        print(f"Warning: Error while trying to kill existing processes: {e}")

def start_blender_server():
    """Start Blender with the server script"""
    # First, kill any existing server processes
    kill_existing_processes()
    
    blender_path = find_blender_executable()
    if not blender_path:
        print("Error: Could not find Blender executable")
        return False
    
    # Get the path to the server script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(script_dir, "blender_server.py")
    
    # On macOS, don't use --background flag to avoid GUI thread issues
    if platform.system() == "Darwin":  # macOS
        cmd = [blender_path, "--python", server_script]
    else:
        cmd = [blender_path, "--background", "--python", server_script]
    
    print(f"Starting Blender server with command: {' '.join(cmd)}")
    
    # Start the process
    process = subprocess.Popen(cmd)
    
    # Give it a moment to start up
    time.sleep(2)
    
    if process.poll() is None:
        print("Blender server started successfully")
        print("NOTE: On macOS, Blender will open with a GUI window. Do not close this window!")
        return True
    else:
        print("Error: Failed to start Blender server")
        return False

if __name__ == "__main__":
    if start_blender_server():
        print("Blender server is running in the background")
        print("Use blender_client.py to send rendering requests")
    else:
        sys.exit(1)