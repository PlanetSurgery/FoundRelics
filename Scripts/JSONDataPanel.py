# Scripts/JSONDataPanel.py
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QScrollArea, QLabel
from PyQt5.QtCore import Qt
from .Buttons import SCROLLBAR_STYLES, create_title_bar

class JSONDataPanel(QFrame):
    """
    Panel that displays JSON data in a scrollable label.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("JSONPanel")
        self.setStyleSheet(f"""
            QFrame#JSONPanel {{
                background-color: #333333; 
                border: 2px solid #002244;
                border-radius: 4px;
            }}
            QLabel {{
                color: #dddddd;
            }}
        """ + SCROLLBAR_STYLES)
        
        # Do not set a fixed height here – Main.py will assign the proper size
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title = create_title_bar("JSON Data")
        layout.addWidget(title)

        # Main content area
        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        layout.addWidget(content, 1)

        self.json_scroll = QScrollArea()
        self.json_scroll.setStyleSheet("background-color: #2A2A2A;")
        self.json_scroll.setWidgetResizable(True)
        self.json_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.json_label = QLabel()
        self.json_label.setStyleSheet("color: #cccccc; font-size: 14px; background-color: #333333;")
        self.json_label.setWordWrap(True)
        self.json_scroll.setWidget(self.json_label)

        content_layout.addWidget(self.json_scroll)

    def set_json_text(self, text):
        self.json_label.setText(text)
