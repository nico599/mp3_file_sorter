import glob
import math
import threading
import time
import statistics
from mutagen.easyid3 import EasyID3
import os
import fnmatch
from os import listdir,makedirs
from os.path import isfile,join,exists,split
import shutil
import concurrent.futures

total_processed_lock = threading.Lock()

simulate = False
src_directory = r"\\path\to\src"
target_directory =  r"\\path\to\dest"
myerrors = []
# Shared variable to store total count
total_processed_count = 0
total_processed_lock = threading.Lock()
# Split files into groups
max_group_size = 30  # Number of files per group
# Define maximum number of threads
max_threads = 10

def split_files_into_groups(file_list, max_group_size):
    num_files = len(file_list)
    num_groups = math.ceil(num_files / max_group_size)
    
    groups = []
    for i in range(num_groups):
        start_index = i * max_group_size
        end_index = min((i + 1) * max_group_size, num_files)
        groups.append(file_list[start_index:end_index])
        
    return groups


# def remove_empty_folders(root_folder):
#     for root, dirs, files in os.walk(root_folder, topdown=False):
#         for directory in dirs:
#             directory_path = os.path.join(root, directory)
#             if not os.listdir(directory_path):
#                 os.rmdir(directory_path)
#                 print(f"Removed empty folder: {directory_path}")

def clean_string(filename):
    """
    This function takes a filename as a string and returns a version of it 
    cleansed of random characters aside from those permitted in 
    the valid_chars, and special characters variable.
    """
    import string
    valid_chars = f"{string.ascii_letters}{string.digits}"
    special_characters = "-_()"
    cleaned_filename = ''
    prev_char = ''
    count = 0

    for c in filename:
        if c in special_characters:
            if c == prev_char:
                count += 1
                if count > 2:
                    continue
            else:
                prev_char = c
                count = 1

        if c in valid_chars or c in f"{special_characters} {valid_chars}":
            cleaned_filename += c

    cleaned_filename = ' '.join(cleaned_filename.split())  # Strip multiple spaces
    return cleaned_filename

def get_mp3_metadata(filepath, category):
    """
    this function takes a category string which it attempts to map from the trackInfo object (EasyID3 meta-data)
    example: get_file_information(artist,r'\\path\to\my.mp3')
    returns a clean property string value or None if either the file or the property does not exist.
    """
    trackInfo = EasyID3(filepath)
    propertyValue = trackInfo[category]

    if propertyValue:
        return clean_string(str(propertyValue[0]))
    else:
        return None

def copy_and_sort_mp3(mp3Group, target_directory):
    
    print(f"\n{len(mp3Group)} files processing...\n")
    for mp3filepath in mp3Group:
        try:
            print(f"path: {mp3filepath}")
            global total_processed_count
            # exists(mp3filepath)
            # exists(target_directory)
            src_mp3_filename = os.path.basename(mp3filepath)
            print(f'Processing: {mp3filepath}.')
            artist = get_mp3_metadata(mp3filepath, 'artist')
            album = get_mp3_metadata(mp3filepath, 'album')

            if artist and album:
                destination_folder_path = os.path.join(target_directory, artist, album)
            elif artist:
                destination_folder_path = os.path.join(target_directory, artist, 'Uncategorized')
            else:
                destination_folder_path = os.path.join(target_directory, 'Uncategorized')
            
            if simulate:
                print(f"SIMULATION ONLY: Would mkdir {destination_folder_path}...\n")
            else:
                os.makedirs(destination_folder_path, exist_ok=True)
            destination_file_path = os.path.join(destination_folder_path, src_mp3_filename)
            if not os.path.exists(destination_file_path):
                if simulate:
                    print(f"SIMULATION ONLY: Would copy {mp3filepath} to {destination_file_path}\n")
                else:
                    shutil.copyfile(mp3filepath, destination_file_path)

        except Exception as e:
            with total_processed_lock:
                append_errors_to_file(f"Error processing mp3: {src_mp3_filename}, {e}")
        finally:
            # Increment processed count
            with total_processed_lock:
                total_processed_count += 1
                print(f"{total_processed_count} Processed...")

def append_errors_to_file(errors):
    with open('errors.txt', 'a') as file:
        file.write(errors + '\n')

def split_files_into_groups(file_list, max_group_size=30):
    num_files = len(file_list)
    print(f"Recieved file_list of length: {num_files}")
    num_groups = math.ceil(num_files / max_group_size)
    groups = []
    for i in range(num_groups):
        start_index = i * max_group_size
        end_index = min((i + 1) * max_group_size, num_files)
        groups.append(file_list[start_index:end_index])
    return groups

def execute_commands_in_threads(gs, max_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        print(f"\nfound {len(gs)} groups\n")
        for g in gs:
            executor.submit(copy_and_sort_mp3, g, target_directory)
            # executor.map(copy_and_sort_mp3, g, target_directory)

# Function to find mp3 files recursively using os.walk and fnmatch
def find_mp3_files(root_dir):
    mp3_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, '*.mp3'):
                mp3_files.append(os.path.join(dirpath, filename))
    return mp3_files

def main():
    print("""
          Welcome to the MP3 Copy and Sort Tool!
          This tool will organize your target MP3 files
          based on the artist and album mp3 meta-data.\n\n
          """)
    
    # Example usage

    src_mp3_files = find_mp3_files(src_directory)
        # src_mp3_files.append(fnmatch.fnmatch(dirpath, os.path.join(root_dir, album_filter)):)
    # src_mp3_files = fnmatch.fnmatch(dirpath, os.path.join(root_dir, album_filter)):
    print(f"{len(src_mp3_files)} files found.")
    time.sleep(2)
    file_groups = split_files_into_groups(src_mp3_files, max_group_size)
    execute_commands_in_threads(file_groups, max_threads)


if __name__ == "__main__":
      main()
