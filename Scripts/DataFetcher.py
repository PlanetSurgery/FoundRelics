# Scripts/DataFetcher.py
# Created by PlanetSurgery

import sys, os, json, requests

from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, QObject

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