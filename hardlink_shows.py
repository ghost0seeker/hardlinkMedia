import os
import json
from pathlib import Path
import re
import time

def sanitize_show_filename(filename):
    # Patterns
    show_pattern = r'^(.*?)\s*-?\s*S(\d+)E(\d+)\s*-?\s*(.*?)(?:\s*\((\d{4})\))?(?:\s*\((.*?)\))?\s*(\d+p)?.*?(\.[^.]+)$'
    movie_pattern = r'^(.*?)\s*(?:\((\d{4})\))?\s*-?\s*(.*?)(?:\s*\((.*?)\))?\s*(\d+p)?.*?(\.[^.]+)$'
    extra_pattern = r'^(.*?)(?:\s*\((\d{4})\))?(\.[^.]+)$'
    temp_file_pattern = r'^\.([a-f0-9]+)\.parts$'

    # Check for temporary files
    if re.match(temp_file_pattern, filename):
        return None  # Skip temporary files

    # Try matching show pattern
    match = re.match(show_pattern, filename, re.IGNORECASE)
    if match:
        show_name, season, episode, episode_name, year, extra_info, quality, extension = match.groups()
        new_filename = f"{show_name.strip()}"
        if year:
            new_filename += f" ({year})"
        new_filename += f" S{season.zfill(2)}E{episode.zfill(2)}"
        if episode_name:
            new_filename += f" - {episode_name.strip()}"
        if quality:
            new_filename += f" {quality}"
        if extra_info:
            new_filename += f" ({extra_info})"
        new_filename += extension
        return new_filename

    # Try matching movie pattern
    match = re.match(movie_pattern, filename, re.IGNORECASE)
    if match:
        movie_name, year, extra_name, extra_info, quality, extension = match.groups()
        new_filename = f"{movie_name.strip()}"
        if year:
            new_filename += f" ({year})"
        if extra_name:
            new_filename += f" - {extra_name.strip()}"
        if quality:
            new_filename += f" {quality}"
        if extra_info:
            new_filename += f" ({extra_info})"
        new_filename += extension
        return new_filename

    # Try matching extra content pattern
    match = re.match(extra_pattern, filename, re.IGNORECASE)
    if match:
        extra_name, year, extension = match.groups()
        new_filename = f"{extra_name.strip()}"
        if year:
            new_filename += f" ({year})"
        new_filename += extension
        return new_filename

    print(f"No match found for: {filename}")
    return filename

def sanitize_folder_name(name):
    """
    Replace spaces and dots in the name with underscores.
    This helps create more uniform directory names.
    """
    return re.sub(r'[\s.]+', '_', name)

def create_hardlink(source_path, target_path):
    """
    Replace spaces and dots in the name with underscores.
    This helps create more uniform directory names.
    """
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

def process_directory(source_dir, target_dir, tracking_file, processed_files, total_files, start_time, unprocessed_files):
    """
    Recursively process a directory, creating hardlinks for all files
    and recreating the directory structure in the target location.
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # Create the target directory if it doesn't exists (it literally doesn't exists?)
    if not target_path.exists():
        target_path.mkdir(parents=True)
    
    #Check for Featurettes Folders
    is_in_featurettes = any(part.lower() == "featurettes" for part in source_path.parts)

    # Iterate through all items in the source directory, this is where the fun begins
    for item in source_path.iterdir():
        try:
            if item.is_dir():
                # If it's a folder, process it recursively
                new_target = target_path / item.name # removed folder sanitizing
                process_directory(item, new_target, tracking_file, processed_files, total_files, start_time, unprocessed_files)
            elif item.is_file():
                new_filename = sanitize_show_filename(item.name)
                
                if new_filename is None:
                    print(f"Skipping temporary file: {item.name}")
                    continue  # Skip this file and move to the next one
                
                if is_in_featurettes:
                    relative_path = item.relative_to(source_path)
                    new_file = target_path / relative_path
                    new_file.parent.mkdir(parents=True, exist_ok=True)
                else:
                    new_file = target_path / new_filename

                processed_files[0] += 1
                if not new_file.exists():
                    create_hardlink(item, new_file)
                    update_tracking_file(tracking_file, str(item), str(new_file))

                # Update and Display progress
                progress = (processed_files[0] / total_files)*100
                elapsed_time = time.time() - start_time
                est_total_time = elapsed_time*100 / progress if progress > 0 else 0
                est_remaining_time = est_total_time - elapsed_time
                print(f"\rProgress: {progress:.2f}% | Processed: {processed_files[0]}/{total_files} | Estimated remaining time: {est_remaining_time:.2f} seconds", end="")
    
        except Exception as e:
            print(f"\nError processing {item}: {str(e)}")
            unprocessed_files.append(str(item))
    
    # if is_in_featurettes:
    #     print(f"\nProcessed Featurette Directory: {source_path}")

def process_tv_shows(source_dir, target_dir, tracking_file):
    """
    Main function to process the entire TV show library.
    Sets up the environment and initiates the recursive processing.
    """
    # Convert to absolute paths
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    # Create json if it doesn't exist
    if not os.path.exists(tracking_file):
        with open(tracking_file, 'w') as f:
            json.dump({}, f)
            #Need to check how this works wrt to json.dump above
    
    # Count total files to process, What?
    total_files = sum(1 for _ in source_path.rglob('*') if _.is_file())
    processed_files = [0] # Using a list to allow modification in nested functions
    unprocessed_files = []
    start_time = time.time() # Not sure how this works wrt to above time.time() call

    print(f"Found {total_files} files to process")

    #Start Recursive processing
    process_directory(source_path, target_path, tracking_file, processed_files, total_files, start_time, unprocessed_files)

    print("\nProcessing Complete.")
    print(f"Took: {time.time() - start_time:.2f} seconds")
    # What's :.2f notation?
   
    # print(f"Unprocessed files: {len(unprocessed_files)}")
    # if unprocessed_files:
    #     print("\nFiles not processed for hardlinking:")
    #     for file in unprocessed_files:
    #         print(file)
    # else:
        #print("\nAll files were processed successfully.")

if __name__ == "__main__":

    current_dir = Path.cwd()
    source_directory = current_dir / "downloads/shows"
    target_directory = current_dir / "media/shows"
    
    # tracking_file = current_dir / "hardlinked_shows.json"
    hardlinks_dir = current_dir / "hardlinks"
    hardlinks_dir.mkdir(exist_ok=True)
    # Set the tracking file path
    tracking_file = hardlinks_dir / "hardlinked_shows.json"

    process_tv_shows(source_directory, target_directory, tracking_file)
