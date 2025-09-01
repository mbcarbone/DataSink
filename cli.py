# cli.py
# This script provides a command-line interface for the DataSync tool.

import argparse
from core import sync_data # Import the main function from core.py

def main():
    """
    Parses command-line arguments and initiates the data synchronization.
    """
    # --- Argument Parser Setup ---
    # We use argparse to define and handle the command-line arguments.
    parser = argparse.ArgumentParser(
        description="A simple command-line tool to back up or transfer data.",
        epilog="Example: python cli.py ./my_folder /mnt/backup_drive"
    )

    # --- Defining Arguments ---
    # 1. Source Path (Positional Argument)
    # This is the file or folder you want to copy/move.
    parser.add_argument(
        "source", 
        type=str, 
        help="The source file or directory path."
    )

    # 2. Destination Path (Positional Argument)
    # This is the directory where the source will be copied/moved to.
    parser.add_argument(
        "destination", 
        type=str, 
        help="The destination directory path."
    )

    # 3. Move Operation (Optional Flag)
    # If this flag is present, the operation will be a 'move' instead of a 'copy'.
    parser.add_argument(
        "-m", "--move",
        action="store_true", # Makes it a flag; if present, its value is True
        help="Move the source to the destination instead of copying."
    )

    # Parse the arguments provided by the user
    args = parser.parse_args()

    # --- Determine Operation and Execute ---
    # Check if the --move flag was used to set the operation type.
    operation = 'move' if args.move else 'copy'

    print(f"Starting '{operation}' operation...")
    print(f"Source: {args.source}")
    print(f"Destination: {args.destination}")
    
    # Call the core logic function with the parsed arguments
    success, message = sync_data(args.source, args.destination, operation)

    # --- Output the Result ---
    # Print the outcome message to the console.
    if success:
        print(f"\nSuccess: {message}")
    else:
        print(f"\nError: {message}")
    
    print(f"Check 'datasync_log.txt' for detailed logs.")

if __name__ == "__main__": # pragma: no cover
    # This ensures the main() function is called only when the script is executed directly.
    main()

