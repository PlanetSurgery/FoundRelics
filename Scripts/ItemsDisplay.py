# Scripts/ItemsDisplay.py
# Created by PlanetSurgery

import sys, ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QFont, QGuiApplication
from PyQt5.QtCore import Qt, QRect, QTimer, QPoint

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

class ItemsDisplay(QWidget):
    def __init__(self, parent=None, num_items=10):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1200, 600)
        
        self.num_items = num_items 
        self.item_counts = [0] * self.num_items
        self.show_blue_box = False  
        self.show_individual_buttons = False

        items = self.load_placeholder_icons()
        self.original_icons = [it[0] for it in items]
        self.original_icon_paths = [it[1] for it in items]
        self.icons = list(self.original_icons)
        self.current_icon_paths = list(self.original_icon_paths)

        self.game_hwnd = None 
        self.game_window_x = 0
        self.game_window_y = 0 
        self.game_window_width = self.width() if self.width() > 0 else 1920
        self.game_window_height = self.height() if self.height() > 0 else 1080

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(16)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_game_window)
        self.check_timer.start(67)

    def load_placeholder_icons(self):
        placeholder = QPixmap(100, 100)
        semi_transparent_grey = QColor(128, 128, 128, 150)
        placeholder.fill(semi_transparent_grey)
        return [(placeholder, "placeholder")] * self.num_items

    def update_icons(self, selected_pixmaps, selected_paths):
        new_icons = []
        new_paths = []
        for i in range(self.num_items):
            if i < len(selected_pixmaps):
                new_icons.append(selected_pixmaps[i])
                new_paths.append(selected_paths[i])
            else:
                new_icons.append(self.original_icons[i])
                new_paths.append(self.original_icon_paths[i])
        self.icons = new_icons
        self.current_icon_paths = new_paths
        self.update()

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
            print("Error checking game window in ItemsDisplay:", e)

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
        
    def is_fullscreen(self):
        screen = QGuiApplication.primaryScreen().geometry()
        return (self.game_window_width == screen.width() and self.game_window_height == screen.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        client_offset = self.get_client_offset()
        if client_offset == 0:
            client_offset = 30  
        offset = int(client_offset * 1.222)
        
        natural_box_size = 55
        base_padding = 20

        box_size = int(natural_box_size * scale)
        padding = int(base_padding * scale)
        group_width = self.num_items * box_size + (self.num_items - 1) * padding

        game_center = self.game_window_x + self.game_window_width // 2
        widget_global_x = self.mapToGlobal(QPoint(0, 0)).x()
        start_x = game_center - (group_width // 2) - widget_global_x

        widget_global_y = self.mapToGlobal(QPoint(0, 0)).y()
        start_y = (self.game_window_y + offset) - widget_global_y

        text_height = int(30 * scale)
        extra_space = int(5 * scale)
        
        font = QFont()
        dynamic_font_size = max(8, int(14 * scale))
        font.setPointSize(dynamic_font_size)
        font.setBold(True)
        painter.setFont(font)
        
        for i in range(self.num_items):
            rect = QRect(start_x + i * (box_size + padding), start_y, box_size, box_size)
            pix = self.icons[i]
            scaled_pix = pix.scaled(box_size, box_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pix_x = rect.x() + (box_size - scaled_pix.width()) // 2
            pix_y = rect.y() + (box_size - scaled_pix.height()) // 2
            painter.drawPixmap(pix_x, pix_y, scaled_pix)
            
            text_rect = QRect(rect.x(), rect.y() + box_size + extra_space, box_size, text_height)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(text_rect, Qt.AlignCenter, str(self.item_counts[i]))
            
            if self.show_individual_buttons:
                button_width = (box_size - padding) // 2
                button_height = button_width
                button_y = text_rect.y() + text_rect.height() + extra_space
                minus_rect = QRect(rect.x(), button_y, button_width, button_height)
                plus_rect = QRect(rect.x() + button_width + padding, button_y, button_width, button_height)
                painter.setBrush(QColor(128, 128, 128))
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                radius = 5
                painter.drawRoundedRect(minus_rect, radius, radius)
                painter.drawRoundedRect(plus_rect, radius, radius)
                painter.drawText(minus_rect, Qt.AlignCenter, "-")
                painter.drawText(plus_rect, Qt.AlignCenter, "+")
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(255, 255, 255)))
            
            border_pen = QPen(QColor(0, 0, 0))
            border_pen.setWidth(2)
            painter.setPen(border_pen)
            painter.drawRect(rect)
            painter.setPen(QPen(QColor(255, 255, 255)))
    
    def mousePressEvent(self, event):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        client_offset = self.get_client_offset()
        if client_offset == 0:
            client_offset = 30 
        offset = int(client_offset * 1.222)
        
        natural_box_size = 55
        base_padding = 20

        box_size = int(natural_box_size * scale)
        padding = int(base_padding * scale)
        group_width = self.num_items * box_size + (self.num_items - 1) * padding

        game_center = self.game_window_x + self.game_window_width // 2
        widget_global_x = self.mapToGlobal(QPoint(0, 0)).x()
        start_x = game_center - (group_width // 2) - widget_global_x

        widget_global_y = self.mapToGlobal(QPoint(0, 0)).y()
        start_y = (self.game_window_y + offset) - widget_global_y
        
        text_height = int(30 * scale)
        extra_space = int(5 * scale)
        
        for i in range(self.num_items):
            rect = QRect(start_x + i * (box_size + padding), start_y, box_size, box_size)
            text_rect = QRect(rect.x(), rect.y() + box_size + extra_space,
                              box_size, text_height)
            button_width = (box_size - padding) // 2
            button_height = button_width
            button_y = text_rect.y() + text_rect.height() + extra_space
            minus_rect = QRect(rect.x(), button_y, button_width, button_height)
            plus_rect = QRect(rect.x() + button_width + padding, button_y,
                              button_width, button_height)
            
            base_name = self.current_icon_paths[i]
            adjust_value = 1
            count = self.item_counts[i]
            if "Enjin Gem" in base_name:
                adjust_value = 0.01

            if minus_rect.contains(event.pos()):
                count -= adjust_value
            elif plus_rect.contains(event.pos()):
                count += adjust_value
                    
            self.item_counts[i] = round(count, 2)
        self.update()