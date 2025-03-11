# Scripts/ItemsDisplay.py
# Created by PlanetSurgery

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QFont
from PyQt5.QtCore import Qt, QRect, QTimer

class ItemsDisplay(QWidget):
    """
    Displays a variable number of boxes with icons.
    """
    def __init__(self, parent=None, num_items=10):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1200, 600)
        
        self.num_items = num_items  # shared variable for number of items (default: 10)
        self.item_counts = [0] * self.num_items
        # The state for blue box and individual buttons now will be controlled externally.
        self.show_blue_box = False  
        self.show_individual_buttons = False

        # Instead of loading random icons, create grey, semi-transparent placeholders.
        items = self.load_placeholder_icons()
        self.original_icons = [it[0] for it in items]  # QPixmaps
        self.original_icon_paths = [it[1] for it in items]
        # Start with these icons.
        self.icons = list(self.original_icons)
        # Maintain a separate list for current file paths (can be updated on selection)
        self.current_icon_paths = list(self.original_icon_paths)

        # Timer to update layout periodically.
        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.update)
        self.position_timer.start(1000)  # update every second

    def load_placeholder_icons(self):
        # Create a grey, semi-transparent pixmap as a placeholder.
        placeholder = QPixmap(100, 100)
        semi_transparent_grey = QColor(128, 128, 128, 150)
        placeholder.fill(semi_transparent_grey)
        # Return a list with the same placeholder for each item.
        return [(placeholder, "placeholder")] * self.num_items

    def update_icons(self, selected_pixmaps, selected_paths):
        """
        Update both the displayed pixmaps and their associated file paths based on selection.
        If fewer than the available slots are selected, the remainder show the original icons and paths.
        """
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

    def paintEvent(self, event):
        painter = QPainter(self)
        padding = 20
        natural_box_size = 75
        max_scale = 0.67
        
        total_natural_width = self.num_items * natural_box_size + (self.num_items - 1) * padding
        available_width = self.width()
        scale = min(max_scale, available_width / total_natural_width)
        box_size = int(natural_box_size * scale)
        group_width = self.num_items * box_size + (self.num_items - 1) * padding

        # Center the group horizontally.
        start_x = (self.width() - group_width) // 2
        start_y = 0

        border_pen = QPen(QColor(0, 0, 0))
        border_pen.setWidth(2)
        painter.setPen(QPen(QColor(255, 255, 255)))
        
        # Create a bold, larger font for item values.
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        for i in range(self.num_items):
            rect = QRect(start_x + i * (box_size + padding), start_y, box_size, box_size)
            pix = self.icons[i]
            scaled_pix = pix.scaled(box_size, box_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pix_x = rect.x() + (box_size - scaled_pix.width()) // 2
            pix_y = rect.y() + (box_size - scaled_pix.height()) // 2
            painter.drawPixmap(pix_x, pix_y, scaled_pix)
            
            text_rect = QRect(rect.x(), rect.y() + box_size + 5, box_size, 30)
            painter.drawText(text_rect, Qt.AlignCenter, str(self.item_counts[i]))
            
            # Draw per–item buttons if enabled.
            if self.show_individual_buttons:
                button_width = (box_size - padding) // 2
                button_height = button_width
                button_y = text_rect.y() + text_rect.height() + 5
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
            
            painter.setPen(border_pen)
            painter.drawRect(rect)
            painter.setPen(QPen(QColor(255, 255, 255)))
        
    def mousePressEvent(self, event):
        if self.show_individual_buttons:
            padding = 20
            natural_box_size = 100
            max_scale = 0.67
            available_width = self.width()
            total_natural_width = self.num_items * natural_box_size + (self.num_items - 1) * padding
            scale = min(max_scale, available_width / total_natural_width)
            box_size = int(natural_box_size * scale)
            group_width = self.num_items * box_size + (self.num_items - 1) * padding
            start_x = (self.width() - group_width) // 2
            start_y = 0

            for i in range(self.num_items):
                rect = QRect(start_x + i * (box_size + padding), start_y, box_size, box_size)
                text_rect = QRect(rect.x(), rect.y() + box_size + 5, box_size, 30)
                button_width = (box_size - padding) // 2
                button_height = button_width
                button_y = text_rect.y() + text_rect.height() + 5
                minus_rect = QRect(rect.x(), button_y, button_width, button_height)
                plus_rect = QRect(rect.x() + button_width + padding, button_y, button_width, button_height)
                
                # Use the current file path for checking button behavior.
                base_name = self.current_icon_paths[i]
                adjust_value = 1
                count = self.item_counts[i]
                if "Enjin Gem" in base_name:
                    adjust_value = 0.01

                if minus_rect.contains(event.pos()):
                    count -= adjust_value
                elif plus_rect.contains(event.pos()):
                    count += adjust_value
                    
                self.item_counts[i] = count
                self.item_counts[i] = round(self.item_counts[i], 2)  # Round to 2 decimals
                self.update()

        # Other mouse events can be handled here.