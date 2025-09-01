# tests/test_core.py
# Pytest file for testing the core logic in core.py

import os
import shutil
import logging
from unittest.mock import patch, mock_open

# Import the function we want to test
from core import sync_data

# --- Test Setup and Teardown ---
# We'll create some temporary directories and files for our tests.

# Define temporary paths for our test environment
TEST_SOURCE_DIR = "test_source"
TEST_DEST_DIR = "test_dest"
TEST_SOURCE_FILE = os.path.join(TEST_SOURCE_DIR, "test_file.txt")

def setup_function():
    """This function runs before each test."""
    # Create the source directory and a dummy file inside it
    os.makedirs(TEST_SOURCE_DIR, exist_ok=True)
    with open(TEST_SOURCE_FILE, "w") as f:
        f.write("This is a test file.")
    # Create the destination directory
    os.makedirs(TEST_DEST_DIR, exist_ok=True)

def teardown_function():
    """This function runs after each test to clean up."""
    # Remove the temporary directories and their contents
    if os.path.exists(TEST_SOURCE_DIR):
        shutil.rmtree(TEST_SOURCE_DIR)
    if os.path.exists(TEST_DEST_DIR):
        shutil.rmtree(TEST_DEST_DIR)

# --- Test Cases ---

def test_copy_file_success():
    """Tests successful copying of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is True
    assert "successfully copied" in message
    # Check that the file actually exists in the destination
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))

def test_move_file_success():
    """Tests successful moving of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'move')
    assert success is True
    assert "successfully moved" in message
    # Check that the file is in the destination and gone from the source
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))
    assert not os.path.exists(TEST_SOURCE_FILE)

def test_copy_directory_success():
    """Tests successful copying of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    assert success is True
    assert "successfully copied" in message
    # Check that the copied directory and its file exist in the destination
    dest_path = os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR)
    assert os.path.exists(dest_path)
    assert os.path.exists(os.path.join(dest_path, "test_file.txt"))

def test_move_directory_success():
    """Tests successful moving of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'move')
    assert success is True
    assert "successfully moved" in message
    # Check that the directory is in the destination and gone from the source
    assert os.path.exists(os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR))
    assert not os.path.exists(TEST_SOURCE_DIR)

# --- NEW TEST TO INCREASE COVERAGE ---

@patch('os.path.exists') # We mock os.path.exists to control its return value
def test_source_path_does_not_exist(mock_exists):
    """
    Tests the error handling when the source path does not exist.
    This specifically covers the lines you asked about.
    """
    # Force os.path.exists to return False
    mock_exists.return_value = False
    
    # Define a non-existent source path for the test
    non_existent_source = "/path/to/non_existent_file.txt"
    
    # Call the function with the non-existent source
    success, message = sync_data(non_existent_source, TEST_DEST_DIR, 'copy')
    
    # --- Assertions ---
    # 1. Check that the function reports failure
    assert success is False
    
    # 2. Check that the correct error message is returned
    expected_message = f"Error: Source path '{non_existent_source}' does not exist."
    assert message == expected_message

@patch('shutil.copy2')
def test_copy_permission_error(mock_copy):
    """
    Tests error handling when a file copy operation fails due to permissions.
    """
    # Simulate a PermissionError during the copy operation
    mock_copy.side_effect = PermissionError("Permission denied")
    
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    
    assert success is False
    assert "Permission denied" in message

@patch('shutil.move')
def test_move_io_error(mock_move):
    """
    Tests error handling when a move operation fails due to an IOError.
    """
    # Simulate an IOError during the move operation
    mock_move.side_effect = IOError("Disk full")

    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'move')

    assert success is False
    assert "Disk full" in message

