from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp


# Flags for alignment
ALIGNMENT = {
    "user": "left",    # Set to "left" or "right"
    "system": "right"  # Set to "left" or "right"
}


class ChatApp(App):
    def build(self):
        # Main layout
        self.root = BoxLayout(orientation='vertical', padding=dp(10))

        # Scrollable chat display
        self.chat_display = ScrollView(size_hint=(1, 0.8))
        self.messages_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        self.chat_display.add_widget(self.messages_layout)

        # Input and send button layout
        input_layout = BoxLayout(size_hint=(1, 0.1), padding=dp(10), spacing=dp(10))
        self.message_input = TextInput(hint_text="Type a message...", multiline=True)
        self.message_input.bind(on_text_validate=self.on_enter_key)

        send_button = Button(text="Send", on_press=self.send_message)

        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_button)

        # Add widgets to main layout
        self.root.add_widget(self.chat_display)
        self.root.add_widget(input_layout)

        return self.root

    def send_message(self, instance=None):
        # Get user input
        message = self.message_input.text.strip()
        if message:
            # Display user's message with configurable alignment
            self.display_message("You", message, align_right=False)
            # Clear input
            self.message_input.text = ""

            # Simulate a system reply
            self.system_reply()

    def system_reply(self):
        # Example system reply
        reply_message = "This is a system reply!"
        # Display system message with configurable alignment
        self.display_message("System", reply_message, align_right=True)

    def display_message(self, sender, message, align_right=False):
        # Layout for a single message
        message_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=(dp(5), dp(0)),  # Minimal padding for messages
            orientation='horizontal'
        )

        message_label = Label(
            text=f"[{sender}]: {message}",
            size_hint_x=0.9,
            size_hint_y=None,
            height=dp(50),
            markup=True,
            halign="right" if align_right else "left",  # Align text based on sender
            valign="middle",
            text_size=(None, dp(50)),
        )

        if align_right:
            # Align message to the right
            message_layout.add_widget(Widget(size_hint_x=0.40))  # Smaller spacer on the left
            message_layout.add_widget(message_label)
        else:
            # Align message to the left
            message_layout.add_widget(message_label)
            message_layout.add_widget(Widget(size_hint_x=0.40))  # Smaller spacer on the right

        self.messages_layout.add_widget(message_layout)
        # Auto-scroll to the bottom
        self.chat_display.scroll_to(message_layout)

    def handle_keyboard(self, window, key, scancode, codepoint, modifier):
        # Check if Enter is pressed
        if key == 13:  # Enter key
            if "shift" in modifier:
                # Shift+Enter for a new line
                self.message_input.text += "\n"
            else:
                # Enter sends the message
                self.send_message()

    def on_enter_key(self, instance):
        # This method is required if the user presses Enter without Shift
        self.send_message()


if __name__ == "__main__":
    ChatApp().run()
