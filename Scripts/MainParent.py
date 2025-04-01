# \Scripts\MainParent.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QPoint

import ctypes, sys, os, json, requests

from ctypes import wintypes
# End of Imports --------

# Our Imports -----------
from Buttons import MainPanelButtons
from ItemsDisplay import ItemsDisplay
from ItemTrackerPanel import ItemTrackerPanel
from JSONDataPanel import JSONDataPanel
from GameWindowMixin import GameWindowMixin
# End of Imports --------

class MainParent(GameWindowMixin, QWidget):
    def Init_Objects(self, parent):
        QWidget.__init__(self, parent)
        GameWindowMixin.__init__(self)
        
    def Init_Vars(self):
        self.is_collapsed = False
        self.game_window_width = self.width() if self.width() > 0 else 1920
        self.game_window_height = self.height() if self.height() > 0 else 1080
        
    def Setup_Parent(self):
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
        
        self.toggle_button.clicked.connect(self.Toggle_Panels)
        self.close_button.clicked.connect(self.Confirm_Close)
        
        btn_layout.addWidget(self.toggle_button, alignment=Qt.AlignLeft)
        btn_layout.addWidget(self.close_button, alignment=Qt.AlignLeft)
        title_layout.addWidget(btn_container, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.title_bar, alignment=Qt.AlignLeft)
        
    def Setup_Stack(self, panels_widget):
        self.stack = QStackedWidget()
        self.stack.addWidget(panels_widget)
        dummy_placeholder = QWidget()
        dummy_placeholder.setFixedSize(panels_widget.size())
        self.stack.addWidget(dummy_placeholder)
        self.main_layout.addWidget(self.stack)
        self.panels_widget = panels_widget
        
    def Setup_Timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.Update_Scaling)
        self.update_timer.start(16)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.Check_Window)
        self.check_timer.start(16)
        
    def __init__(self, panels_widget, parent=None):
        self.Init_Objects(parent)
        self.Init_Vars()
        self.Setup_Parent()
        self.Setup_Stack(panels_widget)
        self.Setup_Timers()
        
    def Confirm_Close(self):
        reply = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit FoundRelics?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()
            
    def Toggle_Panels(self):
        if self.is_collapsed:
            self.stack.setCurrentIndex(0)
            self.toggle_button.setText("_")
        else:
            self.stack.setCurrentIndex(1)
            self.toggle_button.setText("☐")
        self.is_collapsed = not self.is_collapsed
        
    def Update_Scaling(self):
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
        offset = int(self.Get_Offset() * 1.222)
        start_y = (self.game_window_y + offset) - global_y
        self.main_layout.setContentsMargins(0, start_y, 0, 0)