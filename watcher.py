import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import threading

# CONFIGURATION
WATCH_FOLDER = r"C:\Users\gargd\Downloads\pipeline\txt_to_csv"
WATCH_FILES = ["H41 no Scrap.csv","H41 Scrap.csv","TESOG INV.csv","MUDC Inv.csv"]
CLEAN_SCRIPT = "clean.py"
DEBOUNCE_DELAY = 1.0  # seconds

# A dictionary to track debounce timers
debounce_timers = {}

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        filename = os.path.basename(event.src_path)
        if filename not in WATCH_FILES:
            return

        def run_clean():
            print(f"\n📁 Detected update in: {filename}")
            print("🧹 Cleaning data...")
            subprocess.run(["python", CLEAN_SCRIPT])
            print("✅ Data cleaned. Dash will update automatically on next refresh cycle.")
            debounce_timers.pop(filename, None)  # Clear the timer after it runs

        # If a debounce timer is already running, cancel it
        if filename in debounce_timers:
            debounce_timers[filename].cancel()

        # Start a new debounce timer
        timer = threading.Timer(DEBOUNCE_DELAY, run_clean)
        debounce_timers[filename] = timer
        timer.start()

if __name__ == "__main__":
    print(f"👀 Watching folder: {WATCH_FOLDER}")
    print(f"📝 Watching files: {', '.join(WATCH_FILES)}")

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping watcher...")
        observer.stop()

    observer.join()
