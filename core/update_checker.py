#update_checker.py
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup

class UpdateChecker(QThread):
    update_available = pyqtSignal(str)
    no_update_found = pyqtSignal()

    def __init__(
        self, 
        version, 
        url, 
        parent=None
        ):
        super().__init__(parent)
        self.url = url
        self.app_version = version

    def run(self):
        response = requests.get(self.url)
        item_version = response.json()["name"]
        item_download = response.json().get("html_url") 

        print(item_version, item_download)

        if item_version is not None and item_version != self.app_version:
            self.update_available.emit(item_download)
        else:
            self.no_update_found.emit()
