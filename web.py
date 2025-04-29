import os
import time
import shutil
import subprocess
import signal
import sys
import threading
from flask import Flask, send_from_directory, render_template_string, jsonify

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# Paths
# download_folder = "error"
download_folder = "/sdcard/Download"
input_folder = "temp_input"
output_folder = "temp_output"

# Extensions to look for
extensions = ('.jpg', '.jpeg', '.png')

# Globals
processing = False
current_filename = ""
latest_output_filename = ""

app = Flask(__name__)

# Handle Ctrl+C
def signal_handler(sig, frame):
    print("\nStopped by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def move_and_process(file_path):
    global processing, current_filename, latest_output_filename
    filename = os.path.basename(file_path)
    current_filename = filename
    processing = True

    os.system("rm -rf temp_input/*")
    os.system("rm -rf temp_output/*")
    shutil.move(file_path, os.path.join(input_folder, filename))
    print(f"Moved {filename} to input folder.")

    # Run your processing app

    process = subprocess.Popen(
        ["python", "autoapp.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate()

    if stdout:
        print("Output from autoapp.py:")
        print(stdout)

    if stderr:
        print("Errors from autoapp.py:", file=sys.stderr)
        print(stderr, file=sys.stderr)
    # res = subprocess.run(["python3", "autoapp.py"], capture_output=True, text=True)
    # print(res.stdout)
    # print(res.stderr)

    # Assume autoapp.py outputs a file in temp_output
    output_files = os.listdir(output_folder)
    output_files = [f for f in output_files if f.lower().endswith(extensions)]

    if output_files:
        latest_output_filename = output_files[-1]  # pick last generated file
        print(f"Processed output: {latest_output_filename}")
    else:
        latest_output_filename = ""

    processing = False

def watch_folder():
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
            time.sleep(1)  # Check every 1 second
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OMR Result Viewer</title>
        <script>
            function checkProcessingStatus() {
                fetch("/status")
                    .then(response => response.json())
                    .then(data => {
                        if (data.processing) {
                            document.getElementById('status').innerText = "Processing " + data.filename + "...";
                            document.getElementById('result').style.display = "none";
                        } else if (data.filename) {
                            document.getElementById('status').innerText = "";
                            document.getElementById('result').style.display = "block";
                            document.getElementById('result').src = "/temp_output/" + data.filename + "?t=" + new Date().getTime();
                        } else {
                            document.getElementById('status').innerText = "No OMR sheet processed yet.";
                            document.getElementById('result').style.display = "none";
                        }
                    });
            }

            setInterval(checkProcessingStatus, 2000);  // Poll every 2 seconds
        </script>
    </head>
    <body style="text-align: center;">
        <h1>OMR Result Viewer</h1>
        <h2 id="status">Waiting for OMR sheet...</h2>
        <img id="result" style="max-width:100%; display:none;">
    </body>
    </html>
    ''')

@app.route('/status')
def status():
    global processing, current_filename, latest_output_filename
    return jsonify({
        "processing": processing,
        "filename": current_filename if processing else latest_output_filename
    })

@app.route('/temp_output/<path:filename>')
def serve_output_file(filename):
    return send_from_directory(output_folder, filename)

if __name__ == "__main__":
    threading.Thread(target=watch_folder, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
