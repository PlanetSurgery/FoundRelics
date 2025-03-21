# Scripts/Buttons.py
# Created by PlanetSurgery

import sys, ctypes
from ctypes import wintypes

from PyQt5.QtGui import QPainter, QPen, QColor, QPalette, QFont
from PyQt5.QtCore import QRect, Qt, QTimer
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

#Changed class to buttons, move later.
def create_title_bar(title_text, scale=1.0):
    exponent = 1 + 0.5 * max(0, 1 - scale)
    dynamic_font_size = max(3, int(20 * (scale ** exponent)))
    title_bar = QFrame()
    title_bar.setObjectName("TitleBar")
    title_bar.setStyleSheet(f"""
        QFrame#TitleBar {{
            background-color: #333333;
        }}
    """)
    layout = QHBoxLayout(title_bar)
    layout.setContentsMargins(int(8 * scale), int(4 * scale), int(8 * scale), int(4 * scale))
    layout.setSpacing(int(8 * scale))
    lbl_title = QLabel(title_text)
    lbl_title.setStyleSheet(f"color: white; font-size: {dynamic_font_size}px; font-weight: bold;")
    layout.addWidget(lbl_title, alignment=Qt.AlignVCenter | Qt.AlignLeft)
    layout.addStretch()
    btn_close = QPushButton("X")
    btn_close.setEnabled(False)
    btn_close.setStyleSheet(f"""
        QPushButton {{
            color: #0F0F0F;
            background: transparent;
            border: none;
            font-size: {int(18 * scale)}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            color: #aaaaaa;
        }}
        QPushButton:disabled {{
            color: #555555;
        }}
    """)
    layout.addWidget(btn_close, alignment=Qt.AlignVCenter | Qt.AlignRight)
    return title_bar

def draw_control_buttons(painter, widget_width, widget_height, show_blue_box, control_padding=15, red_box_size=100, scale=1.0):
    cp = int(control_padding * scale)
    red_size = int(red_box_size * scale)
    red_x = widget_width - red_size - cp
    red_y = widget_height - red_size - cp
    painter.fillRect(red_x, red_y, red_size, red_size, QColor(255, 0, 0))
    blue_rect = None
    if show_blue_box:
        blue_size = int(100 * scale)
        blue_x = red_x
        blue_y = red_y - blue_size - cp
        painter.fillRect(blue_x, blue_y, blue_size, blue_size, QColor(0, 0, 255))
        blue_rect = QRect(blue_x, blue_y, blue_size, blue_size)
    button_size = int((red_size - cp) / 2)
    green_x = red_x - button_size - cp
    green_y = red_y
    painter.fillRect(green_x, green_y, button_size, button_size, QColor(0, 255, 0))
    orange_rect = QRect(green_x, green_y + button_size + cp, button_size, button_size)
    painter.fillRect(orange_rect, QColor(255, 165, 0))
    cyan_rect = QRect(green_x - button_size - cp, green_y + button_size + cp, button_size, button_size)
    painter.fillRect(cyan_rect, QColor(0, 255, 255))
    return {
        "red_rect": QRect(red_x, red_y, red_size, red_size),
        "blue_rect": blue_rect,
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

        self.game_hwnd = None
        self.game_window_x = 0
        self.game_window_y = 0
        self.game_window_width = self.width() if self.width() > 0 else 1920
        self.game_window_height = self.height() if self.height() > 0 else 1080

        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("–")
        self.toggle_button = QPushButton("!")
        self.reset_button = QPushButton("RESET")
        self.ui_button = QPushButton("UI")
        self.donate_button = QPushButton("Donate")

        self.plus_button.clicked.connect(self.handle_plus)
        self.minus_button.clicked.connect(self.handle_minus)
        self.toggle_button.clicked.connect(self.handle_toggle)
        self.reset_button.clicked.connect(self.handle_reset)
        self.ui_button.clicked.connect(self.handle_ui)
        self.donate_button.clicked.connect(self.handle_donate)

        self.top_layout = QHBoxLayout()
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.plus_button)
        self.top_layout.addWidget(self.minus_button)
        self.top_layout.addWidget(self.toggle_button)
        self.top_layout.addStretch()

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.reset_button)
        self.bottom_layout.addWidget(self.ui_button)
        self.bottom_layout.addWidget(self.donate_button)
        self.bottom_layout.addStretch()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.bottom_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 10)
        self.setLayout(self.main_layout)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_scaling_from_game_window)
        self.update_timer.start(16)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_game_window)
        self.check_timer.start(67)

    if sys.platform.startswith("win"):
        def check_game_window(self):
            try:
                hwnd = ctypes.windll.user32.FindWindowW(None, "LostRelics")
                if hwnd:
                    self.game_hwnd = hwnd
                    rect = wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    self.game_window_x = rect.left
                    self.game_window_y = rect.top
                    self.game_window_width = rect.right - rect.left
                    self.game_window_height = rect.bottom - rect.top
            except Exception as e:
                print("Error checking game window in MainPanelButtons:", e)

        def is_game_maximized(self):
            if self.game_hwnd:
                wp = WINDOWPLACEMENT()
                wp.length = ctypes.sizeof(WINDOWPLACEMENT)
                ctypes.windll.user32.GetWindowPlacement(self.game_hwnd, ctypes.byref(wp))
                SW_MAXIMIZE = 3
                return wp.showCmd == SW_MAXIMIZE
            return False

        def get_client_offset(self):
            if self.game_hwnd:
                pt = wintypes.POINT(0, 0)
                ctypes.windll.user32.ClientToScreen(self.game_hwnd, ctypes.byref(pt))
                return pt.y - self.game_window_y
            return 0
    else:
        def check_game_window(self):
            pass
        def is_game_maximized(self):
            return False
        def get_client_offset(self):
            return 0

    def update_scaling_from_game_window(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        self.update_scaling(scale)

    def update_scaling(self, scale):
        exponent = 1 + 0.5 * max(0, 1 - scale)
        top_button_size = int(38 * (scale ** exponent))
        bottom_button_width = int(70 * (scale ** exponent))
        bottom_button_height = int(30 * (scale ** exponent))
        top_font_size = max(3, int(18 * (scale ** exponent)))
        bottom_font_size = max(3, int(14 * (scale ** exponent)))
        for btn in (self.plus_button, self.minus_button, self.toggle_button):
            btn.setFixedSize(top_button_size, top_button_size)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    font-size: {top_font_size}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #555555;
                }}
            """)
        for btn in (self.reset_button, self.ui_button, self.donate_button):
            btn.setFixedSize(bottom_button_width, bottom_button_height)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    font-size: {bottom_font_size}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #555555;
                }}
            """)
        self.main_layout.setContentsMargins(0, 0, 0, int(10 * scale))
        self.top_layout.setSpacing(int(8 * scale))
        self.bottom_layout.setSpacing(int(8 * scale))

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