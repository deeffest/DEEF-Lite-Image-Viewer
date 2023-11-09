#main_window.py
from qfluentwidgets import (
    MSFluentWindow, SplashScreen, NavigationItemPosition,
    MessageBox
    )
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWidgets import QApplication, QFileDialog
from qfluentwidgets import FluentIcon as FIF
import webbrowser
import sys
import os

from core.image_viewer import ImageViewer
from core.app_settings import AppSettings
from core.web_image_msg_box import WebImageMsgBox
from core.update_checker import UpdateChecker

class Window(MSFluentWindow):
    def __init__(
        self, 
        name, 
        current_dir, 
        current_window_size, 
        current_app_color_theme, 
        current_app_theme, 
        settings, 
        current_scene_theme, 
        filter_, 
        version,
        current_check_updates,
        supported_formats,
        image_path=None, 
        parent=None
        ):
        super().__init__(parent=parent)

        self.app_name = name
        self.current_app_dir = current_dir
        self.current_app_window_size = current_window_size
        self.current_app_color_theme = current_app_color_theme
        self.current_app_theme = current_app_theme
        self.app_settings = settings
        self.current_app_scene_theme = current_scene_theme
        self.image_extensions_filter = filter_
        self.app_version = version
        self.current_app_check_updates = current_check_updates
        self.supported_formats = supported_formats

        self._init_network_manager()
        self._init_window()
        self._init_navigation(image_path=image_path)

    def _init_network_manager(self):
        self.networkManager = QNetworkAccessManager(self)
        self.networkManager.finished.connect(self.handleNetworkData)

    def _init_window(self):        
        self.setWindowTitle(self.app_name)
        self.setWindowIcon(QIcon(
            f"{self.current_app_dir}/resources/icons/icon.ico")
        )
        self.resize(800, 600)
        if self.current_app_window_size == "true":
            self.restoreWindowSize()

        self._init_splash_screen()
        self._move_window_to_center()

        self.show()

    def _move_window_to_center(self):
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def _init_splash_screen(self):
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

    def _init_navigation(self, image_path=None):
        self.homeInterface = ImageViewer(
            self.current_app_scene_theme,
            self.app_name,
            self.supported_formats,
            parent=self
        )
        self.homeInterface.setObjectName('Home')
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')

        self.settingsInterface = AppSettings(
            self.current_app_dir, 
            self.current_app_color_theme, 
            self.app_version, 
            self.current_app_theme, 
            self.current_app_scene_theme, 
            self.current_app_check_updates,
            self.current_app_window_size,
            self.app_settings,
            parent=self
        )
        self.settingsInterface.setObjectName('Settings')
        self.addSubInterface(self.settingsInterface, FIF.SETTING, 'Settings', None, NavigationItemPosition.BOTTOM) 

        self._handle_image_opening(image_path)
        self._delete_splash_screen()

    def _handle_image_opening(self, image_path):
        if image_path is None or not os.path.exists(image_path):
            self.open_image_dialog()
        else:
            self.homeInterface.open_image(image_path)

    def _delete_splash_screen(self):
        self.splashScreen.finish()
        if self.current_app_check_updates == "true":
            self.starter_check_updates(first_update=True)

    def open_image_dialog(self):
        file_dlg = QFileDialog(self)
        file_path, _ = file_dlg.getOpenFileName(
            self, "Open image", "", self.image_extensions_filter
        )
        
        if file_path:
            self.homeInterface.open_image(file_path)

    def starter_check_updates(self, first_update):
        url_version = (
            'https://sites.google.com/view/deeffest-updates/dliviewer'
        )
        url_download = (
            'https://sites.google.com/view/deeffest-updates/dliviewer/dliviewer-url'
        )
        self.update_checker_thread = UpdateChecker(self.app_version, url_version, url_download, parent=self)
        self.update_checker_thread.update_available.connect(self.msg_box_new_update)
        if first_update == False:
            self.update_checker_thread.no_update_found.connect(self.no_update_found_dialog)
        self.update_checker_thread.start()

    def msg_box_new_update(self, item_download):
        self.settingsInterface.PushButton.setEnabled(True)

        update_available_msg = MessageBox(
            f"New update is available!",
            f"A new version of the program has been released! Download and install it soon!\n*You can always disable checking for updates in the settings.",
            self
        )
        update_available_msg.yesButton.setText('Download')
        update_available_msg.cancelButton.setText("Later")

        if update_available_msg.exec():    
            webbrowser.open_new_tab(item_download)
            sys.exit() 

    def no_update_found_dialog(self):
        self.settingsInterface.PushButton.setEnabled(True)
        
        no_update_msg = MessageBox(
            "No updates found",
            "You are already using the latest version of the program.",
            self
        )
        no_update_msg.cancelButton.hide()
        no_update_msg.exec()

    def open_url_action(self):
        custom_msg = WebImageMsgBox(self)
        if custom_msg.exec():
            url = custom_msg.urlLineEdit.text()
            self.networkManager.get(QNetworkRequest(QUrl(url)))

    def handleNetworkData(self, networkReply):
        ioDevice = networkReply.readAll()
        image = QImage()
        image.loadFromData(ioDevice)
        pixmap = QPixmap.fromImage(image)
        self.homeInterface.scene.clear()
        self.homeInterface.scene.addPixmap(pixmap)
        self.homeInterface.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self.homeInterface.resizeEvent()

        url = networkReply.url().toString() 
        self.setWindowTitle(url)
        self.homeInterface.current_image_path = "NoLocal"

    def restoreWindowSize(self):
        window_size = self.app_settings.value("window_size")
        if window_size is not None:
            self.resize(window_size)

    def resizeEvent(self, event):
        self.app_settings.setValue("window_size", self.size())

        return super().resizeEvent(event)