# tests/test_cli.py
# Pytest file for testing the command-line interface in cli.py

import pytest
import sys
from unittest.mock import patch

# We import the main function for the tests
from cli import main

# --- CLI Behavior Tests ---

# The key fix is to patch 'cli.sync_data' because that is where the 
# function is being called FROM in our tests.
@patch('cli.sync_data') 
def test_cli_successful_copy(mock_sync_data, monkeypatch, capsys):
    """Tests the CLI for a successful copy operation."""
    # Arrange
    mock_sync_data.return_value = (True, "Operation was a success!")
    monkeypatch.setattr(sys, 'argv', ['cli.py', 'source_dir', 'dest_dir'])
    
    # Act
    main()
    
    # Assert
    mock_sync_data.assert_called_once_with('source_dir', 'dest_dir', 'copy')
    captured = capsys.readouterr()
    assert "Success: Operation was a success!" in captured.out

@patch('cli.sync_data')
def test_cli_successful_move(mock_sync_data, monkeypatch, capsys):
    """Tests the CLI for a successful move operation."""
    # Arrange
    mock_sync_data.return_value = (True, "Move was successful!")
    monkeypatch.setattr(sys, 'argv', ['cli.py', '--move', 'source.txt', 'dest_dir'])
    
    # Act
    main()
    
    # Assert
    mock_sync_data.assert_called_once_with('source.txt', 'dest_dir', 'move')
    captured = capsys.readouterr()
    assert "Success: Move was successful!" in captured.out

@patch('cli.sync_data')
def test_cli_failed_operation(mock_sync_data, monkeypatch, capsys):
    """Tests the CLI for a failed operation."""
    # Arrange
    mock_sync_data.return_value = (False, "Something went wrong.")
    monkeypatch.setattr(sys, 'argv', ['cli.py', 'source', 'dest'])
    
    # Act
    main()
    
    # Assert
    mock_sync_data.assert_called_once_with('source', 'dest', 'copy')
    captured = capsys.readouterr()
    assert "Error: Something went wrong." in captured.out

# --- Argument Parsing Tests ---

def test_cli_help_message(monkeypatch, capsys):
    """Tests that the --help flag works and prints usage information."""
    monkeypatch.setattr(sys, 'argv', ['cli.py', '--help'])
    with pytest.raises(SystemExit):
        main()
    
    captured = capsys.readouterr()
    assert "usage: cli.py" in captured.out

def test_cli_missing_arguments(monkeypatch, capsys):
    """Tests that missing arguments print an error and exit."""
    monkeypatch.setattr(sys, 'argv', ['cli.py'])
    with pytest.raises(SystemExit):
        main()
        
    captured = capsys.readouterr()
    # argparse prints errors to the standard error stream (stderr)
    assert "usage: cli.py" in captured.err

