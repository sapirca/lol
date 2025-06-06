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
from controller.message_streamer import (
    TAG_USER_INPUT,
    TAG_ASSISTANT,
    TAG_SYSTEM,
    TAG_SYSTEM_INTERNAL,
    TAG_ACTION_RESULTS,
)
from constants import MODEL_CONFIGS

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

# Message type constants
TYPE_USER = "user"
TYPE_ASSISTANT = "assistant"
TYPE_SYSTEM = "system"
TYPE_INTERNAL = "internal"

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

FONT_SIZE_LABELS = 12
FONT_SIZE_CHAT = 16


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


def append_message_to_window(sender, message, context, visible):
    """Adds a message to the chat window."""
    timestamp = datetime.now().strftime(TIME_FORMAT)
    append_message_to_window_w_timestamp(timestamp, sender, message, context,
                                         visible)


def build_message_title(timestamp, sender, context, visible):
    """Builds a standardized message title."""
    title = f"[{timestamp}]"
    if context:
        title += " | + LLM"
    title += f" | {sender}"
    title += ":\n"
    return title


def append_message_to_window_w_timestamp(timestamp, sender, message, context,
                                         visible):
    """Adds a message to the chat window with proper formatting and clickable links."""
    if not visible:
        type_name = TYPE_INTERNAL
    elif sender.lower() == "you":
        type_name = TYPE_USER
    elif sender.lower() == "assistant":
        type_name = TYPE_ASSISTANT
    elif sender.lower() == "system":
        type_name = TYPE_SYSTEM
    else:
        type_name = TYPE_SYSTEM

    label_tag = get_label_tag(type_name)
    message_tag = get_message_tag(type_name)

    # Ensure chat_window is writable
    original_state = chat_window.cget("state")
    chat_window.config(state=tk.NORMAL)

    # Configure tags with colors and alignments
    configure_chat_tags(chat_window)

    title = build_message_title(timestamp, sender, context, visible)
    chat_window.insert(tk.END, title, label_tag)

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

    # Add confirmation buttons if this is an assistant message that requires confirmation
    if type_name == TYPE_ASSISTANT and controller:
        # Check for pending action instead of last action result
        pending_info = controller.get_pending_action_info()
        if pending_info and pending_info[
                "confirmation_type"] != "no-action-required":
            # Create a frame for the buttons
            button_frame = tk.Frame(chat_window, bg="#2c2c2c")
            chat_window.window_create(tk.END, window=button_frame)

            # Create the OK button
            ok_button = tk.Button(
                button_frame,
                text="Run",
                command=lambda: handle_confirmation(True),
                bg="#4CAF50",  # Green color
                fg="white",
                font=(CHAT_FONT, 12),
                padx=10,
                pady=5,
                relief=tk.RAISED,
                borderwidth=2)
            ok_button.pack(side=tk.LEFT, padx=5)

            # Create the No button
            no_button = tk.Button(
                button_frame,
                text="Cancel",
                command=lambda: handle_confirmation(False),
                bg="#f44336",  # Red color
                fg="white",
                font=(CHAT_FONT, 12),
                padx=10,
                pady=5,
                relief=tk.RAISED,
                borderwidth=2)
            no_button.pack(side=tk.LEFT, padx=5)

            # Add a separator line
            chat_window.insert(tk.END, "\n" + "─" * 50 + "\n\n")

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
    # start with captial letter
    framework_info = framework_info.capitalize()
    # Get model info from config if available
    model_info = ""
    if controller and controller.config and "model_config" in controller.config:
        model_name = controller.config["model_config"]["model_name"]
        max_tokens = controller.config["model_config"]["max_tokens"]
        song_name = controller.config["song_name"]
        model_info = f" {model_name[:10]} ({max_tokens})"

    active_chat_label.config(
        text=f"{song_name} | {framework_info}| {model_info} | {button_name}")

    # Update status with step number
    step_number = len(
        controller.msgs.messages) if controller and controller.msgs else 0
    if button_name == "untitled":
        save_status_label.config(
            text=f"Started new chat session (msg no {step_number})")
    else:
        save_status_label.config(
            text=
            f"Successfully loaded snapshot: {button_name} (Step {step_number})"
        )

    set_active_chat_button(button)


