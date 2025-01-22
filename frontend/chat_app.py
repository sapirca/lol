import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
import json
from main_controller import MainController

# Constants
LOGS_FOLDER_PATH = "logs"  # Folder where system snapshots are stored
# UNTITLED_CHAT_FILE = "untitled.json"  # Default chat file for initialization

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

# Global variables
active_chat_snapshot = None
controller = None  # Will be initialized dynamically based on selected snapshot

def initialize_main_controller(snapshot_folder):
    """Initialize the MainController with the selected snapshot folder."""
    global controller
    snapshot_path = os.path.abspath(os.path.join(LOGS_FOLDER_PATH, snapshot_folder))
    controller = MainController(snapshot_path)

def append_message_to_window(timestamp, sender, message):
    """Adds a message to the chat window with proper formatting and colors."""
    label_tag = f"{sender.lower()}_label"
    message_tag = f"{sender.lower()}_message"

    chat_window.insert(tk.END, f"[{timestamp}] {sender}:\n", label_tag)
    chat_window.insert(tk.END, f"{message}\n\n", message_tag)

    if sender.lower() == "system":
        chat_window.tag_configure(label_tag, foreground="lime", justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "assistant":
        chat_window.tag_configure(label_tag, foreground="yellow", justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "you":
        chat_window.tag_configure(label_tag, foreground="hot pink", justify=USER_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=USER_ALIGNMENT)

def send_message(event=None):
    user_message = user_input.get("1.0", tk.END).strip()
    if user_message:
        chat_window.config(state=tk.NORMAL)

        # Get the current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Add user message
        append_message_to_window(current_time, "You", user_message)

        # Save user message to the chat history
        # Chat saving now handled internally by MainController

        # Call the MainController for the system reply 
       # Call the MainController for the system reply
        replies = controller.communicate(user_message)

        # Add system reply
        for tag, system_reply in replies.items():
            if tag == 'assistant':
                append_message_to_window(current_time, 'Assistant', system_reply)
            elif tag == 'system':
                append_message_to_window(current_time, 'System', system_reply)
            else:
                append_message_to_window(current_time, tag.capitalize(), system_reply)


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
    active_chat_snapshot = None

def load_chat_content(snapshot_folder):
    """Load chat content after saving the current chat session."""
    close_current_chat()  # Save and exit the current chat before loading a new one
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
        append_message_to_window(current_time, "System", "Welcome to LOL - the Light Animations Orchestrator Dialog Agent!")
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

def create_or_reset_untitled_chat():
    """Ensure an untitled chat session exists and is initialized."""
    global controller, active_chat_snapshot
    close_current_chat()  # Ensure any existing chat is closed

    # untitled_folder = os.path.abspath(os.path.join(LOGS_FOLDER_PATH, "untitled"))
    # if not os.path.exists(untitled_folder):
    #     os.makedirs(untitled_folder, exist_ok=True)

    # new controller!
    controller = MainController()
    active_chat_snapshot = "untitled"

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    current_time = datetime.now().strftime("%H:%M:%S")
    append_message_to_window(current_time, "System", "Welcome to the untitled chat session!")
    chat_window.config(state=tk.DISABLED)

    print(f"Untitled chat session initialized in")

def create_new_chat():
    """Creates a new empty chat session."""
    global controller, active_chat_snapshot
    close_current_chat()  # Ensure the previous chat is closed

    # Create a unique folder for the new chat
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_chat_folder = os.path.abspath(os.path.join(LOGS_FOLDER_PATH, f"snapshot_{timestamp}"))
    os.makedirs(new_chat_folder, exist_ok=True)

    # Initialize a new controller for the new chat
    controller = MainController(new_chat_folder)
    active_chat_snapshot = f"snapshot_{timestamp}"

    # Display a welcome message in the new chat
    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    current_time = datetime.now().strftime("%H:%M:%S")
    append_message_to_window(current_time, "System", "Welcome to a new chat session!")
    chat_window.config(state=tk.DISABLED)

    print(f"New chat session created: {new_chat_folder}")

def populate_snapshot_list():
    """Populates the snapshot list on the left UI bar by reading directories in the logs folder."""
    for widget in chat_list_frame.winfo_children():
        widget.destroy()  # Clear existing buttons

    snapshot_folders = [f for f in os.listdir(LOGS_FOLDER_PATH) if os.path.isdir(os.path.join(LOGS_FOLDER_PATH, f))]

    for snapshot_folder in snapshot_folders:
        snapshot_button = tk.Button(
            chat_list_frame,
            text=snapshot_folder,
            command=lambda folder=snapshot_folder: load_chat_content(folder)
        )
        snapshot_button.pack(fill=tk.X, pady=2)

    # Always add a button for the untitled chat at the top
    untitled_button = tk.Button(
        chat_list_frame,
        text="untitled",
        command=create_or_reset_untitled_chat
    )
    untitled_button.pack(fill=tk.X, pady=2)

    # Click on the last button to load its chat
    buttons = chat_list_frame.winfo_children()
    if buttons:
        buttons[-1].invoke()


def handle_keypress(event):
    """Handles the Enter key press to send messages."""
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        user_input.delete("1.0", tk.END)  # Clear the input field after sending the message
        return "break"  # Prevent default newline behavior

# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("1000x500")

# Create a frame for the left chat list
chat_list_frame = tk.Frame(root, width=200, bg="#2c2c2c")
chat_list_frame.pack(side=tk.LEFT, fill=tk.Y)

# Populate the snapshot list
populate_snapshot_list()

# Create a frame for the chat window
chat_frame = tk.Frame(root)
chat_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a scrolled text widget for the chat window
chat_window = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, width=50, bg="#2c2c2c", fg="#ffffff", insertbackground="#ffffff")
chat_window.pack(fill=tk.BOTH, expand=True)

# Create a frame for the input
input_frame = tk.Frame(chat_frame)
input_frame.pack(padx=10, pady=10, fill=tk.X)

# Create a text widget for user input
user_input = tk.Text(input_frame, height=3, wrap=tk.WORD)
user_input.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
user_input.bind("<Return>", handle_keypress)
user_input.bind("<Shift-Return>", lambda event: None)  # Allow new line on Shift+Enter

# Create a send button
send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Start the application
root.mainloop()
