import sys
import os
from flask import Flask, render_template, request, jsonify

# Add project root to sys.path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Attempt to import controller and constants
try:
    from controller.logic_pp import LogicPlusPlus
    from controller.message_streamer import (TAG_USER_INPUT, TAG_ASSISTANT,
                                             TAG_SYSTEM, TAG_SYSTEM_INTERNAL,
                                             TAG_ACTION_RESULTS)
    import constants  # Assuming constants.py might be needed by LogicPlusPlus
    CONTROLLER_AVAILABLE = True
except ImportError as e:
    print(
        f"Error importing controller modules: {e}. Controller functionality will be disabled."
    )
    CONTROLLER_AVAILABLE = False

    # Define dummy classes/variables if needed for the script to run without controller
    class LogicPlusPlus:
        pass

    TAG_USER_INPUT, TAG_ASSISTANT, TAG_SYSTEM, TAG_SYSTEM_INTERNAL, TAG_ACTION_RESULTS = [
        None
    ] * 5

app = Flask(__name__)

# Initialize LogicPlusPlus controller
if CONTROLLER_AVAILABLE:
    try:
        controller = LogicPlusPlus()
        print("LogicPlusPlus initialized successfully.")
    except Exception as e:
        print(f"Error initializing LogicPlusPlus: {e}")
        controller = None  # Fallback if initialization fails
else:
    controller = None
    print("LogicPlusPlus controller is not available due to import errors.")

chat_messages = [
]  # This will now be populated from the controller or with error messages


def format_controller_messages_to_chat_messages():
    global chat_messages
    chat_messages = []  # Start fresh

    if not controller:
        error_msg = "Error: Controller not initialized or not available."
        if not CONTROLLER_AVAILABLE:
            error_msg = "Error: Controller modules could not be imported. Please check server logs."
        chat_messages.append({"sender": "System", "text": error_msg})
        return

    try:
        history = controller.get_chat_history(
        )  # Returns list of (timestamp, message, tag, visible, context)

        if not history:
            chat_messages.append({
                "sender": "System",
                "text": "Welcome! Send a message to start."
            })
            if hasattr(controller,
                       'selected_backend') and controller.selected_backend:
                chat_messages.append({
                    "sender":
                    "System",
                    "text":
                    f"Active Backend: {controller.selected_backend}"
                })
            elif hasattr(controller, 'config') and controller.config.get(
                    'selected_backend'):  # Fallback for config
                chat_messages.append({
                    "sender":
                    "System",
                    "text":
                    f"Active Backend: {controller.config.get('selected_backend')}"
                })

            return

        for _timestamp, message, tag, visible, _context in history:
            sender_name = "System"
            if tag == TAG_USER_INPUT or tag == TAG_ACTION_RESULTS:
                sender_name = "User"
            elif tag == TAG_ASSISTANT:
                sender_name = "Assistant"
            elif tag == TAG_SYSTEM_INTERNAL:
                sender_name = "Internal"
            elif tag == TAG_SYSTEM:
                sender_name = "System"

            if not visible and sender_name == "Internal":
                continue

            chat_messages.append({"sender": sender_name, "text": message})
    except Exception as e:
        print(f"Error formatting controller messages: {e}")
        chat_messages.append({
            "sender": "System",
            "text": f"Error retrieving chat history: {e}"
        })


@app.route('/')
def index():
    if CONTROLLER_AVAILABLE and controller:
        format_controller_messages_to_chat_messages()
    else:
        global chat_messages
        chat_messages = []  # Clear any previous messages
        error_msg = "Error: Controller could not be initialized. Please check server logs."
        if not CONTROLLER_AVAILABLE:
            error_msg = "Error: Controller modules could not be imported. Functionality will be limited."
        chat_messages.append({"sender": "System", "text": error_msg})
    return render_template('index.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    if not CONTROLLER_AVAILABLE or not controller:
        error_msg = "Controller not initialized or not available."
        if not CONTROLLER_AVAILABLE:
            error_msg = "Controller modules not imported."
        return jsonify({"status": "error", "message": error_msg}), 500

    data = request.get_json()
    user_message = data.get('message')
    if user_message:
        try:
            controller.add_user_input_to_chat(user_message)
            controller.communicate(user_message)
            format_controller_messages_to_chat_messages()
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error during communication with controller: {e}")
            format_controller_messages_to_chat_messages(
            )  # attempt to load existing history
            chat_messages.append({
                "sender": "System",
                "text": f"Error processing message: {str(e)}"
            })
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": "No message provided"}), 400


@app.route('/get_messages', methods=['GET'])
def get_messages():
    # If controller failed to load, format_controller_messages_to_chat_messages
    # would have already populated chat_messages with an error.
    # This route just returns the current state.
    if not chat_messages:  # Should ideally be populated by index() or send_message()
        # This case might happen if /get_messages is called before /
        if CONTROLLER_AVAILABLE and controller:
            format_controller_messages_to_chat_messages()
        else:
            error_msg = "Error: Controller not initialized or not available."
            if not CONTROLLER_AVAILABLE:
                error_msg = "Error: Controller modules could not be imported."
            return jsonify([{"sender": "System", "text": error_msg}])

    return jsonify(chat_messages)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