def refresh():
    """Refresh the chat window with new messages and save the current state."""
    # Get any new messages that were added
    new_messages = controller.msgs.get_new_messages()
    # Update UI with new messages
    for tag, message, context, visible in new_messages:
        # Determine message type based on tag
        if tag == TAG_USER_INPUT or tag == TAG_ACTION_RESULTS:
            type_name = TYPE_USER
        elif tag == TAG_ASSISTANT:
            type_name = TYPE_ASSISTANT
        elif tag == TAG_SYSTEM_INTERNAL:
            type_name = TYPE_INTERNAL
        elif tag == TAG_SYSTEM:
            type_name = TYPE_SYSTEM
        else:
            type_name = TYPE_INTERNAL

        if type_name == TYPE_INTERNAL and not controller.config.get(
                "print_internal_messages", False):
            continue

        # Schedule message display
        sender_name = get_sender_name(type_name)
        root.after(0,
                   lambda s=sender_name, m=message, c=context, v=visible:
                   append_message_to_window(s, m, c, v))


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
        send_button.configure(state=tk.DISABLED, text="Waiting...")

        user_input.unbind("<Return>")  # Disable Enter key
        controller.add_user_input_to_chat(user_message)

        refresh()

        # Use the thread pool to run the backend communication
        thread_pool.submit(run_backend_communication, user_message)


def run_backend_communication(user_message):
    """Runs the backend communication in a separate thread."""
    try:
        controller.communicate(user_message)
        refresh()
        root.after(0, enable_ui)
        root.after(0, update_animation_data)

    except Exception as e:
        root.after(
            0, lambda: update_chat_window(get_label_tag(TYPE_SYSTEM),
                                          get_sender_name(TYPE_SYSTEM),
                                          f"Error: {str(e)}"))
        root.after(0, enable_ui)


def update_chat_window(tag, sender, message):
    """Updates the chat window with a new message."""
    append_message_to_window(sender, message, context=False, visible=True)
    chat_window.see(tk.END)
    # if controller and controller.config.get("print_internal_messages", False):
    #     append_message_to_window(sender, message, True, True)
    # else:
    #     append_message_to_window(sender, message, True, tag
    #                              != TAG_SYSTEM_INTERNAL)


def enable_ui():
    """Re-enables the UI elements."""
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    send_button.configure(state=tk.NORMAL, text="Send")
    user_input.config(state=tk.NORMAL)  # Re-enable the text input
    user_input.bind("<Return>", handle_keypress)


