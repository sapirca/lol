import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
import json

# Constants
CHAT_FOLDER_PATH = "chats/chat_history_folder"  # Folder where chat files are stored
UNTITLED_CHAT_FILE = "untitled.json"  # Default chat file for initialization

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

# Global variable to track the active chat file
active_chat_file = UNTITLED_CHAT_FILE

def save_chat_to_file(chat_file, new_entry):
    """Saves a new entry to the specified chat file."""
    file_path = os.path.join(CHAT_FOLDER_PATH, chat_file)
    chat_history = get_chat_history(chat_file)
    chat_history.append(new_entry)
    with open(file_path, "w") as file:
        json.dump(chat_history, file, indent=4)

def append_message_to_window(timestamp, sender, message):
    """Adds a message to the chat window with proper formatting and colors."""
    chat_window.insert(tk.END, f"[{timestamp}] {sender}:\n", f"{sender.lower()}_label")
    chat_window.insert(tk.END, f"{message}\n\n", f"{sender.lower()}_message")
    if sender.lower() == "system":
        chat_window.tag_configure("system_label", foreground="lime", justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure("system_message", justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "you":
        chat_window.tag_configure("user_label", foreground="hot pink", justify=USER_ALIGNMENT)
        chat_window.tag_configure("user_message", justify=USER_ALIGNMENT)

def send_message(event=None):
    global active_chat_file
    user_message = user_input.get("1.0", tk.END).strip()
    if user_message:
        chat_window.config(state=tk.NORMAL)

        # Get the current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Add user message
        append_message_to_window(current_time, "You", user_message)

        # Save user message to the active chat file
        save_chat_to_file(active_chat_file, {"timestamp": current_time, "sender": "You", "message": user_message})

        # Call the main controller for the system reply
        system_reply = main_controller(user_message)

        # Add system reply
        append_message_to_window(current_time, "System", system_reply)

        # Save system reply to the active chat file
        save_chat_to_file(active_chat_file, {"timestamp": current_time, "sender": "System", "message": system_reply})

        chat_window.config(state=tk.DISABLED)
        chat_window.see(tk.END)
        user_input.delete("1.0", tk.END)

def main_controller(user_message):
    """Handles the business logic for user input and generates a system reply."""
    # Replace this logic with your actual business logic
    if user_message.lower() == "hello":
        return "Hi there! How can I assist you today?"
    elif user_message.lower() == "bye":
        return "Goodbye! Have a great day!"
    else:
        return "I'm not sure how to respond to that."

def get_chat_history(chat_key):
    """Retrieves chat history from a file based on chat_key."""
    file_path = os.path.join(CHAT_FOLDER_PATH, chat_key)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

def load_chat_content(chat_file):
    """Loads chat history into the chat window using the provided content and sets the active chat file."""
    global active_chat_file
    active_chat_file = chat_file

    # Retrieve the most recent content from the file
    chat_history = get_chat_history(chat_file)
    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)
    if not chat_history:
        # Initialize with a welcome message if history is empty
        current_time = datetime.now().strftime("%H:%M:%S")
        append_message_to_window(current_time, "System", "Welcome to LOL - the Light Animations Orchestrator Dialog Agent!")
    else:
        for entry in chat_history:
            append_message_to_window(entry['timestamp'], entry['sender'], entry['message'])
    chat_window.config(state=tk.DISABLED)

def create_or_increment_untitled():
    """Ensures an untitled chat file exists or increments its name if one already exists."""
    untitled_path = os.path.join(CHAT_FOLDER_PATH, UNTITLED_CHAT_FILE)
    if os.path.exists(untitled_path):
        counter = 1
        while True:
            new_untitled_file = f"untitled_{counter}.json"
            new_untitled_path = os.path.join(CHAT_FOLDER_PATH, new_untitled_file)
            if not os.path.exists(new_untitled_path):
                return new_untitled_file
            counter += 1
    else:
        return UNTITLED_CHAT_FILE

def populate_chat_list():
    """Populates the chat list on the left UI bar by reading filenames in the chat history folder."""
    if not os.path.exists(CHAT_FOLDER_PATH):
        os.makedirs(CHAT_FOLDER_PATH)  # Create the folder if it doesn't exist

    # Ensure the untitled chat exists
    untitled_file = create_or_increment_untitled()
    untitled_path = os.path.join(CHAT_FOLDER_PATH, untitled_file)
    if not os.path.exists(untitled_path):
        with open(untitled_path, "w") as file:
            json.dump([], file)

    # Add untitled chat to the top of the list
    chat_files = [untitled_file] + [f for f in os.listdir(CHAT_FOLDER_PATH) if f.endswith(".json") and f != untitled_file]

    for chat_file in chat_files:
        chat_name = os.path.splitext(chat_file)[0]  # Use filename without extension as chat name
        chat_button = tk.Button(chat_list_frame, text=chat_name, command=lambda file=chat_file: load_chat_content(file))
        chat_button.pack(fill=tk.X, pady=2)

def handle_keypress(event):
    """Handles the Enter key press to send messages."""
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        return "break"  # Prevent default newline behavior

def initialize_chat():
    """Initializes the chat window with the untitled chat."""
    untitled_file = create_or_increment_untitled()
    load_chat_content(untitled_file)

# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("1000x500")

# Create a frame for the left chat list
chat_list_frame = tk.Frame(root, width=200, bg="#2c2c2c")
chat_list_frame.pack(side=tk.LEFT, fill=tk.Y)

# Populate the chat list
populate_chat_list()

# Create a frame for the chat window
chat_frame = tk.Frame(root)
chat_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a scrolled text widget for the chat window
chat_window = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, width=50)
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

# Initialize chat
initialize_chat()

# Start the application
root.mainloop()
