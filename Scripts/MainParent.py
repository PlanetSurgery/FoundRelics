# Scripts/MainParent.py
# Created by PlanetSurgery

import sys, os, json, requests, ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QPoint

from Buttons import MainPanelButtons 
from ItemsDisplay import ItemsDisplay
from ItemTrackerPanel import ItemTrackerPanel
from JSONDataPanel import JSONDataPanel

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

class MainParent(QWidget):
    def __init__(self, panels_widget, parent=None):
        super().__init__(parent)
        self.is_collapsed = False

        self.game_hwnd = None
        self.game_window_x = 0
        self.game_window_y = 0
        self.game_window_width = self.width() if self.width() > 0 else 1920
        self.game_window_height = self.height() if self.height() > 0 else 1080

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setStyleSheet("background-color: #222222;")
        self.title_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        title_layout.setContentsMargins(8, 4, 8, 4)
        title_layout.setSpacing(8)

        self.lbl_title = QLabel("FoundRelics")
        self.lbl_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title_layout.addWidget(self.lbl_title, alignment=Qt.AlignLeft)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)

        self.toggle_button = QPushButton("_")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #aaaaaa;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_panels)
        btn_layout.addWidget(self.toggle_button, alignment=Qt.AlignLeft)

        self.close_button = QPushButton("X")
        self.close_button.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ff5555;
            }
        """)
        self.close_button.clicked.connect(self.confirm_close)
        btn_layout.addWidget(self.close_button, alignment=Qt.AlignLeft)

        title_layout.addWidget(btn_container, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.title_bar, alignment=Qt.AlignLeft)

        self.stack = QStackedWidget()
        self.stack.addWidget(panels_widget)
        dummy_placeholder = QWidget()
        dummy_placeholder.setFixedSize(panels_widget.size())
        self.stack.addWidget(dummy_placeholder)
        self.main_layout.addWidget(self.stack)

        self.panels_widget = panels_widget

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_scaling)
        self.update_timer.start(16) 

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_game_window)
        self.check_timer.start(67)
        
    def confirm_close(self):
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit FoundRelics?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()

    def toggle_panels(self):
        if self.is_collapsed:
            self.stack.setCurrentIndex(0)
            self.toggle_button.setText("_")
        else:
            self.stack.setCurrentIndex(1)
            self.toggle_button.setText("☐")
        self.is_collapsed = not self.is_collapsed

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
                print("Error checking game window in MainParent:", e)
    else:
        def check_game_window(self):
            pass

    def update_scaling(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        
        dynamic_title_font = max(8, int(18 * scale))
        dynamic_button_font = max(8, int(16 * scale))

        self.lbl_title.setStyleSheet(f"color: white; font-size: {dynamic_title_font}px; font-weight: bold;")
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background: transparent;
                border: none;
                font-size: {dynamic_button_font}px;
            }}
            QPushButton:hover {{
                color: #aaaaaa;
            }}
        """)
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background: transparent;
                border: none;
                font-size: {dynamic_button_font}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #ff5555;
            }}
        """)

        global_y = self.mapToGlobal(QPoint(0, 0)).y()
        offset = int(self.get_client_offset() * 1.222)
        start_y = (self.game_window_y + offset) - global_y
        self.main_layout.setContentsMargins(0, start_y, 0, 0)

    def is_game_maximized(self):
        if self.game_hwnd:
            wp = WINDOWPLACEMENT()
            wp.length = ctypes.sizeof(WINDOWPLACEMENT)
            ctypes.windll.user32.GetWindowPlacement(self.game_hwnd, ctypes.byref(wp))
            return wp.showCmd == SW_MAXIMIZE
        return False

    def get_client_offset(self):
        if self.game_hwnd:
            pt = wintypes.POINT(0, 0)
            ctypes.windll.user32.ClientToScreen(self.game_hwnd, ctypes.byref(pt))
            return pt.y - self.game_window_y
        return 0