def handle_auto_continue(auto_continue_value):
    """Handle auto-continue checkbox state change."""
    update_chat_window(get_label_tag(TYPE_SYSTEM),
                       get_sender_name(TYPE_SYSTEM),
                       "Automatically continuing conversation...")
    # Disable UI while auto-continuing
    send_button.configure(state=tk.DISABLED)
    user_input.config(state=tk.DISABLED)
    # Schedule the next backend communication
    thread_pool.submit(run_backend_communication, auto_continue_value)
    # if controller and controller.config.get("auto_render", False):
    #     restart_with_latest_sequence()


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
            # Create popup window for naming
            save_popup = tk.Toplevel(root)
            save_popup.title("Save Chat")
            save_popup.geometry("400x200")
            save_popup.transient(root)  # Make it modal
            save_popup.grab_set()  # Make it modal

            # Add label and entry for name
            name_label = tk.Label(save_popup, text="Enter snapshot name:")
            name_label.pack(pady=10)

            name_entry = tk.Entry(save_popup, width=40)
            name_entry.pack(pady=5)
            # Pre-fill the entry with active chat name if not untitled
            if active_chat_snapshot and active_chat_snapshot != "untitled":
                name_entry.insert(0, active_chat_snapshot)
            name_entry.focus_set()  # Set focus to entry

            # Add checkbox frame
            checkbox_frame = tk.Frame(save_popup)
            checkbox_frame.pack(pady=5)

            # Create checkbox with dynamic text
            checkbox_var = tk.BooleanVar()
            checkbox_text = "Use default name" if active_chat_snapshot == "untitled" else "Override current chat"
            checkbox = tk.Checkbutton(checkbox_frame,
                                      text=checkbox_text,
                                      variable=checkbox_var)
            checkbox.pack(side=tk.LEFT)

            def on_checkbox_change():
                if checkbox_var.get():
                    if active_chat_snapshot == "untitled":
                        name_entry.delete(0, tk.END)
                    else:
                        name_entry.delete(0, tk.END)
                        name_entry.insert(0, active_chat_snapshot)
                    name_entry.config(state=tk.DISABLED)
                else:
                    name_entry.config(state=tk.NORMAL)

            checkbox.config(command=on_checkbox_change)

            # Add buttons frame
            button_frame = tk.Frame(save_popup)
            button_frame.pack(pady=20)

            def on_save():
                global controller, active_chat_snapshot
                snapshot_name = name_entry.get().strip()
                # if checkbox is checked, use the default name
                if checkbox_var.get():
                    snapshot_name = None
                save_popup.destroy()
                if snapshot_name:
                    # verify that the name is legit, without spaces or special characters
                    if not re.match(r"^[a-zA-Z0-9_-]+$", snapshot_name):
                        save_status_label.config(text="Invalid name", fg="red")
                        return
                    save_message = controller.shutdown(snapshot_name)
                else:
                    save_message = "No name provided. "
                    save_message += controller.shutdown()
                save_status_label.config(text=save_message, fg="light gray")

                # Store controller reference before clearing
                old_controller = controller

                # Clear the chat window after saving
                chat_window.config(state=tk.NORMAL)
                chat_window.delete("1.0", tk.END)
                chat_window.config(state=tk.DISABLED)

                # Clear the controller and active snapshot
                controller = None
                active_chat_snapshot = None

                # Load the newly saved chat
                if snapshot_name:
                    _load_chat(snapshot_name)
                else:
                    # If no name provided, use the timestamp from the save message
                    # Extract timestamp from save message (format: "Snapshot saved: timestamp_framework_backend")
                    match = re.search(r"Snapshot saved: (\d{6}_\d{6}_\w+_\w+)",
                                      save_message)
                    if match:
                        snapshot_name = match.group(1)
                        _load_chat(snapshot_name)
                    else:
                        # Fallback to untitled if we can't extract the name
                        _load_untitled_chat()

                populate_snapshot_list()  # Refresh the snapshot list

            def on_cancel():
                save_popup.destroy()

            # Add buttons
            save_button = tk.Button(button_frame, text="Save", command=on_save)
            save_button.pack(side=tk.LEFT, padx=5)

            cancel_button = tk.Button(button_frame,
                                      text="Cancel",
                                      command=on_cancel)
            cancel_button.pack(side=tk.LEFT, padx=5)

            # Handle window close button
            save_popup.protocol("WM_DELETE_WINDOW", on_cancel)

            # Bind Enter key to save
            save_popup.bind("<Return>", lambda e: on_save())

        except Exception as e:
            save_status_label.config(text=f"Failed to save chat: {str(e)}",
                                     fg="red")
    else:
        save_status_label.config(text="No active chat to save", fg="red")


PRIMARY_COLOR = "#BBDEFB"  # Example: Blue 100 (lighter blue)
PRIMARY_COLOR_VARIANT = "#64B5F6"  # Example: Blue 300
SECONDARY_COLOR = "#F48FB1"  # Example: Pink 200 (lighter pink)
SECONDARY_COLOR_VARIANT = "#F06292"  # Example: Pink 300

# Error color
ERROR_COLOR = "#CF6679"


def get_label_tag(type_name):
    """Get the label tag for a given type."""
    return f"{type_name}_label"


def get_message_tag(type_name):
    """Get the message tag for a given type."""
    return f"{type_name}_message"


def get_sender_name(type_name):
    """Get the sender name for a given type."""
    return type_name.capitalize() if type_name != TYPE_USER else "You"


