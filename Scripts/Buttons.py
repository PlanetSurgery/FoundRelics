from PyQt5.QtGui import QPainter, QPen, QColor, QPalette
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
import requests

########################################
# SCROLLBAR_STYLES now lives here
########################################
SCROLLBAR_STYLES = """
QScrollBar:vertical {
    background: #000000;  /* darker gray background inside panel */
    width: 12px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #666666;  /* handle color */
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

########################################
# create_title_bar
########################################
def create_title_bar(title_text):
    title_bar = QFrame()
    title_bar.setObjectName("TitleBar")
    title_bar.setStyleSheet("""
        QFrame#TitleBar {
            background-color: #333333;
        }
    """)
    layout = QHBoxLayout(title_bar)
    layout.setContentsMargins(8, 4, 8, 4)
    layout.setSpacing(8)

    lbl_title = QLabel(title_text)
    lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
    layout.addWidget(lbl_title, alignment=Qt.AlignVCenter | Qt.AlignLeft)

    layout.addStretch()

    btn_close = QPushButton("X")
    btn_close.setEnabled(False)  # grayed out for now
    btn_close.setStyleSheet("""
        QPushButton {
            color: #0F0F0F;
            background: transparent;
            border: none;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            color: #aaaaaa;
        }
        QPushButton:disabled {
            color: #555555;
        }
    """)
    #layout.addWidget(btn_close, alignment=Qt.AlignVCenter | Qt.AlignRight)
    return title_bar

########################################
# draw_control_buttons & handle_control_buttons_click
########################################
def draw_control_buttons(painter, widget_width, widget_height,
                         show_blue_box, control_padding=15, red_box_size=100):
    # Red box
    red_x = widget_width - red_box_size - control_padding
    red_y = widget_height - red_box_size - control_padding
    painter.fillRect(red_x, red_y, red_box_size, red_box_size, QColor(255, 0, 0))

    # Optional blue box
    if show_blue_box:
        blue_box_size = 100
        blue_x = red_x
        blue_y = red_y - blue_box_size - control_padding
        painter.fillRect(blue_x, blue_y, blue_box_size, blue_box_size, QColor(0, 0, 255))

    # Smaller squares
    button_size = int((red_box_size - control_padding) / 2)
    green_x = red_x - button_size - control_padding
    green_y = red_y
    painter.fillRect(green_x, green_y, button_size, button_size, QColor(0, 255, 0))

    orange_rect = QRect(green_x, green_y + button_size + control_padding,
                        button_size, button_size)
    painter.fillRect(orange_rect, QColor(255, 165, 0))

    cyan_rect = QRect(green_x - button_size - control_padding,
                      green_y + button_size + control_padding,
                      button_size, button_size)
    painter.fillRect(cyan_rect, QColor(0, 255, 255))

    return {
        "red_rect": QRect(red_x, red_y, red_box_size, red_box_size),
        "blue_rect": QRect(red_x, red_y - 100 - control_padding, 100, 100) if show_blue_box else None,
        "green_rect": QRect(green_x, green_y, button_size, button_size),
        "orange_rect": orange_rect,
        "cyan_rect": cyan_rect
    }

def handle_control_buttons_click(event, rects,
                                 show_blue_box, show_individual_buttons,
                                 on_exit, on_reset, on_increment, on_decrement):
    pos = event.pos()

    # Red => toggle blue box + individual buttons
    if rects["red_rect"].contains(pos):
        return not show_blue_box, not show_individual_buttons

    # Green => reset
    if rects["green_rect"].contains(pos):
        on_reset()
        return show_blue_box, show_individual_buttons

    # Orange => decrement item count
    if rects["orange_rect"].contains(pos):
        on_decrement()
        return show_blue_box, show_individual_buttons

    # Cyan => increment item count
    if rects["cyan_rect"].contains(pos):
        on_increment()
        return show_blue_box, show_individual_buttons

    # No change
    return show_blue_box, show_individual_buttons

########################################
# MainPanelButtons: New widget for the main panel buttons.
########################################
class MainPanelButtons(QWidget):
    """
    A control widget to be embedded in the main panel (DevUIPanel).
    It shows a top row with three buttons:
      + (increment),
      – (decrement),
      ! (toggle per-item buttons);
    and a bottom row with two buttons:
      RESET (resets counts) and UI (toggles the UI via an HTTP call).
    All buttons are styled with a grey background to match the panel,
    top row buttons are fixed at 38x38, and the bottom buttons are sized to fit their text (70x40).
    The widget's background is set to match the panel's background color,
    and extra bottom padding is added so the buttons don't touch the frame edge.
    """
    def __init__(self, parent=None, on_increment=None, on_decrement=None, on_toggle=None, on_reset=None):
        super().__init__(parent)
        self.on_increment = on_increment
        self.on_decrement = on_decrement
        self.on_toggle = on_toggle
        self.on_reset = on_reset

        # Set the widget's background using a palette.
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#1A1A1A"))  # Adjust to match your panel background if needed
        self.setPalette(palette)

        # Define sizes for the buttons.
        top_button_size = 38
        bottom_button_width = 70
        bottom_button_height = 40

        # Create top row buttons.
        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("–")
        self.toggle_button = QPushButton("!")

        # Set fixed size for top row buttons.
        for btn in (self.plus_button, self.minus_button, self.toggle_button):
            btn.setFixedSize(top_button_size, top_button_size)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    font-size: 18px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #555555;
                }}
            """)

        # Create bottom row buttons: RESET and UI.
        self.reset_button = QPushButton("RESET")
        self.reset_button.setFixedSize(bottom_button_width, bottom_button_height)
        self.reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)

        self.ui_button = QPushButton("UI")
        self.ui_button.setFixedSize(bottom_button_width, bottom_button_height)
        self.ui_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)

        # Connect signals.
        self.plus_button.clicked.connect(self.handle_plus)
        self.minus_button.clicked.connect(self.handle_minus)
        self.toggle_button.clicked.connect(self.handle_toggle)
        self.reset_button.clicked.connect(self.handle_reset)
        self.ui_button.clicked.connect(self.handle_ui)

        # Layout for top row.
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.plus_button)
        top_layout.addWidget(self.minus_button)
        top_layout.addWidget(self.toggle_button)
        top_layout.addStretch()

        # Layout for bottom row.
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.reset_button)
        bottom_layout.addWidget(self.ui_button)
        bottom_layout.addStretch()

        # Combine rows in a vertical layout with bottom padding.
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.setContentsMargins(0, 0, 0, 10)  # 10 px bottom margin for padding
        self.setLayout(main_layout)

    def handle_plus(self):
        if self.on_increment:
            self.on_increment()

    def handle_minus(self):
        if self.on_decrement:
            self.on_decrement()

    def handle_toggle(self):
        if self.on_toggle:
            self.on_toggle()

    def handle_reset(self):
        if self.on_reset:
            self.on_reset()

    def handle_ui(self):
        # Simple HTTP call to toggle UI
        try:
            requests.get("http://localhost:11990/ToggleUI")
        except Exception as e:
            print("Error toggling UI:", e)
