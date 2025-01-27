import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
import json
from main_controller import MainController
import re
import subprocess
import platform
from constants import ANIMATION_OUT_TEMP_DIR
import threading

# Constants
LOGS_FOLDER_PATH = "logs"  # Folder where system snapshots are stored

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

# Global variables
active_chat_snapshot = None
controller = None  # Will be initialized dynamically based on selected snapshot


def initialize_main_controller(snapshot_folder):
    """Initialize the MainController with the selected snapshot folder."""
    global controller
    snapshot_path = os.path.abspath(
        os.path.join(LOGS_FOLDER_PATH, snapshot_folder))
    controller = MainController(snapshot_path)


def append_message_to_window(timestamp, sender, message):
    """Adds a message to the chat window with proper formatting and clickable links."""
    label_tag = f"{sender.lower()}_label"
    message_tag = f"{sender.lower()}_message"

    chat_window.insert(tk.END, f"[{timestamp}] {sender}:\n", label_tag)

    def open_file_in_editor(event, file_path):
        """Opens the file in the default editor based on the platform."""
        try:
            system_platform = platform.system()
            if system_platform == "Darwin":  # macOS
                subprocess.run(["open", file_path], check=True)
            elif system_platform == "Linux":  # Linux
                subprocess.run(["xdg-open", file_path], check=True)
            elif system_platform == "Windows":  # Windows
                subprocess.run(["start", file_path], shell=True, check=True)
            else:
                print(f"Unsupported platform: {system_platform}")
        except Exception as e:
            print(f"Failed to open file: {file_path}. Error: {e}")

    def add_link(text, link_tag, file_path):
        start = chat_window.index(tk.INSERT)
        chat_window.insert(tk.END, text)
        end = chat_window.index(tk.INSERT)
        chat_window.tag_add(link_tag, start, end)
        chat_window.tag_config(link_tag, foreground="light blue", underline=1)
        chat_window.tag_bind(link_tag, "<Button-1>",
                             lambda e: open_file_in_editor(e, file_path))

    working_dir = os.getcwd()
    full_path = os.path.join(working_dir, ANIMATION_OUT_TEMP_DIR)
    absolute_path = os.path.abspath(full_path)
    # Match file paths that start with ANIMATION_OUT_TEMP_DIR
    file_links = re.finditer(rf"({re.escape(absolute_path)}[^\s]+)",
                             message)  # Match full file path
    last_end = 0

    for match in file_links:
        chat_window.insert(tk.END, message[last_end:match.start()],
                           message_tag)

        # Use the matched group directly as the file path
        file_path = match.group()
        add_link(file_path, f"link_{match.start()}", file_path)
        last_end = match.end()

    chat_window.insert(tk.END, message[last_end:], message_tag)
    chat_window.insert(tk.END, "\n\n")

    # Style the labels
    if sender.lower() == "system":
        chat_window.tag_configure(label_tag,
                                  foreground="lime",
                                  justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "assistant":
        chat_window.tag_configure(label_tag,
                                  foreground="yellow",
                                  justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "you":
        chat_window.tag_configure(label_tag,
                                  foreground="hot pink",
                                  justify=USER_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=USER_ALIGNMENT)


def send_message(event=None):
    """Handles sending a message by the user and calling the backend in a separate thread."""
    global controller
    user_message = user_input.get("1.0", tk.END).strip()
    user_input.delete("1.0", tk.END)
    if user_message:
        # Check if the user wants to exit
        if user_message.lower() == "exit":
            if controller:
                controller.shutdown(
                )  # Ensure the controller finalizes and saves state
            root.destroy()  # Close the application
            return

    if user_message:
        chat_window.config(state=tk.NORMAL)

        # Get the current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Add user message
        append_message_to_window(current_time, "You", user_message)

        # Run the backend communication in a separate thread
        threading.Thread(target=communicate_with_backend,
                         args=(user_message, current_time),
                         daemon=True).start()


def communicate_with_backend(user_message, current_time):
    """Handles communication with the backend without freezing the UI."""
    global controller
    replies = controller.communicate(user_message)

    for tag, system_reply in replies.items():
        if tag == 'assistant':
            append_message_to_window(current_time, 'Assistant', system_reply)
        elif tag == 'system':
            append_message_to_window(current_time, 'System', system_reply)
        else:
            append_message_to_window(current_time, tag.capitalize(),
                                     system_reply)

        # # Save system reply to the chat history
        # save_chat_to_file(UNTITLED_CHAT_FILE, {"timestamp": current_time, "sender": "System", "message": system_reply})

    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    user_input.delete("1.0", tk.END)


def close_current_chat():
    """Gracefully close the current chat controller, saving changes if necessary."""
    global controller, active_chat_snapshot
    if controller:
        controller.shutdown()  # Ensure controller finalizes and saves state
        print(f"Saved changes to snapshot: {active_chat_snapshot}")

    # Clear global references to free resources
    controller = None
    active_chat_snapshot = None  # TODO(sapir) remove the snapshots


def save_chat():
    """Saves the current chat session explicitly."""
    global controller, active_chat_snapshot
    if controller:
        try:
            controller.shutdown()  # Save the current session state
            save_status_label.config(text=f"Saved changes to snapshot",
                                     fg="light gray")
        except Exception as e:
            save_status_label.config(text=f"Failed to save chat: {str(e)}",
                                     fg="red")


def load_chat_content(snapshot_folder):
    """Load chat content and alert if the current chat is unsaved."""
    if controller and controller.logger.logs:
        unsaved_warning = tk.Toplevel(root)
        unsaved_warning.title("Unsaved Changes")
        unsaved_warning.geometry("300x150")

        label = tk.Label(
            unsaved_warning,
            text=
            "System doesn't save automatically. Use Save button. Agree to exit?",
            wraplength=250)
        label.pack(pady=10)

        def proceed():
            unsaved_warning.destroy()
            _load_chat(snapshot_folder)

        def cancel():
            unsaved_warning.destroy()

        button_frame = tk.Frame(unsaved_warning)
        button_frame.pack(pady=10)

        yes_button = tk.Button(button_frame, text="Yes", command=proceed)
        yes_button.pack(side=tk.LEFT, padx=5)

        no_button = tk.Button(button_frame, text="No", command=cancel)
        no_button.pack(side=tk.RIGHT, padx=5)

    else:
        _load_chat(snapshot_folder)


def _load_chat(snapshot_folder):
    """Load chat content and alert if the current chat is unsaved."""
    if controller:
        # Alert user if current chat is not saved
        if not controller.logger.logs:  # Assuming the logger's logs indicate changes
            print("Warning: Current chat session is not saved!")
    """Load chat content without saving the current chat session."""
    """Loads chat history into the chat window using the selected snapshot folder."""
    global active_chat_snapshot
    active_chat_snapshot = snapshot_folder

    # Initialize the MainController with the selected snapshot
    initialize_main_controller(snapshot_folder)

    # Retrieve visible chat from the controller
    chat_history = controller.get_visible_chat()

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    if not chat_history:
        # Initialize with a welcome message if history is empty
        current_time = datetime.now().strftime("%H:%M:%S")
        append_message_to_window(
            current_time, "System",
            "Welcome to LOL - the Light Animations Orchestrator Dialog Agent!")
    else:
        for timestamp, message, tag in chat_history:
            if tag == 'user_input':
                sender = 'You'
            elif tag == 'assistant':
                sender = 'Assistant'
            else:
                sender = 'System'
            append_message_to_window(timestamp, sender, message)
    chat_window.config(state=tk.DISABLED)


def create_or_ensure_untitled_chat():
    """Ensure an untitled chat session exists without resetting."""
    global controller, active_chat_snapshot
    if controller is None or active_chat_snapshot != "untitled":
        # Initialize untitled session only if it doesn't exist
        controller = MainController()
        active_chat_snapshot = "untitled"

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    current_time = datetime.now().strftime("%H:%M:%S")
    append_message_to_window(current_time, "System",
                             "Welcome to the untitled chat session!")
    chat_window.config(state=tk.DISABLED)

    print(f"Untitled chat session ensured")
    active_chat_snapshot = "untitled"

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    current_time = datetime.now().strftime("%H:%M:%S")
    append_message_to_window(current_time, "System",
                             "Welcome to the untitled chat session!")
    chat_window.config(state=tk.DISABLED)

    print(f"Untitled chat session initialized in")


def create_new_chat():
    """Creates a new empty chat session."""
    global controller, active_chat_snapshot
    close_current_chat()  # Ensure the previous chat is closed

    # Create a unique folder for the new chat
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_chat_folder = os.path.abspath(
        os.path.join(LOGS_FOLDER_PATH, f"snapshot_{timestamp}"))
    os.makedirs(new_chat_folder, exist_ok=True)

    # Initialize a new controller for the new chat
    controller = MainController(new_chat_folder)
    active_chat_snapshot = f"snapshot_{timestamp}"

    # Display a welcome message in the new chat
    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    current_time = datetime.now().strftime("%H:%M:%S")
    append_message_to_window(current_time, "System",
                             "Welcome to a new chat session!")
    chat_window.config(state=tk.DISABLED)

    print(f"New chat session created: {new_chat_folder}")


def populate_snapshot_list():
    """Populates the snapshot list on the left UI bar by reading directories in the logs folder."""
    for widget in chat_list_frame.winfo_children():
        widget.destroy()  # Clear existing buttons

    snapshot_folders = [
        f for f in os.listdir(LOGS_FOLDER_PATH)
        if os.path.isdir(os.path.join(LOGS_FOLDER_PATH, f))
    ]

    for snapshot_folder in snapshot_folders:
        snapshot_button = tk.Button(
            chat_list_frame,
            text=snapshot_folder,
            command=lambda folder=snapshot_folder: load_chat_content(folder))
        snapshot_button.pack(fill=tk.X, pady=2)

    # Always add a button for the untitled chat at the top
    untitled_button = tk.Button(chat_list_frame,
                                text="untitled",
                                command=create_or_ensure_untitled_chat)
    untitled_button.pack(fill=tk.X, pady=2)

    # Click on the last button to load its chat
    buttons = chat_list_frame.winfo_children()
    if buttons:
        buttons[-1].invoke()


def handle_keypress(event):
    """Handles the Enter key press to send messages."""
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        return "break"  # Prevent default newline behavior


# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("1000x500")

# Create a frame for the left chat list
chat_list_frame = tk.Frame(root, width=200, bg="#2c2c2c")
chat_list_frame.pack(side=tk.LEFT, fill=tk.Y)

# Create a frame for the chat window
chat_frame = tk.Frame(root)
chat_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Add a save button to the top of the chat window
save_button = tk.Button(chat_frame, text="Snapshot", command=save_chat)
save_button.pack(side=tk.TOP, padx=5, pady=5, anchor="ne")

# Add a status label for saving feedback
save_status_label = tk.Label(chat_frame,
                             text="",
                             fg="light gray",
                             anchor="w",
                             bg="#2c2c2c")
save_status_label.pack(side=tk.TOP, fill=tk.X, padx=5)

# Create a scrolled text widget for the chat window
chat_window = scrolledtext.ScrolledText(chat_frame,
                                        wrap=tk.WORD,
                                        state=tk.DISABLED,
                                        height=20,
                                        width=50,
                                        bg="#2c2c2c",
                                        fg="#ffffff",
                                        insertbackground="#ffffff")

# Create a context menu for right-click
context_menu = tk.Menu(chat_window, tearoff=0)
context_menu.add_command(
    label="Copy", command=lambda: chat_window.event_generate("<<Copy>>"))


def show_context_menu(event):
    """Show the context menu at the cursor position."""
    print("Right-click event detected")  # Debug: Check if the event triggers
    context_menu.tk_popup(event.x_root, event.y_root)


# Bind right-click to show the context menu
chat_window.bind("<Button-2>", show_context_menu)

chat_window.pack(fill=tk.BOTH, expand=True)

# Create a frame for the input
input_frame = tk.Frame(chat_frame)
input_frame.pack(padx=10, pady=10, fill=tk.X)

# Create a text widget for user input
user_input = tk.Text(input_frame, height=3, wrap=tk.WORD)
user_input.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
user_input.bind("<Return>", handle_keypress)
user_input.bind("<Shift-Return>",
                lambda event: None)  # Allow new line on Shift+Enter

# Create a send button
send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Populate the snapshot list
populate_snapshot_list()
# Start the application
root.mainloop()
