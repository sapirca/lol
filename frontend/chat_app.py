import tkinter as tk
from tkinter import scrolledtext

def send_message(event=None):
    user_message = user_input.get("1.0", tk.END).strip()
    if user_message:
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"You: {user_message}\n")
        chat_window.tag_add("user", "end-2l linestart", "end-1l")
        chat_window.insert(tk.END, "System: This is a static reply.\n")
        chat_window.tag_add("system", "end-2l linestart", "end-1l")
        chat_window.tag_configure("system", justify="right")
        chat_window.config(state=tk.DISABLED)
        chat_window.see(tk.END)
        user_input.delete("1.0", tk.END)

def handle_keypress(event):
    if event.keysym == "Return" and not event.state & 1:  # Enter without Shift
        send_message()
        return "break"  # Prevent default newline behavior

# Create the main window
root = tk.Tk()
root.title("Chat App")
root.geometry("400x500")

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

# Start the application
root.mainloop()
