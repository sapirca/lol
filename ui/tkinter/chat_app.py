import tkinter as tk
from tkinter import scrolledtext, ttk
from datetime import datetime
import os
import json
from controller.logic_pp import LogicPlusPlus
import re
import subprocess
import platform
from constants import ANIMATION_OUT_TEMP_DIR, SNAPSHOTS_DIR
from constants import TIME_FORMAT
import threading
import _tkinter
import asyncio
from queue import Queue
from tkinter import filedialog
import concurrent.futures

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

# CHAT_FONT = "Helvetica"
CHAT_FONT = "Verdana"

# Global variables
active_chat_snapshot = None

controller = None  # Will be initialized dynamically based on selected snapshot
active_chat_button = None  # Store the currently active chat button
button_mapping = {}  # Dictionary to store button references

# Create a queue for async communication
message_queue = Queue()

# Create an event loop for the main thread
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Create a thread pool executor for running blocking operations
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)


# Function to detect macOS appearance (light or dark)
def get_macos_appearance():
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True)
        return result.stdout.strip().lower()
    except Exception:
        return "light"  # Default to light if detection fails


# Set colors based on the detected theme
appearance = get_macos_appearance()
if appearance == "dark":
    normal_color = "gray"
    active_color = "lightblue"
else:
    normal_color = "lightgray"
    active_color = "lightblue"


def initialize_logic_controller(a_snapshot):  # Updated function name
    """Initialize the LogicPlusPlus with the selected snapshot folder."""
    global controller
    snapshot_path = os.path.abspath(os.path.join(SNAPSHOTS_DIR, a_snapshot))
    controller = LogicPlusPlus(snapshot_path)


def append_message_to_window(sender, message):
    timestamp = datetime.now().strftime(TIME_FORMAT)
    append_message_to_window_w_timestamp(timestamp, sender, message)


