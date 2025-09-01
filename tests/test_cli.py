# tests/test_cli.py
# Pytest file for testing the command-line interface in cli.py

import sys
import pytest
from unittest.mock import patch, call

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
    mock_sync_data.return_value = (True, "Success")
    main()
    mock_sync_data.assert_called_once_with('source_folder', 'dest_folder', 'copy')

@patch('cli.sync_data')
@patch('sys.argv', ['cli.py', 'source_file.txt', 'dest_folder', '--move']) # Args with --move
def test_cli_move_operation(mock_sync_data):
    """
    Tests that the CLI calls sync_data with 'move' when the --move flag is used.
    """
    mock_sync_data.return_value = (True, "Success")
    main()
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
    mock_sync_data.return_value = (True, "Operation was a success!")
    main()
    all_print_calls = [c.args[0] for c in mock_print.call_args_list]
    assert any("Success: Operation was a success!" in c for c in all_print_calls)

@patch('builtins.print')
@patch('cli.sync_data')
@patch('sys.argv', ['cli.py', 'source', 'dest'])
def test_cli_prints_error_message(mock_sync_data, mock_print):
    """
    Tests that the CLI prints the error message returned by sync_data.
    """
    mock_sync_data.return_value = (False, "Something went wrong.")
    main()
    all_print_calls = [c.args[0] for c in mock_print.call_args_list]
    assert any("Error: Something went wrong." in c for c in all_print_calls)

# --- NEW TESTS TO INCREASE COVERAGE ---

@patch('builtins.print')
@patch('sys.argv', ['cli.py', '--help'])
def test_cli_help_message(mock_print):
    """
    Tests that running with --help prints a help message and exits.
    This covers the code path where the main logic is NOT run.
    """
    # argparse's --help action calls sys.exit(), which raises SystemExit.
    # We use pytest.raises to assert that this exit happens as expected.
    with pytest.raises(SystemExit):
        main()

    # We can also check that the help message was printed.
    # We look for a keyword that is likely to be in any help message.
    all_print_calls_as_string = " ".join([c.args[0] for c in mock_print.call_args_list])
    assert "usage:" in all_print_calls_as_string.lower()

@patch('builtins.print')
@patch('sys.argv', ['cli.py']) # No arguments provided
def test_cli_missing_arguments(mock_print):
    """
    Tests that running with no arguments prints an error and exits.
    This also covers a path where the main logic is not executed.
    """
    with pytest.raises(SystemExit):
        main()

    # argparse will print an error message to stderr, which we can't easily
    # capture here, but we can confirm that the program exited, which is
    # the most important behavior to test. By running this path, we
    # ensure the lines in the main function are covered from this angle.
