from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QPlainTextEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from .Buttons import SCROLLBAR_STYLES, create_title_bar

class DevUIPanel(QFrame):
    """
    The Dev UI panel that shows player info, run count, a log field,
    and two buttons for toggling JSON panel and item tracker panel.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DevPanel")
        self.setStyleSheet(f"""
            QFrame#DevPanel {{
                background-color: #000000;
                border: 2px solid black;
                border-radius: 4px;
            }}
            QPlainTextEdit {{
                background-color: #333333;
                color: black;
            }}
            QLabel {{
                color: #dddddd;
            }}
        """ + SCROLLBAR_STYLES)
        
        # Do not set fixed height here – Main.py will do that
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title = create_title_bar("FoundRelics")
        layout.addWidget(title)

        # Main content area
        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        layout.addWidget(content, 1)

        # Dev UI elements
        self.player_name_label = QLabel("Player Name: ")
        content_layout.addWidget(self.player_name_label)

        self.player_level_label = QLabel("Player Level Progress: ")
        content_layout.addWidget(self.player_level_label)

        self.run_count_label = QLabel("Run Count: 0")
        content_layout.addWidget(self.run_count_label)

        self.log_field = QPlainTextEdit()
        self.log_field.setPlainText("Application has started.")
        content_layout.addWidget(self.log_field)

        # Two buttons row
        btn_row = QHBoxLayout()
        self.json_button = QPushButton("Show JSON Data")
        self.json_button.setStyleSheet("""
            background-color: #444444;
            color: #cccccc;
            padding: 6px 10px;
            font-size: 14px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.json_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.json_button.setEnabled(False)  # enabled once data is fetched
        btn_row.addWidget(self.json_button, alignment=Qt.AlignLeft)

        self.item_selector_button = QPushButton("Show Tracked Items")
        self.item_selector_button.setStyleSheet("""
            background-color: #444444;
            color: #cccccc;
            padding: 6px 10px;
            font-size: 14px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.item_selector_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_row.addWidget(self.item_selector_button, alignment=Qt.AlignLeft)

        btn_row.addStretch()
        content_layout.addLayout(btn_row)

    # Convenient setters/getters
    def set_player_name(self, name):
        self.player_name_label.setText(f"Player Name: {name}")

    def set_player_level(self, level):
        self.player_level_label.setText(f"Player Level Progress: {level}")

    def set_run_count(self, count):
        self.run_count_label.setText(f"Run Count: {count}")

    def log_message(self, msg):
        self.log_field.setPlainText(msg)
