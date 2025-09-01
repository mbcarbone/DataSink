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
    os.makedirs(TEST_SOURCE_DIR, exist_ok=True)
    with open(TEST_SOURCE_FILE, "w") as f:
        f.write("This is a test file.")
    os.makedirs(TEST_DEST_DIR, exist_ok=True)

def teardown_function():
    """This function runs after each test to clean up."""
    if os.path.exists(TEST_SOURCE_DIR):
        shutil.rmtree(TEST_SOURCE_DIR)
    if os.path.exists(TEST_DEST_DIR):
        shutil.rmtree(TEST_DEST_DIR)

# --- Test Cases ---

def test_copy_file_success():
    """Tests successful copying of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is True
    # --- FIX: Match the capitalization from the core.py message ---
    assert "Successfully copied" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))

def test_move_file_success():
    """Tests successful moving of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'move')
    assert success is True
    # --- FIX: Match the capitalization ---
    assert "Successfully moved" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))
    assert not os.path.exists(TEST_SOURCE_FILE)

def test_copy_directory_success():
    """Tests successful copying of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    assert success is True
    # --- FIX: Match the capitalization ---
    assert "Successfully copied" in message
    dest_path = os.path.join(TEST_DEST_DIR, os.path.basename(TEST_SOURCE_DIR))
    assert os.path.exists(dest_path)
    assert os.path.exists(os.path.join(dest_path, "test_file.txt"))

def test_move_directory_success():
    """Tests successful moving of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'move')
    assert success is True
    # --- FIX: Match the capitalization ---
    assert "Successfully moved" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, os.path.basename(TEST_SOURCE_DIR)))
    assert not os.path.exists(TEST_SOURCE_DIR)

@patch('os.path.exists')
def test_source_path_does_not_exist(mock_exists):
    """Tests the error handling when the source path does not exist."""
    mock_exists.return_value = False
    non_existent_source = "/path/to/non_existent_file.txt"
    success, message = sync_data(non_existent_source, TEST_DEST_DIR, 'copy')
    assert success is False
    expected_message = f"Error: Source path '{non_existent_source}' does not exist."
    assert message == expected_message

@patch('shutil.copy2')
def test_copy_permission_error(mock_copy):
    """Tests error handling when a file copy operation fails due to permissions."""
    mock_copy.side_effect = PermissionError("Permission denied")
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is False
    assert "Permission denied" in message

@patch('shutil.move')
def test_move_io_error(mock_move):
    """Tests error handling when a move operation fails due to an IOError."""
    mock_move.side_effect = IOError("Disk full")
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'move')
    assert success is False
    assert "Disk full" in message

