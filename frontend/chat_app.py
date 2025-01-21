from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.bubble import Bubble
from kivy.graphics import Color, Rectangle

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
            # User message bubble (right-aligned)
            user_bubble = Bubble(orientation='vertical', size_hint_y=None, height=40)
            with user_bubble.canvas.before:
                Color(0, 0, 1, 1)  # Blue
                self.rect = Rectangle(pos=user_bubble.pos, size=user_bubble.size)
            user_label = Label(text=f"You: {message}")
            user_bubble.add_widget(user_label)  # Add label to the bubble
            self.chat_history_layout.add_widget(user_bubble)

            # System reply bubble (left-aligned)
            system_bubble = Bubble(orientation='vertical', size_hint_y=None, height=40)
            with system_bubble.canvas.before:
                Color(1, 0, 0, 1)  # Red
                self.rect = Rectangle(pos=system_bubble.pos, size=system_bubble.size)
            system_label = Label(text="System: Received!")
            system_bubble.add_widget(system_label)  # Add label to the bubble
            self.chat_history_layout.add_widget(system_bubble)

            # Clear the input field
            self.message_input.text = ""

if __name__ == '__main__':
    ChatApp().run()