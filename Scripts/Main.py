# Scripts/Main.py
# Created by PlanetSurgery

import sys, os, json, requests, re, ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QThread, QEvent, QPoint
from PyQt5.QtGui import QCursor, QIcon

import DataFetcher as Data
from Buttons import MainPanelButtons
from DataFetcher import DataFetcherThread, update_player_data, load_all_icons, check_github_update
from DonatePanel import DonatePanel
from MainPanel import MainPanel
from MainParent import MainParent
from ItemsDisplay import ItemsDisplay
from ItemTrackerPanel import ItemTrackerPanel
from JSONDataPanel import JSONDataPanel

class FullScreenOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.change = False
        self.skip = True
        self.selected_items = []
        self.num_items = 15
        self.run_count = 0
        self.run_time_total = 0
        self.market_gold = 0
        self.market_enj = 0
        self.map_counts = {}
        self.last_progress = None
        self.last_gold_coins = 0
        self.current_data_thread = None

        self.dragging = False
        self.drag_offset = QPoint(0, 0)

        self.setWindowTitle("FoundRelics")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.showFullScreen()
        self.setup_widgets()
        self.setup_timers()
        self.setup_window_check()

        self.dev_panel.json_button.clicked.connect(self.toggle_json_panel)
        self.dev_panel.item_selector_button.clicked.connect(self.toggle_item_selector_panel)

        self.all_icons = load_all_icons(self)
        self.item_selector_panel.populate_items(self.all_icons)
        self.item_selector_panel.set_items_display(self.items_display)
        
    def setup_window_check(self):
        self.window_check_timer = QTimer(self)
        self.window_check_timer.timeout.connect(self.check_game_window)
        self.window_check_timer.start(67)
        
    def check_game_window(self):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "LostRelics")
            if hwnd:
                rect = wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                x = rect.left
                y = rect.top
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                self.setGeometry(x, y, width, height)
                if not self.isVisible():
                    self.show()
                    self.raise_()
                if not hasattr(self, 'base_width'):
                    self.base_width = width
                    self.base_height = height
            else:
                if self.isVisible():
                    self.hide()
        except Exception as e:
            print("Error checking game window:", e)

    def setup_timers(self):
        self.fetch_timer = QTimer(self)
        self.fetch_timer.timeout.connect(self.show_fetching_data)
        self.fetch_timer.setSingleShot(True)
        self.fetch_timer.start(3000)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(lambda: update_player_data(self))
        self.data_timer.start(5000)

        self.pos_timer = QTimer(self)
        self.pos_timer.timeout.connect(self.update_positions)
        self.pos_timer.start(16)
        
        self.github_timer = QTimer(self)
        self.github_timer.timeout.connect(lambda: check_github_update(self))
        self.github_timer.start(1800000)
        check_github_update(self)
        
        self.update_buttons_timer = QTimer(self)
        self.update_buttons_timer.timeout.connect(self.update_dev_panel_button_scaling)
        self.update_buttons_timer.start(16)  

    def update_positions(self):
        if self.dragging:
            global_pos = QCursor.pos()
            parent_pos = self.mapFromGlobal(global_pos)
            new_top_left = parent_pos - self.drag_offset

            game_width = 0
            game_height = 0
            hwnd = ctypes.windll.user32.FindWindowW(None, "LostRelics")
            if hwnd:
                rect = wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                game_width = rect.right - rect.left
                game_height = rect.bottom - rect.top

            margin = 20
            panel_width = self.side_panel_container.width()
            panel_height = self.side_panel_container.height()

            min_x = 10
            max_x = game_width
            min_y = 10
            max_y = game_height

            new_x = max(min_x, min(new_top_left.x(), max_x))
            new_y = max(min_y, min(new_top_left.y(), max_y))

            self.side_panel_container.move(new_x, new_y)

            
    def setup_widgets(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")
        central_widget.setStyleSheet("#central_widget { background: transparent; }")
        self.setCentralWidget(central_widget)

        scale_x = self.width() / 1920.0
        scale_y = self.height() / 1080.0

        self.items_display = ItemsDisplay(central_widget, num_items=self.num_items)
        self.items_display.setGeometry(
            int(370 * scale_x),
            int(20 * scale_y),
            int(1200 * scale_x),
            int(600 * scale_y)
        )

        panel_scale = min(scale_x, scale_y)

        self.left_container_inner = QWidget()
        self.left_container_inner.setFixedSize(
            int(330 * panel_scale),
            int(960 * panel_scale)
        )

        left_layout = QVBoxLayout(self.left_container_inner)
        left_layout.setContentsMargins(0, int(15 * panel_scale), 0, int(15 * panel_scale))
        left_layout.setSpacing(int(15 * panel_scale))

        self.dev_panel = MainPanel()
        self.json_panel = JSONDataPanel()
        self.item_selector_panel = ItemTrackerPanel()
        self.donate_panel = DonatePanel()
        self.side_panel_container = MainParent(self.left_container_inner, central_widget)

        self.json_panel.setVisible(False)
        self.item_selector_panel.setVisible(False)
        self.donate_panel.setVisible(False)

        common_panel_width = int(300 * panel_scale)
        common_panel_height = int(420 * panel_scale)
        self.dev_panel.setFixedSize(common_panel_width, common_panel_height)
        self.json_panel.setFixedSize(common_panel_width, int(400 * panel_scale))
        self.item_selector_panel.setFixedSize(common_panel_width, int(400 * panel_scale))
        self.donate_panel.setFixedSize(common_panel_width, int(400 * panel_scale))

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
            on_reset=self.reset_items,
            on_donate=self.on_donate
        )
        dev_layout.addWidget(self.main_panel_buttons)

        left_layout.addWidget(self.dev_panel)
        left_layout.addWidget(self.json_panel)
        left_layout.addWidget(self.item_selector_panel)
        left_layout.addWidget(self.donate_panel)
        left_layout.addStretch()

        self.items_display.raise_()

    def update_dev_panel_button_scaling(self):
        scale = self.width() / 1920.0
        exponent = 1 + 1.5 * max(0, 1 - scale)
        new_font_size = max(6, int(14 * (scale ** exponent)))
        padding_v = max(2, int(6 * (scale ** exponent)))
        padding_h = max(4, int(10 * (scale ** exponent)))
        self.dev_panel.json_button.setStyleSheet(f"""
            background-color: #444444;
            color: #cccccc;
            padding: {padding_v}px {padding_h}px;
            font-size: {new_font_size}px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)
        self.dev_panel.item_selector_button.setStyleSheet(f"""
            background-color: #444444;
            color: #cccccc;
            padding: {padding_v}px {padding_h}px;
            font-size: {new_font_size}px;
            border: 1px solid #666666;
            border-radius: 4px;
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, 'items_display'):
            return

        scale_x = self.width() / 1920.0
        scale_y = self.height() / 1080.0

        self.items_display.setGeometry(
            int(370 * scale_x),
            int(20 * scale_y),
            int(1200 * scale_x),
            int(600 * scale_y)
        )

        panel_scale = min(scale_x, scale_y)

        self.left_container_inner.setFixedSize(
            int(330 * panel_scale),
            int(960 * panel_scale)
        )

        common_panel_width = int(300 * panel_scale)
        common_panel_height = int(420 * panel_scale)
        self.dev_panel.setFixedSize(common_panel_width, common_panel_height)
        self.json_panel.setFixedSize(common_panel_width, int(400 * panel_scale))
        self.item_selector_panel.setFixedSize(common_panel_width, int(400 * panel_scale))
        self.donate_panel.setFixedSize(common_panel_width, int(400 * panel_scale))
        self.side_panel_container.setGeometry(20, 20, self.width() - 40, self.height() - 40)

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent 
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

    def show_fetching_data(self):
        self.dev_panel.log_message("Fetching data...")

    def toggle_json_panel(self):
        is_visible = not self.json_panel.isVisible()
        self.json_panel.setVisible(is_visible)
        if is_visible:
            self.item_selector_panel.setVisible(False)
            self.donate_panel.setVisible(False)
            self.dev_panel.json_button.setText("Hide Data")
            self.dev_panel.item_selector_button.setText("Show Items")
        else:
            self.dev_panel.json_button.setText("Show Data")

    def toggle_item_selector_panel(self):
        is_visible = not self.item_selector_panel.isVisible()
        self.item_selector_panel.setVisible(is_visible)
        if is_visible:
            self.json_panel.setVisible(False)
            self.donate_panel.setVisible(False)
            self.dev_panel.item_selector_button.setText("Hide Items")
            self.dev_panel.json_button.setText("Show Data")
            if not self.item_selector_panel.selected_items:
                default_paths = set(self.items_display.original_icon_paths)
                self.item_selector_panel.highlight_defaults(default_paths)
            selected_pixmaps = self.item_selector_panel.get_selected_pixmaps()
            self.items_display.update_icons(selected_pixmaps, self.items_display.current_icon_paths)
        else:
            self.dev_panel.item_selector_button.setText("Show Items")
    
    def on_donate(self):
        is_visible = not self.donate_panel.isVisible()
        self.donate_panel.setVisible(is_visible)
        if is_visible:
            self.json_panel.setVisible(False)
            self.item_selector_panel.setVisible(False)
    
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
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icon.ico"))
    change_console_icon(icon_path)
    
    app = QApplication(sys.argv)
    window = FullScreenOverlay()
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec_())