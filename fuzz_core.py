import atheris
import sys
import os
import tempfile
from pathlib import Path

# We need to add the parent directory to the path to import from 'datasink'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datasink.core import sync_data

def TestOneInput(data):
    """
    The entry point for the fuzzer. Atheris calls this with random bytes.
    This function must be sandboxed to avoid changing the user's real files.
    """
    # Use a FuzzedDataProvider to turn the raw bytes into structured data
    fdp = atheris.FuzzedDataProvider(data)

    # Generate two strings to use as file paths
    source_name = fdp.ConsumeUnicode(fdp.remaining_bytes() // 2)
    dest_name = fdp.ConsumeUnicode(fdp.remaining_bytes())
    
    # Have the fuzzer choose between the two valid operations
    operation = fdp.PickValueInList(['copy', 'move'])

    # --- Fuzzer Environment Setup ---
    # Create a dummy source file for the operation to act upon.
    # This helps the fuzzer get past the initial "source exists" check.
    try:
        # Create a source file or directory to ensure there's something to copy/move
        if len(source_name) % 2 == 0 and source_name: # Make a dir sometimes
            os.makedirs(source_name, exist_ok=True)
            with open(Path(source_name) / "test.txt", "w") as f:
                f.write("fuzz")
        elif source_name: # Make a file other times
             with open(source_name, "w") as f:
                f.write("fuzz")
    except (OSError, UnicodeEncodeError, ValueError):
        # The generated path might be invalid for the OS (e.g., contains null bytes).
        # This is a valid state to test, so we just pass.
        pass

    # --- Call the Target Function ---
    # Run the function with the fuzzed inputs. Atheris will report any
    # unhandled exceptions as crashes.
    sync_data(source_name, dest_name, operation)

def main():
    """
    Sets up the fuzzer in a temporary directory to sandbox file operations.
    """
    # --- NEW: Build an absolute path to the corpus directory ---
    # Get the directory where the script is located
    script_dir = os.path.dirname(__file__)
    # Look for a corpus directory passed as an argument
    corpus_path = ""
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        # If an argument is a directory, make its path absolute
        potential_path = os.path.join(script_dir, sys.argv[1])
        if os.path.isdir(potential_path):
            corpus_path = potential_path
            # Replace the relative path argument with the absolute one
            sys.argv[1] = corpus_path

    # Keep track of the original directory
    original_cwd = os.getcwd()

    # Create a temporary directory that will be automatically cleaned up
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir) # Move into the sandbox

        try:
            # Setup and run the fuzzer
            atheris.Setup(sys.argv, TestOneInput)
            atheris.Fuzz()
        finally:
            # IMPORTANT: Change back to the original directory after fuzzing
            os.chdir(original_cwd)

if __name__ == "__main__":
    main()
