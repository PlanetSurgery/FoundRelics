# Main.py
# Created by PlanetSurgery

import sys, os, json, requests, re

import ctypes

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, QObject, QEvent, QPoint
from PyQt5.QtGui import QCursor, QIcon

from Scripts.Buttons import MainPanelButtons
from Scripts.DataFetcher import DataFetcher
from Scripts.MainPanel import MainPanel
from Scripts.ItemsDisplay import ItemsDisplay
from Scripts.ItemTrackerPanel import ItemTrackerPanel
from Scripts.JSONDataPanel import JSONDataPanel
from Scripts.MainParent import MainParent

class FullScreenOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Class Vars
        self.change = False
        self.skip = True
        self.selected_items = []
        self.num_items = 15
        self.run_count = 0
        self.run_time_total = 0
        self.market_gold = 0
        self.market_enj = 0
        self.map_counts = {}
        self.last_progress = 0
        self.last_gold_coins = 0

        # Variables for dragging the panel
        self.dragging = False
        self.drag_offset = QPoint(0, 0)

        # Window Setup
        self.setWindowTitle("FoundRelics")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.setup_widgets()

        # Setup Timers
        self.setup_timers()

        # Connect DevUIPanel buttons.
        self.dev_panel.json_button.clicked.connect(self.toggle_json_panel)
        self.dev_panel.item_selector_button.clicked.connect(self.toggle_item_selector_panel)

        # Update Display
        self.all_icons = self.load_all_icons()
        self.item_selector_panel.populate_items(self.all_icons)
        self.item_selector_panel.set_items_display(self.items_display)
        
    def setup_timers(self):
        self.fetch_timer = QTimer(self)
        self.fetch_timer.timeout.connect(self.show_fetching_data)
        self.fetch_timer.setSingleShot(True)
        self.fetch_timer.start(3000)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_player_data)
        self.data_timer.start(5000)

        self.pos_timer = QTimer(self)
        self.pos_timer.timeout.connect(self.update_positions)
        self.pos_timer.start(16)
        
        self.github_timer = QTimer(self)
        self.github_timer.timeout.connect(self.check_github_update)
        self.github_timer.start(120000)
        self.check_github_update()
        
    def check_github_update(self):
        url = "https://raw.githubusercontent.com/PlanetSurgery/FoundRelics/refs/heads/main/README.md"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                readme_text = response.text
                # Check for App Version
                version_match = re.search(r'App Version:\s*([^\s]+)', readme_text)
                if version_match:
                    version = version_match.group(1).strip()
                    if version != "0.01_03":
                        message = "2 Minute Log:: Project has been updated to version " + version + ". Update for latest changes!"
                        self.dev_panel.log_message(message)
                        print(message)
                    else:
                        print("2 Minute Log:: Your version is up to date.")
                else:
                    message = "No Version Found"
                    self.dev_panel.log_message(message)
                    print(message)
                
                # Check for Notice
                notice_match = re.search(r'Notice:\s*(.*)', readme_text)
                if notice_match:
                    notice_text = notice_match.group(1).strip()
                    if notice_text:
                        notice_message = "2 Minute Log:: Notice: " + notice_text
                        self.dev_panel.log_message(notice_message)
                        print(notice_message)
            else:
                message = "Failed to fetch GitHub README. HTTP status code: " + str(response.status_code)
                self.dev_panel.log_message(message)
                print(message)
        except Exception as e:
            message = "Error fetching GitHub README: " + str(e)
            self.dev_panel.log_message(message)
            print(message)

    def update_positions(self):
        if self.dragging:
            global_pos = QCursor.pos()
            parent_pos = self.centralWidget().mapFromGlobal(global_pos)
            new_top_left = parent_pos - self.drag_offset
            self.side_panel_container.move(new_top_left)
        
    def setup_widgets(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")
        central_widget.setStyleSheet("#central_widget { background: transparent; }")
        self.setCentralWidget(central_widget)
        
        self.items_display = ItemsDisplay(central_widget, num_items=self.num_items)
        self.items_display.setGeometry(370, 20, 1200, 600)
        
        common_panel_width = 300
        common_panel_height = 420
        left_container_inner = QWidget()
        left_container_inner.setFixedSize(330, 960)
        
        left_layout = QVBoxLayout(left_container_inner)
        left_layout.setContentsMargins(0, 15, 0, 15)
        left_layout.setSpacing(15)

        self.dev_panel = MainPanel()
        self.json_panel = JSONDataPanel()
        self.item_selector_panel = ItemTrackerPanel()
        self.side_panel_container = MainParent(left_container_inner, central_widget)
        
        self.json_panel.setVisible(False)
        self.item_selector_panel.setVisible(False)
        
        self.dev_panel.setFixedSize(common_panel_width, common_panel_height)
        self.json_panel.setFixedSize(common_panel_width, 400)
        self.item_selector_panel.setFixedSize(common_panel_width, 400)
        
        self.side_panel_container.setGeometry(20, 20, self.width() - 40, self.height() - 40)
        self.side_panel_container.installEventFilter(self)

        dev_layout = self.dev_panel.layout()
        if dev_layout is None:
            dev_layout = QVBoxLayout(self.dev_panel)
            self.dev_panel.setLayout(dev_layout)
        dev_layout.addStretch()
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
        
        self.items_display.raise_()

    def eventFilter(self, obj, event):
        if obj == self.side_panel_container:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton and event.pos().y() < 30:
                    self.dragging = True
                    self.drag_offset = event.pos()
                    return True
            elif event.type() == QEvent.MouseMove:
                if self.dragging:
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton and self.dragging:
                    self.dragging = False
                    return True
        return super().eventFilter(obj, event)

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
        self.dev_panel.log_message("Fetching data in background...")
        self.thread = QThread()
        self.worker = DataFetcher()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.fetch)

        self.worker.data_fetched.connect(self.handle_data)
        self.worker.error.connect(self.handle_error)

        self.worker.data_fetched.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.data_fetched.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_data(self, data):
        if data:
            self.dev_panel.log_message("We have grabbed data.")
            echelon = data.get("PlayerLevel")
            player_name = data.get("PlayerName", "")
            self.dev_panel.set_player_name(f"{player_name} || Echelon {echelon}")
                        
            try:
                current_xp = int(data.get("PlayerLevelProgress", 0))
            except (ValueError, TypeError):
                current_xp = 0

            try:
                max_xp = int(data.get("PlayerLevelMax", 0))
            except (ValueError, TypeError):
                max_xp = 0

            formatted_current = "{:,}".format(current_xp)
            formatted_max = "{:,}".format(max_xp)
            percentage = (current_xp / max_xp) * 100 if max_xp != 0 else 0
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
                    self.change = True
                if self.last_progress is None:
                    self.last_progress = new_progress
                    self.last_gold_coins = gold_coins
                elif new_progress != self.last_progress and (gold_coins is None or gold_coins != self.last_gold_coins) and (self.change is False or (self.change is True and gold_coins is not None)):
                    self.change = False
                    self.last_progress = new_progress
                    self.last_gold_coins = gold_coins

                    if self.skip:
                        self.skip = False
                        return
                        
                    if gold_coins is not None:
                        self.run_count += 1
                    
                    time_taken = data.get("TimeTaken", 0)
                    try:
                        time_taken = float(time_taken)
                    except Exception:
                        time_taken = 0
                    self.run_time_total += time_taken

                    adventure_name = last_adv.get("AdventureName", None)
                    if adventure_name:
                        if adventure_name in self.map_counts:
                            self.map_counts[adventure_name] += 1
                        else:
                            self.map_counts[adventure_name] = 1

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
                                market_enj_total += round((market_value * amount) / 100, 2)
                            else:
                                market_gold_total += market_value * amount

                    self.market_gold += market_gold_total
                    self.market_enj += market_enj_total
                    self.dev_panel.set_market_gold("{:,}".format(self.market_gold))
                    self.dev_panel.set_market_enj("{:,}".format(self.market_enj))

                    import os
                    index = -1
                    for icon in self.item_selector_panel.selected_items:
                        index += 1
                        base_name = os.path.splitext(os.path.basename(icon.file_path))[0].strip()
                        self.dev_panel.log_message("Checking icon: " + base_name)
                        matching_item = next((item for item in last_adv.get("Items", []) if base_name in item.get("Name", "")), None)
                        if matching_item:
                            try:
                                count = 0
                                if base_name in ["Enjin Gem", "Flame Crystal", "Golden Grind Chest"]:
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
    
def change_console_icon(icon_path):
    WM_SETICON = 0x80
    ICON_SMALL = 0
    ICON_BIG = 1

    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        hicon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 32, 32, 0x00000010)
        if hicon == 0:
            print("Failed to load icon from:", icon_path)
            return
        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
    else:
        print("No console window found.")

if __name__ == "__main__":
    icon_path = os.path.abspath("icon.ico")
    change_console_icon(icon_path)
    app = QApplication(sys.argv)
    window = FullScreenOverlay()
    window.setWindowIcon(QIcon("icon.ico"))
    window.show()
    sys.exit(app.exec_())
