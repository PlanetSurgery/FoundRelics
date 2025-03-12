# Scripts/MainParent.py
# Created by PlanetSurgery

import sys, os, json, requests

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, QObject

from .Buttons import MainPanelButtons 
from .ItemsDisplay import ItemsDisplay
from .ItemTrackerPanel import ItemTrackerPanel
from .JSONDataPanel import JSONDataPanel

class MainParent(QWidget):
    def __init__(self, panels_widget, parent=None):
        super().__init__(parent)
        self.is_collapsed = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #222222;")
        title_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        title_layout.setContentsMargins(8, 4, 8, 4)
        title_layout.setSpacing(8)

        lbl_title = QLabel("Panels")
        lbl_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title_layout.addWidget(lbl_title, alignment=Qt.AlignLeft)

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

        close_button = QPushButton("X")
        close_button.setStyleSheet("""
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
        close_button.clicked.connect(QApplication.instance().quit)
        btn_layout.addWidget(close_button, alignment=Qt.AlignLeft)

        title_layout.addWidget(btn_container, alignment=Qt.AlignRight)
        main_layout.addWidget(title_bar, alignment=Qt.AlignLeft)

        self.stack = QStackedWidget()
        self.stack.addWidget(panels_widget)
        dummy_placeholder = QWidget()
        dummy_placeholder.setFixedSize(panels_widget.size())
        self.stack.addWidget(dummy_placeholder)
        main_layout.addWidget(self.stack)

        self.panels_widget = panels_widget

    def toggle_panels(self):
        if self.is_collapsed:
            self.stack.setCurrentIndex(0)
            self.toggle_button.setText("_")
        else:
            self.stack.setCurrentIndex(1)
            self.toggle_button.setText("☐")
        self.is_collapsed = not self.is_collapsed