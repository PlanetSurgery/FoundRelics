# \Scripts\ItemTrackerPanel.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
import os, sys, ctypes

from ctypes import wintypes

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QScrollArea, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
# End of Imports --------

# Our Imports -----------
from UIUtilities import Create_TitleBar, SCROLLBAR_STYLES
from GameWindowMixin import GameWindowMixin
# End of Imports --------

class SelectableIcon(QLabel):
    def Init_Vars(self, pixmap, file_path, toggle_callback, thumb_size=64):
        self.thumb_size = thumb_size
        self.original_pixmap = pixmap
        self.file_path = file_path
        self.selected = False
        self.toggle_callback = toggle_callback
        
    def Setup_Params(self, pixmap, thumb_size):
        #self.setFixedSize(self.thumb_size, self.thumb_size)
        self.setPixmap(pixmap.scaled(self.thumb_size, self.thumb_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
    def __init__(self, pixmap, file_path, toggle_callback, thumb_size=64, parent=None):
        super().__init__(parent)
        self.Init_Vars(pixmap, file_path, toggle_callback, thumb_size)
        self.Setup_Params(pixmap, thumb_size)

    # QWidget Override
    def mousePressEvent(self, event):
        self.selected = not self.selected
        if self.toggle_callback:
            self.toggle_callback(self)
        self.update()

    # QPainter Override
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            painter.setBrush(QColor(255, 255, 255, 100))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

class ItemTrackerPanel(GameWindowMixin, QFrame):
    def Init_Objects(self, parent):
        QWidget.__init__(self, parent)
        GameWindowMixin.__init__(self)
        
    def Init_Vars(self):
        self.selected_items = [] 
        self.items_display = None
        self.icon_widgets = [] 
        self.game_window_width = self.width()
        self.game_window_height = self.height()
    
    def Setup_Panel(self):
        self.setObjectName("ItemSelectorPanel")
        self.setStyleSheet(f"QFrame#ItemSelectorPanel {{ background-color: #0F0F0F; border: 2px solid #002244; border-radius: 4px; }} QLabel {{ color: #dddddd; }}"+SCROLLBAR_STYLES)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_bar = Create_TitleBar("Item Selector")
        layout.addWidget(self.title_bar)
        self.lbl_title = self.title_bar.findChild(QLabel)
        
        self.btn_close = None
        for btn in self.title_bar.findChildren(QPushButton):
            if btn.text() == "X":
                self.btn_close = btn
                break

        content = QWidget()
        content.setStyleSheet("background-color: #1A1A1A;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        layout.addWidget(content, 1)

        self.selection_counter = QLabel("Selected: 0/10")
        content_layout.addWidget(self.selection_counter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("background-color: #2A2A2A;")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        content_layout.addWidget(self.scroll_area)

        self.icon_container = QWidget()
        self.icon_grid = QGridLayout(self.icon_container)
        self.icon_grid.setSpacing(8)
        self.icon_grid.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.icon_container)
        
    def Setup_Timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.Update_Scaling)
        self.update_timer.start(16)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.Check_Window)
        self.check_timer.start(16)
        
    def __init__(self, parent=None):
        self.Init_Objects(parent)
        self.Init_Vars()
        self.Setup_Panel()
        self.Setup_Timers()

    def Update_Scaling(self):
        base_resolution = 1920.0
        scale = (self.game_window_width / base_resolution) if self.game_window_width else (self.width() / base_resolution)
        exponent = 1 + 1.5 * max(0, 1 - scale)
        
        dynamic_font_size = max(6, int(15 * (scale ** exponent)))
        counter_font = self.selection_counter.font()
        counter_font.setPointSize(dynamic_font_size)
        self.selection_counter.setFont(counter_font)
        
        if self.lbl_title:
            title_font_size = max(8, int(19 * (scale ** exponent)))
            self.lbl_title.setStyleSheet(f"color: white; font-size: {title_font_size}px; font-weight: bold;")
            new_height = title_font_size + 10  
            self.title_bar.setFixedHeight(new_height)
        
        if self.btn_close:
            close_font_size = max(8, int(16 * (scale ** exponent)))
            self.btn_close.setStyleSheet(f"""
                QPushButton {{
                    color: #0F0F0F;
                    background: transparent;
                    border: none;
                    font-size: {close_font_size}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: #aaaaaa;
                }}
                QPushButton:disabled {{
                    color: #555555;
                }}
            """)

    # QWidget Override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        viewport_width = self.scroll_area.viewport().width()
        self.icon_container.setMinimumWidth(viewport_width)
        self.Update_Layout()

    # QWidget Override
    def showEvent(self, event):
        super().showEvent(event)
        viewport_width = self.scroll_area.viewport().width()
        self.icon_container.setMinimumWidth(viewport_width)
        self.Update_Layout()

    def Update_Layout(self):
        while self.icon_grid.count():
            item = self.icon_grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        spacing = self.icon_grid.spacing()  # e.g., 8 pixels
        available_width = self.scroll_area.viewport().width()
        new_thumb_size = max(10, (available_width - (2 * spacing)) // 3)
        
        for widget in self.icon_widgets:
            widget.setFixedSize(new_thumb_size, new_thumb_size)
            widget.setPixmap(widget.original_pixmap.scaled(new_thumb_size, new_thumb_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        cols = 3
        row = 0
        col = 0
        
        for widget in self.icon_widgets:
            self.icon_grid.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def Set_Display(self, items_display):
        self.items_display = items_display

    def Populate_Display(self, all_items):
        while self.icon_grid.count():
            item = self.icon_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
              
        self.icon_widgets = []  
        for pix, path in all_items:
            icon_widget = SelectableIcon(pix, path, self.On_Toggle, thumb_size=64)
            self.icon_widgets.append(icon_widget)
            
        self.Update_Layout()

    def On_Toggle(self, icon_widget):
        max_items = self.items_display.num_items if self.items_display else 10

        if icon_widget.selected:
            if len(self.selected_items) < max_items:
                if icon_widget not in self.selected_items:
                    self.selected_items.append(icon_widget)
            else:
                icon_widget.selected = False
                icon_widget.update()
        else:
            if icon_widget in self.selected_items:
                self.selected_items.remove(icon_widget)

        self.selection_counter.setText(f"Selected: {len(self.selected_items)}/{max_items}")

        if self.items_display:
            selected_pixmaps = [w.original_pixmap for w in self.selected_items]
            selected_paths = [w.file_path for w in self.selected_items] 
            self.items_display.Update_Icons(selected_pixmaps, selected_paths)

    def Highlight_Defaults(self, default_paths):
        if self.selected_items:
            return
            
        for widget in self.icon_widgets:
            if widget and widget.file_path in default_paths:
                widget.selected = True
                widget.update()
                self.selected_items.append(widget)

        max_items = self.items_display.num_items if self.items_display else 10
        self.selection_counter.setText(f"Selected: {len(self.selected_items)}/{max_items}")

        if self.items_display:
            pixmaps = [w.original_pixmap for w in self.selected_items]
            paths = [w.file_path for w in self.selected_items]
            self.items_display.Update_Icons(pixmaps, paths)

    def Get_Selected_Map(self):
        return [icon.original_pixmap for icon in self.selected_items]