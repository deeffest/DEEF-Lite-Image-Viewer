import os
import mimetypes
import platform
import ctypes
import webbrowser
import resources.resources_rc
from PySide6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, \
    QLabel, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFileDialog, \
    QInputDialog, QToolBar, QMessageBox, QSizePolicy, QToolButton, \
    QColorDialog
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtCore import QSettings, Qt, QTimer, QUrl, QEvent, QDateTime
from PySide6.QtGui import QIcon, QAction, QPixmap, QImage, QTransform, \
    QImageWriter, QActionGroup
from core.update_checker import UpdateChecker
from packaging import version as pkg_version

class MainWindow(QMainWindow):
    def __init__(self, app, theme, image_path=None, parent=None):
        super().__init__(parent)
        self.app = app
        self.theme = theme
        self.plaform = platform.system()
        self.settings = QSettings()
        self.image_size = None
        self.image_files = []
        self.current_image_index = -1
        self.image = None
        if self.settings.contains("sort_option"):
            self.sort_option = self.settings.value("sort_option")
        else:
            self.sort_option = "Date"
        if self.settings.contains("sort_order"):
            self.sort_order_descending = self.settings.value("sort_order")
        else:
            self.sort_order_descending = True

        self.setWindowTitle("DEEF Lite Image Viewer")
        self.setObjectName("MainWindow")
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.installEventFilter(self)

        if self.plaform == "Windows":
            self.setWindowIcon(QIcon(":/icons/icon_win"))
        else:
            self.setWindowIcon(QIcon(":/icons/icon_linux"))

        if self.settings.contains("geometry") and self.settings.contains("window_state"):
            self.restoreGeometry(self.settings.value("geometry"))
            self.restoreState(self.settings.value("window_state"))
        else:
            self.resize(800, 600)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setMenuBar(self.menu_bar)

        self.file_menu = QMenu("File", self)
        self.menu_bar.addMenu(self.file_menu)

        self.open_file_action = QAction("Open File", self)
        self.open_file_action.setIcon(QIcon(f":/icons/file_{self.theme}"))
        self.open_file_action.setShortcut("Ctrl+O")
        self.open_file_action.triggered.connect(self.open_file_dialog)
        self.file_menu.addAction(self.open_file_action)
        self.addAction(self.open_file_action)

        self.open_url_action = QAction("Open URL", self)
        self.open_url_action.setIcon(QIcon(f":/icons/url_{self.theme}"))
        self.open_url_action.setShortcut("Ctrl+U")
        self.open_url_action.triggered.connect(self.open_url_dialog)
        self.file_menu.addAction(self.open_url_action)
        self.addAction(self.open_url_action)

        self.file_menu.addSeparator()

        self.copy_image_action = QAction("Copy", self)
        self.copy_image_action.setIcon(QIcon(f":/icons/copy_{self.theme}"))
        self.copy_image_action.setShortcut("Ctrl+Shift+C")
        self.copy_image_action.triggered.connect(self.copy_image)
        self.file_menu.addAction(self.copy_image_action)

        self.paste_image_action = QAction("Paste", self)
        self.paste_image_action.setIcon(QIcon(f":/icons/paste_{self.theme}"))
        self.paste_image_action.setShortcut("Ctrl+Shift+V")
        self.paste_image_action.triggered.connect(self.paste_image)
        self.file_menu.addAction(self.paste_image_action)
        self.addAction(self.paste_image_action)

        self.file_menu.addSeparator()

        self.save_as_action = QAction("Save as...", self)
        self.save_as_action.setIcon(QIcon(f":/icons/save_as_{self.theme}"))
        self.save_as_action.setShortcut("Ctrl+S")
        self.save_as_action.triggered.connect(self.save_image_as)
        self.file_menu.addAction(self.save_as_action)
        self.addAction(self.save_as_action)

        self.set_as_wallpaper_action = QAction("Set as wallpaper", self)
        self.set_as_wallpaper_action.setIcon(QIcon(f":/icons/wallpaper_{self.theme}"))
        self.set_as_wallpaper_action.setShortcut("Ctrl+W")
        self.set_as_wallpaper_action.triggered.connect(self.set_as_wallpaper)
        self.file_menu.addAction(self.set_as_wallpaper_action)
        self.addAction(self.set_as_wallpaper_action)

        self.file_menu.addSeparator()

        self.properties_action = QAction("Properties", self)
        self.properties_action.setIcon(QIcon(f":/icons/properties_{self.theme}"))
        self.properties_action.setShortcut("Ctrl+P")
        self.properties_action.triggered.connect(self.show_properties)
        self.file_menu.addAction(self.properties_action)
        self.addAction(self.properties_action)

        self.file_menu.addSeparator()

        self.quit_action = QAction("Quit", self)
        self.quit_action.setIcon(QIcon(f":/icons/quit_{self.theme}"))
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.quit_action)
        self.addAction(self.quit_action)

        self.view_menu = QMenu("View", self)
        self.menu_bar.addMenu(self.view_menu)

        self.full_screen_action = QAction("Full screen", self)
        self.full_screen_action.setIcon(QIcon(f":/icons/full_screen_{self.theme}"))
        self.full_screen_action.setShortcut("F11")
        self.full_screen_action.triggered.connect(self.toggle_full_screen)
        self.view_menu.addAction(self.full_screen_action)
        self.addAction(self.full_screen_action)

        self.view_menu.addSeparator()

        self.zoom_in_action = QAction("Zoom in", self)
        self.zoom_in_action.setIcon(QIcon(f":/icons/zoom_in_disabled"))
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.setEnabled(False)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.view_menu.addAction(self.zoom_in_action)
        self.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction("Zoom out", self)
        self.zoom_out_action.setIcon(QIcon(f":/icons/zoom_out_disabled"))
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.setEnabled(False)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.view_menu.addAction(self.zoom_out_action)
        self.addAction(self.zoom_out_action)

        self.rotate_image_action = QAction("Rotate", self)
        self.rotate_image_action.setIcon(QIcon(f":/icons/rotate_{self.theme}"))
        self.rotate_image_action.setShortcut("Ctrl+R")
        self.rotate_image_action.triggered.connect(self.rotate_image)
        self.view_menu.addAction(self.rotate_image_action)
        self.addAction(self.rotate_image_action)

        self.view_menu.addSeparator()

        self.scene_color_menu = QMenu("Scene color", self)
        self.scene_color_menu.setIcon(QIcon(f":/icons/color_{self.theme}"))
        self.view_menu.addMenu(self.scene_color_menu)

        self.white_scene_color_action = QAction("White", self)
        self.white_scene_color_action.setIcon(QIcon(f":/icons/white_{self.theme}"))
        self.white_scene_color_action.triggered.connect(self.set_white_scene_color)
        self.scene_color_menu.addAction(self.white_scene_color_action)
        self.addAction(self.white_scene_color_action)

        self.black_scene_color_action = QAction("Black", self)
        self.black_scene_color_action.setIcon(QIcon(f":/icons/black_{self.theme}"))
        self.black_scene_color_action.triggered.connect(self.set_black_scene_color)
        self.scene_color_menu.addAction(self.black_scene_color_action)
        self.addAction(self.black_scene_color_action)

        self.default_scene_color_action = QAction("Default", self)
        self.default_scene_color_action.setIcon(QIcon(f":/icons/clear_filters_{self.theme}"))
        self.default_scene_color_action.triggered.connect(self.set_default_scene_color)
        self.scene_color_menu.addAction(self.default_scene_color_action)
        self.addAction(self.default_scene_color_action)

        self.scene_color_menu.addSeparator()

        self.pick_scene_color_action = QAction("Pick color", self)
        self.pick_scene_color_action.setIcon(QIcon(f":/icons/color_dropper_{self.theme}"))
        self.pick_scene_color_action.triggered.connect(self.pick_scene_color)
        self.scene_color_menu.addAction(self.pick_scene_color_action)

        self.clear_scene_action = QAction("Clear scene", self)
        self.clear_scene_action.setIcon(QIcon(f":/icons/clear_{self.theme}"))
        self.clear_scene_action.setShortcut("Ctrl+C")
        self.clear_scene_action.triggered.connect(self.clear_scene)
        self.view_menu.addAction(self.clear_scene_action)
        self.addAction(self.clear_scene_action)

        self.navigation_menu = QMenu("Navigation", self)
        self.menu_bar.addMenu(self.navigation_menu)

        self.previous_action = QAction("Previous", self)
        self.previous_action.setIcon(QIcon(f":/icons/previous_{self.theme}"))
        self.previous_action.setShortcut("Left")
        self.previous_action.triggered.connect(self.previous_image)
        self.navigation_menu.addAction(self.previous_action)
        self.addAction(self.previous_action)

        self.next_action = QAction("Next", self)
        self.next_action.setIcon(QIcon(f":/icons/next_{self.theme}"))
        self.next_action.setShortcut("Right")
        self.next_action.triggered.connect(self.next_image)
        self.navigation_menu.addAction(self.next_action)
        self.addAction(self.next_action)

        self.navigation_menu.addSeparator()

        self.sort_by_menu = QMenu("Sort by...", self)
        self.sort_by_menu.setIcon(QIcon(f":/icons/sort_by_{self.theme}"))
        self.navigation_menu.addMenu(self.sort_by_menu)

        self.sort_by_date_action = QAction("Date", self)
        self.sort_by_date_action.setCheckable(True)
        self.sort_by_date_action.triggered.connect(lambda: self.set_sort_option("Date"))

        self.sort_by_name_action = QAction("Name", self)
        self.sort_by_name_action.setCheckable(True)
        self.sort_by_name_action.triggered.connect(lambda: self.set_sort_option("Name"))

        self.sort_by_type_action = QAction("Type", self)
        self.sort_by_type_action.setCheckable(True)
        self.sort_by_type_action.triggered.connect(lambda: self.set_sort_option("Type"))

        self.sort_by_size_action = QAction("Size", self)
        self.sort_by_size_action.setCheckable(True)
        self.sort_by_size_action.triggered.connect(lambda: self.set_sort_option("Size"))

        if self.sort_option == "Date":
            self.sort_by_date_action.setChecked(True)
        elif self.sort_option == "Name":
            self.sort_by_name_action.setChecked(True)
        elif self.sort_option == "Type":
            self.sort_by_type_action.setChecked(True)
        elif self.sort_option == "Size":
            self.sort_by_size_action.setChecked(True)

        self.sort_ascending_action = QAction("Ascending", self)
        self.sort_ascending_action.setCheckable(True)
        self.sort_ascending_action.triggered.connect(lambda: self.set_sort_order(False))

        self.sort_descending_action = QAction("Descending", self)
        self.sort_descending_action.setCheckable(True)
        self.sort_descending_action.triggered.connect(lambda: self.set_sort_order(True))

        if self.sort_order_descending:
            self.sort_descending_action.setChecked(True)
            self.sort_ascending_action.setChecked(False)
        else:
            self.sort_ascending_action.setChecked(True)
            self.sort_descending_action.setChecked(False)

        self.sort_group = QActionGroup(self)
        self.sort_group.addAction(self.sort_by_date_action)
        self.sort_group.addAction(self.sort_by_name_action)
        self.sort_group.addAction(self.sort_by_type_action)
        self.sort_group.addAction(self.sort_by_size_action)

        self.order_group = QActionGroup(self)
        self.order_group.addAction(self.sort_ascending_action)
        self.order_group.addAction(self.sort_descending_action)

        self.sort_by_menu.addAction(self.sort_by_date_action)
        self.sort_by_menu.addAction(self.sort_by_name_action)
        self.sort_by_menu.addAction(self.sort_by_type_action)
        self.sort_by_menu.addAction(self.sort_by_size_action)
        self.sort_by_menu.addSeparator()
        self.sort_by_menu.addAction(self.sort_ascending_action)
        self.sort_by_menu.addAction(self.sort_descending_action)

        self.help_menu = QMenu("Help", self)
        self.menu_bar.addMenu(self.help_menu)

        self.search_for_updates_action = QAction("Search for Updates", self)
        self.search_for_updates_action.setIcon(QIcon(f":/icons/search_{self.theme}"))
        self.search_for_updates_action.triggered.connect(lambda: self.check_updates(manual_check=True))
        self.help_menu.addAction(self.search_for_updates_action)

        self.help_menu.addSeparator()

        self.about_action = QAction("About", self)
        self.about_action.setIcon(QIcon(f":/icons/about_{self.theme}"))
        self.about_action.triggered.connect(self.about)
        self.help_menu.addAction(self.about_action)

        self.about_qt_action = QAction("About Qt", self)
        self.about_qt_action.setIcon(QIcon(f":/qt-project.org/logos/pysidelogo.png"))
        self.about_qt_action.triggered.connect(self.app.aboutQt)
        self.help_menu.addAction(self.about_qt_action)

        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.horizontal_layout = QHBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        saved_color = self.settings.value("scene_color")
        if saved_color:
            self.scroll_area.setStyleSheet(f"background-color: {saved_color};")

        self.scroll_area_widget = QWidget()
        self.scroll_area_widget.setGeometry(0, 0, 0, 0)

        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)

        self.image_viewer = QLabel()
        self.image_viewer.setScaledContents(False)
        self.image_viewer.setAlignment(Qt.AlignCenter)

        self.scroll_area_layout.addWidget(self.image_viewer)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.horizontal_layout.addWidget(self.scroll_area)
        self.central_layout.addLayout(self.horizontal_layout)
        self.setCentralWidget(self.central_widget)
        self.centralWidget().setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tool_bar = QToolBar(self)
        self.tool_bar.setObjectName("tool_bar")
        self.tool_bar.setFloatable(False)
        self.tool_bar.setMovable(False)
        self.tool_bar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.BottomToolBarArea, self.tool_bar)

        self.tool_bar.addAction(self.open_file_action)
        self.tool_bar.addAction(self.open_url_action)
        self.tool_bar.addAction(self.save_as_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.previous_action)
        self.tool_bar.addAction(self.next_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.zoom_in_action)
        self.tool_bar.addAction(self.zoom_out_action)
        self.tool_bar.addAction(self.rotate_image_action)
        self.tool_bar.addSeparator()
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tool_bar.addWidget(spacer)
        self.tool_bar.addAction(self.copy_image_action)
        self.tool_bar.addAction(self.paste_image_action)
        self.tool_bar.addSeparator()
        tool_button = QToolButton(self)
        tool_button.setIcon(QIcon(f":/icons/color_{self.theme}"))
        tool_button.setToolTip("Scene color")
        tool_button.setPopupMode(QToolButton.InstantPopup)
        tool_button.setMenu(self.scene_color_menu)
        self.tool_bar.addWidget(tool_button)
        self.tool_bar.addAction(self.full_screen_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.clear_scene_action)

        self.context_menu = QMenu(self)
        self.context_menu.addMenu(self.file_menu)
        self.context_menu.addMenu(self.view_menu)
        self.context_menu.addMenu(self.navigation_menu)
        self.context_menu.addMenu(self.help_menu)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.full_screen_action)
        self.context_menu.addAction(self.quit_action)

        self.full_context_menu = QMenu(self)

        self.full_context_menu.addAction(self.open_file_action)
        self.full_context_menu.addAction(self.open_url_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addAction(self.copy_image_action)
        self.full_context_menu.addAction(self.paste_image_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addAction(self.save_as_action)
        self.full_context_menu.addAction(self.set_as_wallpaper_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addAction(self.previous_action)
        self.full_context_menu.addAction(self.next_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addAction(self.zoom_in_action)
        self.full_context_menu.addAction(self.zoom_out_action)
        self.full_context_menu.addAction(self.rotate_image_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addMenu(self.sort_by_menu)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addMenu(self.scene_color_menu)
        self.full_context_menu.addAction(self.clear_scene_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addAction(self.full_screen_action)
        self.full_context_menu.addSeparator()

        self.full_context_menu.addAction(self.properties_action)
        self.full_context_menu.addAction(self.quit_action)

        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_network_data)

        if image_path is not None and (self.is_valid_mime_type(image_path) or self.is_valid_url(image_path)):
            self.load_image(image_path)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        if self.isFullScreen():
            self.full_mode()

        self.check_updates(manual_check=False)

    def is_valid_mime_type(self, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith('image/')

    def is_valid_url(self, url):
        return url.lower().startswith(('http://', 'https://'))

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            if self.is_valid_mime_type(selected_file):
                self.load_image(selected_file)
            else:
                self.status_bar.showMessage("Invalid file type", 3000)

    def open_url_dialog(self):
        url_dialog = QInputDialog(self)
        url_dialog.setWindowTitle("Open URL")
        url_dialog.setLabelText("Enter URL:")
        url_dialog.resize(500, 100)
        if url_dialog.exec() == QInputDialog.Accepted:
            url = url_dialog.textValue()
            if url and self.is_valid_url(url):
                self.load_image(url)
            else:
                self.status_bar.showMessage("Invalid URL", 3000)

    def normalize_path(self, path):
        return path.replace('\\', '/')
    
    def set_sort_order(self, descending):
        self.sort_order_descending = descending
    
    def set_sort_option(self, option):
        self.sort_option = option
        self.status_bar.showMessage(f"Sort by {option}", 3000)

    def get_files_in_folder(self, folder_path):
        files = []
        folder_path = self.normalize_path(os.path.normpath(folder_path))

        with os.scandir(folder_path) as entries:
            entries = [entry for entry in entries if entry.is_file()]

            if self.sort_option == "Date":
                entries.sort(key=lambda e: e.stat().st_mtime, reverse=self.sort_order_descending)
            elif self.sort_option == "Name":
                entries.sort(key=lambda e: e.name.lower(), reverse=self.sort_order_descending)
            elif self.sort_option == "Type":
                entries.sort(key=lambda e: os.path.splitext(e.name)[1], reverse=self.sort_order_descending)
            elif self.sort_option == "Size":
                entries.sort(key=lambda e: e.stat().st_size, reverse=self.sort_order_descending)

            for entry in entries:
                file_path = self.normalize_path(os.path.normpath(entry.path))
                if self.is_valid_mime_type(file_path):
                    files.append(file_path)

        return files

    def load_image(self, source):
        source = self.normalize_path(source)
        self.setWindowTitle(f"DEEF Lite Image Viewer - {source}")
        self.image_viewer.clear()
        
        if self.is_valid_url(source):
            self.image_files = []
            self.current_image_index = -1
            self.network_manager.get(QNetworkRequest(QUrl(source)))
        else:
            folder = os.path.dirname(source)
            self.image_files = self.get_files_in_folder(folder)
            self.current_image_index = self.image_files.index(source)
            image = QImage(source)
            self.display_image(image)

    def handle_network_data(self, reply):
        data = reply.readAll()
        image = QImage()
        image.loadFromData(data)
        self.display_image(image)
        reply.deleteLater()

    def display_image(self, image):
        self.image = QPixmap.fromImage(image)
        self.image_viewer.setPixmap(self.image)
        self.image_size = self.image.size()
        QTimer.singleShot(0, self.fit_in_view)

    def fit_in_view(self):
        if self.image_size is not None and self.image is not None:
            if self.image_size.width() > self.scroll_area.width() or self.image_size.height() > self.scroll_area.height():
                self.image_viewer.setPixmap(self.image.scaled(self.scroll_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_viewer.setPixmap(self.image)

    def resizeEvent(self, event):
        self.fit_in_view()
        return super().resizeEvent(event)
    
    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
            self.normal_mode()
        else:
            self.showFullScreen()
            self.full_mode()

    def normal_mode(self):
        self.menu_bar.show()
        self.tool_bar.show()
        self.status_bar.show()
        self.fit_in_view()

        self.full_screen_action.setText("Full Screen")
        self.full_screen_action.setIcon(QIcon(f":/icons/full_screen_{self.theme}"))

    def full_mode(self):
        self.menu_bar.hide()
        self.tool_bar.hide()
        self.status_bar.hide()
        QTimer.singleShot(0, self.fit_in_view)
    
        self.full_screen_action.setText("Exit Full Screen")
        self.full_screen_action.setIcon(QIcon(f":/icons/close_full_screen_{self.theme}"))

    def rotate_image(self):
        if self.image_size:
            transform = QTransform().rotate(90)
            rotated_image = self.image.transformed(transform, Qt.SmoothTransformation)
            self.image = rotated_image
            self.image_viewer.setPixmap(self.image)
            self.image_size = self.image.size()
            self.fit_in_view()
        else:
            self.status_bar.showMessage("No image to rotate.", 3000)
    
    def set_white_scene_color(self):
        color = "white"
        self.settings.setValue("scene_color", color)
        self.scroll_area.setStyleSheet(f"background-color: {color};")
        self.status_bar.showMessage("Scene color set to white.", 3000)

    def set_black_scene_color(self):
        color = "black"
        self.settings.setValue("scene_color", color)
        self.scroll_area.setStyleSheet(f"background-color: {color};")
        self.status_bar.showMessage("Scene color set to black.", 3000)

    def pick_scene_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            color = color.name()
            self.settings.setValue("scene_color", color)
            self.scroll_area.setStyleSheet(f"background-color: {color};")
            self.status_bar.showMessage(f"Scene color set to {color}.", 3000)
        else:
            self.status_bar.showMessage("No valid color selected.", 3000)

    def set_default_scene_color(self):
        self.settings.remove("scene_color")
        self.scroll_area.setStyleSheet("")
        self.status_bar.showMessage("Scene color reset to default.", 3000)

    def clear_scene(self):
        self.image = None
        self.image_size = None
        self.image_viewer.clear()
        self.image_files = []
        self.current_image_index = -1
        self.setWindowTitle("DEEF Lite Image Viewer")
        self.status_bar.showMessage("Scene cleared successfully.", 3000)

    def copy_image(self):
        if self.image is not None:
            clipboard = self.app.clipboard()
            clipboard.setPixmap(self.image)
            self.status_bar.showMessage("Image copied to clipboard.", 3000)
        else:
            self.status_bar.showMessage("No image to copy.", 3000)

    def paste_image(self):
        clipboard = self.app.clipboard()
        pasted_image = clipboard.image()
        if not pasted_image.isNull():
            self.clear_scene()
            self.image = QPixmap.fromImage(pasted_image)
            self.display_image(pasted_image)
            self.status_bar.showMessage("Image pasted successfully.", 3000)
        else:
            self.status_bar.showMessage("No valid image found on the clipboard.", 3000)

    def save_image_as(self):
        if self.image is None:
            self.status_bar.showMessage("No image is currently displayed to save.", 3000)
            return

        default_filename = "untitled.png"
        if hasattr(self, 'image_source_url') and self.image_source_url:
            parsed_url = QUrl(self.image_source_url)
            file_name = os.path.basename(parsed_url.path())
            if not file_name:
                file_name = default_filename
            else:
                file_name = os.path.splitext(file_name)[0]
                default_filename = f"{file_name}.png"

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilters([
            "Images (*.bmp *.cur *.icns *.ico *.jpeg *.jpg *.pbm *.pgm *.png *.ppm *.tif *.tiff *.wbmp *.webp *.xbm *.xpm)", 
            "All Files (*)"])
        file_dialog.setDefaultSuffix("png")
        file_dialog.selectFile(default_filename)

        if file_dialog.exec():
            save_path = file_dialog.selectedFiles()[0]

            image_writer = QImageWriter(save_path)
            if not image_writer.write(self.image.toImage()):
                self.status_bar.showMessage(f"Failed to save image: {image_writer.errorString()}", 3000)
            else:
                self.status_bar.showMessage("The image has been saved successfully.", 3000)

    def set_as_wallpaper(self):
        if self.image_files:
            if self.plaform == "Windows":
                msg_box = QMessageBox.question(self, 'Confirmation', 
                                               'Are you sure you want to set this image as wallpaper?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if msg_box == QMessageBox.Yes:
                    image_path = self.image_files[self.current_image_index]
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)
                    self.status_bar.showMessage("Wallpaper set successfully.", 3000)
            else:
                self.status_bar.showMessage("Setting wallpaper is only supported on Windows.", 3000)
        else:
            self.status_bar.showMessage("The image is missing or not local.", 3000)

    def show_properties(self):
        if not self.image_files:
            self.status_bar.showMessage("The image is missing or not local.", 3000)
            return

        image_path = self.image_files[self.current_image_index]

        image = QImage(image_path)
        image_size = image.size()
        image_width = image_size.width()
        image_height = image_size.height()
        image_format = image.format()
        color_depth = image.depth()

        file_size = os.path.getsize(image_path)
        if file_size < 1024:
            file_size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            file_size_str = f"{file_size / 1024:.2f} KB"
        else:
            file_size_str = f"{file_size / (1024 * 1024):.2f} MB"

        last_modified_timestamp = int(os.path.getmtime(image_path))
        last_modified = QDateTime.fromSecsSinceEpoch(last_modified_timestamp).toString("yyyy-MM-dd HH:mm:ss")

        properties_html = f"""
        <html>
            <body>
                <h3>Image Properties</h3>
                <p><b>File:</b> {image_path}</p>
                <p><b>Size:</b> {image_width} x {image_height} pixels</p>
                <p><b>File Size:</b> {file_size_str}</p>
                <p><b>Format:</b> {image_format}</p>
                <p><b>Color Depth:</b> {color_depth} bits</p>
                <p><b>Last Modified:</b> {last_modified}</p>
            </body>
        </html>
        """

        QMessageBox.information(self, "Image Properties", properties_html)

    def zoom_in(self):
        # not realized
        pass

    def zoom_out(self):
        # not realized
        pass

    def previous_image(self):
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image(self.image_files[self.current_image_index])
        else:
            self.status_bar.showMessage("This is the first image.", 3000)

    def next_image(self):
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image(self.image_files[self.current_image_index])
        else:
            self.status_bar.showMessage("This is the last image.", 3000)

    def check_updates(self, manual_check=False):
        self.search_for_updates_action.setEnabled(False)

        self.update_checker = UpdateChecker(manual_check)
        self.update_checker.update_checked.connect(self.handle_update_checked)
        self.update_checker.update_checked_failed.connect(self.handle_update_checked_failed)
        self.update_checker.start()
        
    def handle_update_checked(self, version, download, manual_check):
        self.search_for_updates_action.setEnabled(True)

        current_version = pkg_version.parse(self.app.applicationVersion())
        latest_version = pkg_version.parse(version)

        if current_version < latest_version:
            msg_box = QMessageBox.question(
                self,
                "Update Available",
                f"A new version {version} is available. Do you want to download it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if msg_box == QMessageBox.Yes:
                webbrowser.open_new_tab(download)
                self.close()
        elif manual_check:
            QMessageBox.information(
                self,
                "No Updates",
                f"You are using the latest version ({self.app.applicationVersion()})."
            )

    def handle_update_checked_failed(self, error, manual_check):
        self.search_for_updates_action.setEnabled(True)
        if manual_check:
            QMessageBox.critical(self, "Update Check Failed", f"Failed to check for updates: {error}")

    def about(self):
        description = (f"<h3>DEEF Lite Image Viewer</h3>"
            "It is a simple, lightweight and open source cross-platform image viewer based on Qt (PySide6).<br><br>"    
            f"{self.app.applicationVersion()}<br>"
            "Created with ♥ by deeffest, 2023-2024")
        QMessageBox.about(self, "About", description)

    def contextMenuEvent(self, event):
        if self.isFullScreen():
            self.full_context_menu.exec(event.globalPos())
        else:
            self.context_menu.exec(event.globalPos())
        return True
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                if self.isFullScreen():
                    self.toggle_full_screen()
                return True
        return super().eventFilter(obj, event)

    def save_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        self.settings.setValue("sort_option", self.sort_option)
        self.settings.setValue("sort_order", self.sort_order_descending)
        self.settings.sync()

    def closeEvent(self, event):
        self.save_settings()
        return super().closeEvent(event)