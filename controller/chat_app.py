import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
import json
from controller.logic_pp import LogicPlusPlus
import re
import subprocess
import platform
from controller.constants import ANIMATION_OUT_TEMP_DIR, SNAPSHOTS_DIR
from controller.constants import TIME_FORMAT
import threading

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

# Global variables
active_chat_snapshot = None
controller = None  # Will be initialized dynamically based on selected snapshot

def initialize_logic_controller(a_snapshot):  # Updated function name
    """Initialize the LogicPlusPlus with the selected snapshot folder."""
    global controller
    snapshot_path = os.path.abspath(
        os.path.join(SNAPSHOTS_DIR, a_snapshot))
    controller = LogicPlusPlus(snapshot_path)

def append_message_to_window(sender, message):
    timestamp = datetime.now().strftime(TIME_FORMAT)
    append_message_to_window_w_timestamp(timestamp, sender, message)

def append_message_to_window_w_timestamp(timestamp, sender, message):
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

    # Automatically scroll to the bottom
    chat_window.see(tk.END)

def update_active_chat_label(snapshot_name):
    """Update the active chat label to reflect the currently active chat."""
    active_chat_label.config(text=f"Active Chat: {snapshot_name}")

def send_message(event=None):
    """Handles sending a message by the user and calling the backend in a separate thread."""
    global controller
    user_message = user_input.get("1.0", tk.END).strip()
    user_input.delete("1.0", tk.END)
    if user_message:
        # Check if the user wants to exit
        if user_message.lower() == "exit":
            if controller:
                controller.shutdown()  # Ensure the controller finalizes and saves state
            root.destroy()  # Close the application
            return

    if user_message:
        chat_window.config(state=tk.NORMAL)
        send_button.config(state=tk.DISABLED)  # Disable send button
        user_input.unbind("<Return>")  # Disable Enter key
        # user_input.unbind("<Shift-Return>")  # Disable Shift+Enter key
        append_message_to_window("You", user_message)

        # Run the backend communication in a separate thread
        threading.Thread(target=communicate_with_backend,
                         args=(user_message,),
                         daemon=True).start()

def communicate_with_backend(user_message):
    """Handles communication with the backend without freezing the UI."""
    global controller
    replies = controller.communicate(user_message)

    for tag, system_reply in replies.items():
        if tag == 'assistant':
            append_message_to_window('Assistant', system_reply)
        elif tag == 'system':
            append_message_to_window('System', system_reply)
        else:
            append_message_to_window(tag.capitalize(),
                                     system_reply)

    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    send_button.config(state=tk.NORMAL)
    user_input.bind("<Return>", handle_keypress)

def close_current_chat():
    """Gracefully close the current chat controller, terminate threads, and save changes if necessary."""
    global controller, active_chat_snapshot
    if controller:
        shutdown_msg = controller.shutdown()
        print(shutdown_msg)
            
    # Clear global references to free resources
    controller = None
    active_chat_snapshot = None

def save_chat():
    """Saves the current chat session explicitly."""
    global controller, active_chat_snapshot
    if controller:
        try:
            save_message = controller.shutdown()
            save_status_label.config(text=save_message, fg="light gray")
        except Exception as e:
            save_status_label.config(text=f"Failed to save chat: {str(e)}", fg="red")
    else:
        save_status_label.config(text="No active chat to save", fg="red")

def save_and_load_chat_content(a_snapshot):
    """Load chat content and display the backend name."""
    save_status_label.config(text="", fg="light gray")  # Clear the status label
    
    # Check for unsaved changes
    if controller and controller.message_streamer.messages:
        show_save_popup(lambda: [close_current_chat(), _load_chat(a_snapshot)], lambda: None)
        root.update()  # Ensure the main loop is updated
    
    _load_chat(a_snapshot)
    update_active_chat_label(a_snapshot)  # Update label here

def _load_chat(a_snapshot):
    save_status_label.config(text="", fg="light gray")  # Ensure the status label is cleared when switching chats
    """Load chat content and alert if the current chat is unsaved."""
    if controller:
        # Alert user if current chat is not saved
        if not controller.message_streamer.messages:  # Assuming the message_streamer's messages indicate changes
            print("Warning: Current chat session is not saved!")
    
    global active_chat_snapshot
    active_chat_snapshot = a_snapshot

    initialize_logic_controller(a_snapshot)  # Updated function call

    chat_history = controller.get_visible_chat()
    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)

    for timestamp, message, tag in chat_history:
        if tag == 'user_input':
            sender = 'You'
        elif tag == 'assistant':
            sender = 'Assistant'
        else:
            sender = 'System'
        append_message_to_window_w_timestamp(timestamp, sender, message)

    print_system_info()
    chat_window.config(state=tk.DISABLED)

