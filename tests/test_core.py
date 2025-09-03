# tests/test_core.py
# Pytest file for testing the core logic in core.py

import os
import shutil
import pytest
from unittest.mock import patch

# We import the function to be tested
from core import sync_data

# --- Test Fixtures and Setup ---

# Define constants for our test files and directories
TEST_SOURCE_DIR = "test_source"
TEST_DEST_DIR = "test_dest"
TEST_SOURCE_FILE = os.path.join(TEST_SOURCE_DIR, "test_file.txt")

# This function runs before each test to set up a clean environment
def setup_function():
    """Create fresh test directories and a sample file for each test."""
    os.makedirs(TEST_SOURCE_DIR, exist_ok=True)
    os.makedirs(TEST_DEST_DIR, exist_ok=True)
    with open(TEST_SOURCE_FILE, "w") as f:
        f.write("This is a test file.")

# This function runs after each test to clean up
def teardown_function():
    """Remove test directories and files after each test."""
    if os.path.exists(TEST_SOURCE_DIR):
        shutil.rmtree(TEST_SOURCE_DIR)
    if os.path.exists(TEST_DEST_DIR):
        shutil.rmtree(TEST_DEST_DIR)

# --- "Happy Path" Tests (Successful Operations) ---

def test_copy_file_success():
    """Tests successful copying of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is True
    assert "Successfully copied" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))

def test_move_file_success():
    """Tests successful moving of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'move')
    assert success is True
    assert "Successfully moved" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))
    assert not os.path.exists(TEST_SOURCE_FILE) # Source should be gone

def test_copy_directory_success():
    """Tests successful copying of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    assert success is True
    assert "Successfully copied" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR, "test_file.txt"))

def test_move_directory_success():
    """Tests successful moving of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'move')
    assert success is True
    assert "Successfully moved" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR))
    assert not os.path.exists(TEST_SOURCE_DIR)

def test_copy_directory_overwrites_existing_content():
    """This test confirms the CORRECT behavior for overwriting content."""
    # 1. Perform an initial copy.
    sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    # 2. Modify the source file.
    with open(TEST_SOURCE_FILE, "w") as f:
        f.write("New updated content.")
    # 3. Run the copy operation again.
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    # 4. Assert that the file was updated.
    assert success is True
    final_file_path = os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR, "test_file.txt")
    with open(final_file_path, "r") as f:
        content = f.read()
    assert content == "New updated content."

# --- "Unhappy Path" Tests (Error Conditions) ---

def test_source_path_does_not_exist():
    """Tests that a non-existent source path returns an error."""
    success, message = sync_data("non_existent_file.txt", TEST_DEST_DIR, 'copy')
    assert success is False
    assert "does not exist" in message

@patch('core.Path.mkdir')
def test_destination_creation_os_error(mock_mkdir):
    """Tests that an OSError during destination creation is handled."""
    mock_mkdir.side_effect = OSError("Permission denied")
    shutil.rmtree(TEST_DEST_DIR) # Ensure destination doesn't exist
    
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is False
    assert "Could not create destination directory" in message

def test_invalid_operation_for_file_raises_error():
    """Tests that providing an invalid operation for a file is handled."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'delete')
    assert success is False
    # FIX: Assert the exact, more descriptive error message.
    assert message == "Invalid operation 'delete' specified for file."

def test_invalid_operation_for_directory_raises_error():
    """Tests that providing an invalid operation for a directory is handled."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'delete')
    assert success is False
    # FIX: Assert the exact, more descriptive error message.
    assert message == "Invalid operation 'delete' specified for directory."

@patch('core.Path.is_dir')
@patch('core.Path.is_file')
@patch('core.Path.mkdir') # Also mock mkdir to prevent side effects
def test_source_is_not_file_or_dir(mock_mkdir, mock_is_file, mock_is_dir):
    """Tests the final 'else' block for an invalid source type."""
    mock_is_dir.return_value = False
    mock_is_file.return_value = False
    
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    assert success is False
    assert "is not a file or directory" in message