def configure_chat_tags(chat_window):
    """Configure the chat window tags with appropriate colors and alignments."""
    # System message styling
    chat_window.tag_configure(
        get_label_tag(TYPE_SYSTEM),
        foreground="#8BE9FD",  # Light cyan
        justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure(get_message_tag(TYPE_SYSTEM),
                              justify=SYSTEM_ALIGNMENT)

    # Assistant message styling
    chat_window.tag_configure(
        get_label_tag(TYPE_ASSISTANT),
        foreground="#FFB86C",  # Soft orange
        justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure(get_message_tag(TYPE_ASSISTANT),
                              justify=SYSTEM_ALIGNMENT)

    # User message styling
    chat_window.tag_configure(
        get_label_tag(TYPE_USER),
        foreground="#9580FF",  # Soft purple
        justify=USER_ALIGNMENT)
    chat_window.tag_configure(get_message_tag(TYPE_USER),
                              justify=USER_ALIGNMENT)

    # Internal message styling
    chat_window.tag_configure(get_label_tag(TYPE_INTERNAL),
                              foreground="grey",
                              justify=SYSTEM_ALIGNMENT)
    chat_window.tag_configure(get_message_tag(TYPE_INTERNAL),
                              foreground="grey",
                              justify=SYSTEM_ALIGNMENT)


def batch_insert_messages(messages):
    """Efficiently insert multiple messages into the chat window."""
    # Pre-configure tags
    configure_chat_tags(chat_window)

    # Build content in memory
    content = []
    for timestamp, message, tag, visible, context in messages:
        if tag == TAG_USER_INPUT:
            type_name = TYPE_USER
        elif tag == TAG_ASSISTANT:
            type_name = TYPE_ASSISTANT
        elif not visible:
            type_name = TYPE_INTERNAL
        else:
            type_name = TYPE_SYSTEM

        if type_name == TYPE_INTERNAL and not controller.config.get(
                "print_internal_messages", False):
            continue

        label_tag = get_label_tag(type_name)
        message_tag = get_message_tag(type_name)
        sender = get_sender_name(type_name)

        title = build_message_title(timestamp, sender, context, visible)
        content.append((title, label_tag))
        content.append((f"{message}\n\n", message_tag))

    # Insert all content at once
    for text, tag in content:
        chat_window.insert(tk.END, text, tag)

    chat_window.see(tk.END)


def initialize_untitled_chat():
    """Initialize a new untitled chat session with consistent welcome messages."""
    global controller, active_chat_snapshot
    controller = LogicPlusPlus()
    active_chat_snapshot = "untitled"

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)

    # Welcome message
    message = "Welcome to a new chat session!"
    update_chat_window(get_label_tag(TYPE_SYSTEM),
                       get_sender_name(TYPE_SYSTEM), message)

    # System info
    print_system_info()

    chat_window.config(state=tk.DISABLED)
    update_active_chat_label("untitled")
    update_animation_data()


def _load_untitled_chat():
    """Load a new untitled chat session."""
    initialize_untitled_chat()


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
            initialize_untitled_chat()
            return
        else:
            snapshot_path = os.path.abspath(
                os.path.join(SNAPSHOTS_DIR, a_snapshot))
            controller = LogicPlusPlus(snapshot_path)

        active_chat_snapshot = a_snapshot

        # Load chat history
        chat_history = controller.get_chat_history()

        # Update chat window in one go
        chat_window.config(state=tk.NORMAL)
        chat_window.delete("1.0", tk.END)

        if chat_history:
            batch_insert_messages(chat_history)
        else:
            message = "No chat history found in snapshot."
            update_chat_window(get_label_tag(TYPE_SYSTEM),
                               get_sender_name(TYPE_SYSTEM), message)

        print_system_info()
        update_active_chat_label(a_snapshot)
        update_animation_data()

        controller.msgs.clear_control_flags()
        update_chat_window(get_label_tag(TYPE_INTERNAL),
                           get_sender_name(TYPE_INTERNAL),
                           "Any control flags are disregarded.")
    except Exception as e:
        error_msg = f"Error loading snapshot {a_snapshot}: {str(e)}"
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM), error_msg)
        save_status_label.config(text=f"Error loading chat: {str(e)}",
                                 fg="red")

    finally:
        chat_window.config(state=tk.DISABLED)
        enable_ui()  # Always re-enable the UI


