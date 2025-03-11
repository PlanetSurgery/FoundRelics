# Scripts/ItemTrackerPanel.py
# Created by PlanetSurgery

import os
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QScrollArea, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
from Scripts.Buttons import SCROLLBAR_STYLES, create_title_bar

class SelectableIcon(QLabel):
    """
    A clickable icon that toggles a white overlay when selected.
    """
    def __init__(self, pixmap, file_path, toggle_callback, thumb_size=64, parent=None):
        super().__init__(parent)
        self.thumb_size = thumb_size
        self.original_pixmap = pixmap
        self.file_path = file_path
        self.selected = False
        self.toggle_callback = toggle_callback
        self.setFixedSize(self.thumb_size, self.thumb_size)
        self.setPixmap(pixmap.scaled(self.thumb_size, self.thumb_size,
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        self.selected = not self.selected
        if self.toggle_callback:
            self.toggle_callback(self)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            painter.setBrush(QColor(255, 255, 255, 100))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

class ItemTrackerPanel(QFrame):
    """
    A panel where the user can select up to a number of items based on ItemsDisplay.
    Immediately updates the ItemsDisplay each time selection changes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ItemSelectorPanel")
        self.setStyleSheet(f"""
            QFrame#ItemSelectorPanel {{
                background-color: #0F0F0F;
                border: 2px solid #002244;
                border-radius: 4px;
            }}
            QLabel {{
                color: #dddddd;
            }}
        """ + SCROLLBAR_STYLES)
        
        self.selected_items = []  # list of SelectableIcon
        self.items_display = None  # Reference to ItemsDisplay

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = create_title_bar("Item Selector")
        layout.addWidget(title)

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
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        content_layout.addWidget(self.scroll_area)

        self.icon_container = QWidget()
        self.icon_grid = QGridLayout(self.icon_container)
        self.icon_grid.setSpacing(8)
        self.scroll_area.setWidget(self.icon_container)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        viewport_width = self.scroll_area.viewport().width()
        self.icon_container.setMinimumWidth(viewport_width)

    def set_items_display(self, items_display):
        self.items_display = items_display

    def populate_items(self, all_items):
        while self.icon_grid.count():
            child = self.icon_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        cols = 7
        row = 5
        col = 0

        for pix, path in all_items:
            icon_widget = SelectableIcon(pix, path, self.on_icon_toggled, thumb_size=64)
            self.icon_grid.addWidget(icon_widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def on_icon_toggled(self, icon_widget):
        # Use the current item count from ItemsDisplay (default to 10 if not set)
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
            selected_paths = [w.file_path for w in self.selected_items]  # update file paths
            self.items_display.update_icons(selected_pixmaps, selected_paths)

    def highlight_defaults(self, default_paths):
        if self.selected_items:
            return
        for i in range(self.icon_grid.count()):
            widget = self.icon_grid.itemAt(i).widget()
            if widget and widget.file_path in default_paths:
                widget.selected = True
                widget.update()
                self.selected_items.append(widget)

        max_items = self.items_display.num_items if self.items_display else 10
        self.selection_counter.setText(f"Selected: {len(self.selected_items)}/{max_items}")

        if self.items_display:
            pixmaps = [w.original_pixmap for w in self.selected_items]
            paths = [w.file_path for w in self.selected_items]
            self.items_display.update_icons(pixmaps, paths)

    def get_selected_pixmaps(self):
        return [icon.original_pixmap for icon in self.selected_items]