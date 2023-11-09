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
        url_version, 
        url_download, 
        parent=None
        ):
        super().__init__(parent)
        self.url_version = url_version
        self.url_download = url_download
        self.app_version = version

    def run(self):
        try:
            response = requests.get(self.url_version)
            page = BeautifulSoup(response.content, "html5lib")
            item_version = page.find("span", class_="C9DxTc")

            response_download = requests.get(self.url_download)
            page_download = BeautifulSoup(
                response_download.content, "html5lib")
            item_download = page_download.find("span", class_="C9DxTc")
        except:
            pass

        if item_version is not None and item_version.text != self.app_version:
            self.update_available.emit(item_download.text)
        else:
            self.no_update_found.emit()