def print_system_info():
    backend_name = controller.selected_backend or "Unknown Backend"
    message = f"Active Backend is: {backend_name}"
    update_chat_window(get_label_tag(TYPE_SYSTEM),
                       get_sender_name(TYPE_SYSTEM), message)


def save_and_load_untitled_chat():
    """Ensure an untitled chat session exists without resetting."""
    global controller, active_chat_snapshot
    if controller and controller.msgs.messages:
        show_save_popup("untitled")
    else:
        _load_untitled_chat()


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

    if controller and controller.msgs.messages:
        show_save_popup(target_snapshot)
    else:
        _load_chat(target_snapshot)


def update_animation_data():
    """Updates the animation data display with the latest animation information."""
    default_message = "No animations generated yet.\nStart chatting to generate animations!"

    if not controller:
        animation_label.config(text="Animation Data")
        animation_window.config(state=tk.NORMAL)
        animation_window.delete(1.0, tk.END)
        animation_window.insert(tk.END, default_message)
        animation_window.config(state=tk.DISABLED)
        return

    try:
        animation_window.config(state=tk.NORMAL)
        animation_window.delete(1.0, tk.END)

        if hasattr(controller,
                   'animation_manager') and controller.animation_manager:
            try:
                sequence_data = controller.animation_manager.get_latest_sequence_with_step(
                )
                if sequence_data:
                    animation_data, step_number = sequence_data
                    animation_label.config(
                        text=f"Animation Data - Step {step_number}")
                    animation_window.insert(tk.END, animation_data)
                else:
                    animation_label.config(text="Animation Data")
                    animation_window.insert(tk.END, default_message)
            except AttributeError:
                # Handle the case where sequences list is not initialized
                animation_label.config(text="Animation Data")
                animation_window.insert(tk.END, default_message)
        else:
            animation_label.config(text="Animation Data")
            animation_window.insert(tk.END, default_message)

        animation_window.config(state=tk.DISABLED)
        animation_window.see(tk.END)  # Auto scroll to bottom
    except Exception as e:
        animation_label.config(text="Animation Data")
        animation_window.config(state=tk.NORMAL)
        animation_window.delete(1.0, tk.END)
        animation_window.insert(tk.END, default_message)
        animation_window.config(state=tk.DISABLED)


def restart_with_latest_sequence():
    """Restart the chat with the latest sequence from the current controller."""
    global controller, active_chat_snapshot

    if not controller:
        save_status_label.config(text="No active chat to restart from",
                                 fg="red")
        return

    try:
        # Store old controller temporarily
        old_controller = controller

        # Initialize new controller with restart config
        controller = LogicPlusPlus(restart_config=old_controller)
        active_chat_snapshot = "untitled"

        # Clear chat window
        chat_window.config(state=tk.NORMAL)
        chat_window.delete("1.0", tk.END)

        # Welcome message
        message = "Welcome to a new chat session with the latest animation sequence!"
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM), message)

        # System info
        print_system_info()

        chat_window.config(state=tk.DISABLED)
        update_active_chat_label("untitled")
        update_animation_data()

        save_status_label.config(
            text="Successfully restarted with latest sequence",
            fg="light gray")

    except Exception as e:
        error_msg = f"Error restarting chat: {str(e)}"
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM), error_msg)
        save_status_label.config(text=f"Error restarting chat: {str(e)}",
                                 fg="red")
    finally:
        enable_ui()


