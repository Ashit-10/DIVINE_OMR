import os
import shutil

def clean_and_move_files():
    # Paths for source and destination
    download_folder = '/sdcard/Download/'
    input_folder = '/sdcard/DIVINE_OMR/input/'
    answer_key_dest = '/sdcard/DIVINE_OMR/answer_key.txt'

    # Step 1: Clean all files in the input folder
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Step 2: Move captured_image* files to input folder
    for filename in os.listdir(download_folder):
        if filename.startswith('OMR'):
            source_path = os.path.join(download_folder, filename)
            destination_path = os.path.join(input_folder, filename)
            shutil.move(source_path, destination_path)
            print(f'Moved: {filename}')

            # Remove spaces from filename after moving
            new_name = filename.replace(' ', '')
            if new_name != filename:
                new_path = os.path.join(input_folder, new_name)
                os.rename(destination_path, new_path)
                print(f'Renamed to: {new_name}')

    # Step 3: Move the first found answer_key*.txt file to the answer_key.txt destination
    for filename in os.listdir(download_folder):
        if filename.startswith('answer_key') and filename.endswith('.txt'):
            source_path = os.path.join(download_folder, filename)

            # Optional: remove spaces before renaming
            if ' ' in filename:
                new_filename = filename.replace(' ', '')
                new_source_path = os.path.join(download_folder, new_filename)
                os.rename(source_path, new_source_path)
                source_path = new_source_path
                print(f'Renamed answer key file to remove spaces: {new_filename}')

            shutil.move(source_path, answer_key_dest)
            print(f'Moved answer key: {filename}')
            break  # Move only the first found answer_key*.txt file

if __name__ == "__main__":
    clean_and_move_files()
