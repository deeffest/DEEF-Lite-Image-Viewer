import webbrowser
import requests
import mimetypes
import os
import sys
import ctypes
import qtawesome as qta

from PyQt5.QtWidgets import qApp, QMainWindow, QFileDialog, QMessageBox, \
    QListWidgetItem, QWidgetAction, QWidget
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTransform
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from PyQt5 import uic

from core._init_attributes import _init_attributes
from core._init_content import _init_content
from core._init_connect import _init_connect
from core._init_shortcuts import _init_shortcuts
from core._init_icons import _init_icons
from core._init_styles import _init_styles
from core._init_menu import _init_menu
from core.settings_dialog import SettingsDialog

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
        _init_icons(self)
        _init_styles(self)

        self._init_window()

        if self.settings.value("check_for_updates_at_startup", "true") == "true":
            self.check_for_updates(is_startup=True)

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
        self.statusbar.showMessage(self.image_path)
        
        self.load_image()

        if not from_list:
            self.update_folder_contents()
        self.select_current_image()
        self.enable_ui()
        self.update_navigation_actions()

    def load_image(self):
        image = QImage(self.image_path)
        self.image = QPixmap.fromImage(image)
        self.image_viewer.setPixmap(self.image)
        self.image_size = self.image.size()
        self.scale_image()

    def rotate_image(self):
        if hasattr(self, "image"):
            self.image = self.image.transformed(QTransform().rotate(90))
            self.image_size = self.image.size()
            self.scale_image()

    def scale_image(self):
        if hasattr(self, "image_size") and self.image_size:
            if self.image_size.width() > self.scrollArea.width() or self.image_size.height() > self.scrollArea.height():
                self.image_viewer.setPixmap(self.image.scaled(self.scrollArea.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_viewer.setPixmap(self.image)

            self.update_zoom_label()

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def update_zoom_label(self):
        if hasattr(self, "image_size") and self.image_size:
            scroll_width = self.scrollArea.width()
            scroll_height = self.scrollArea.height()
            image_width = self.image_size.width()
            image_height = self.image_size.height()

            scale_percent_width = (scroll_width / image_width) * 100
            scale_percent_height = (scroll_height / image_height) * 100
            scale_percent = min(scale_percent_width, scale_percent_height)

            if scale_percent > 100:
                scale_percent = 100

            self.zoom_label.setText(f"Zoom: {scale_percent:.2f}%")

            if scale_percent < 100:
                self.image_viewer.setPixmap(self.image.scaled(self.scrollArea.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_viewer.setPixmap(self.image)

    def update_folder_contents(self):
        directory = os.path.dirname(self.image_path)
        image_files = [f for f in os.listdir(directory) if self.is_image_file(os.path.join(directory, f))]
        sorted_image_files = sorted(image_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)

        self.folder_contents_widget.listWidget.clear()

        for image_file in sorted_image_files:
            item = QListWidgetItem(image_file)
            item.setToolTip(image_file)
            self.folder_contents_widget.listWidget.addItem(item)

    def on_list_item_double_clicked(self, item):
        if isinstance(item, QListWidgetItem):
            image_file = item.text()
            image_path = os.path.join(os.path.dirname(self.image_path), image_file)
            if os.path.exists(image_path):
                self.open_image(image_path, from_list=True)

    def select_current_image(self):
        current_image = os.path.basename(self.image_path)
        items = self.folder_contents_widget.listWidget.findItems(current_image, Qt.MatchExactly)
        for i in range(self.folder_contents_widget.listWidget.count()):
            self.folder_contents_widget.listWidget.item(i).setForeground(Qt.white if self.settings.value("app_theme", "dark") == "dark" else Qt.black)

        if items:
            item = items[0]
            item.setSelected(True)
            item.setForeground(Qt.red)

    def create_folder_contents_menu(self):
        self.folder_contents_widget = QWidget()
        uic.loadUi(f'{self.current_dir}/core/ui/folder_contents_frame.ui', self.folder_contents_widget)

        widgetAction = QWidgetAction(self.menuFolder_Contents)
        widgetAction.setDefaultWidget(self.folder_contents_widget)
        self.folder_contents_widget.listWidget.itemDoubleClicked.connect(self.on_list_item_double_clicked)

        if self.menuFolder_Contents.actions():
            firstAction = self.menuFolder_Contents.actions()[0]
            self.menuFolder_Contents.insertAction(firstAction, widgetAction)    
            
    def filter_list_items(self):
        text = self.folder_contents_widget.lineEdit.text().strip().lower()
        for i in range(self.folder_contents_widget.listWidget.count()):
            item = self.folder_contents_widget.listWidget.item(i)
            if text and text not in item.text().lower():
                item.setHidden(True)
            else:
                item.setHidden(False)

    def enable_ui(self):
        self.actionPrevious.setEnabled(True)
        self.actionNext.setEnabled(True)
        self.menuSet_As.setEnabled(True)
        self.actionRotate.setEnabled(True)
        self.menuFolder_Contents.setEnabled(True)
        self.actionSlide_Show.setEnabled(True)

    def previous(self):
        current_image_index = self.get_current_image_index()
        if current_image_index > 0:
            previous_image_file = self.folder_contents_widget.listWidget.item(current_image_index - 1).text()
            previous_image_path = os.path.join(os.path.dirname(self.image_path), previous_image_file)
            if os.path.exists(previous_image_path):
                self.open_image(previous_image_path, from_list=True)

    def next(self):
        current_image_index = self.get_current_image_index()
        if current_image_index < self.folder_contents_widget.listWidget.count() - 1:
            next_image_file = self.folder_contents_widget.listWidget.item(current_image_index + 1).text()
            next_image_path = os.path.join(os.path.dirname(self.image_path), next_image_file)
            if os.path.exists(next_image_path):
                self.open_image(next_image_path, from_list=True)

    def get_current_image_index(self):
        current_image = os.path.basename(self.image_path)
        for i in range(self.folder_contents_widget.listWidget.count()):
            if self.folder_contents_widget.listWidget.item(i).text() == current_image:
                return i
        return -1

    def update_navigation_actions(self):
        current_image_index = self.get_current_image_index()
        self.actionPrevious.setEnabled(current_image_index > 0)
        self.actionNext.setEnabled(current_image_index < self.folder_contents_widget.listWidget.count() - 1)

    def toggle_dark_theme(self):
        if self.actionDark_Theme.isChecked():
            self.settings.setValue("app_theme", "dark")
        else:
            self.settings.setValue("app_theme", "light")

    def open_settings(self):
        Dlg = SettingsDialog(self)
        Dlg.exec()

    def full_screen(self):
        if self.windowState() & Qt.WindowFullScreen:
            self.menubar.show()
            self.show_toolbar()
            self.showNormal()
            self.actionFull_Screen.setChecked(False)
            self.actionFull_Screen.setIcon(qta.icon('ei.resize-full'))
        else:
            self.menubar.hide()
            self.hide_toolbar()
            self.setWindowState(Qt.WindowFullScreen)
            self.actionFull_Screen.setChecked(True)
            self.actionFull_Screen.setIcon(qta.icon('ei.resize-small'))

    def slide_show(self):
        if self.actionSlide_Show.isChecked() == False:
            self.actionSlide_Show.setChecked(False)
            self.actionSlide_Show.setIcon(qta.icon('ri.slideshow-2-line'))
            self.stop_slide_show()
        else:
            self.actionSlide_Show.setChecked(True)
            self.actionSlide_Show.setIcon(qta.icon('ri.slideshow-2-fill'))
            self.start_slide_show()

    def slide_show_shortcut(self, checked):
        if checked == True:
            self.actionSlide_Show.setChecked(False)
            self.actionSlide_Show.setIcon(qta.icon('ri.slideshow-2-line'))
            self.stop_slide_show()
        else:
            self.actionSlide_Show.setChecked(True)
            self.actionSlide_Show.setIcon(qta.icon('ri.slideshow-2-fill'))
            self.start_slide_show()

    def start_slide_show(self):
        self.slide_show_timer = QTimer(self)
        self.slide_show_timer.timeout.connect(self.next) 
        self.slide_show_timer.start(3000)

    def stop_slide_show(self):
        self.slide_show_timer.stop()

    def set_wallpaper(self):
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to set this image as wallpaper?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            wallpaper = bytes(self.image_path, 'utf-8')
            ctypes.windll.user32.SystemParametersInfoA(20, 0, wallpaper, 3)
    
    def set_timer(self):
        self.mouse_timer = QTimer(self)
        self.mouse_timer.setInterval(3000)
        self.mouse_timer.timeout.connect(self.hide_elements)

        self.image_viewer.setMouseTracking(True)  

    def hide_elements(self):
        self.setCursor(Qt.BlankCursor)

    def show_elements(self):
        self.setCursor(Qt.ArrowCursor)  

    def hide_toolbar(self):
        if self.isFullScreen():
            self.toolBar.hide()
            self.statusbar.hide()
            self.scale_image()

    def show_toolbar(self):
        if self.isFullScreen():
            self.toolBar.show()
            self.statusbar.show()
            self.scale_image()

    def eventFilter(self, obj, event):
        if obj == self.image_viewer:
            if event.type() == QEvent.Enter:
                self.mouse_timer.start()
            elif event.type() == QEvent.Leave:
                self.mouse_timer.stop()
                self.show_elements()
            elif event.type() == QEvent.MouseMove:
                self.mouse_timer.stop()
                
                hot_zone_height = 60
                if self.isFullScreen():
                    window_height = self.height()
                    
                    if event.y() > window_height - hot_zone_height:
                        self.show_toolbar()
                    else:
                        self.hide_toolbar()

                self.show_elements()

                self.mouse_timer.start()
        return super().eventFilter(obj, event)

    def check_for_updates(self, is_startup=None):
        try:
            response = requests.get(
                "https://api.github.com/repos/deeffest/DEEF-Lite-Image-Viewer/releases/latest")
            item_version = response.json()["name"]
            item_download = response.json().get("html_url")         

            if item_version != self.version:
                reply = QMessageBox.question(self, "Update Checker",
                                             "A new update has been found! Want to download and install?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    webbrowser.open_new_tab(item_download)
                    sys.exit(0)
            else:
                if not is_startup:
                    QMessageBox.information(self, "Update Checker", "No new updates were found.")

        except Exception as e:
            QMessageBox.critical(self, "Update Checker", f"Update search error: {e}")

    def about(self):
        QMessageBox.about(self,
            f"About {self.name}",
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
        if self.settings.value("save_last_window_size", "true") == "true":
            size = self.settings.value("last_window_size", QSize(800,600))
        else:
            size = QSize(800,600)
        self.resize(size)
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
    
    def exit_app(self):
        sys.exit(0)

    def closeEvent(self, event):
        self.settings.setValue('last_window_size', self.size())
        self.exit_app()