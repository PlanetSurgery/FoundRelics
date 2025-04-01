# \Scripts\GameWindowMixin.py
# Created by PlanetSurgery
# Assisted by OpenAI

# Py Imports ------------
import ctypes, sys
from ctypes import wintypes
# End of Imports --------

class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("rcNormalPosition", wintypes.RECT)
    ]

class GameWindowMixin:
    def __init__(self):
        self.game_hwnd = None
        self.game_window_x = 0
        self.game_window_y = 0
        self.game_window_width = 1920
        self.game_window_height = 1080
        
    def Check_Window(self):
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
            print("Error checking game window:", e)
            
    def Is_Maximized(self):
        if self.game_hwnd:
            wp = WINDOWPLACEMENT()
            wp.length = ctypes.sizeof(WINDOWPLACEMENT)
            ctypes.windll.user32.GetWindowPlacement(self.game_hwnd, ctypes.byref(wp))
            return wp.showCmd == 3
        return False
        
    def Get_Offset(self):
        if self.game_hwnd:
            pt = wintypes.POINT(0, 0)
            ctypes.windll.user32.ClientToScreen(self.game_hwnd, ctypes.byref(pt))
            return pt.y - self.game_window_y
        return 0