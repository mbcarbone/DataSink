# cli.py
# The command-line interface for the DataSync tool.

import argparse
from core import sync_data

def main():
    """
    Parses command-line arguments and calls the core data sync logic.
    """
    parser = argparse.ArgumentParser(
        description="A simple command-line tool to back up or transfer data.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("source", help="The source file or directory.")
    parser.add_argument("destination", help="The destination directory.")
    parser.add_argument(
        "-m", "--move", 
        action="store_true", 
        help="Move the source instead of copying (the default action)."
    )
    args = parser.parse_args()

    # Determine the operation based on the '--move' flag
    operation = 'move' if args.move else 'copy'

    print(f"Starting '{operation}' operation...")
    print(f"Source: {args.source}")
    print(f"Destination: {args.destination}")
    
    # Call the core logic function with the parsed arguments
    success, message = sync_data(args.source, args.destination, operation)
    
    # Print the outcome message to the console
    if success:
        print(f"\nSuccess: {message}")
    else:
        print(f"\nError: {message}")
        
    print(f"Check 'datasync_log.txt' for detailed logs.")

# This block is the entry point when you run `python cli.py`
# We exclude it from coverage because it's difficult to test directly
# and its only job is to call main(), which IS tested.
if __name__ == "__main__": # pragma: no cover
    main()

