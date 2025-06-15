print("DEBUG: main.py script execution started.")
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QWidget,
    QVBoxLayout, QListWidget, QPushButton, QListWidgetItem,
    QHBoxLayout, QLabel, QTextEdit, QLineEdit, QCheckBox,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt

# Attempt to import controller and constants
try:
    from controller.logic_pp import LogicPlusPlus
    from constants import SNAPSHOTS_DIR
except ImportError as e:
    print(f"Error importing controller or constants: {e}. Ensure they are in PYTHONPATH.")
    if 'SNAPSHOTS_DIR' not in globals():
        SNAPSHOTS_DIR = "chat_snapshots_fallback"
        print(f"Using fallback SNAPSHOTS_DIR: {SNAPSHOTS_DIR}")

DARK_THEME_STYLESHEET = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    border: none; /* Default no border, specific widgets can override */
}

QLabel {
    color: #f0f0f0;
    background-color: transparent; /* Ensure labels don't obscure parent background */
}

QPushButton {
    background-color: #4a4a4a;
    color: #f0f0f0;
    border: 1px solid #569cd6;
    padding: 5px 10px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #5a5a5a;
    border: 1px solid #78b3e0;
}
QPushButton:pressed {
    background-color: #3a3a3a;
}
QPushButton:disabled {
    background-color: #333333;
    color: #808080;
    border-color: #555555;
}

QLineEdit {
    background-color: #3c3c3c;
    color: #f0f0f0;
    border: 1px solid #555555;
    padding: 4px;
    border-radius: 3px;
}
QLineEdit:focus {
    border: 1px solid #569cd6;
}

QTextEdit {
    background-color: #3c3c3c;
    color: #f0f0f0;
    border: 1px solid #555555;
    padding: 4px;
    border-radius: 3px;
}
QTextEdit:focus {
    border: 1px solid #569cd6;
}

QListWidget {
    background-color: #3c3c3c;
    color: #f0f0f0;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 2px;
}
QListWidget::item {
    padding: 5px;
}
QListWidget::item:selected {
    background-color: #569cd6;
    color: #ffffff;
}
QListWidget::item:hover:!selected { /* Hover on non-selected items */
    background-color: #4a4a4a;
}


QSplitter::handle {
    background-color: #4a4a4a; /* Color of the splitter handle itself */
    border: 1px solid #3c3c3c; /* Optional: border around the handle */
}
QSplitter::handle:horizontal {
    width: 5px; /* Width of the vertical handle */
    margin: 0px 2px; /* Spacing around the handle */
}
QSplitter::handle:vertical {
    height: 5px; /* Height of the horizontal handle */
    margin: 2px 0px; /* Spacing around the handle */
}
QSplitter::handle:hover {
    background-color: #569cd6;
}

QCheckBox {
    spacing: 5px; /* Space between checkbox and text */
    background-color: transparent;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #3c3c3c;
}
QCheckBox::indicator:checked {
    background-color: #569cd6;
    border: 1px solid #569cd6;
    /* image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-apply-16.png); */ /* Example for check mark */
}
QCheckBox::indicator:unchecked:hover {
    border: 1px solid #78b3e0;
}
QCheckBox::indicator:checked:hover {
    background-color: #78b3e0;
    border: 1px solid #78b3e0;
}

/* Style for header-like areas if they are QWidgets.
   If using QFrame for headers, you might need QFrame specific styles. */
