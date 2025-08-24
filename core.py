# core.py
# Contains the main logic for copying and moving files and directories.

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# --- Configuration for Logging ---
# This sets up a logger to save operation details into a file.
LOG_FILE = 'datasync_log.txt'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def sync_data(source_path: str, destination_path: str, operation: str = 'copy'):
    """
    Synchronizes data from a source to a destination.

    This is the main function that handles the logic for both copying and moving
    files and directories. It validates paths, checks for errors, and logs
    every action.

    Args:
        source_path (str): The path to the source file or directory.
        destination_path (str): The path to the destination directory.
        operation (str): The operation to perform ('copy' or 'move'). 
                         Defaults to 'copy'.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating success or failure,
                          and a message describing the outcome.
    """
    source = Path(source_path)
    destination = Path(destination_path)
    
    # --- Path Validation ---
    if not source.exists():
        message = f"Error: Source path '{source}' does not exist."
        logging.error(message)
        return False, message

    if not destination.is_dir():
        try:
            # Create destination directory if it doesn't exist
            destination.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created destination directory: '{destination}'")
        except OSError as e:
            message = f"Error: Could not create destination directory '{destination}'. Reason: {e}"
            logging.error(message)
            return False, message

    try:
        # --- Perform The Operation ---
        if source.is_dir():
            # If the source is a directory, use copytree or move
            # We create a subdirectory in the destination to hold the contents
            dest_dir = destination / source.name
            if operation == 'copy':
                # shutil.copytree requires the destination not to exist
                if dest_dir.exists():
                    # Add a timestamp to make the folder name unique
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_dir = destination / f"{source.name}_{timestamp}"
                
                shutil.copytree(source, dest_dir)
                message = f"Successfully copied directory '{source}' to '{dest_dir}'."
            elif operation == 'move':
                shutil.move(str(source), str(dest_dir))
                message = f"Successfully moved directory '{source}' to '{dest_dir}'."
            else:
                raise ValueError("Invalid operation specified.")
                
        elif source.is_file():
            # If the source is a file, use copy2 or move
            if operation == 'copy':
                shutil.copy2(source, destination) # copy2 preserves metadata
                message = f"Successfully copied file '{source}' to '{destination}'."
            elif operation == 'move':
                shutil.move(str(source), str(destination))
                message = f"Successfully moved file '{source}' to '{destination}'."
            else:
                raise ValueError("Invalid operation specified.")
        else:
            message = f"Error: Source path '{source}' is not a file or directory."
            logging.error(message)
            return False, message
            
        logging.info(message)
        return True, message

    except (shutil.Error, OSError, ValueError) as e:
        # --- Error Handling ---
        # Catch potential exceptions during file operations
        message = f"An error occurred: {e}"
        logging.error(message)
        return False, message

if __name__ == '__main__':
    # --- Example Usage (for testing) ---
    # This block runs only when you execute core.py directly.
    print("Testing core.py...")
    
    # Create dummy directories and a file for testing
    os.makedirs("test_source/subfolder", exist_ok=True)
    with open("test_source/sample.txt", "w") as f:
        f.write("This is a test file.")
    os.makedirs("test_destination", exist_ok=True)

    # Test 1: Copy a file
    success, message = sync_data("test_source/sample.txt", "test_destination")
    print(f"File Copy Test: {'Success' if success else 'Failed'} - {message}")

    # Test 2: Copy a directory
    success, message = sync_data("test_source", "test_destination")
    print(f"Directory Copy Test: {'Success' if success else 'Failed'} - {message}")
    
    # Test 3: Move a directory
    success, message = sync_data("test_source", "test_destination", operation='move')
    print(f"Directory Move Test: {'Success' if success else 'Failed'} - {message}")

    # Clean up dummy files and directories
    if os.path.exists("test_source"):
        shutil.rmtree("test_source")
    if os.path.exists("test_destination"):
        shutil.rmtree("test_destination")
    print("\nTest complete. Check 'datasync_log.txt' for details.")

