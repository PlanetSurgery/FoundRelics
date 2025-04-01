# \Scripts\UIUtilities.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
# End of Imports --------

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

def Create_TitleBar(title_text, scale=1.0):
    exponent = 1 + 0.5 * max(0, 1 - scale)
    dynamic_font_size = max(3, int(20 * (scale ** exponent)))
    
    title_bar = QFrame()
    title_bar.setObjectName("TitleBar")
    title_bar.setStyleSheet("QFrame#TitleBar { background-color: #333333; }")
    
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