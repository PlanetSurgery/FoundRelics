# Scripts/DonatePanel.py
# Created by PlanetSurgery

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

import os

from Buttons import SCROLLBAR_STYLES, create_title_bar

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
        
        title = create_title_bar("ENJ Wallet Donation")
        layout.addWidget(title)
        
        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        layout.addWidget(content, 1)
        
        instruction = QLabel("Please scan the QR code with your ENJ wallet to donate any amount you want on Relaychain. I greatly appreciate any support at all, even if just vocal! Also, make sure you got this from the original source!")
        instruction.setWordWrap(True)
        instruction.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(instruction)
        
        qr_label = QLabel()
        qr_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "W3", "qr"))
        qr_pixmap = QPixmap(qr_image_path)
        
        if not qr_pixmap.isNull():
            scaled_pixmap = qr_pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            qr_label.setPixmap(scaled_pixmap)
        else:
            qr_label.setText("QR code image not found.")
        qr_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(qr_label)
