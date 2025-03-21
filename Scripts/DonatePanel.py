# Scripts/DonatePanel.py
# Created by PlanetSurgery

import sys, ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

import os

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

class DonatePanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName("DonatePanel")
        self.setStyleSheet(f"""
            QFrame#DonatePanel {{
                background-color: #000000;
                border: 2px solid black;
                border-radius: 4px;
            }}
            QLabel {{
                color: #dddddd;
            }}
        """ + SCROLLBAR_STYLES)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_bar = create_title_bar("Donation")
        layout.addWidget(self.title_bar)
        self.lbl_title = self.title_bar.findChild(QLabel)
        self.btn_close = None
        for btn in self.title_bar.findChildren(QPushButton):
            if btn.text() == "X":
                self.btn_close = btn
                break
        
        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(8)
        layout.addWidget(content, 1)
        
        self.instruction = QLabel(
            "Please scan the QR code with your ENJ wallet on Relaychain to donate any amount you want. "
            "I greatly appreciate any support at all, even if just vocal! Also, make sure you got this from the original source!"
        )
        self.instruction.setWordWrap(True)
        self.instruction.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.instruction)
        
        self.qr_label = QLabel()
        qr_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "W3", "qr"))
        qr_pixmap = QPixmap(qr_image_path)
        if not qr_pixmap.isNull():
            self.original_qr_pixmap = qr_pixmap
            scaled_pixmap = self.original_qr_pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
        else:
            self.qr_label.setText("QR code image not found.")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.qr_label) 
       
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_scaling)
        self.update_timer.start(16)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_game_window)
        self.check_timer.start(67)
        
        self.game_window_width = self.width()
        self.game_window_height = self.height()

    def check_game_window(self):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "LostRelics")
            if hwnd:
                self.game_hwnd = hwnd
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                self.game_window_x = rect.left
                self.game_window_y = rect.top
                self.game_window_width = rect.right - rect.left
                self.game_window_height = rect.bottom - rect.top
        except Exception as e:
            print("Error checking game window in DonatePanel:", e)
            
    def update_scaling(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        exponent = 1 + 1.5 * max(0, 1 - scale)
        
        dynamic_font_size = max(3, int(9 * (scale ** exponent)))
        instruction_font = self.instruction.font()
        instruction_font.setPointSize(dynamic_font_size)
        self.instruction.setFont(instruction_font)
        
        margin = int(8 * scale)
        spacing = int(8 * scale)
        self.content_layout.setContentsMargins(margin, margin, margin, margin)
        self.content_layout.setSpacing(spacing)
        
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
        
        if hasattr(self, 'original_qr_pixmap'):
            new_width = max(69, int(250 * (scale ** exponent)))
            new_width = min(new_width, self.original_qr_pixmap.width())
            available_width = self.width() - 2 * margin
            new_width = min(new_width, available_width)
            scaled_qr_pixmap = self.original_qr_pixmap.scaledToWidth(new_width, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_qr_pixmap)