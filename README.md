Of course. Here is a comprehensive `README.md` file for your `DataSink` project.

-----

# DataSink

DataSink is a simple, cross-platform utility for backing up and transferring files and directories. It offers both a straightforward command-line interface (CLI) and an intuitive graphical user interface (GUI), making it easy to copy or move data.

The project is built with security and robustness in mind, featuring path validation to prevent common traversal attacks and a comprehensive test suite, including a fuzzing harness, to ensure reliability.

## Features

  * **Copy or Move**: Supports both copying and moving of files and entire directories.
  * **Dual Interface**:
      * A full-featured **command-line interface (CLI)** for scripting and automation.
      * An easy-to-use **graphical user interface (GUI)** for interactive use.
  * **Safety First**: Includes security checks to prevent writing to unsafe system directories.
  * **Robust Testing**: Comes with a full `pytest` test suite for verifying functionality.
  * **Fuzzing Harness**: Includes a fuzzing harness built with Google's Atheris to find and fix bugs proactively.
  * **Logging**: All operations are logged to `datasync_log.txt` for easy review.

## Installation

You can install DataSink directly from the source directory using `pip`.

```bash
# Navigate to the root of the DataSink project directory
pip install .
```

## Usage

DataSink can be run from either the command line or through its graphical interface.

### Command-Line Interface (CLI)

The CLI is perfect for quick operations or for use in scripts.

**Basic Syntax:**

```bash
datasink <source> <destination> [options]
```

**Examples:**

  * **To copy a directory:**

    ```bash
    datasink /path/to/source_directory /path/to/destination
    ```

  * **To move a file:**

    ```bash
    datasink /path/to/source_file.txt /path/to/destination --move
    ```

    *(You can also use the `-m` flag instead of `--move`)*

### Graphical User Interface (GUI)

The GUI provides a user-friendly way to select your source and destination and run operations.

**To launch the GUI, run the following command in your terminal:**

```bash
datasink-gui
```

This will open the application window, where you can use the "Browse" buttons to select your paths and choose between "Copy" and "Move".

## Testing

The project includes a comprehensive test suite to ensure the reliability of the core logic, CLI, and GUI.

**To run the tests, first install `pytest` and then run it from the project's root directory:**

```bash
pip install pytest
pytest
```

## Fuzz Testing

For advanced users and developers, DataSink includes a fuzzing harness to test the robustness of the file operation logic against unexpected or invalid inputs.

**To run the fuzzer:**

1.  **Install Atheris:**
    ```bash
    pip install atheris
    ```
2.  **Run the harness:**
    ```bash
    python fuzz_core.py
    ```
    The fuzzer will run indefinitely until it finds a crash or you stop it with `Ctrl+C`. You can also run it on the included corpus of previous crashes:
    ```bash
    python fuzz_core.py corpus
    ```

## License

This project is licensed under the MIT License.
