# gui.py
# The graphical user interface for the DataSync tool.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

# We will import our trusted datasink.core logic
from datasink.core import sync_data

class DataSinkGUI:
    """
    The main application class for the DataSink GUI.
    This class is responsible for creating and managing all the UI components.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("DataSink | Simple File Transfer")
        self.root.geometry("600x450")
        self.root.minsize(500, 400)
        
        # --- Style Configuration ---
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') # A clean, modern theme
        self.root.configure(bg="#f0f0f0")

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # --- UI Elements ---
        self._create_widgets(main_frame)

    def _create_widgets(self, parent):
        """Create and layout all the widgets in the application."""
        parent.columnconfigure(1, weight=1)

        # --- Source Selection ---
        ttk.Label(parent, text="Source:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(parent, textvariable=self.source_var, width=50)
        source_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Browse...", command=self.browse_source).grid(row=0, column=2, padx=5)

        # --- Destination Selection ---
        ttk.Label(parent, text="Destination:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(parent, textvariable=self.dest_var, width=50)
        dest_entry.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(parent, text="Browse...", command=self.browse_destination).grid(row=1, column=2, padx=5)

        # --- Operation Selection ---
        self.operation_var = tk.StringVar(value='copy')
        operation_frame = ttk.LabelFrame(parent, text="Operation", padding="10")
        operation_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Radiobutton(operation_frame, text="Copy", variable=self.operation_var, value='copy').pack(side='left', padx=10)
        ttk.Radiobutton(operation_frame, text="Move", variable=self.operation_var, value='move').pack(side='left', padx=10)

        # --- Run Button ---
        self.run_button = ttk.Button(parent, text="Run Operation", command=self._start_operation_thread)
        self.run_button.grid(row=3, column=0, columnspan=3, pady=15)

        # --- Status Display ---
        status_frame = ttk.LabelFrame(parent, text="Status & Log", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=5)
        parent.rowconfigure(4, weight=1)

        self.status_text = tk.Text(status_frame, height=8, state='disabled', wrap='word', bg="#ffffff")
        self.status_text.pack(expand=True, fill='both')
        
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.status_text.config(yscrollcommand=scrollbar.set)

    def browse_source(self):
        """Open a dialog to select a source file or directory."""
        path = filedialog.askdirectory(title="Select a Source Directory")
        if not path:
            path = filedialog.askopenfilename(title="Select a Source File")
        if path:
            self.source_var.set(os.path.normpath(path))

    def browse_destination(self):
        """Open a dialog to select a destination directory."""
        path = filedialog.askdirectory(title="Select a Destination Directory")
        if path:
            self.dest_var.set(os.path.normpath(path))

    def _log_status(self, message, level="info"):
        """Append a message to the status text box."""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"[{level.upper()}] {message}\n")
        self.status_text.config(state='disabled')
        self.status_text.see(tk.END)

    def _start_operation_thread(self):
        """Validate inputs and start the sync_data operation in a new thread."""
        source = self.source_var.get()
        destination = self.dest_var.get()
        operation = self.operation_var.get()

        if not source or not destination:
            messagebox.showerror("Input Error", "Please select both a source and a destination.")
            return

        self._log_status(f"Starting '{operation}' operation...")
        self._log_status(f"Source: {source}")
        self._log_status(f"Destination: {destination}")
        
        self.run_button.config(state='disabled')

        # Run the file operation in a separate thread to prevent the GUI from freezing
        thread = threading.Thread(
            target=self._run_sync_data, 
            args=(source, destination, operation)
        )
        thread.daemon = True # Allows main window to close even if thread is running
        thread.start()

    def _run_sync_data(self, source, dest, op):
        """Worker function that calls the datasink.core logic."""
        success, message = sync_data(source, dest, op)
        # Schedule the UI update to run on the main thread
        self.root.after(0, self.update_ui_after_operation, success, message)

    def update_ui_after_operation(self, success, message):
        """Update the UI after the operation is finished."""
        if success:
            self._log_status(f"SUCCESS: {message}", level="info")
            messagebox.showinfo("Success", message)
        else:
            self._log_status(f"ERROR: {message}", level="error")
            messagebox.showerror("Error", message)
        
        self.run_button.config(state='normal')

def launch_app():
    """Create and run the Tkinter application."""
    root = tk.Tk()
    app = DataSinkGUI(root)
    root.mainloop()

if __name__ == '__main__': # pragma: no cover
    launch_app()

