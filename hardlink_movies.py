import os
import json
from pathlib import Path
import re

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

def process(source_dir, target_dir, tracking_file):
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not os.path.exists(tracking_file):
        with open(tracking_file, 'w') as f:
            json.dump({},f)

    for item in source_path.iterdir():
        if item.is_dir():
            new_target = target_path / item.name
            new_target.mkdir(parents=True, exist_ok=True)
            process(item, new_target, tracking_file)
        elif item.is_file():
            new_hardlink = target_path / item.name
            if not new_hardlink.exists():
                create_hardlink(str(item), str(new_hardlink))
                update_tracking_file(tracking_file, str(item), str(new_hardlink))

if __name__ == "__main__":

    current_dir = Path.cwd()
    source_directory = current_dir / "downloads/movies"
    target_directory = current_dir / "media/movies"

    hardlinks_dir = current_dir / "hardlinks"
    hardlinks_dir.mkdir(parents=True, exist_ok=True)
    # Set the tracking file path
    tracking_file = hardlinks_dir / "hardlinked_movies.json"

    process(source_directory, target_directory, tracking_file)
    print("Processing complete.")