def print_system_info():
    current_time = datetime.now().strftime(TIME_FORMAT)
    backend_name = controller.selected_backend or "Unknown Backend"
    message = f"Active Backend is: {backend_name}"
    controller.message_streamer.add_message("system_output", message, visible=True, context=False)  
    append_message_to_window("System", message)

def save_and_load_untitled_chat():
    """Ensure an untitled chat session exists without resetting."""
    global controller, active_chat_snapshot
    if controller:
        show_save_popup(close_current_chat, lambda: None)
        root.update()  # Ensure the main loop is updated
    
    if controller is None or active_chat_snapshot != "untitled":
        controller = LogicPlusPlus()
        active_chat_snapshot = "untitled"

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)

    print_system_info()

    current_time = datetime.now().strftime(TIME_FORMAT)
    append_message_to_window("System",
                             "Welcome to a new chat session!")
    chat_window.config(state=tk.DISABLED)

    update_active_chat_label("untitled")  # Update label here

    print(f"Untitled chat session ensured")
    active_chat_snapshot = "untitled"

def populate_snapshot_list():
    """Populates the snapshot list with a scrollbar and highlights the active chat."""
    for widget in chat_list_frame.winfo_children():
        widget.destroy()

    snapshot_folders = []
    if os.path.exists(SNAPSHOTS_DIR):
        snapshot_folders = [
            f for f in os.listdir(SNAPSHOTS_DIR)
            if os.path.isdir(os.path.join(SNAPSHOTS_DIR, f))
        ]

    canvas = tk.Canvas(chat_list_frame)
    scrollbar_y = tk.Scrollbar(chat_list_frame, orient="vertical", command=canvas.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.config(yscrollcommand=scrollbar_y.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    buttons_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=buttons_frame, anchor=tk.NW)

    for snapshot_folder in snapshot_folders:
        snapshot_button = tk.Button(
            buttons_frame,
            text=snapshot_folder,
            command=lambda folder=snapshot_folder: save_and_load_chat_content(folder)) 
        snapshot_button.pack(fill=tk.X, pady=2)

    untitled_button = tk.Button(buttons_frame,
                                text="untitled",
                                command=save_and_load_untitled_chat)
    untitled_button.pack(fill=tk.X, pady=2)

    buttons_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

    buttons = buttons_frame.winfo_children()
    if buttons:
       buttons[-1].invoke()

def handle_keypress(event):
    """Handles the Enter key press to send messages."""
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        return "break"  # Prevent default newline behavior

def show_save_popup(proceed_callback, cancel_callback):
    """Show a warning dialog for unsaved changes."""
    unsaved_warning = tk.Toplevel(root)
    unsaved_warning.title("Unsaved Changes")
    unsaved_warning.geometry("300x150")

    label = tk.Label(
        unsaved_warning,
        text="Do you want to save a NEW Snapshot before discarding this chat?",
        wraplength=250)
    label.pack(pady=10)

    button_frame = tk.Frame(unsaved_warning)
    button_frame.pack(pady=10)

    def on_yes():
        proceed_callback()
        unsaved_warning.destroy()

    def on_no():
        cancel_callback()
        unsaved_warning.destroy()

    yes_button = tk.Button(button_frame, text="Yes", command=on_yes)
    yes_button.pack(side=tk.LEFT, padx=5)

    no_button = tk.Button(button_frame, text="No", command=on_no)
    no_button.pack(side=tk.RIGHT, padx=5)

    root.wait_window(unsaved_warning)  # Wait for the popup to be closed

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

# Create a frame for the top bar
top_bar = tk.Frame(chat_frame, bg="#2c2c2c")
top_bar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Add a label to display the active chat name
active_chat_label = tk.Label(top_bar,
                             text="Active Chat: None",
                             fg="#ffffff",
                             bg="#2c2c2c",
                             anchor="w",
                             font=("Helvetica", 12, "bold"))
active_chat_label.pack(side=tk.LEFT, padx=5)

# Add a status label for saving feedback
save_status_label = tk.Label(top_bar,
                             text="",
                             fg="light gray",
                             bg="#2c2c2c",
                             font=("Helvetica", 10))
save_status_label.pack(side=tk.LEFT, padx=10)

# Add a save button for snapshots
save_button = tk.Button(top_bar, text="Snapshot", command=save_chat)
save_button.pack(side=tk.RIGHT, padx=5)

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
