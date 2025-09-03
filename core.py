# core.py
# Contains the main logic for copying and moving files and directories.

import os
import shutil
import logging
from pathlib import Path

# --- Configuration for Logging ---
LOG_FILE = 'datasync_log.txt'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def is_safe_path(path: Path) -> bool:
    """
    Checks if a path is safe to write to.
    A safe path is one that resolves within the current user's home directory 
    or a subdirectory of the current working directory.
    This helps prevent path traversal attacks.
    """
    try:
        # Resolve the path to its absolute form, following any symlinks.
        abs_path = path.resolve(strict=True)
        # Get the user's home directory.
        home_dir = Path.home().resolve(strict=True)
        # Get the current working directory.
        cwd = Path.cwd().resolve(strict=True)
        
        # A path is "safe" if it is within the user's home directory OR
        # within the current working directory.
        is_in_home = home_dir in abs_path.parents or abs_path == home_dir
        is_in_cwd = cwd in abs_path.parents or abs_path == cwd
        
        return is_in_home or is_in_cwd
    except (FileNotFoundError, RuntimeError):
        # The path doesn't exist or is a broken symlink, but we can still check
        # its intended absolute location.
        abs_path = Path(os.path.abspath(path))
        home_dir = Path.home()
        cwd = Path.cwd()
        is_in_home = home_dir in abs_path.parents or abs_path == home_dir
        is_in_cwd = cwd in abs_path.parents or abs_path == cwd
        return is_in_home or is_in_cwd
    except Exception as e:
        logging.error(f"Path safety check failed for '{path}': {e}")
        return False


def sync_data(source_path: str, destination_path: str, operation: str = 'copy'):
    """
    Synchronizes data from a source to a destination.
    """
    source = Path(source_path)
    destination = Path(destination_path)
    
    # --- SECURITY: Path Validation ---
    if not source.exists():
        message = f"Error: Source path '{source}' does not exist."
        logging.error(message)
        return False, message

    if not is_safe_path(destination):
        message = f"Error: Destination path '{destination}' is outside of the allowed directories (your home directory or current working directory)."
        logging.error(message)
        return False, message
        
    # SECURITY: Prevent copying a directory into itself
    try:
        if source.resolve() in destination.resolve().parents or source.resolve() == destination.resolve():
            message = "Error: Cannot copy or move a directory into itself or a subdirectory."
            logging.error(message)
            return False, message
    except FileNotFoundError:
        # This can happen if the destination doesn't exist yet, which is fine.
        pass

    # Ensure the destination directory exists before file operations
    if not destination.is_dir():
        try:
            destination.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created destination directory: '{destination}'")
        except OSError as e:
            message = f"Error: Could not create destination directory '{destination}'. Reason: {e}"
            logging.error(message)
            return False, message

    try:
        if source.is_dir():
            dest_dir = destination / source.name
            if operation == 'copy':
                shutil.copytree(source, dest_dir, dirs_exist_ok=True)
                message = f"Successfully copied directory '{source}' to '{dest_dir}'."
            elif operation == 'move':
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.move(str(source), str(destination))
                message = f"Successfully moved directory '{source}' to '{destination}'."
            else:
                message = f"Invalid operation '{operation}' specified for directory."
                logging.error(message)
                return False, message
                
        elif source.is_file():
            if operation == 'copy':
                shutil.copy2(source, destination)
                message = f"Successfully copied file '{source}' to '{destination}'."
            elif operation == 'move':
                shutil.move(str(source), str(destination))
                message = f"Successfully moved file '{source}' to '{destination}'."
            else:
                message = f"Invalid operation '{operation}' specified for file."
                logging.error(message)
                return False, message
        else:
            message = f"Error: Source path '{source}' is not a file or directory."
            logging.error(message)
            return False, message
            
        logging.info(message)
        return True, message

    except (shutil.Error, OSError) as e:
        message = f"An error occurred during the '{operation}' operation: {e}"
        logging.error(message)
        return False, message

if __name__ == '__main__': # pragma: no cover
    # This block is for direct script execution and testing
    print("Executing core.py for demonstration...")
    os.makedirs("demo_source/sub", exist_ok=True)
    with open("demo_source/demo.txt", "w") as f: f.write("hello")
    os.makedirs("demo_dest", exist_ok=True)
    
    print("\n--- Testing Safe Copy ---")
    sync_data("demo_source", "demo_dest")
    
    print("\n--- Testing Unsafe Destination (should fail) ---")
    sync_data("demo_source", "/etc/unsafe_dest") # Unsafe path
    
    print("\n--- Testing Self-Copy (should fail) ---")
    sync_data("demo_source", "demo_source/sub") # Self-copy
    
    shutil.rmtree("demo_source")
    shutil.rmtree("demo_dest")
    print("\nDemonstration complete.")

