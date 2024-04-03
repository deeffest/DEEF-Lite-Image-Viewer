import webbrowser
import requests
import mimetypes
import os
import sys

from PyQt5.QtWidgets import qApp, QMainWindow, QFileDialog, QMessageBox, \
    QListWidgetItem
from PyQt5.QtGui import QIcon, QColor, QPixmap, QImage, QPalette
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5 import uic

from core._init_attributes import _init_attributes
from core._init_content import _init_content
from core._init_connect import _init_connect
from core._init_shortcuts import _init_shortcuts
from core._init_config import _init_config
from core._init_icons import _init_icons
from core._init_styles import _init_styles
from core._init_menu import _init_menu

class MainWindow(QMainWindow):
    def __init__(
        self,
        name,
        version,
        current_dir,
        settings,
        image_path=None,
        parent=None
    ):
        super().__init__(parent)

        self.name = name
        self.version = version
        self.current_dir = current_dir
        self.image_path = image_path
        self.settings = settings

        self._init_ui()

    def _init_ui(self):
        uic.loadUi(f"{self.current_dir}/core/ui/main_window.ui", self)
        self.show()
        
        self._init()

    def _init(self):
        _init_attributes(self)
        _init_content(self)
        _init_connect(self)
        _init_shortcuts(self)
        _init_config(self)
        _init_icons(self)
        _init_styles(self)

        self._init_window()
        self.check_for_updates()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image File",
            self.settings.value("last_file_dialog_path", self.current_dir),
            f"All Files (*)",
            options=options
        )
        if image_path:
            self.settings.setValue("last_file_dialog_path", image_path)
            self.open_image(image_path, from_list=False)

    def is_image_file(self, image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        return mime_type is not None and mime_type.startswith('image/')

    def open_image(self, image_path, from_list=None):
        if not self.is_image_file(image_path):
            return

        self.image_path = image_path
        self.setWindowTitle(f"{self.image_path} - {self.name}")
        self.statusbar.showMessage(self.image_path, 2000)
        
        self.load_image()

        if not from_list:
            self.update_folder_contents()
        self.select_current_image()
        self.enable_navigation_buttons()

    def load_image(self):
        image = QImage(self.image_path)
        self.image = QPixmap.fromImage(image)
        self.image_viewer.setPixmap(self.image)
        self.image_size = self.image.size()
        self.scale_image()

    def scale_image(self):
        if hasattr(self, "image_size") and self.image_size:
            if self.image_size.width() > self.scrollArea.width() or self.image_size.height() > self.scrollArea.height():
                self.image_viewer.setPixmap(self.image.scaled(self.scrollArea.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_viewer.setPixmap(self.image)

    def update_folder_contents(self):
        directory = os.path.dirname(self.image_path)
        image_files = [f for f in os.listdir(directory) if self.is_image_file(os.path.join(directory, f))]
        sorted_image_files = sorted(image_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)

        self.listWidget.clear()

        for image_file in sorted_image_files:
            item = QListWidgetItem(image_file)
            item.setToolTip(image_file)
            self.listWidget.addItem(item)

        self.listWidget.itemDoubleClicked.connect(self.on_list_item_double_clicked)

    def on_list_item_double_clicked(self, item):
        if isinstance(item, QListWidgetItem):
            image_file = item.text()
            image_path = os.path.join(os.path.dirname(self.image_path), image_file)
            if os.path.exists(image_path):
                self.open_image(image_path, from_list=True)

    def select_current_image(self):
        current_image = os.path.basename(self.image_path)
        items = self.listWidget.findItems(current_image, Qt.MatchExactly)
        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setForeground(Qt.white if self.settings.value("app_theme") == "dark" else Qt.black)

        if items:
            item = items[0]
            item.setSelected(True)
            item.setForeground(Qt.red)

    def enable_navigation_buttons(self):
        self.actionPrevious.setEnabled(True)
        self.toolButton.setEnabled(True)
        self.actionNext.setEnabled(True)
        self.toolButton_2.setEnabled(True)

    def previous(self):
        current_image_index = self.get_current_image_index()
        if current_image_index > 0:
            previous_image_file = self.listWidget.item(current_image_index - 1).text()
            previous_image_path = os.path.join(os.path.dirname(self.image_path), previous_image_file)
            if os.path.exists(previous_image_path):
                self.open_image(previous_image_path, from_list=True)

    def next(self):
        current_image_index = self.get_current_image_index()
        if current_image_index < self.listWidget.count() - 1:
            next_image_file = self.listWidget.item(current_image_index + 1).text()
            next_image_path = os.path.join(os.path.dirname(self.image_path), next_image_file)
            if os.path.exists(next_image_path):
                self.open_image(next_image_path, from_list=True)

    def get_current_image_index(self):
        current_image = os.path.basename(self.image_path)
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).text() == current_image:
                return i
        return -1

    def toggle_dark_theme(self):
        if self.actionDark_Theme.isChecked():
            self.settings.setValue("app_theme", "dark")
        else:
            self.settings.setValue("app_theme", "light")

    def full_screen(self):
        if self.windowState() & Qt.WindowFullScreen:            
            self.menubar.show()
            self.statusbar.show()
            self.showNormal()
            self.actionFull_Screen.setChecked(False)
        else:
            self.menubar.hide()
            self.statusbar.hide()
            self.setWindowState(Qt.WindowFullScreen)
            self.actionFull_Screen.setChecked(True)

    def check_for_updates(self):
        try:
            response = requests.get(
                "https://api.github.com/repos/deeffest/DEEF-Lite-Image-Viewer/releases/latest")
            item_version = response.json()["name"]
            item_download = response.json().get("html_url")         

            if item_version != self.version:
                reply = QMessageBox.question(self, self.name,
                                             "A new version is available! Want to download and install?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    webbrowser.open_new_tab(item_download)
                    sys.exit(0)
            else:
                self.statusbar.showMessage("No new versions were found.", 2000)

        except Exception as e:
            self.statusbar.showMessage(f"Update check failed: {e}", 10000)

    def about(self):
        QMessageBox.about(self,
            self.name,
            f"<h3>{self.name}</h3> - is a simple Image Viewer for Windows "
            "tries to stick to the principle: Lightweight, Fast, Open.<br><br>"    
            f"<a href='https://github.com/deeffest/DEEF-Lite-Image-Viewer'>"
            "The source code is available on GitHub</a><br>"
            f"<a href='https://github.com/deeffest/DEEF-Lite-Image-Viewer/issues/new/choose'>"
            "Bug Report</a><br>"
            f"<a href='https://donationalerts.com/r/deeffest'>"
            "Donate</a><br><br>"
            f"Version: {self.version}<br>"
            "Created with ♥ by deeffest, 2023-2024")

    def _init_window(self):
        if self.image_path is None:    
            self.setWindowTitle(self.name)
        self.setWindowIcon(QIcon(f"{self.current_dir}/resources/icons/icon.ico"))
        self.resize(self.settings.value("window_size", self.size()))
        self.center_window()
       
    def center_window(self):    
        desktop = qApp.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def show_context_menu(self, point):
        _init_menu(self, point)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scale_image()

    def eventFilter(self, source, event):
        if source is self.scrollArea and event.type() == QEvent.Resize:
            self.scale_image()
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        self.settings.setValue('window_state', self.saveState())
        self.settings.setValue('window_size', self.size())
        super().closeEvent(event)
