# tests/test_cli.py
# Pytest file for testing the command-line interface in cli.py

import sys
from unittest.mock import patch
# Import the main function from the cli script
from cli import main

# We use the @patch decorator to temporarily replace parts of the code.
# This lets us test the CLI logic in isolation without actually touching the filesystem.

@patch('cli.sync_data') # Mock the sync_data function
@patch('sys.argv', ['cli.py', 'source_folder', 'dest_folder']) # Mock command-line args
def test_cli_copy_operation(mock_sync_data):
    """
    Tests that the CLI calls sync_data with 'copy' operation by default.
    """
    # Set a return value for our mocked function
    mock_sync_data.return_value = (True, "Success")
    
    # Run the main function from cli.py
    main()
    
    # Assert that sync_data was called once with the correct arguments
    mock_sync_data.assert_called_once_with('source_folder', 'dest_folder', 'copy')

@patch('cli.sync_data')
@patch('sys.argv', ['cli.py', 'source_file.txt', 'dest_folder', '--move']) # Args with --move
def test_cli_move_operation(mock_sync_data):
    """
    Tests that the CLI calls sync_data with 'move' when the --move flag is used.
    """
    mock_sync_data.return_value = (True, "Success")
    
    main()
    
    # Assert that the last argument passed to sync_data was 'move'
    mock_sync_data.assert_called_once_with('source_file.txt', 'dest_folder', 'move')

@patch('cli.sync_data')
@patch('sys.argv', ['cli.py', 'source', 'dest', '-m']) # Short flag for move
def test_cli_move_operation_short_flag(mock_sync_data):
    """
    Tests that the CLI calls sync_data with 'move' when the -m flag is used.
    """
    mock_sync_data.return_value = (True, "Success")
    
    main()
    
    mock_sync_data.assert_called_once_with('source', 'dest', 'move')

@patch('builtins.print') # Mock the print function to capture output
@patch('cli.sync_data')
@patch('sys.argv', ['cli.py', 'source', 'dest'])
def test_cli_prints_success_message(mock_sync_data, mock_print):
    """
    Tests that the CLI prints the success message returned by sync_data.
    """
    # Simulate a successful operation
    mock_sync_data.return_value = (True, "Operation was a success!")
    
    main()
    
    # --- FIX ---
    # Instead of checking only the LAST call, we check ALL calls to print.
    # We create a list of all strings that were printed.
    all_print_calls = [call.args[0] for call in mock_print.call_args_list]
    
    # We check if ANY of the print calls contain our success message.
    assert any("Success: Operation was a success!" in call for call in all_print_calls)

@patch('builtins.print')
@patch('cli.sync_data')
@patch('sys.argv', ['cli.py', 'source', 'dest'])
def test_cli_prints_error_message(mock_sync_data, mock_print):
    """
    Tests that the CLI prints the error message returned by sync_data.
    """
    # Simulate a failed operation
    mock_sync_data.return_value = (False, "Something went wrong.")
    
    main()
    
    # --- FIX ---
    # We apply the same fix here for the error message test.
    all_print_calls = [call.args[0] for call in mock_print.call_args_list]
    
    # Check if ANY of the print calls contain our error message.
    assert any("Error: Something went wrong." in call for call in all_print_calls)

