# tests/test_core.py
# Pytest file for testing the core logic in core.py

import os
import shutil
from pathlib import Path
import pytest # Make sure you have pytest installed (`pip install pytest`)
import sys

# Include the current directory
sys.path.insert(0, '..')
sys.path.insert(0, '.')

# Import the function we want to test
from core import sync_data

@pytest.fixture
def test_environment(tmp_path):
    """
    A pytest fixture to create a temporary directory structure for testing.
    This runs before each test function that uses it.
    """
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "destination"
    
    # Create a source directory with a subfolder and a file
    (source_dir / "subfolder").mkdir(parents=True, exist_ok=True)
    (source_dir / "test_file.txt").write_text("hello world")
    
    # Create the destination directory
    dest_dir.mkdir()
    
    # Yield the paths to the test function
    yield source_dir, dest_dir
    
    # Teardown (cleanup) is handled automatically by tmp_path

# --- Test Cases ---

def test_copy_file_successfully(test_environment):
    """Tests that a single file is copied correctly."""
    source_dir, dest_dir = test_environment
    source_file = source_dir / "test_file.txt"
    
    success, message = sync_data(str(source_file), str(dest_dir), operation='copy')
    
    assert success is True
    assert "Successfully copied file" in message
    assert (dest_dir / "test_file.txt").exists()
    assert (dest_dir / "test_file.txt").read_text() == "hello world"

def test_copy_directory_successfully(test_environment):
    """Tests that a whole directory is copied correctly."""
    source_dir, dest_dir = test_environment
    
    success, message = sync_data(str(source_dir), str(dest_dir), operation='copy')
    
    expected_dest_path = dest_dir / "source"
    
    assert success is True
    assert "Successfully copied directory" in message
    assert expected_dest_path.is_dir()
    assert (expected_dest_path / "test_file.txt").exists()
    assert (expected_dest_path / "subfolder").is_dir()

def test_move_file_successfully(test_environment):
    """Tests that a single file is moved correctly."""
    source_dir, dest_dir = test_environment
    source_file = source_dir / "test_file.txt"
    
    success, message = sync_data(str(source_file), str(dest_dir), operation='move')
    
    assert success is True
    assert "Successfully moved file" in message
    assert (dest_dir / "test_file.txt").exists() # File is in destination
    assert not source_file.exists() # File is gone from source

def test_move_directory_successfully(test_environment):
    """Tests that a whole directory is moved correctly."""
    source_dir, dest_dir = test_environment
    
    success, message = sync_data(str(source_dir), str(dest_dir), operation='move')
    
    assert success is True
    assert "Successfully moved directory" in message
    assert (dest_dir / "source").is_dir()
    assert not source_dir.exists() # Directory is gone from source

def test_copy_to_existing_directory_creates_timestamped_folder(test_environment):
    """
    Tests that copying a directory to a destination where it already
    exists results in a new, timestamped directory.
    """
    source_dir, dest_dir = test_environment
    
    # First copy: should create 'destination/source'
    sync_data(str(source_dir), str(dest_dir), operation='copy')
    assert (dest_dir / "source").exists()

    # Second copy: should create a timestamped folder
    success, message = sync_data(str(source_dir), str(dest_dir), operation='copy')
    
    assert success is True
    # Find the new directory (it will have a timestamp)
    new_dir_name = message.split("'")[-2] # Extracts path from message
    assert Path(new_dir_name).exists()
    assert "source_" in Path(new_dir_name).name # Check for timestamped format

def test_error_on_nonexistent_source(test_environment):
    """Tests that the function fails if the source doesn't exist."""
    _, dest_dir = test_environment
    non_existent_source = "non_existent_folder"
    
    success, message = sync_data(non_existent_source, str(dest_dir))
    
    assert success is False
    assert "Source path" in message and "does not exist" in message

def test_destination_creation(tmp_path):
    """Tests that the destination directory is created if it doesn't exist."""
    source_file = tmp_path / "source.txt"
    source_file.write_text("data")
    new_dest = tmp_path / "new_destination"
    
    assert not new_dest.exists() # Ensure it doesn't exist initially
    
    success, _ = sync_data(str(source_file), str(new_dest))
    
    assert success is True
    assert new_dest.is_dir()
    assert (new_dest / "source.txt").exists()

