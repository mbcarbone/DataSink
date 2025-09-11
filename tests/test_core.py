# tests/test_datasink.core.py
# Pytest file for testing the datasink.core logic in datasink.core.py

import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# We import the functions to be tested
from datasink.core import sync_data, is_safe_path

# --- Test Fixtures and Setup ---

TEST_SOURCE_DIR = "test_source"
TEST_DEST_DIR = "test_dest"
TEST_SOURCE_FILE = os.path.join(TEST_SOURCE_DIR, "test_file.txt")

def setup_function():
    """Create fresh test directories and a sample file for each test."""
    if os.path.exists(TEST_SOURCE_DIR):
        shutil.rmtree(TEST_SOURCE_DIR)
    if os.path.exists(TEST_DEST_DIR):
        shutil.rmtree(TEST_DEST_DIR)

    os.makedirs(os.path.join(TEST_SOURCE_DIR, "subfolder"), exist_ok=True)
    os.makedirs(TEST_DEST_DIR, exist_ok=True)
    with open(TEST_SOURCE_FILE, "w") as f:
        f.write("This is a test file.")

def teardown_function():
    """Remove test directories and files after each test."""
    if os.path.exists(TEST_SOURCE_DIR):
        shutil.rmtree(TEST_SOURCE_DIR)
    if os.path.exists(TEST_DEST_DIR):
        shutil.rmtree(TEST_DEST_DIR)

# --- NEW TEST TO COVER LINES 67-69 ---

def test_unsafe_destination_is_rejected():
    """
    Tests that an unsafe destination path is correctly blocked by the
    is_safe_path check, covering the corresponding error message block.
    """
    # Using a path like /etc/ is a classic example of an unsafe destination
    success, message = sync_data(TEST_SOURCE_FILE, "/etc/unsafe_destination", 'copy')
    assert success is False
    assert "is outside of the allowed directories" in message

# --- Existing Comprehensive Test Suite ---

def test_copy_directory_success():
    """Tests the straightforward successful copy of an entire directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    assert success is True
    assert "Successfully copied" in message
    copied_dir_path = os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR)
    assert os.path.isdir(copied_dir_path)
    assert os.path.exists(os.path.join(copied_dir_path, "test_file.txt"))

def test_self_copy_check_with_nonexistent_dest():
    """
    Tests the self-copy check's 'except FileNotFoundError' block.
    """
    non_existent_dest = os.path.join(TEST_SOURCE_DIR, "non_existent_subfolder")
    success, message = sync_data(TEST_SOURCE_DIR, non_existent_dest, 'copy')
    assert success is False
    assert "Cannot copy or move a directory into itself" in message

def test_copy_file_success():
    """Tests the successful copy of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is True
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))

def test_move_file_success():
    """Tests the successful move of a single file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'move')
    assert success is True
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))
    assert not os.path.exists(TEST_SOURCE_FILE)

def test_destination_is_created_if_not_exists():
    """Tests that the destination directory is created if it does not exist."""
    shutil.rmtree(TEST_DEST_DIR)
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is True
    assert os.path.isdir(TEST_DEST_DIR)
    assert os.path.exists(os.path.join(TEST_DEST_DIR, "test_file.txt"))

def test_source_path_does_not_exist():
    """Tests that a non-existent source path returns an error."""
    success, message = sync_data("non_existent_file.txt", TEST_DEST_DIR, 'copy')
    assert success is False
    assert "does not exist" in message

def test_self_copy_check_with_existing_dest():
    """Tests self-copy check when destination exists and is a subdir of source."""
    dest_subdir = os.path.join(TEST_SOURCE_DIR, "subfolder")
    success, message = sync_data(TEST_SOURCE_DIR, dest_subdir, 'copy')
    assert success is False
    assert "Cannot copy or move a directory into itself" in message

@patch('datasink.core.is_safe_path', return_value=True) # Isolate the test
@patch('pathlib.Path.resolve')
def test_self_copy_check_handles_filenotfound(mock_resolve, mock_is_safe):
    """
    Covers the 'except FileNotFoundError' block in the self-copy check
    by simulating a resolve failure on the destination path.
    """
    # The code will call resolve() on source, then destination. We make the second one fail.
    mock_resolve.side_effect = [
        Path(TEST_SOURCE_DIR).resolve(), 
        FileNotFoundError
    ]
    
    # Since the exception is caught and passed, the operation should succeed.
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    
    assert success is True
    assert "Successfully copied" in message

def test_move_directory_to_existing_destination_overwrites():
    """Tests moving a directory to an existing location, ensuring overwrite."""
    dest_with_source_name = os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR)
    os.makedirs(dest_with_source_name, exist_ok=True)
    with open(os.path.join(dest_with_source_name, "old_file.txt"), "w") as f:
        f.write("This should be deleted.")
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'move')
    assert success is True
    assert "Successfully moved" in message
    assert os.path.exists(os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR, "test_file.txt"))
    assert not os.path.exists(os.path.join(TEST_DEST_DIR, TEST_SOURCE_DIR, "old_file.txt"))
    assert not os.path.exists(TEST_SOURCE_DIR)

@patch('shutil.copy2', side_effect=OSError("Disk full"))
def test_generic_os_error_on_file_copy(mock_copy2):
    """Tests the final 'except' block by simulating an OSError during a file copy."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is False
    assert "An error occurred during the 'copy' operation: Disk full" in message
    
def test_invalid_operation_for_file():
    """Tests providing an invalid operation for a file."""
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'delete')
    assert success is False
    assert "Invalid operation 'delete'" in message

def test_invalid_operation_for_directory():
    """Tests providing an invalid operation for a directory."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'delete')
    assert success is False
    assert "Invalid operation 'delete'" in message

@patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied"))
def test_destination_creation_os_error(mock_mkdir):
    """Tests handling of OSError during destination directory creation."""
    shutil.rmtree(TEST_DEST_DIR)
    success, message = sync_data(TEST_SOURCE_FILE, TEST_DEST_DIR, 'copy')
    assert success is False
    assert "Could not create destination directory" in message

@patch('datasink.core.Path.mkdir')
@patch('datasink.core.Path.is_dir', return_value=False)
@patch('datasink.core.Path.is_file', return_value=False)
def test_source_is_not_file_or_dir(mock_is_file, mock_is_dir, mock_mkdir):
    """Tests the final 'else' block for an invalid source type."""
    success, message = sync_data(TEST_SOURCE_DIR, TEST_DEST_DIR, 'copy')
    assert success is False
    assert "is not a file or directory" in message

# --- is_safe_path Specific Tests ---

def test_is_safe_path_for_safe_paths():
    """Tests that is_safe_path correctly identifies safe paths."""
    assert is_safe_path(Path.cwd() / "safe_subdir") is True
    assert is_safe_path(Path.home() / "safe_subdir") is True

def test_is_safe_path_for_unsafe_paths():
    """Tests that is_safe_path correctly identifies unsafe paths."""
    assert is_safe_path(Path("/etc/")) is False

@patch('pathlib.Path.resolve')
def test_is_safe_path_handles_runtime_error(mock_resolve):
    """Tests the except block for broken symbolic links."""
    mock_resolve.side_effect = RuntimeError("Broken symlink")
    assert is_safe_path(Path.cwd() / "some_path") is True

@patch('datasink.core.Path.home', side_effect=Exception("Unexpected mock error"))
def test_is_safe_path_handles_unexpected_error(mock_home):
    """Tests the generic 'except Exception' block in is_safe_path."""
    assert is_safe_path(Path(TEST_DEST_DIR)) is False

