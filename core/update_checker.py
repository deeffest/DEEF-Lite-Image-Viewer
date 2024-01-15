#update_checker.py
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str, str)
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
        if response.status_code == 200:
            data = response.json()
            item_version = data["name"]
            item_download = data.get("html_url")
            item_notes = data.get("body")

            if item_version != self.app_version:
                self.update_available.emit(
                    item_version, item_download, item_notes
                )
            else:
                self.no_update_found.emit()