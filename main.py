import glob
import os
import threading
from mutagen.easyid3 import EasyID3
import os
from os import listdir,makedirs
from os.path import isfile,join,exists,split

target_directory = r"\\path\to\music"
num_threads = 1
myerrors = []
# Shared variable to store total count
total_processed_count = 0
total_processed_lock = threading.Lock()

# x = glob.glob(os.path.join(target_directory, "*.mp3"))
# print(x)
# print(len(x))

def clean_string(filename):
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

def append_errors_to_file(errors):
    with open('errors.txt', 'a') as file:
        file.write(errors + '\n')

def remove_empty_folders(root_folder):
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for directory in dirs:
            directory_path = os.path.join(root, directory)
            if not os.listdir(directory_path):
                os.rmdir(directory_path)
                print(f"Removed empty folder: {directory_path}")

def copy_and_sort_mp3(mp3files):
    # print(mp3files)
    import shutil
    global total_processed_count
    for mp3 in mp3files:
        try:
            # print(f'Processing {mp3}')
            trackInfo = EasyID3(mp3)
            mp3_filename = os.path.basename(mp3)
            
            artist = trackInfo.get('artist')
            album = trackInfo.get('album')
            if artist:
                artist = clean_string(artist[0])
                finalpath = join(, artist)
            
            if album:
                album = clean_string(album[0])
                finalpath = join(finalpath, album)
            
            if not exists(finalpath):
                    makedirs(finalpath, exist_ok=True)
                    print (f"Made folder(s) {finalpath}...")
                
            if not exists(join(finalpath, mp3_filename)):
                    if exists(mp3):
                        shutil.copyfile(mp3, join(finalpath, mp3_filename))
                        print(f"{mp3_filename} copied to {finalpath}.")
            with total_processed_lock:
                total_processed_count += 1
        except Exception as e:
            with total_processed_lock:
                append_errors_to_file(f"mp3: {mp3}, {e}")

def main():
    print("Welcome to the MP3 Copy and Sort Tool!")

    # Prompt user for the number of threads
    
    num_threads = int(input("Enter the number of threads to use: "))

    # Get list of MP3 files in target directory

    #  = 
    input("Enter the target directory: ")
    
    mp3_files = glob.glob(os.path.join(, "*.mp3"))
     # Calculate number of batches
    num_files = len(mp3_files)
    print(f"Number of files: {num_files}")
    num_batches = (num_files + 9) // 10  # Ceiling division
    print(f"Number of Batches: {num_batches}")
     # Create batches
    batches = [mp3_files[i:i+10] for i in range(0, num_files, 10)]
    # Create threads and start processing batches
    threads = []

    # Create threads for all batches
    for batch in batches:
        thread = threading.Thread(target=copy_and_sort_mp3, args=(batch,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Print total count of processed MP3 files
    with total_processed_lock:
        print(f"{total_processed_count} MP3 files copied and sorted successfully!")

    # Remove empty folders
    remove_empty_folders(target_directory)

if __name__ == "__main__":
    main()
