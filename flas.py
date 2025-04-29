import os
import time
import shutil
import subprocess
import signal
import sys
from flask import Flask, send_from_directory, render_template_string
import threading

# Paths
download_folder = "/sdcard/Download"
input_folder = "temp_input"
output_folder = "temp_output"
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Clean old output files
os.system("rm -rf temp_output/*")

# Extensions to look for
extensions = ('.jpg', '.jpeg', '.png')

# Global state
current_status = "waiting"  # can be 'waiting', 'processing', 'ready'
latest_output_image = None

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    global current_status, latest_output_image

    if current_status == "waiting":
        return "<h1>Waiting for new OMR sheet...</h1>"
    elif current_status == "processing":
        return "<h1>Processing new OMR sheet...</h1>"
    elif current_status == "ready" and latest_output_image:
        return render_template_string('''
            <h1>Latest Processed Sheet:</h1>
            <img src="/output/{{filename}}" style="max-width:100%;height:auto;">
        ''', filename=latest_output_image)
    else:
        return "<h1>Unknown status...</h1>"

@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory(output_folder, filename)

# Handle Ctrl+C
def signal_handler(sig, frame):
    print("\nStopped by user.")
    os._exit(0)  # kill everything

signal.signal(signal.SIGINT, signal_handler)

# Move and process function
def move_and_process(file_path):
    global current_status, latest_output_image

    filename = os.path.basename(file_path)
    destination = os.path.join(input_folder, filename)

    # Clean input folder
    os.system("rm -rf temp_input/*")

    # Move file
    shutil.move(file_path, destination)
    print(f"Moved {filename} to input folder.")

    # Update status
    current_status = "processing"

    # Run app.py
    subprocess.run(["python", "autoapp.py"])

    # After processing, find latest output image
    files = [f for f in os.listdir(output_folder) if f.lower().endswith(extensions)]
    if files:
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(output_folder, f)))
        latest_output_image = latest_file
        print(f"New output image: {latest_output_image}")
        current_status = "ready"

# Watcher function
def watcher():
    print("Watching for new OMR images...")
    already_seen = set()

    while True:
        try:
            files = [f for f in os.listdir(download_folder) if f.startswith("OMR_") and f.lower().endswith(extensions)]
            for file in files:
                full_path = os.path.join(download_folder, file)
                if full_path not in already_seen:
                    move_and_process(full_path)
                    already_seen.add(full_path)
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

# Main
if __name__ == "__main__":
    threading.Thread(target=watcher, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
