# Scripts/Buttons.py
# Created by PlanetSurgery

from PyQt5.QtGui import QPainter, QPen, QColor, QPalette
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
import requests

SCROLLBAR_STYLES = """
QScrollBar:vertical {
    background: #000000;
    width: 12px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #666666;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
    border: none;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}
"""

def create_title_bar(title_text):
    title_bar = QFrame()
    title_bar.setObjectName("TitleBar")
    title_bar.setStyleSheet("""
        QFrame#TitleBar {
            background-color: #333333;
        }
    """)
    layout = QHBoxLayout(title_bar)
    layout.setContentsMargins(8, 4, 8, 4)
    layout.setSpacing(8)
    lbl_title = QLabel(title_text)
    lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
    layout.addWidget(lbl_title, alignment=Qt.AlignVCenter | Qt.AlignLeft)
    layout.addStretch()
    btn_close = QPushButton("X")
    btn_close.setEnabled(False)
    btn_close.setStyleSheet("""
        QPushButton {
            color: #0F0F0F;
            background: transparent;
            border: none;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            color: #aaaaaa;
        }
        QPushButton:disabled {
            color: #555555;
        }
    """)
    return title_bar

def draw_control_buttons(painter, widget_width, widget_height, show_blue_box, control_padding=15, red_box_size=100):
    red_x = widget_width - red_box_size - control_padding
    red_y = widget_height - red_box_size - control_padding
    painter.fillRect(red_x, red_y, red_box_size, red_box_size, QColor(255, 0, 0))
    if show_blue_box:
        blue_box_size = 100
        blue_x = red_x
        blue_y = red_y - blue_box_size - control_padding
        painter.fillRect(blue_x, blue_y, blue_box_size, blue_box_size, QColor(0, 0, 255))
    button_size = int((red_box_size - control_padding) / 2)
    green_x = red_x - button_size - control_padding
    green_y = red_y
    painter.fillRect(green_x, green_y, button_size, button_size, QColor(0, 255, 0))
    orange_rect = QRect(green_x, green_y + button_size + control_padding, button_size, button_size)
    painter.fillRect(orange_rect, QColor(255, 165, 0))
    cyan_rect = QRect(green_x - button_size - control_padding, green_y + button_size + control_padding, button_size, button_size)
    painter.fillRect(cyan_rect, QColor(0, 255, 255))
    return {
        "red_rect": QRect(red_x, red_y, red_box_size, red_box_size),
        "blue_rect": QRect(red_x, red_y - 100 - control_padding, 100, 100) if show_blue_box else None,
        "green_rect": QRect(green_x, green_y, button_size, button_size),
        "orange_rect": orange_rect,
        "cyan_rect": cyan_rect
    }

def handle_control_buttons_click(event, rects, show_blue_box, show_individual_buttons, on_exit, on_reset, on_increment, on_decrement):
    pos = event.pos()
    if rects["red_rect"].contains(pos):
        return not show_blue_box, not show_individual_buttons
    if rects["green_rect"].contains(pos):
        on_reset()
        return show_blue_box, show_individual_buttons
    if rects["orange_rect"].contains(pos):
        on_decrement()
        return show_blue_box, show_individual_buttons
    if rects["cyan_rect"].contains(pos):
        on_increment()
        return show_blue_box, show_individual_buttons
    return show_blue_box, show_individual_buttons

class MainPanelButtons(QWidget):
    def __init__(self, parent=None, on_increment=None, on_decrement=None, on_toggle=None, on_reset=None, on_donate=None):
        super().__init__(parent)
        self.on_increment = on_increment
        self.on_decrement = on_decrement
        self.on_toggle = on_toggle
        self.on_reset = on_reset
        self.on_donate = on_donate
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#1A1A1A"))
        self.setPalette(palette)
        top_button_size = 38
        bottom_button_width = 70
        bottom_button_height = 30
        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("–")
        self.toggle_button = QPushButton("!")
        for btn in (self.plus_button, self.minus_button, self.toggle_button):
            btn.setFixedSize(top_button_size, top_button_size)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    font-size: 18px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #555555;
                }}
            """)
        self.reset_button = QPushButton("RESET")
        self.reset_button.setFixedSize(bottom_button_width, bottom_button_height)
        self.reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)
        self.ui_button = QPushButton("UI")
        self.ui_button.setFixedSize(bottom_button_width, bottom_button_height)
        self.ui_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)
        self.donate_button = QPushButton("Donate")
        self.donate_button.setFixedSize(bottom_button_width, bottom_button_height)
        self.donate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)
        self.plus_button.clicked.connect(self.handle_plus)
        self.minus_button.clicked.connect(self.handle_minus)
        self.toggle_button.clicked.connect(self.handle_toggle)
        self.reset_button.clicked.connect(self.handle_reset)
        self.ui_button.clicked.connect(self.handle_ui)
        self.donate_button.clicked.connect(self.handle_donate)
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.plus_button)
        top_layout.addWidget(self.minus_button)
        top_layout.addWidget(self.toggle_button)
        top_layout.addStretch()
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.reset_button)
        bottom_layout.addWidget(self.ui_button)
        bottom_layout.addWidget(self.donate_button)
        bottom_layout.addStretch()
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.setContentsMargins(0, 0, 0, 10)
        self.setLayout(main_layout)

    def handle_plus(self):
        if self.on_increment:
            self.on_increment()

    def handle_minus(self):
        if self.on_decrement:
            self.on_decrement()

    def handle_toggle(self):
        if self.on_toggle:
            self.on_toggle()

    def handle_reset(self):
        if self.on_reset:
            self.on_reset()

    def handle_ui(self):
        try:
            requests.get("http://localhost:11990/ToggleUI")
        except Exception as e:
            print("Error toggling UI:", e)

    def handle_donate(self):
        if self.on_donate:
            self.on_donate()