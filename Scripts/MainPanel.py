# \Scripts\MainPanel.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
import sys, ctypes

from ctypes import wintypes

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QPlainTextEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
# End of Imports --------

# Our Imports -----------
from UIUtilities import SCROLLBAR_STYLES, Create_TitleBar
from GameWindowMixin import GameWindowMixin
# End of Imports --------

class MainPanel(GameWindowMixin, QFrame):
    def Init_Objects(self, parent):
        QWidget.__init__(self, parent)
        GameWindowMixin.__init__(self)
        
    def Setup_Panel(self):
        self.setObjectName("DevPanel")
        self.setStyleSheet(f"QFrame#DevPanel {{ background-color: #000000; border: 2px solid black; border-radius: 4px; }} QPlainTextEdit {{ background-color: #333333; color: black; }} QLabel {{ color: #dddddd; }}"+SCROLLBAR_STYLES)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        title = Create_TitleBar("Main Panel")
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
        self.player_level_label = QLabel("Level Progress: ")
        self.run_count_label = QLabel("Run Count: 0")
        self.run_time_label = QLabel("Run Time: 0")
        self.gold_rate_label = QLabel("Earned Gold Per Minute: 0")
        self.market_gold_label = QLabel("Earned Market Gold: 0")
        self.market_enj_label = QLabel("Earned Market ENJ: 0")
        self.fav_map = QLabel("Favorite Map: N/A")
        self.content_layout.addWidget(self.player_name_label)
        self.content_layout.addWidget(self.player_level_label)
        self.content_layout.addWidget(self.run_count_label)
        self.content_layout.addWidget(self.run_time_label)
        self.content_layout.addWidget(self.gold_rate_label)
        self.content_layout.addWidget(self.market_gold_label)
        self.content_layout.addWidget(self.market_enj_label)
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
        
    def Setup_Timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.Update_Scaling)
        self.update_timer.start(16)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.Check_Window)
        self.check_timer.start(16)
        
    def __init__(self, parent=None):
        self.Init_Objects(parent)
        self.Setup_Panel()
        self.Setup_Timers()
        
    def Update_Scaling(self):
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
            
    def Set_Name(self, name):
        self.player_name_label.setText(f"Player: {name}")
        
    def Set_Level(self, level):
        self.player_level_label.setText(f"Level Progress: {level}")
        
    def Set_Count(self, count):
        self.run_count_label.setText(f"Run Count: {count}")
        
    def Set_Time(self, time_taken):
        self.run_time_label.setText(f"Run Time: {time_taken}")
        
    def Set_GRate(self, gold_found):
        self.gold_rate_label.setText(f"Earned Gold Per Minute: {gold_found}")
        
    def Set_GMarket(self, market_gold):
        self.market_gold_label.setText(f"Earned Market Gold: {market_gold}")
        
    def Set_EMarket(self, market_enj):
        self.market_enj_label.setText(f"Earned Market ENJ: {market_enj}")
        
    def Set_Map(self, map_name):
        self.fav_map.setText(f"Favorite Map: {map_name}")
        
    def Log_Message(self, msg):
        self.log_field.setPlainText(msg)