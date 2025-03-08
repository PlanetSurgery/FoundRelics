import sys, os, json, requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, QObject
from Scripts.DevUIPanel import DevUIPanel
from Scripts.JSONDataPanel import JSONDataPanel
from Scripts.ItemTrackerPanel import ItemTrackerPanel
from Scripts.ItemsDisplay import ItemsDisplay
from Scripts.Buttons import MainPanelButtons  # New widget with the three-button row + RESET + UI

# Worker class to fetch data in a separate thread.
class DataFetcher(QObject):
    data_fetched = pyqtSignal(dict)
    error = pyqtSignal(str)

    @pyqtSlot()
    def fetch(self):
        try:
            response = requests.get("http://localhost:11990/Player")
            response.raise_for_status()
            data = response.json()
            self.data_fetched.emit(data)
        except Exception as e:
            self.error.emit(str(e))

class SidePanelContainer(QWidget):
    """
    Container widget for the left panels with a custom title bar.
    The title bar now places its contents on one horizontal line (title plus toggle and close buttons).
    The content below is managed using a QStackedWidget.
    """
    def __init__(self, panels_widget, parent=None):
        super().__init__(parent)
        self.is_collapsed = False  # track collapsed state
        self.change = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
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

        # Button container.
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

        # QStackedWidget for the panels.
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