/* Example: Style a QWidget if it has an object name "headerBar" */
QWidget#headerBar {
    background-color: #3c3c3c; /* Slightly different from main background */
    border-bottom: 1px solid #555555;
}
"""

class ChatListPanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.clicked.connect(self.main_window.handle_new_chat_button_clicked)
        self.snapshot_list_widget = QListWidget()
        self.snapshot_list_widget.currentItemChanged.connect(self.on_snapshot_selected)
        layout.addWidget(self.new_chat_button)
        layout.addWidget(self.snapshot_list_widget)
        self.setLayout(layout)
        print("ChatListPanel initialized")

    def on_snapshot_selected(self, current_item, previous_item):
        if current_item:
            print(f"ChatListPanel: Snapshot selected: {current_item.text()}")
            self.main_window.handle_snapshot_selection(current_item)
        else:
            print("ChatListPanel: Snapshot selection cleared.")

class ChatAreaPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        top_bar_widget = QWidget()
        # top_bar_widget.setObjectName("headerBar") # Example if specific styling needed via object name
        top_bar_layout = QHBoxLayout(top_bar_widget)
        self.active_chat_label = QLabel("Active Chat: None")
        save_chat_button = QPushButton("Save Chat")
        new_chat_options_button = QPushButton("New Chat Options")
        top_bar_layout.addWidget(self.active_chat_label)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(save_chat_button)
        top_bar_layout.addWidget(new_chat_options_button)
        top_bar_widget.setLayout(top_bar_layout)
        # Removed: top_bar_widget.setStyleSheet("background-color: #e0e0e0;")

        self.chat_window = QTextEdit()
        self.chat_window.setReadOnly(True)
        self.chat_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        input_area_widget = QWidget()
        input_area_layout = QHBoxLayout(input_area_widget)
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        send_button = QPushButton("Send")
        input_area_layout.addWidget(self.message_input)
        input_area_layout.addWidget(send_button)
        input_area_widget.setLayout(input_area_layout)

        main_layout.addWidget(top_bar_widget)
        main_layout.addWidget(self.chat_window)
        main_layout.addWidget(input_area_widget)
        main_layout.setStretchFactor(self.chat_window, 1)
        self.setLayout(main_layout)
        print("ChatAreaPanel initialized")

class AnimationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        header_widget = QWidget()
        # header_widget.setObjectName("headerBar") # Example
        header_layout = QHBoxLayout(header_widget)
        header_label = QLabel("Animation Data")
        stop_button = QPushButton("Stop")
        render_button = QPushButton("Render")
        self.store_animation_checkbox = QCheckBox("Store Animation")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.store_animation_checkbox)
        header_layout.addWidget(stop_button)
        header_layout.addWidget(render_button)
        header_widget.setLayout(header_layout)
        # Removed: header_widget.setStyleSheet("background-color: #e0e0e0;")

        self.animation_display = QTextEdit()
        self.animation_display.setReadOnly(True)
        self.animation_display.setPlaceholderText("Animation data will appear here...")
        self.animation_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(header_widget)
        main_layout.addWidget(self.animation_display)
        main_layout.setStretchFactor(self.animation_display, 1)
        self.setLayout(main_layout)
        print("AnimationPanel initialized")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Chat App - Dark Theme")
        self.setGeometry(100, 100, 1200, 800)
        print("PySide6 app started - initializing MainWindow with controller logic")

        self.controller = None
        self.active_chat_snapshot = None

        self.chat_list_panel = ChatListPanel(main_window=self)
        self.chat_area_panel = ChatAreaPanel()
        self.animation_panel = AnimationPanel()

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.chat_list_panel)
        self.main_splitter.addWidget(self.chat_area_panel)
        self.main_splitter.addWidget(self.animation_panel)
        self.main_splitter.setSizes([200, 500, 300])
        self.setCentralWidget(self.main_splitter)

        print("Panels created, initializing controller and loading snapshots...")
        self.initialize_controller_and_load_snapshots()
        print("PySide6 app layout configured with controller logic")

    def initialize_controller_and_load_snapshots(self):
        print("Attempting to populate snapshots...")
        if not hasattr(self, 'chat_list_panel'):
            print("Error: chat_list_panel not initialized before loading snapshots.")
            return
        self.chat_list_panel.snapshot_list_widget.clear()
        if not os.path.exists(SNAPSHOTS_DIR):
            print(f"Snapshots directory '{SNAPSHOTS_DIR}' does not exist. Creating it.")
            try:
                os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
            except OSError as e:
                print(f"Error creating snapshot directory: {e}")
                self.load_untitled_chat()
                return
        try:
            snapshot_names = sorted([
                name for name in os.listdir(SNAPSHOTS_DIR)
                if os.path.isdir(os.path.join(SNAPSHOTS_DIR, name))
            ])
            print(f"Found snapshots: {snapshot_names}")
        except FileNotFoundError:
            print(f"Snapshots directory '{SNAPSHOTS_DIR}' not found.")
            snapshot_names = []
        except Exception as e:
            print(f"Error listing snapshots: {e}")
            snapshot_names = []

        if snapshot_names:
            for name in snapshot_names:
                self.chat_list_panel.snapshot_list_widget.addItem(QListWidgetItem(name))
            print(f"Attempting to auto-load most recent snapshot: {snapshot_names[-1]}")
            self.chat_list_panel.snapshot_list_widget.blockSignals(True)
            self.chat_list_panel.snapshot_list_widget.setCurrentRow(len(snapshot_names) - 1)
            self.chat_list_panel.snapshot_list_widget.blockSignals(False)
            if self.active_chat_snapshot != snapshot_names[-1]:
                 self.load_chat_snapshot(snapshot_names[-1])
        else:
            print("No snapshots found or directory error. Loading untitled chat.")
            self.load_untitled_chat()
        print("Snapshot population/loading attempt finished.")

    def load_chat_snapshot(self, snapshot_name):
        if not snapshot_name:
            print("Error: load_chat_snapshot called with no name.")
            return
        if self.active_chat_snapshot == snapshot_name and self.controller:
            print(f"Chat {snapshot_name} is already active.")
            return
        print(f"Attempting to load chat: {snapshot_name}")
        try:
            full_snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_name)
            self.controller = LogicPlusPlus(snapshot_dir=full_snapshot_path)
            self.active_chat_snapshot = snapshot_name
            self.chat_area_panel.active_chat_label.setText(f"Active Chat: {snapshot_name}")
            print(f"Successfully loaded chat: {snapshot_name}")
        except Exception as e:
            print(f"Error loading chat snapshot '{snapshot_name}': {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load chat '{snapshot_name}':\n{e}")
            self.load_untitled_chat()

    def load_untitled_chat(self):
        print("Attempting to load untitled chat")
        try:
            self.controller = LogicPlusPlus(snapshot_dir=None)
            self.active_chat_snapshot = "untitled"
            self.chat_area_panel.active_chat_label.setText("Active Chat: untitled")
            current_selection = self.chat_list_panel.snapshot_list_widget.currentItem()
            if current_selection is None or current_selection.text() != "untitled":
                 self.chat_list_panel.snapshot_list_widget.setCurrentItem(None)
            print("Successfully loaded untitled chat.")
        except Exception as e:
            print(f"Error loading untitled chat: {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load untitled chat:\n{e}")

    def handle_new_chat_button_clicked(self):
        print("MainWindow: New Chat button clicked.")
        self.load_untitled_chat()

    def handle_snapshot_selection(self, selected_item):
        if selected_item:
            snapshot_name = selected_item.text()
            print(f"MainWindow: Snapshot selection changed to: {snapshot_name}")
            self.load_chat_snapshot(snapshot_name)
        else:
            print("MainWindow: Snapshot selection cleared, loading untitled chat.")
            if self.active_chat_snapshot != "untitled":
                self.load_untitled_chat()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("QApplication instantiated")

    # Apply the dark theme stylesheet
    app.setStyleSheet(DARK_THEME_STYLESHEET)
    print("Dark theme stylesheet applied.")

    if 'SNAPSHOTS_DIR' in globals() and not os.path.exists(SNAPSHOTS_DIR):
        try:
            print(f"Creating SNAPSHOTS_DIR for standalone run: {SNAPSHOTS_DIR}")
            os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
        except Exception as e:
            print(f"Could not create SNAPSHOTS_DIR: {e}")

    window = MainWindow()
    window.show()
    print("PySide6 MainWindow.show() called")
    sys.exit(app.exec())