def reduce_tokens():
    """Reduce tokens by summarizing the conversation."""
    global controller

    if not controller:
        save_status_label.config(text="No active chat to reduce tokens",
                                 fg="red")
        return

    try:
        # Disable UI while processing
        send_button.config(state=tk.DISABLED)
        user_input.config(state=tk.DISABLED)
        reduce_tokens_button.config(state=tk.DISABLED)

        # Call controller to reduce tokens
        result = controller.reduce_tokens()

        # Clear and update chat window
        chat_window.config(state=tk.NORMAL)
        chat_window.delete("1.0", tk.END)

        # Get the new chat history
        chat_history = controller.get_chat_history()

        # Update chat window with new history
        if chat_history:
            batch_insert_messages(chat_history)
        else:
            message = "No chat history found after token reduction."
            update_chat_window(get_label_tag(TYPE_SYSTEM),
                               get_sender_name(TYPE_SYSTEM), message)

        # Update status
        save_status_label.config(text=result, fg="light gray")

    except Exception as e:
        error_msg = f"Error reducing tokens: {str(e)}"
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM), error_msg)
        save_status_label.config(text=f"Error reducing tokens: {str(e)}",
                                 fg="red")
    finally:
        chat_window.config(state=tk.DISABLED)
        enable_ui()
        reduce_tokens_button.config(state=tk.NORMAL)


def handle_confirmation(confirmed: bool):
    """Handle user confirmation of an action."""
    pending_info = controller.get_pending_action_info()
    auto_continue = False
    if confirmed:
        if pending_info and pending_info.get("turn") == "llm":
            auto_continue = True

        # Execute the pending action
        result = controller.execute_pending_action()
        # if result:
        #     # Add a system message about the action being executed
        #     update_chat_window(
        #         get_label_tag(TYPE_SYSTEM), get_sender_name(TYPE_SYSTEM),
        #         f"Executing action: {result.get('message', '')}")
    else:
        # Cancel the pending action
        controller.cancel_pending_action()
        # Add a system message about the action being cancelled
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM),
                           "Action cancelled by user")

    # Refresh the UI and update animation data
    refresh()
    update_animation_data()
    if auto_continue:
        # If it's LLM's turn, set auto-continue
        controller.msgs.set_control_flag("auto_continue", True)
        handle_auto_continue("")

    # Re-enable the UI
    enable_ui()


