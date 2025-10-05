#!/usr/bin/env python3
"""
Crash-Resistant Bicep Curl Tracker Launcher
Automatically restarts the tracker if it crashes
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def log_message(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_bicep_tracker():
    """Run the bicep tracker with crash recovery"""
    max_restarts = 5
    restart_count = 0
    
    log_message("🏋️ Starting Crash-Resistant Bicep Curl Tracker")
    log_message("Press Ctrl+C to stop completely")
    
    while restart_count < max_restarts:
        try:
            log_message(f"🚀 Starting tracker (attempt {restart_count + 1}/{max_restarts})")
            
            # Run the bicep tracker
            result = subprocess.run([
                sys.executable, "advanced_bicep_tracker.py"
            ], check=False)
            
            if result.returncode == 0:
                log_message("✅ Tracker ended normally")
                break
            else:
                log_message(f"⚠️  Tracker crashed with code {result.returncode}")
                restart_count += 1
                
                if restart_count < max_restarts:
                    log_message(f"🔄 Restarting in 3 seconds... ({restart_count}/{max_restarts})")
                    time.sleep(3)
                else:
                    log_message("❌ Maximum restart attempts reached")
                    break
                    
        except KeyboardInterrupt:
            log_message("🛑 Stopped by user")
            break
        except Exception as e:
            log_message(f"❌ Launcher error: {e}")
            restart_count += 1
            if restart_count < max_restarts:
                time.sleep(3)
    
    log_message("🏁 Bicep tracker launcher finished")

if __name__ == "__main__":
    run_bicep_tracker()