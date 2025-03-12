# Scripts/MainPanel.py
# Created by PlanetSurgery

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QPlainTextEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

from Buttons import SCROLLBAR_STYLES, create_title_bar

class MainPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DevPanel")
        self.setStyleSheet(f"""
            QFrame#DevPanel {{
                background-color: #000000;
                border: 2px solid black;
                border-radius: 4px;
            }}
            QPlainTextEdit {{
                background-color: #333333;
                color: black;
            }}
            QLabel {{
                color: #dddddd;
            }}
        """ + SCROLLBAR_STYLES)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = create_title_bar("FoundRelics")
        layout.addWidget(title)

        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        layout.addWidget(content, 1)

        self.player_name_label = QLabel("Player: ")
        content_layout.addWidget(self.player_name_label)

        self.player_level_label = QLabel("Level Progress: ")
        content_layout.addWidget(self.player_level_label)

        self.run_count_label = QLabel("Run Count: 0")
        content_layout.addWidget(self.run_count_label)

        self.run_time_label = QLabel("Run Time: 0")
        content_layout.addWidget(self.run_time_label)

        self.gold_rate_label = QLabel("Earned Gold Per Minute: 0")
        content_layout.addWidget(self.gold_rate_label)

        self.market_gold_label = QLabel("Earned Market Gold: 0")
        content_layout.addWidget(self.market_gold_label)

        self.market_enj_label = QLabel("Earned Market ENJ: 0")
        content_layout.addWidget(self.market_enj_label)

        self.fav_map = QLabel("Favorite Map: N/A")
        content_layout.addWidget(self.fav_map)

        self.log_field = QPlainTextEdit()
        self.log_field.setPlainText("Application has started.")
        content_layout.addWidget(self.log_field)

        # Two buttons row
        btn_row = QHBoxLayout()
        self.json_button = QPushButton("Show JSON Data")
        self.json_button.setStyleSheet("""
            background-color: #444444;
            color: #cccccc;
            padding: 6px 10px;
            font-size: 14px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.json_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.json_button.setEnabled(False) 
        btn_row.addWidget(self.json_button, alignment=Qt.AlignLeft)

        self.item_selector_button = QPushButton("Show Tracked Items")
        self.item_selector_button.setStyleSheet("""
            background-color: #444444;
            color: #cccccc;
            padding: 6px 10px;
            font-size: 14px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.item_selector_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_row.addWidget(self.item_selector_button, alignment=Qt.AlignLeft)

        btn_row.addStretch()
        content_layout.addLayout(btn_row)

    def set_player_name(self, name):
        self.player_name_label.setText(f"Player: {name}")

    def set_player_level(self, level):
        self.player_level_label.setText(f"Level Progress: {level}")

    def set_run_count(self, count):
        self.run_count_label.setText(f"Run Count: {count}")

    def set_run_time(self, time_taken):
        self.run_time_label.setText(f"Run Time: {time_taken}")

    def set_gold_rate(self, gold_found):
        self.gold_rate_label.setText(f"Earned Gold Per Minute: {gold_found}")

    def set_market_gold(self, market_gold):
        self.market_gold_label.setText(f"Earned Market Gold: {market_gold}")

    def set_market_enj(self, market_enj):
        self.market_enj_label.setText(f"Earned Market ENJ: {market_enj}")

    def set_fav_map(self, map_name):
        self.fav_map.setText(f"Favorite Map: {map_name}")

    def log_message(self, msg):
        self.log_field.setPlainText(msg)
