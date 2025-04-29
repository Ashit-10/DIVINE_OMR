import os
import time
import shutil
import subprocess
import signal
import sys
import threading
from flask import Flask, render_template_string

# Paths
download_folder = "/sdcard/Download"
input_folder = "temp_input"
output_folder = "temp_output"

os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.system("rm -rf temp_output/*")
os.system("rm -rf temp_input/*")

# Extensions to watch
extensions = ('.jpg', '.jpeg', '.png')

# Global variable to store last status
last_status = "Waiting for images..."

# Setup Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
        <html>
        <head><title>OMR Processing Status</title></head>
        <body style="font-family:Arial;text-align:center;margin-top:50px;">
            <h1>📄 OMR Processing</h1>
            <h2>Status:</h2>
            <p style="font-size:24px;color:green;">{{status}}</p>
            <p><small>Refresh the page manually to update.</small></p>
        </body>
        </html>
    """, status=last_status)

# Handle Ctrl+C to shutdown both threads
def signal_handler(sig, frame):
    print("\nStopped by user.")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

def move_and_process(file_path):
    global last_status
    filename = os.path.basename(file_path)
    destination = os.path.join(input_folder, filename)

    os.system("rm -rf temp_input/*")

    # Move the file
    shutil.move(file_path, destination)
    print(f"Moved {filename} to input folder.")
    last_status = f"Processing {filename}..."

    # Run app.py (autoapp.py)
    result = subprocess.run(["python", "autoapp.py"], capture_output=True, text=True)
    
    # Update the status after running
    if result.returncode == 0:
        last_status = f"✅ Processed {filename} successfully."
    else:
        last_status = f"❌ Error processing {filename}."

    # Clean temp_input
    os.system("rm -rf temp_input/*")

def watcher():
    global last_status
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
            time.sleep(1)  # Check every second
        except Exception as e:
            print(f"Error: {e}")
            last_status = f"Error: {str(e)}"
            time.sleep(1)

def main():
    # Start the watcher in a separate thread
    watcher_thread = threading.Thread(target=watcher)
    watcher_thread.start()

    # Start Flask server
    ip = get_ip_address()
    print(f"🌐 Visit this page from any device: http://{ip}:5000/")
    app.run(host="0.0.0.0", port=5000)

def get_ip_address():
    import subprocess
    import re
    try:
        result = subprocess.run(["ifconfig"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        matches = re.findall(r'inet (192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)', output)
        if matches:
            return matches[0]
        else:
            return "127.0.0.1"
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    main()