class FullScreenOverlay(QMainWindow):
    def __init__(self):
        super().__init__()

        # Frameless full-screen with transparency.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.selected_items = []  # references from item tracker

        # Shared variable: total number of items (default 13)
        self.num_items = 13
        self.run_count = 0
        self.run_time_total = 0
        self.market_gold = 0
        self.market_enj = 0


        # Initialize a dictionary to track map play counts.
        self.map_counts = {}

        # Create central widget for absolute positioning.
        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")
        central_widget.setStyleSheet("#central_widget { background: transparent; }")
        self.setCentralWidget(central_widget)

        # ---------------------------
        # Left Panels Setup (Absolute)
        # ---------------------------
        left_container_inner = QWidget()
        left_container_inner.setFixedSize(330, 960)
        left_layout = QVBoxLayout(left_container_inner)
        left_layout.setContentsMargins(0, 15, 0, 15)
        left_layout.setSpacing(15)

        self.dev_panel = DevUIPanel()  # Main panel holding name, level, count, etc.
        self.json_panel = JSONDataPanel()
        self.json_panel.setVisible(False)
        self.item_selector_panel = ItemTrackerPanel()
        self.item_selector_panel.setVisible(False)

        # Extend dev_panel height to accommodate new buttons.
        common_panel_width = 300
        common_panel_height = 420  # Extended height
        self.dev_panel.setFixedSize(common_panel_width, common_panel_height)
        self.json_panel.setFixedSize(common_panel_width, 400)
        self.item_selector_panel.setFixedSize(common_panel_width, 400)

        # Assume dev_panel has a layout; add new buttons at its bottom.
        dev_layout = self.dev_panel.layout()
        if dev_layout is None:
            dev_layout = QVBoxLayout(self.dev_panel)
            self.dev_panel.setLayout(dev_layout)
        dev_layout.addStretch()  # Spacer between existing content and buttons
        self.main_panel_buttons = MainPanelButtons(
            on_increment=self.increment_items,
            on_decrement=self.decrement_items,
            on_toggle=self.toggle_item_buttons,
            on_reset=self.reset_items
        )
        dev_layout.addWidget(self.main_panel_buttons)

        left_layout.addWidget(self.dev_panel)
        left_layout.addWidget(self.json_panel)
        left_layout.addWidget(self.item_selector_panel)
        left_layout.addStretch()

        self.side_panel_container = SidePanelContainer(left_container_inner, central_widget)
        self.side_panel_container.setGeometry(20, 20, left_container_inner.width(), left_container_inner.height())

        # ---------------------------
        # ItemsDisplay Setup (Absolute)
        # ---------------------------
        self.items_display = ItemsDisplay(central_widget, num_items=self.num_items)
        self.items_display.setGeometry(370, 20, 1200, 600)
        self.items_display.raise_()

        # ---------------------------
        # Timers and Data Fetching Setup
        # ---------------------------
        self.fetch_timer = QTimer(self)
        self.fetch_timer.timeout.connect(self.show_fetching_data)
        self.fetch_timer.setSingleShot(True)
        self.fetch_timer.start(3000)

        # Use a QTimer to trigger data updates, which now run in a separate thread.
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_player_data)
        self.data_timer.start(5000)

        self.last_progress = 0
        self.last_gold_coins = 0

        # Connect DevUIPanel buttons.
        self.dev_panel.json_button.clicked.connect(self.toggle_json_panel)
        self.dev_panel.item_selector_button.clicked.connect(self.toggle_item_selector_panel)

        self.all_icons = self.load_all_icons()
        self.item_selector_panel.populate_items(self.all_icons)
        self.item_selector_panel.set_items_display(self.items_display)

    # Callback methods for the new main panel buttons:
    def increment_items(self):
        if self.items_display.num_items < self.num_items:
            self.items_display.num_items += 1
            self.items_display.item_counts.append(0)
            if len(self.items_display.original_icons) > len(self.items_display.icons):
                self.items_display.icons.append(self.items_display.original_icons[len(self.items_display.icons)])
            else:
                self.items_display.icons.append(self.items_display.icons[-1])
            self.items_display.update()

    def decrement_items(self):
        if self.items_display.num_items > 1:
            self.items_display.num_items -= 1
            self.items_display.item_counts.pop()
            self.items_display.icons.pop()
            self.items_display.update()

    def toggle_item_buttons(self):
        # Toggle the per-item +/- buttons.
        self.items_display.show_individual_buttons = not self.items_display.show_individual_buttons
        self.items_display.update()

    def reset_items(self):
        self.items_display.item_counts = [0] * self.items_display.num_items
        self.items_display.update()

    def load_all_icons(self):
        from PyQt5.QtGui import QPixmap
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icons_folder = os.path.join(base_dir, "Icons")
        all_items = []
        for root, dirs, files in os.walk(icons_folder):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    path = os.path.join(root, file)
                    pix = QPixmap(path)
                    if pix.isNull():
                        print(f"Failed to load icon: {path}")
                        pix = QPixmap(64, 64)
                        pix.fill(Qt.gray)
                    all_items.append((pix, path))
        return all_items

    def show_fetching_data(self):
        self.dev_panel.log_message("Fetching data...")

    def update_player_data(self):
        # Start the data fetching in a separate thread.
        self.dev_panel.log_message("Fetching data in background...")
        self.thread = QThread()
        self.worker = DataFetcher()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.fetch)
        self.worker.data_fetched.connect(self.handle_data)
        self.worker.error.connect(self.handle_error)
        # Clean up the thread once done.
        self.worker.data_fetched.connect(self.thread.quit)
        self.worker.data_fetched.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def handle_data(self, data):
        if data:
            self.dev_panel.log_message("We have grabbed data.")
            self.dev_panel.set_player_name(data.get("PlayerName", ""))
            
            # Extract current XP and max XP, ensuring they are integers
            try:
                current_xp = int(data.get("PlayerLevelProgress", 0))
            except (ValueError, TypeError):
                current_xp = 0

            try:
                max_xp = int(data.get("PlayerLevelMax", 0))
            except (ValueError, TypeError):
                max_xp = 0

            # Format the numbers with commas
            formatted_current = "{:,}".format(current_xp)
            formatted_max = "{:,}".format(max_xp)

            # Calculate the percentage (avoid division by zero)
            percentage = (current_xp / max_xp) * 100 if max_xp != 0 else 0

            # Construct the final string with "xp" added after the numbers
            final_string = f"{formatted_current} XP / {formatted_max} XP || {percentage:.0f}%"

            self.dev_panel.set_player_level(final_string)

            new_progress = data.get("PlayerLevelProgress", None)
            last_adv = data.get("LastAdventure", {})
            gold_coins = None
            for item in last_adv.get("Items", []):
                if item.get("Name", "").strip() == "Gold Coins":
                    gold_coins = item.get("Amount", None)
                    break

            if new_progress is not None and self.last_progress is not None:
                changed = new_progress - self.last_progress
                if 0 < changed <= 500:
                    change = True
                if self.last_progress is None:
                    # First fetch: initialize without incrementing run count.
                    self.last_progress = new_progress
                    self.last_gold_coins = gold_coins
                elif new_progress != self.last_progress and (gold_coins is None or gold_coins != self.last_gold_coins) and (change is False or (change is True and gold_coins is not None)):
                    change = False
                    # A new run is confirmed; increment run count.
                    if gold_coins is not None:
                        self.run_count += 1
                    self.last_progress = new_progress
                    self.last_gold_coins = gold_coins
                    
                    # Accumulate run time.
                    time_taken = data.get("TimeTaken", 0)
                    try:
                        time_taken = float(time_taken)
                    except Exception:
                        time_taken = 0
                    self.run_time_total += time_taken

                    # Update map counts using LastAdventure>AdventureName.
                    adventure_name = last_adv.get("AdventureName", None)
                    if adventure_name:
                        if adventure_name in self.map_counts:
                            self.map_counts[adventure_name] += 1
                        else:
                            self.map_counts[adventure_name] = 1

                        # Determine the favorite map (most played).
                        favorite_map = max(self.map_counts, key=self.map_counts.get)
                        self.dev_panel.set_fav_map(favorite_map)
                        
                    market_gold_total = 0
                    market_enj_total = 0
                    for item in last_adv.get("Items", []):
                        try:
                            market_value = float(item.get("MarketValue", 0))
                        except (ValueError, TypeError):
                            market_value = 0
                        if item.get("Name", None) not in ["Enjin Gem", "Waygate Orb", "Gold Coins"]:
                            amount = item.get("Amount", 1)
                            if item.get("IsBlockchain", False):
                                market_enj_total += market_value * amount
                            else:
                                market_gold_total += market_value * amount


                    # Add the new values to the cumulative totals.
                    self.market_gold += market_gold_total
                    self.market_enj += market_enj_total

                    # Update the display (formatted with commas).
                    self.dev_panel.set_market_gold("{:,}".format(self.market_gold))
                    self.dev_panel.set_market_enj("{:,}".format(self.market_enj))

                    # For each selected icon, check if its file name matches any item in LastAdventure>Items.
                    import os
                    index = -1
                    for icon in self.item_selector_panel.selected_items:
                        index += 1
                        base_name = os.path.splitext(os.path.basename(icon.file_path))[0].strip()
                        self.dev_panel.log_message("Checking icon: " + base_name)
                        # Find the first matching item from LastAdventure>Items.
                        matching_item = next((item for item in last_adv.get("Items", []) if base_name in item.get("Name", "")), None)
                        if matching_item:
                            try:
                                count = 0
                                if base_name == "Enjin Gem" or base_name == "Flame Crystal":
                                    if base_name == "Enjin Gem":
                                        count = round(matching_item.get("Amount", 1) / 100, 2)
                                    else:
                                        count = matching_item.get("Amount", 1)
                                        self.run_count += 1
                                    self.items_display.item_counts[index] += round(count, 2)
                                else:
                                    self.items_display.item_counts[index] += 1
                            except Exception as e:
                                self.dev_panel.log_message("Error updating count for " + base_name + ": " + str(e))

            self.dev_panel.set_run_count(self.run_count)
            self.dev_panel.set_run_time(self.run_time_total)
            json_text = json.dumps(data, indent=2)
            self.json_panel.set_json_text(json_text)
            self.dev_panel.json_button.setEnabled(True)
        else:
            self.dev_panel.log_message("Failed to load data: Empty response.")

    def handle_error(self, error_msg):
        self.dev_panel.log_message("Failed to load data: " + error_msg)

    def toggle_json_panel(self):
        is_visible = not self.json_panel.isVisible()
        self.json_panel.setVisible(is_visible)
        if is_visible:
            self.item_selector_panel.setVisible(False)
            self.dev_panel.json_button.setText("Hide JSON Data")
            self.dev_panel.item_selector_button.setText("Show Tracked Items")
        else:
            self.dev_panel.json_button.setText("Show JSON Data")

    def toggle_item_selector_panel(self):
        is_visible = not self.item_selector_panel.isVisible()
        self.item_selector_panel.setVisible(is_visible)
        if is_visible:
            self.json_panel.setVisible(False)
            self.dev_panel.item_selector_button.setText("Hide Tracked Items")
            self.dev_panel.json_button.setText("Show JSON Data")
            if not self.item_selector_panel.selected_items:
                default_paths = set(self.items_display.original_icon_paths)
                self.item_selector_panel.highlight_defaults(default_paths)
            selected_pixmaps = self.item_selector_panel.get_selected_pixmaps()
            self.items_display.update_icons(selected_pixmaps, self.items_display.current_icon_paths)
        else:
            self.dev_panel.item_selector_button.setText("Show Tracked Items")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FullScreenOverlay()
    window.show()
    sys.exit(app.exec_())
