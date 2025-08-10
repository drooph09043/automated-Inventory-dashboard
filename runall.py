import subprocess
import time

try:
    # Step 1: Run the initial cleaning script
    print("🔄 Running clean.py to prepare data...")
    subprocess.run(["python", "clean.py"])

    # Step 2: Start the watcher in the background
    print("👀 Starting watcher.py to monitor file changes...")
    watcher_process = subprocess.Popen(["python", "watcher.py"])

    # Optional delay to let watcher start properly
    time.sleep(2)

    # Step 3: Launch the Dash dashboard
    print("🚀 Launching app.py (Dash Dashboard)...")
    subprocess.run(["python", "app.py"])

except KeyboardInterrupt:
    print("\n🛑 Detected keyboard interrupt. Cleaning up...")

finally:
    # Cleanup: Kill watcher process when app.py exits or on Ctrl+C
    print("🛑 Stopping watcher...")
    watcher_process.terminate()
