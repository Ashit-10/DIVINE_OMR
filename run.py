import os
import time
import shutil
import subprocess
import signal
import sys

# Paths
download_folder = "/sdcard/Download"
input_folder = "temp_input"
output_folder = "temp_output"

os.system("rm -rf temp_output/*")
# Extensions to look for
extensions = ('.jpg', '.jpeg', '.png')

# Handle Ctrl+C
def signal_handler(sig, frame):
    print("\nStopped by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def move_and_process(file_path):
    filename = os.path.basename(file_path)
    destination = os.path.join(input_folder, filename)
    
    os.system("rm -rf temp_input/*")
    # Move file to input folder
    shutil.move(file_path, destination)
    print(f"Moved {filename} to input folder.")

    # Run app.py
    subprocess.run(["python", "autoapp.py"])

    # After processing, remove the input file
   # if os.path.exists(destination):
      #  os.remove(destination)
      #  print(f"Removed {filename} from input folder.")

def main():
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

if __name__ == "__main__":
    main()
    