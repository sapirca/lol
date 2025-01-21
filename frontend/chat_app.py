import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

# Alignment flags
USER_ALIGNMENT = "left"
SYSTEM_ALIGNMENT = "left"

def send_message(event=None):
    user_message = user_input.get("1.0", tk.END).strip()
    if user_message:
        chat_window.config(state=tk.NORMAL)

        # Get the current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Add user message with label, color, and timestamp
        chat_window.insert(tk.END, f"[{current_time}] You:\n", "user_label")
        chat_window.insert(tk.END, f"{user_message}\n\n", "user_message")
        chat_window.tag_add("user_label", "end-5l linestart", "end-4l")
        chat_window.tag_add("user_message", "end-4l linestart", "end-2l")
        chat_window.tag_configure("user_label", foreground="hot pink", justify=USER_ALIGNMENT)
        chat_window.tag_configure("user_message", justify=USER_ALIGNMENT)

        # Call the main controller for the system reply
        system_reply = main_controller(user_message)

        # Add system message with label, color, and timestamp
        chat_window.insert(tk.END, f"[{current_time}] System:\n", "system_label")
        chat_window.insert(tk.END, f"{system_reply}\n\n", "system_message")
        chat_window.tag_add("system_label", "end-5l linestart", "end-4l")
        chat_window.tag_add("system_message", "end-4l linestart", "end-2l")
        chat_window.tag_configure("system_label", foreground="lime", justify=SYSTEM_ALIGNMENT)
        chat_window.tag_configure("system_message", justify=SYSTEM_ALIGNMENT)

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

def handle_keypress(event):
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        return "break"  # Prevent default newline behavior

def initialize_chat():
    chat_window.config(state=tk.NORMAL)
    current_time = datetime.now().strftime("%H:%M:%S")
    chat_window.insert(tk.END, f"[{current_time}] System:\n", "system_label")
    chat_window.insert(tk.END, "Welcome to LOL - the Light Animations Orchestrator Dialog Agent!\n\n", "system_message")
    chat_window.tag_add("system_label", "1.0", "1.8")
    chat_window.tag_add("system_message", "1.8", "end-1c")
    chat_window.tag_configure("system_label", foreground="lime", justify=SYSTEM_ALIGNMENT, spacing1=1, spacing3=5)
    chat_window.tag_configure("system_message", justify=SYSTEM_ALIGNMENT, spacing1=1, spacing3=5)
    chat_window.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("800x500")

# Create a frame for the chat window
chat_frame = tk.Frame(root)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a scrolled text widget for the chat window
chat_window = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, width=50)
chat_window.pack(fill=tk.BOTH, expand=True)

# Create a frame for the input
input_frame = tk.Frame(root)
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