def is_valid_chat_name(name):
    """Validate chat name format.
    
    Args:
        name (str): The chat name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Chat name should:
    # - Not be empty
    # - Not contain special characters except underscore and hyphen
    # - Not start with a number
    # - Not contain spaces
    if not name or not isinstance(name, str):
        return False
    
    # Check if name starts with a number
    if name[0].isdigit():
        return False
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False
    
    return True


def initialize_from_config(config, chat_name):
    """Initialize a new chat session with the given configuration and name.
    
    Args:
        config (dict): The configuration to use
        chat_name (str): The name for the new chat
    """
    global controller, active_chat_snapshot, button_mapping
    controller = LogicPlusPlus()
    controller.update_config(config)
    active_chat_snapshot = chat_name

    chat_window.config(state=tk.NORMAL)
    chat_window.delete("1.0", tk.END)

    # Welcome message
    message = f"Welcome to chat session: {chat_name}!"
    update_chat_window(get_label_tag(TYPE_SYSTEM),
                       get_sender_name(TYPE_SYSTEM), message)

    # System info
    print_system_info()

    chat_window.config(state=tk.DISABLED)

    # Add the new chat to the snapshot list
    # Get the buttons frame from the canvas
    canvas = chat_list_frame.winfo_children()[0]  # Get the canvas
    buttons_frame = canvas.winfo_children()[0]    # Get the buttons frame
    
    snapshot_button = tk.Button(
        buttons_frame,
        text=chat_name,
        command=lambda: save_and_load_chat_content(chat_name),
        wraplength=260,
        justify=tk.CENTER,
        anchor=tk.CENTER)
    snapshot_button.pack(fill=tk.X, pady=2, padx=2)
    button_mapping[chat_name] = snapshot_button

    update_active_chat_label(chat_name)
    update_animation_data()



def show_new_chat_dialog():
    """Show dialog to configure new chat settings."""
    dialog = tk.Toplevel(root)
    dialog.title("New Chat Configuration")
    dialog.geometry("400x550")  # Made slightly taller for new field
    dialog.transient(root)
    dialog.grab_set()

    # Create main frame with padding
    main_frame = tk.Frame(dialog, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Get current config values
    current_config = controller.config if controller else {}
    
    # Chat name entry
    tk.Label(main_frame, text="Chat Name:").pack(anchor=tk.W, pady=(0, 5))
    chat_name_var = tk.StringVar(value="untitled")
    chat_name_entry = tk.Entry(main_frame, textvariable=chat_name_var)
    chat_name_entry.pack(fill=tk.X, pady=(0, 10))
    
    # Song selection
    tk.Label(main_frame, text="Song:").pack(anchor=tk.W, pady=(0, 5))
    song_var = tk.StringVar(value=current_config.get("song_name", "aladdin"))
    song_dropdown = ttk.Combobox(main_frame, textvariable=song_var, state="readonly")
    song_dropdown['values'] = ["aladdin", "nikki", "sandstorm"]
    song_dropdown.pack(fill=tk.X, pady=(0, 10))

    # Framework selection
    tk.Label(main_frame, text="Framework:").pack(anchor=tk.W, pady=(0, 5))
    framework_var = tk.StringVar(value=current_config.get("framework", "kivsee"))
    framework_dropdown = ttk.Combobox(main_frame, textvariable=framework_var, state="readonly")
    framework_dropdown['values'] = ["kivsee", "xlights", "conceptual"]
    framework_dropdown.pack(fill=tk.X, pady=(0, 10))

    # Backend selection
    tk.Label(main_frame, text="Backend:").pack(anchor=tk.W, pady=(0, 5))
    backend_var = tk.StringVar(value=current_config.get("selected_backend", "Claude"))
    backend_dropdown = ttk.Combobox(main_frame, textvariable=backend_var, state="readonly")
    backend_dropdown['values'] = ["Claude", "GPT", "Gemini"]
    backend_dropdown.pack(fill=tk.X, pady=(0, 10))

    # Model selection
    tk.Label(main_frame, text="Model:").pack(anchor=tk.W, pady=(0, 5))
    model_var = tk.StringVar()
    model_dropdown = ttk.Combobox(main_frame, textvariable=model_var, state="readonly")
    
    def update_model_options(*args):
        backend = backend_var.get()
        model_dropdown['values'] = [k for k in MODEL_CONFIGS.keys() if k.startswith(backend.lower())]
        if model_dropdown['values']:
            model_var.set(model_dropdown['values'][0])
    
    backend_var.trace('w', update_model_options)
    update_model_options()
    model_dropdown.pack(fill=tk.X, pady=(0, 10))

    # Start with skeleton checkbox
    skeleton_var = tk.BooleanVar(value=False)
    skeleton_check = tk.Checkbutton(main_frame, text="Start with a skeleton", variable=skeleton_var)
    skeleton_check.pack(anchor=tk.W, pady=(0, 10))

    # Error label for validation messages
    error_label = tk.Label(main_frame, text="", fg="red")
    error_label.pack(anchor=tk.W, pady=(0, 10))

    def on_save():
        chat_name = chat_name_var.get().strip()
        if not is_valid_chat_name(chat_name):
            error_label.config(text="Invalid chat name. Use only letters, numbers, underscore, and hyphen.")
            return
            
        new_config = {
            "song_name": song_var.get(),
            "framework": framework_var.get(),
            "selected_backend": backend_var.get(),
            "model_config": MODEL_CONFIGS[model_var.get()]
        }
        
        # Initialize new chat with config
        initialize_from_config(new_config, chat_name)
        
        # Build skeleton if requested
        if skeleton_var.get():
            controller.build_skeleton()
        
        # # Save the chat with the new name
        # save_chat()
        
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    # Buttons frame
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(20, 0))
    
    save_button = tk.Button(button_frame, text="Save", command=on_save, width=10)
    save_button.pack(side=tk.RIGHT, padx=5)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel, width=10)
    cancel_button.pack(side=tk.RIGHT, padx=5)


# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("1600x800")  # Increased width and height for better visibility

# Create custom styles for buttons
style = ttk.Style()
style.configure("Waiting.TButton",
                background="#4a4a4a",
                foreground="white",
                padding=5,
                relief="flat")
style.configure("Normal.TButton", padding=5)

# Create a PanedWindow to make the divider adjustable
paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# Create a frame for the left chat list
chat_list_frame = tk.Frame(paned_window, bg="#2c2c2c")
paned_window.add(chat_list_frame, minsize=250,
                 width=250)  # Slightly reduced width for chat list

# Create a frame for the middle chat area
chat_frame = tk.Frame(paned_window)
paned_window.add(chat_frame, minsize=650)  # Increased minsize for chat area

# Create a frame for the right animation panel
animation_frame = tk.Frame(paned_window, bg="#2c2c2c")
paned_window.add(animation_frame, minsize=600,
                 width=600)  # Increased width for animation panel

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
                             font=(CHAT_FONT, FONT_SIZE_LABELS))
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
save_button = tk.Button(buttons_frame, text="Save", command=save_chat, width=6)
save_button.pack(side=tk.RIGHT, padx=5)

# Add restart with latest sequence button
restart_button = tk.Button(buttons_frame,
                           text="Restart+",
                           command=lambda: restart_with_latest_sequence(),
                           width=6)
restart_button.pack(side=tk.RIGHT, padx=5)

# Add new chat button
new_chat_button = tk.Button(buttons_frame,
                           text="New Chat",
                           command=show_new_chat_dialog,
                           width=6)
new_chat_button.pack(side=tk.RIGHT, padx=5)

# Add reduce tokens button
reduce_tokens_button = tk.Button(buttons_frame,
                                 text="Summarize",
                                 command=lambda: reduce_tokens(),
                                 width=6)
reduce_tokens_button.pack(side=tk.RIGHT, padx=5)

# Create a header frame for the animation panel
animation_header = tk.Frame(animation_frame, bg="#2c2c2c")
animation_header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Add a label for the animation panel
animation_label = tk.Label(animation_header,
                           text="Animation Data",
                           fg="#ffffff",
                           bg="#2c2c2c",
                           font=(CHAT_FONT, FONT_SIZE_LABELS))
animation_label.pack(side=tk.LEFT, padx=5)


# Define handler functions for the buttons
def handle_stop():
    original_state = chat_window.cget("state")
    chat_window.config(state=tk.NORMAL)
    if controller:
        response = controller.stop()
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM), response)
    else:
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM),
                           "Controller not initialized.")
    chat_window.config(state=original_state)


def handle_render(store_animation=False):
    original_state = chat_window.cget("state")
    chat_window.config(state=tk.NORMAL)
    if controller:
        response = controller.render(store_animation=store_animation)
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM), response)
    else:
        update_chat_window(get_label_tag(TYPE_SYSTEM),
                           get_sender_name(TYPE_SYSTEM),
                           "Controller not initialized.")
    chat_window.config(state=original_state)


# Add render and stop buttons to animation header
stop_button = tk.Button(animation_header, text="Stop", command=handle_stop)
stop_button.pack(side=tk.RIGHT, padx=5)

render_button = tk.Button(
    animation_header,
    text="Render",
    command=lambda: handle_render(store_animation_var.get()))
render_button.pack(side=tk.RIGHT, padx=5)

# Add store animation checkbox
store_animation_var = tk.BooleanVar(value=False)
store_animation_checkbox = tk.Checkbutton(animation_header,
                                          text="Store Animation",
                                          variable=store_animation_var,
                                          bg="#2c2c2c",
                                          fg="#ffffff",
                                          selectcolor="#2c2c2c")
store_animation_checkbox.pack(side=tk.RIGHT, padx=5)

# Create a scrolled text widget for the animation data
animation_window = scrolledtext.ScrolledText(
    animation_frame,
    wrap=tk.WORD,
    width=60,  # Increased width
    height=30,  # Increased height
    bg="#2c2c2c",
    fg="#ffffff",
    font=(CHAT_FONT, FONT_SIZE_CHAT))
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
                                        font=(CHAT_FONT, FONT_SIZE_CHAT))


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
