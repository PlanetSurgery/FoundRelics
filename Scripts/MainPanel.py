# Scripts/MainPanel.py
# Created by PlanetSurgery

import sys, ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QPlainTextEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer

from Buttons import SCROLLBAR_STYLES, create_title_bar

class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("rcNormalPosition", wintypes.RECT),
    ]
SW_MAXIMIZE = 3

class MainPanel(QFrame):
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
        
        self.game_hwnd = None
        self.game_window_x = 0
        self.game_window_y = 0
        self.game_window_width = self.width() if self.width() > 0 else 1920
        self.game_window_height = self.height() if self.height() > 0 else 1080

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = create_title_bar("Main Panel")
        layout.addWidget(title)
        self.lbl_title = title.findChild(QLabel)
        self.btn_close = None
        for btn in title.findChildren(QPushButton):
            if btn.text() == "X":
                self.btn_close = btn
                break

        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(8)
        layout.addWidget(content, 1)

        self.player_name_label = QLabel("Player: ")
        self.content_layout.addWidget(self.player_name_label)

        self.player_level_label = QLabel("Level Progress: ")
        self.content_layout.addWidget(self.player_level_label)

        self.run_count_label = QLabel("Run Count: 0")
        self.content_layout.addWidget(self.run_count_label)

        self.run_time_label = QLabel("Run Time: 0")
        self.content_layout.addWidget(self.run_time_label)

        self.gold_rate_label = QLabel("Earned Gold Per Minute: 0")
        self.content_layout.addWidget(self.gold_rate_label)

        self.market_gold_label = QLabel("Earned Market Gold: 0")
        self.content_layout.addWidget(self.market_gold_label)

        self.market_enj_label = QLabel("Earned Market ENJ: 0")
        self.content_layout.addWidget(self.market_enj_label)

        self.fav_map = QLabel("Favorite Map: N/A")
        self.content_layout.addWidget(self.fav_map)

        self.log_field = QPlainTextEdit()
        self.log_field.setPlainText("Application has started.")
        self.content_layout.addWidget(self.log_field)

        btn_row = QHBoxLayout()
        self.json_button = QPushButton("Show Data")
        self.json_button.setStyleSheet("""
            background-color: #444444;
            color: #cccccc;
            padding: 6px 10px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.json_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.json_button.setEnabled(False)
        btn_row.addWidget(self.json_button, alignment=Qt.AlignLeft)

        self.item_selector_button = QPushButton("Show Items")
        self.item_selector_button.setStyleSheet("""
            background-color: #444444;
            color: #cccccc;
            padding: 6px 10px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.item_selector_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_row.addWidget(self.item_selector_button, alignment=Qt.AlignLeft)

        btn_row.addStretch()
        self.content_layout.addLayout(btn_row)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_scaling)
        self.update_timer.start(16)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_game_window)
        self.check_timer.start(67)

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
            print("Error checking game window in MainPanel:", e)

    def update_scaling(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        
        exponent = 1 + 1.5 * max(0, 1 - scale)
        
        dynamic_font_size = max(3, int(9 * (scale ** exponent)))
        widgets_to_scale = [
            self.player_name_label,
            self.player_level_label,
            self.run_count_label,
            self.run_time_label,
            self.gold_rate_label,
            self.market_gold_label,
            self.market_enj_label,
            self.fav_map,
            self.log_field,
            self.json_button,
            self.item_selector_button,
        ]
        for widget in widgets_to_scale:
            font = widget.font()
            font.setPointSize(dynamic_font_size)
            widget.setFont(font)

        if hasattr(self, 'content_layout'):
            margin = int(8 * scale)
            spacing = int(8 * scale)
            self.content_layout.setContentsMargins(margin, margin, margin, margin)
            self.content_layout.setSpacing(spacing)
        
        title_font_size = max(8, int(19 * (scale ** exponent)))
        if self.lbl_title:
            self.lbl_title.setStyleSheet(f"color: white; font-size: {title_font_size}px; font-weight: bold;")
        
        if self.btn_close:
            close_font_size = max(8, int(16 * (scale ** exponent)))
            self.btn_close.setStyleSheet(f"""
                QPushButton {{
                    color: #0F0F0F;
                    background: transparent;
                    border: none;
                    font-size: {close_font_size}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: #aaaaaa;
                }}
                QPushButton:disabled {{
                    color: #555555;
                }}
            """)

    def set_player_name(self, name):
        self.player_name_label.setText(f"Player: {name}")

    def set_player_level(self, level):
        self.player_level_label.setText(f"Level Progress: {level}")

    def set_run_count(self, count):
        self.run_count_label.setText(f"Run Count: {count}")

    def set_run_time(self, time_taken):
        self.run_time_label.setText(f"Run Time: {time_taken}")

    def set_gold_rate(self, gold_found):
        self.gold_rate_label.setText(f"Earned Gold Per Minute: {gold_found}")

    def set_market_gold(self, market_gold):
        self.market_gold_label.setText(f"Earned Market Gold: {market_gold}")

    def set_market_enj(self, market_enj):
        self.market_enj_label.setText(f"Earned Market ENJ: {market_enj}")

    def set_fav_map(self, map_name):
        self.fav_map.setText(f"Favorite Map: {map_name}")

    def log_message(self, msg):
        self.log_field.setPlainText(msg)