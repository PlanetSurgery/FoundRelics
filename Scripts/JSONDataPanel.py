# \Scripts\JSONDataPanel.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
import sys, ctypes

from ctypes import wintypes

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QScrollArea, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
# End of Imports --------

# Our Imports -----------
from UIUtilities import SCROLLBAR_STYLES, Create_TitleBar
from GameWindowMixin import GameWindowMixin
# End of Imports --------

class JSONDataPanel(GameWindowMixin, QFrame):
    def Init_Objects(self, parent):
        QWidget.__init__(self, parent)
        GameWindowMixin.__init__(self)
        
    def Init_Vars(self):
        self.game_window_width = self.width()
        self.game_window_height = self.height()
        
    def Setup_Panel(self):
        self.setObjectName("JSONPanel")
        self.setStyleSheet(f"QFrame#JSONPanel {{ background-color: #333333; border: 2px solid #002244; border-radius: 4px; }} QLabel {{ color: #dddddd; }}"+SCROLLBAR_STYLES)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_bar = Create_TitleBar("JSON Data")
        layout.addWidget(self.title_bar)
        self.lbl_title = self.title_bar.findChild(QLabel)
        
        self.btn_close = None
        for btn in self.title_bar.findChildren(QPushButton):
            if btn.text() == "X":
                self.btn_close = btn
                break
                
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
        self.json_label.setStyleSheet("color: #cccccc; background-color: #333333;")
        self.json_label.setWordWrap(True)
        
        self.json_scroll.setWidget(self.json_label)
        content_layout.addWidget(self.json_scroll)
    
    def Setup_Timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.Update_Scaling)
        self.update_timer.start(16)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.Check_Window)
        self.check_timer.start(16)
        
    def __init__(self, parent=None):
        self.Init_Objects(parent)
        self.Init_Vars()
        self.Setup_Panel()
        self.Setup_Timers()
        
    def Update_Scaling(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        exponent = 1 + 1.5 * max(0, 1 - scale)
        
        dynamic_font_size = max(3, int(12 * (scale ** exponent)))
        json_font = self.json_label.font()
        json_font.setPointSize(dynamic_font_size)
        self.json_label.setFont(json_font)
        
        if self.lbl_title:
            title_font_size = max(8, int(19 * (scale ** exponent)))
            self.lbl_title.setStyleSheet(f"color: white; font-size: {title_font_size}px; font-weight: bold;")
            new_height = title_font_size + 10
            self.title_bar.setFixedHeight(new_height)
            
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
            
    def Set_JSON(self, text):
        self.json_label.setText(text)