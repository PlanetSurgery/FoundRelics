# \Scripts\Buttons.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
import sys, ctypes

from ctypes import wintypes

from PyQt5.QtGui import QPainter, QPen, QColor, QPalette, QFont
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

import requests
# End of Imports --------

# Our Imports -----------
from GameWindowMixin import GameWindowMixin
# End of Imports --------

class MainPanelButtons(GameWindowMixin, QWidget):
    def Init_Overrides(self, parent=None, On_Increment=None, On_Decrement=None, On_Toggle=None, On_Reset=None, On_Donate=None):
        self.On_Increment = On_Increment
        self.On_Decrement = On_Decrement
        self.On_Toggle = On_Toggle
        self.On_Reset = On_Reset
        self.On_Donate = On_Donate
        
    def Init_Vars(self):
        self.game_window_width = self.width() if self.width() > 0 else 1920
        self.game_window_height = self.height() if self.height() > 0 else 1080
        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("–")
        self.toggle_button = QPushButton("!")
        self.reset_button = QPushButton("RESET")
        self.ui_button = QPushButton("UI")
        self.donate_button = QPushButton("Donate")
    
    def Init_Objects(self, parent):
        QWidget.__init__(self, parent)
        GameWindowMixin.__init__(self)
        
    def Connect_Buttons(self):
        self.plus_button.clicked.connect(self.ButtonHandler_Plus)
        self.minus_button.clicked.connect(self.ButtonHandler_Minus)
        self.toggle_button.clicked.connect(self.ButtonHandler_Toggle)
        self.reset_button.clicked.connect(self.ButtonHandler_Reset)
        self.ui_button.clicked.connect(self.ButtonHandler_UI)
        self.donate_button.clicked.connect(self.ButtonHandler_Donate)
        
    def Setup_Layout(self):
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
        
    def Setup_Timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.Update)
        self.update_timer.start(16)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.Check_Window)
        self.check_timer.start(16)
        
    def Set_Palette(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#1A1A1A"))
        self.setPalette(palette)
    
    def __init__(self, parent=None, On_Increment=None, On_Decrement=None, On_Toggle=None, On_Reset=None, On_Donate=None):
        self.Init_Objects(parent)
        self.Init_Overrides(parent, On_Increment, On_Decrement, On_Toggle, On_Reset, On_Donate)
        self.Init_Vars()
        self.Set_Palette()
        self.Connect_Buttons()
        self.Setup_Layout()
        self.Setup_Timers()
        
    def Update(self):
        self.Update_Scaling()
       
    def Update_Scaling(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
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
        
    def ButtonHandler_Plus(self):
        if self.On_Increment:
            self.On_Increment()
            
    def ButtonHandler_Minus(self):
        if self.On_Decrement:
            self.On_Decrement()
            
    def ButtonHandler_Toggle(self):
        if self.On_Toggle:
            self.On_Toggle()
            
    def ButtonHandler_Reset(self):
        if self.On_Reset:
            self.On_Reset()
            
    def ButtonHandler_UI(self):
        try:
            requests.get("http://localhost:11990/ToggleUI")
        except Exception as e:
            print("Error toggling UI:", e)
            
    def ButtonHandler_Donate(self):
        if self.On_Donate:
            self.On_Donate()