def append_message_to_window_w_timestamp(timestamp, sender, message):
    """Adds a message to the chat window with proper formatting and clickable links."""
    label_tag = f"{sender.lower()}_label"
    message_tag = f"{sender.lower()}_message"

    # Ensure chat_window is writable
    original_state = chat_window.cget("state")
    chat_window.config(state=tk.NORMAL)

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
        chat_window.tag_config(link_tag, foreground="#8BE9FD", underline=1)
        chat_window.tag_bind(link_tag, "<Button-1>",
                             lambda e: open_file_in_editor(e, file_path))

    # Check if controller exists before trying to access its attributes
    tmp_animation_path = None
    if controller and hasattr(controller, 'animation_manager') and \
       hasattr(controller.animation_manager, 'sequence_manager'):
        tmp_animation_path = controller.animation_manager.sequence_manager.get_animation_filename(
        )

    last_end = 0  # Initialize last_end to 0
    if tmp_animation_path:
        # Look for the path in the message, allowing for newlines and other characters around it
        file_links = re.finditer(
            rf".*?({re.escape(tmp_animation_path)})[^\n]*", message, re.DOTALL)

        for match in file_links:
            chat_window.insert(tk.END, message[last_end:match.start(1)],
                               message_tag)

            # Use the matched group directly as the file path
            file_path = match.group(1)
            add_link(file_path, f"link_{match.start()}", file_path)
            last_end = match.end(1)

    chat_window.insert(tk.END, message[last_end:], message_tag)
    chat_window.insert(tk.END, "\n\n")

    # Style the labels
    if sender.lower() == "system":
        chat_window.tag_configure(
            label_tag,
            foreground="#8BE9FD",  # Light cyan (keeping this)
            justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "assistant":
        chat_window.tag_configure(
            label_tag,
            foreground="#FFB86C",  # Soft orange
            justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=SYSTEM_ALIGNMENT)
    elif sender.lower() == "you":
        chat_window.tag_configure(
            label_tag,
            foreground="#9580FF",  # Soft purple
            justify=USER_ALIGNMENT)
        chat_window.tag_configure(message_tag, justify=USER_ALIGNMENT)

    # Automatically scroll to the bottom
    chat_window.see(tk.END)

    # Restore original state
    chat_window.config(state=original_state)


def update_active_chat_label(button_name):
    """Update the active chat label to reflect the currently active chat."""
    button = button_mapping[button_name]
    # Ensure controller is initialized before accessing its attributes
    backend_info = controller.selected_backend if controller else "N/A"
    framework_info = controller.selected_framework if controller else "N/A"
    active_chat_label.config(
        text=f"{backend_info} | {framework_info} | {button_name}")
    set_active_chat_button(button)


def send_message(event=None):
    """Handles sending a message by the user and calling the backend in a separate thread."""
    global controller
    user_message = user_input.get("1.0", tk.END).strip()
    user_input.delete("1.0", tk.END)
    if user_message:
        # Check if the user wants to exit
        if user_message.lower() == "exit":
            if controller:
                controller.shutdown()
            root.destroy()  # Close the application
            return

    if user_message:
        chat_window.config(state=tk.NORMAL)
        send_button.config(state=tk.DISABLED,
                           text="Waiting...",
                           foreground="black",
                           background="grey")
        user_input.unbind("<Return>")  # Disable Enter key
        append_message_to_window("You", user_message)

        # Use the thread pool to run the backend communication
        thread_pool.submit(run_backend_communication, user_message)


def run_backend_communication(user_message):
    """Runs the backend communication in a separate thread."""
    try:
        replies = controller.communicate(user_message)

        auto_continue = False
        auto_continue_value = None

        for tag, system_reply in replies:
            if tag == 'auto_continue':
                auto_continue = True
                auto_continue_value = system_reply
            else:
                # Update UI immediately for each message
                root.after(
                    0, lambda t=tag, m=system_reply: update_chat_window(t, m))

        # Update animation data after processing replies
        root.after(0, update_animation_data)

        if auto_continue:
            root.after(0, lambda: handle_auto_continue(auto_continue_value))
        else:
            root.after(0, enable_ui)

    except Exception as e:
        root.after(0, lambda: update_chat_window('system', f"Error: {str(e)}"))
        root.after(0, enable_ui)


def update_chat_window(tag, message):
    """Updates the chat window with a new message."""
    append_message_to_window(tag.capitalize(), message)
    chat_window.see(tk.END)  # Make sure to scroll to bottom after each message


def enable_ui():
    """Re-enables the UI elements."""
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    send_button.config(state=tk.NORMAL, text="Send")
    user_input.config(state=tk.NORMAL)  # Re-enable the text input
    user_input.bind("<Return>", handle_keypress)


def handle_auto_continue(auto_continue_value):
    """Handles auto-continue functionality."""
    update_chat_window('system', "Automatically continuing conversation...")
    # Schedule the next backend communication
    thread_pool.submit(run_backend_communication, auto_continue_value)


def close_current_chat():
    """Gracefully close the current chat controller and terminate threads."""
    global controller, active_chat_snapshot
    if controller:
        # Don't call shutdown here, just clear references
        controller = None
        active_chat_snapshot = None


def save_chat():
    """Saves the current chat session explicitly."""
    global controller, active_chat_snapshot
    if controller:
        try:
            save_message = controller.shutdown()
            save_status_label.config(text=save_message, fg="light gray")
            # Clear the chat window after saving
            chat_window.config(state=tk.NORMAL)
            chat_window.delete("1.0", tk.END)
            chat_window.config(state=tk.DISABLED)
            # Clear the controller and active snapshot
            controller = None
            active_chat_snapshot = None
            populate_snapshot_list()  # Refresh the snapshot list
        except Exception as e:
            save_status_label.config(text=f"Failed to save chat: {str(e)}",
                                     fg="red")
    else:
        save_status_label.config(text="No active chat to save", fg="red")


def batch_insert_messages(messages):
    """Efficiently insert multiple messages into the chat window."""
    # Pre-configure tags
    chat_window.tag_configure("system_label",
                              foreground="lime",
                              justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure("system_message", justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure("assistant_label",
                              foreground="yellow",
                              justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure("assistant_message", justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure("user_label",
                              foreground="hot pink",
                              justify=USER_ALIGNMENT)
    chat_window.tag_configure("user_message", justify=USER_ALIGNMENT)

    # Build content in memory
    content = []
    for timestamp, message, tag in messages:
        if tag == 'user_input':
            label_tag = "user_label"
            message_tag = "user_message"
            sender = "You"
        elif tag == 'assistant':
            label_tag = "assistant_label"
            message_tag = "assistant_message"
            sender = "Assistant"
        else:
            label_tag = "system_label"
            message_tag = "system_message"
            sender = "System"

        content.append((f"[{timestamp}] {sender}:\n", label_tag))
        content.append((f"{message}\n\n", message_tag))

    # Insert all content at once
    for text, tag in content:
        chat_window.insert(tk.END, text, tag)

    chat_window.see(tk.END)


def _load_chat(a_snapshot):
    """Load chat content and alert if the current chat is unsaved."""
    global controller, active_chat_snapshot

    save_status_label.config(text="", fg="light gray")

    try:
        # Clean up old controller without saving
        if controller:
            close_current_chat()

        # Initialize the new controller
        if a_snapshot == "untitled":
            controller = LogicPlusPlus()
        else:
            snapshot_path = os.path.abspath(
                os.path.join(SNAPSHOTS_DIR, a_snapshot))
            controller = LogicPlusPlus(snapshot_path)

        active_chat_snapshot = a_snapshot

        # Load chat history
        chat_history = controller.get_visible_chat()

        # Update chat window in one go
        chat_window.config(state=tk.NORMAL)
        chat_window.delete("1.0", tk.END)

        if chat_history:
            batch_insert_messages(chat_history)
        elif a_snapshot == "untitled":
            message = "Welcome to a new chat session!"
            controller.message_streamer.add_message("system_output",
                                                    message,
                                                    visible=True,
                                                    context=False)
            append_message_to_window("System", message)
        else:
            message = "No chat history found in snapshot."
            controller.message_streamer.add_message("system_output",
                                                    message,
                                                    visible=True,
                                                    context=False)
            append_message_to_window("System", message)

        print_system_info()
        update_active_chat_label(a_snapshot)
        update_animation_data()  # Add this line to update animation data

        # Show success message
        if a_snapshot == "untitled":
            save_status_label.config(text="Started new chat session",
                                     fg="light gray")
        else:
            save_status_label.config(
                text=f"Successfully loaded snapshot: {a_snapshot}",
                fg="light gray")

    except Exception as e:
        error_msg = f"Error loading snapshot {a_snapshot}: {str(e)}"
        if controller:
            controller.message_streamer.add_message("system_output",
                                                    error_msg,
                                                    visible=True,
                                                    context=False)
        append_message_to_window("System", error_msg)
        save_status_label.config(text=f"Error loading chat: {str(e)}",
                                 fg="red")

    finally:
        chat_window.config(state=tk.DISABLED)
        enable_ui()  # Always re-enable the UI


def print_system_info():
    # current_time = datetime.now().strftime(TIME_FORMAT)
    backend_name = controller.selected_backend or "Unknown Backend"
    message = f"Active Backend is: {backend_name}"
    controller.message_streamer.add_message("system_output",
                                            message,
                                            visible=True,
                                            context=False)
    append_message_to_window("System", message)


def save_and_load_untitled_chat():
    """Ensure an untitled chat session exists without resetting."""
    global controller, active_chat_snapshot
    if controller and controller.message_streamer.messages:
        show_save_popup("untitled")
    else:
        _load_untitled_chat()


def _load_untitled_chat():
    global controller, active_chat_snapshot
    controller = LogicPlusPlus()
    active_chat_snapshot = "untitled"

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)

    print_system_info()

    # current_time = datetime.now().strftime(TIME_FORMAT)
    # append_message_to_window("System", "Welcome to a new chat session!")
    chat_window.config(state=tk.DISABLED)
    print(f"Untitled chat session ensured")
    active_chat_snapshot = "untitled"
    update_active_chat_label("untitled")


def format_button_text(text, max_width):
    """Format the button text to break into two lines after max_width characters."""
    if len(text) > max_width:
        return text[:max_width] + "\n" + text[max_width:]
    return text


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

    canvas = tk.Canvas(chat_list_frame, width=280)  # Set explicit canvas width
    scrollbar_y = tk.Scrollbar(chat_list_frame,
                               orient="vertical",
                               command=canvas.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.config(yscrollcommand=scrollbar_y.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    buttons_frame = tk.Frame(canvas, width=280)  # Set explicit frame width
    canvas.create_window((0, 0), window=buttons_frame, anchor=tk.NW,
                         width=280)  # Set explicit window width

    global button_mapping
    button_mapping = {}

    for snapshot_folder in snapshot_folders:
        snapshot_button = tk.Button(
            buttons_frame,
            text=snapshot_folder,
            command=lambda folder=snapshot_folder: save_and_load_chat_content(
                folder),
            wraplength=260,  # Allow text wrapping
            justify=tk.CENTER,  # Center the wrapped text
            anchor=tk.CENTER)  # Center the text in button
        snapshot_button.pack(fill=tk.X, pady=2, padx=2)
        button_mapping[snapshot_folder] = snapshot_button

    untitled_button = tk.Button(
        buttons_frame,
        text="untitled",
        command=save_and_load_untitled_chat,
        wraplength=260,  # Allow text wrapping
        justify=tk.CENTER,  # Center the wrapped text
        anchor=tk.CENTER)  # Center the text in button
    untitled_button.pack(fill=tk.X, pady=2, padx=2)
    button_mapping["untitled"] = untitled_button

    buttons_frame.bind(
        "<Configure>",
        lambda e: canvas.config(scrollregion=canvas.bbox("all")))

    # Update buttons frame width when window is resized
    def update_buttons_width(event):
        canvas_width = event.width
        canvas.itemconfig(canvas.find_withtag("all")[0], width=canvas_width)
        for button in buttons_frame.winfo_children():
            button.config(wraplength=canvas_width - 20)

    canvas.bind("<Configure>", update_buttons_width)

    buttons = buttons_frame.winfo_children()
    if buttons:
        buttons[-1].invoke()


def handle_keypress(event):
    """Handles the Enter key press to send messages."""
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        return "break"  # Prevent default newline behavior


def show_save_popup(target_snapshot):
    """Show a warning dialog for unsaved changes."""
    unsaved_warning = tk.Toplevel(root)
    unsaved_warning.title("Unsaved Changes")
    unsaved_warning.geometry("300x150")
    unsaved_warning.transient(root)  # Make it modal
    unsaved_warning.grab_set()  # Make it modal

    label = tk.Label(
        unsaved_warning,
        text="Do you want to save a NEW Snapshot before discarding this chat?",
        wraplength=250)
    label.pack(pady=10)

    button_frame = tk.Frame(unsaved_warning)
    button_frame.pack(pady=10)

    def on_yes():
        unsaved_warning.grab_release()
        unsaved_warning.destroy()
        # First save the current chat
        save_chat()
        # Then load the target chat after a brief delay to ensure cleanup
        root.after(100, lambda: _load_chat(target_snapshot))

    def on_no():
        unsaved_warning.grab_release()
        unsaved_warning.destroy()
        # Disable UI while loading
        send_button.config(state=tk.DISABLED)
        user_input.config(state=tk.DISABLED)
        _load_chat(target_snapshot)

    def on_cancel():
        unsaved_warning.grab_release()
        unsaved_warning.destroy()
        enable_ui()

    yes_button = tk.Button(button_frame, text="Yes", command=on_yes)
    yes_button.pack(side=tk.LEFT, padx=5)

    no_button = tk.Button(button_frame, text="No", command=on_no)
    no_button.pack(side=tk.LEFT, padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.LEFT, padx=5)

    # Handle window close button
    unsaved_warning.protocol("WM_DELETE_WINDOW", on_cancel)


def set_active_chat_button(button):
    global active_chat_button
    if active_chat_button:
        try:
            active_chat_button.config(relief="raised")
        except _tkinter.TclError:
            pass  # Handle the case where the widget no longer exists
    active_chat_button = button
    if active_chat_button:
        active_chat_button.config(relief="sunken")


def save_and_load_chat_content(target_snapshot):
    """Save current chat if needed and load the target snapshot."""
    global controller, active_chat_snapshot

    # Disable UI while checking
    send_button.config(state=tk.DISABLED)
    user_input.config(state=tk.DISABLED)

    if controller and controller.message_streamer.messages:
        show_save_popup(target_snapshot)
    else:
        _load_chat(target_snapshot)


def update_animation_data():
    """Updates the animation data display with the latest animation information."""
    if not controller:
        animation_label.config(text="Animation Data - No active session")
        animation_window.config(state=tk.NORMAL)
        animation_window.delete(1.0, tk.END)
        animation_window.insert(
            tk.END,
            "No active chat session.\nPlease start a chat to view animation data."
        )
        animation_window.config(state=tk.DISABLED)
        return

    try:
        step_number = len(controller.message_streamer.messages
                          ) if controller.message_streamer else 0
        animation_label.config(text=f"Animation Data - Step {step_number}")

        animation_window.config(state=tk.NORMAL)
        animation_window.delete(1.0, tk.END)

        if hasattr(controller,
                   'animation_manager') and controller.animation_manager:
            animation_data = controller.animation_manager.get_latest_sequence()
            if animation_data:
                animation_window.insert(tk.END, animation_data)
            else:
                animation_window.insert(
                    tk.END,
                    "No animation data available for the current step.")
        else:
            animation_window.insert(tk.END,
                                    "Animation manager not initialized.")

        animation_window.config(state=tk.DISABLED)
        animation_window.see(tk.END)  # Auto scroll to bottom
    except Exception as e:
        animation_window.config(state=tk.NORMAL)
        animation_window.delete(1.0, tk.END)
        animation_window.insert(tk.END,
                                f"Error fetching animation data: {str(e)}")
        animation_window.config(state=tk.DISABLED)


# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("1200x500")  # Increased width to accommodate new panel

# Create a PanedWindow to make the divider adjustable
paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# Create a frame for the left chat list
chat_list_frame = tk.Frame(paned_window, bg="#2c2c2c")
paned_window.add(chat_list_frame, minsize=300, width=300)

# Create a frame for the middle chat area
chat_frame = tk.Frame(paned_window)
paned_window.add(chat_frame, minsize=400)

# Create a frame for the right animation panel
animation_frame = tk.Frame(paned_window, bg="#2c2c2c")
paned_window.add(animation_frame, minsize=400, width=400)  # Increased width

# Create a frame for the top bar
top_bar = tk.Frame(chat_frame, bg="#2c2c2c")
top_bar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Create a frame for the labels (title and status) on the left
labels_frame = tk.Frame(top_bar, bg="#2c2c2c")
labels_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Add a label to display the active chat name
active_chat_label = tk.Label(labels_frame,
                             text="Active Chat: None",
                             fg="#ffffff",
                             bg="#2c2c2c",
                             anchor="w",
                             font=(CHAT_FONT, 12))
active_chat_label.pack(side=tk.TOP, fill=tk.X, padx=5)

# Add a save status label for feedback with text wrapping
save_status_label = tk.Label(labels_frame,
                             text="",
                             fg="light gray",
                             bg="#2c2c2c",
                             font=(CHAT_FONT, 10),
                             anchor="w",
                             wraplength=600)  # Increased wraplength
save_status_label.pack(side=tk.TOP, fill=tk.X, padx=5)

# Create a frame for the buttons on the right
buttons_frame = tk.Frame(top_bar, bg="#2c2c2c")
buttons_frame.pack(side=tk.RIGHT)

# Add a save button for snapshots
save_button = tk.Button(buttons_frame, text="Save", command=save_chat)
save_button.pack(side=tk.RIGHT, padx=5)

# Create a header frame for the animation panel
animation_header = tk.Frame(animation_frame, bg="#2c2c2c")
animation_header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Add a label for the animation panel
animation_label = tk.Label(animation_header,
                           text="Animation Data",
                           fg="#ffffff",
                           bg="#2c2c2c",
                           font=(CHAT_FONT, 12))
animation_label.pack(side=tk.LEFT, padx=5)


# Define handler functions for the buttons
def handle_stop():
    original_state = chat_window.cget("state")
    chat_window.config(state=tk.NORMAL)
    if controller:
        response = controller.stop()
        append_message_to_window("System", response)
    else:
        append_message_to_window("System", "Controller not initialized.")
    chat_window.config(state=original_state)


def handle_render():
    original_state = chat_window.cget("state")
    chat_window.config(state=tk.NORMAL)
    if controller:
        response = controller.render()
        append_message_to_window("System", response)
    else:
        append_message_to_window("System", "Controller not initialized.")
    chat_window.config(state=original_state)


# Add render and stop buttons to animation header
stop_button = tk.Button(animation_header, text="Stop", command=handle_stop)
stop_button.pack(side=tk.RIGHT, padx=5)

render_button = tk.Button(animation_header,
                          text="Render",
                          command=handle_render)
render_button.pack(side=tk.RIGHT, padx=5)

# Create a scrolled text widget for the animation data
animation_window = scrolledtext.ScrolledText(animation_frame,
                                             wrap=tk.WORD,
                                             width=40,
                                             height=20,
                                             bg="#2c2c2c",
                                             fg="#ffffff",
                                             font=(CHAT_FONT, 12))
animation_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Add zoom capability to animation window
animation_window.bind("<Control-MouseWheel>",
                      lambda e: zoom(e, animation_window))
animation_window.bind("<Control-Button-4>",
                      lambda e: zoom(e, animation_window))
animation_window.bind("<Control-Button-5>",
                      lambda e: zoom(e, animation_window))

# Create a scrolled text widget for the chat window
chat_window = scrolledtext.ScrolledText(chat_frame,
                                        wrap=tk.WORD,
                                        state=tk.DISABLED,
                                        height=20,
                                        width=50,
                                        bg="#2c2c2c",
                                        fg="#ffffff",
                                        insertbackground="#ffffff",
                                        font=(CHAT_FONT, 16))


def zoom(event, widget):
    current_font_size = widget.cget("font").split()[-1]
    new_font_size = int(current_font_size) + (1 if event.delta > 0 else -1)
    new_font_size = max(8, new_font_size)  # Set a minimum font size
    widget.config(font=(CHAT_FONT, new_font_size))


chat_window.bind("<Control-MouseWheel>", lambda e: zoom(e, chat_window))
chat_window.bind("<Control-Button-4>",
                 lambda e: zoom(e, chat_window))  # For Linux
chat_window.bind("<Control-Button-5>",
                 lambda e: zoom(e, chat_window))  # For Linux

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
# input_frame = tk.Frame(chat_frame)
input_frame = tk.Frame(chat_frame,
                       height=10)  # Adjusted height to allow more space
input_frame.pack(padx=10, pady=10, fill=tk.BOTH)

send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Create a text widget for user input
user_input = tk.Text(input_frame, height=5, wrap=tk.WORD,
                     font=(CHAT_FONT,
                           16))  # Adjusted height to allow 2-3 lines of text
user_input.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
user_input.bind("<Return>", handle_keypress)
user_input.bind("<Shift-Return>",
                lambda event: None)  # Allow new line on Shift+Enter

# Ensure the input_frame size is not being squeezed by other elements
# input_frame.pack_propagate(False)

user_input.bind("<Control-MouseWheel>", lambda e: zoom(e, user_input))
user_input.bind("<Control-Button-4>",
                lambda e: zoom(e, user_input))  # For Linux
user_input.bind("<Control-Button-5>",
                lambda e: zoom(e, user_input))  # For Linux

# Populate the snapshot list
populate_snapshot_list()


# Make sure to clean up the thread pool on exit
def on_closing():
    """Handle application shutdown."""
    if controller:
        controller.shutdown()  # Final save on application exit
    thread_pool.shutdown(wait=False)
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the application
root.mainloop()
