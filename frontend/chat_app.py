from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

class ChatApp(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical')

        # Scroll view for chat history
        self.chat_history = ScrollView()
        self.chat_history_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.chat_history_layout.bind(minimum_height=self.chat_history_layout.setter('height'))
        self.chat_history.add_widget(self.chat_history_layout)
        layout.add_widget(self.chat_history)

        # Input area
        input_layout = BoxLayout(size_hint_y=None, height=100)
        self.message_input = TextInput(hint_text="Enter message", size_hint_y=None, height=80, multiline=True, size_hint_x=.8)
        send_button = Button(text="Send", size_hint_y=None, height=80, size_hint_x=.2)
        send_button.bind(on_press=self.send_message)
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_button)
        layout.add_widget(input_layout)

        # Bind Enter and Shift+Enter keys
        Window.bind(on_key_down=self.on_key_down)

        return layout

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:  # Enter key
            if 'shift' in modifiers:
                self.message_input.text += '\n'
            else:
                self.send_message(None)

    def send_message(self, instance):
        message = self.message_input.text.strip()
        if message:
            # User message (right-aligned)
            user_label = Label(text=f"You: {message}", size_hint_y=None, height=40, halign='left', pos_hint={'right': 1})  # Right align with pos_hint
            self.chat_history_layout.add_widget(user_label)

            # System reply (left-aligned)
            system_label = Label(text="System: Received!", size_hint_y=None, height=40, halign='left')  # Left align
            self.chat_history_layout.add_widget(system_label)

            # Clear the input field
            self.message_input.text = ""

if __name__ == '__main__':
    ChatApp().run()