import os
import json
from pathlib import Path
import re
import time

# def sanitize_name(name):
#     return re.sub(r'[\s.]+', '_', name)

def create_hardlink(source_path, target_path):
    os.link(source_path, target_path)

def update_tracking_file(tracking_file, source_path, target_path):
    """
    Update the JSON tracking file with information about processed files.
    This allows the script to keep track of which files have been hardlinked.
    """
    # Load existing json or create an empty dictionary if file doesn't exist
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    
    # Add or Update the entry for json
    data[str(source_path)] = str(target_path)

    # Write the updated data back to the file
    with open(tracking_file, 'w') as f:
        json.dump(data, f, indent=2)

def discover_files(directory):
    return [f for f in Path(directory).rglob('*') if f.is_file()]

def process_files(files, target_dir, tracking_file):

    total_files = len(files)
    processed_files = 0 # Using a list to allow modification in nested functions
    start_time = time.time()

    if not os.path.exists(tracking_file):
        with open(tracking_file, 'w') as f:
            json.dump({},f)

    for file in files:
            relative_path = file.relative_to(source_directory)
            new_hardlink = target_dir / relative_path
            new_hardlink.parent.mkdir(parents=True, exist_ok=True)
            
            processed_files += 1
            if not new_hardlink.exists():
                create_hardlink(str(file), str(new_hardlink))
                update_tracking_file(tracking_file, str(file), str(new_hardlink))
            
            progress = (processed_files / total_files)*100
            elapsed_time = time.time() - start_time
            est_total_time = elapsed_time*100 / progress if progress > 0 else 0
            est_remaining_time = est_total_time - elapsed_time
            print(f"\rProgress: {progress:.2f}% | Processed: {processed_files}/{total_files} | Estimated remaining time: {est_remaining_time:.2f} seconds", end="")

    print("\nProcessing Complete")
    print(f"Took: {time.time() - start_time:.2f} seconds")            

if __name__ == "__main__":

    current_dir = Path.cwd()
    source_directory = current_dir / "downloads/movies"
    target_directory = current_dir / "media/movies"

    hardlinks_dir = current_dir / "hardlinks"
    hardlinks_dir.mkdir(parents=True, exist_ok=True)
    # Set the tracking file path
    tracking_file = hardlinks_dir / "hardlinked_movies.json"

    print("Discovering files...")
    files_to_process = discover_files(source_directory)
    print(f"Found {len(files_to_process)} files to process")
    process_files(files_to_process, target_directory, tracking_file)
    
