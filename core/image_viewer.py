#image_viewer.py
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QFrame, QShortcut, QApplication,
    QGraphicsPixmapItem
    )
from PyQt5.QtCore import Qt, QSize, QTimer, QRectF
from PyQt5.QtGui import (
    QPainter, QKeySequence, QPixmap, QMovie, QDragEnterEvent, 
    QDropEvent
    )
from qfluentwidgets import (
    TransparentToolButton, RoundMenu, Action, MenuAnimationType,
    InfoBar, InfoBarPosition, MessageBox
    )
from qfluentwidgets import FluentIcon as FIF
import os
import webbrowser
from PIL import Image
from datetime import datetime

class ImageViewer(QGraphicsView):
    def __init__(
        self, 
        current_scene_theme,
        name,
        supported_formats,
        image_path=None, 
        parent=None
        ):
        super().__init__(parent)

        self.window = parent
        self.current_app_scene_theme = current_scene_theme
        self.app_name = name
        self.supported_formats = tuple(supported_formats)

        self._init_attributes()
        self._init_content()
        self._init_shortcut()
        self._init_scene()

    def _init_scene(self):
        if self.current_app_scene_theme == 'dark':
            self.setStyleSheet("background-color: rgb(22,22,22); border-top-left-radius: 8px;")
        else:
            self.setStyleSheet("background-color: rgb(230,230,230); border-top-left-radius: 8px;")
    
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.wheelEvent = self.zoom_wheel_event

    def _init_shortcut(self):
        hotkey01 = QShortcut(QKeySequence("Left"), self) 
        hotkey02 = QShortcut(QKeySequence("Right"), self)     
        hotkey1 = QShortcut(QKeySequence("Ctrl+Q"), self)       
        hotkey2 = QShortcut(QKeySequence("Ctrl+C"), self)
        hotkey3 = QShortcut(QKeySequence("Ctrl+V"), self)
        hotkey4 = QShortcut(QKeySequence("Ctrl+X"), self)
        hotkey5 = QShortcut(QKeySequence("Ctrl+R"), self)
        hotkey6 = QShortcut(QKeySequence("Del"), self)
        hotkey7 = QShortcut(QKeySequence("Ctrl+P"), self)
        hotkey8 = QShortcut(QKeySequence("Ctrl+O"), self)

        hotkey01.activated.connect(self.show_previous_image)
        hotkey02.activated.connect(self.show_next_image)
        hotkey1.activated.connect(self.window.open_image_dialog)
        hotkey2.activated.connect(self.copy)
        hotkey3.activated.connect(self.paste)
        hotkey4.activated.connect(self.cut)
        hotkey5.activated.connect(self.rotate_object)
        hotkey6.activated.connect(self.delete)
        hotkey7.activated.connect(self.properties)
        hotkey8.activated.connect(self.window.open_url_action)

    def _init_content(self):
        self.PrevTransparentToolButton = TransparentToolButton(FIF.LEFT_ARROW, self)
        self.PrevTransparentToolButton.clicked.connect(self.show_previous_image)
        self.PrevTransparentToolButton.setIconSize(QSize(20, 20))

        self.NextTransparentToolButton = TransparentToolButton(FIF.RIGHT_ARROW, self) 
        self.NextTransparentToolButton.clicked.connect(self.show_next_image)
        self.NextTransparentToolButton.setIconSize(QSize(20, 20))

        self.resizeEvent()
        self.update_navigation_buttons()

    def _init_attributes(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setFrameShape(QFrame.NoFrame)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.HighQualityAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.copied_image_path = None
        self.cut_image_path = None
        self.current_image_path = None
        self.rotate_state = 0
        self.movie = None

    def open_image(self, path):
        self.resetTransform()

        if path.lower().endswith('.gif'):
            self.open_gif(path)
        else:
            self.open_static_image(path)

        if self.current_image_path:
            directory = os.path.dirname(self.current_image_path)
            self.image_files = sorted([f for f in os.listdir(directory) if f.lower().endswith(self.supported_formats)], key=lambda f: os.path.getmtime(os.path.join(directory, f)))
        self.update_navigation_buttons()

    def open_gif(self, path):
        self.scene.clear()
        
        self.movie = QMovie(path)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.movie.frameChanged.connect(self.update_gif_frame)

        self.movie.start()

        self.setSceneRect(QRectF(self.scene.itemsBoundingRect()))

        QTimer.singleShot(0, self.resizeEvent)

        self.current_image_path = path
        self.cut_image_path = None

        self.window.setWindowTitle(f"{path} - {self.app_name}")

    def update_gif_frame(self, frame):
        try:
            self.pixmap_item.setPixmap(self.movie.currentPixmap())
        except:
            pass

    def open_static_image(self, path):
        pixmap = QPixmap(path)
        self.scene.clear()
        self.scene.addPixmap(pixmap)

        self.setSceneRect(0, 0, pixmap.width(), pixmap.height())

        QTimer.singleShot(0, self.resizeEvent)

        self.current_image_path = path
        self.cut_image_path = None

        self.window.setWindowTitle(f"{path} - {self.app_name}")

    def _fitInView(self):
        if self.sceneRect().width() > self.width() or self.sceneRect().height() > self.height():  
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event=None):
        new_width = min(132, self.width() * 0.10)  
        new_height = self.window.height()

        self.PrevTransparentToolButton.setFixedSize(int(new_width), int(new_height))
        self.NextTransparentToolButton.setFixedSize(int(new_width), int(new_height))
        
        self.updateButtonPositions()
        self._fitInView()

        super(ImageViewer, self).resizeEvent(event) 
    
    def updateButtonPositions(self):
        self.PrevTransparentToolButton.move(0, self.height() // 2 - self.PrevTransparentToolButton.height() // 2)
        self.NextTransparentToolButton.move(self.width() - self.NextTransparentToolButton.width(), self.height() // 2 - self.NextTransparentToolButton.height() // 2)
    
    def update_navigation_buttons(self):
        self.PrevTransparentToolButton.setEnabled(False)
        self.NextTransparentToolButton.setEnabled(False)

        if self.current_image_path and self.image_files:
            current_index = self.image_files.index(os.path.basename(self.current_image_path))
            self.PrevTransparentToolButton.setEnabled(current_index < len(self.image_files) - 1)
            self.NextTransparentToolButton.setEnabled(current_index > 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.rotate_object()

        super(ImageViewer, self).mousePressEvent(event) 

    def zoom_wheel_event(self, event):
        zoom_in_factor = 1.2
        zoom_out_factor = 1 / zoom_in_factor

        factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        self.scale(factor, factor)

    def contextMenuEvent(self, e):
        menu = RoundMenu(parent=self)

        open_image_action = Action(FIF.PHOTO, 'Quickly Open File...', shortcut="Ctrl+Q")
        open_image_action.triggered.connect(self.window.open_image_dialog)
        menu.addAction(open_image_action)

        open_url_action = Action(FIF.LINK, 'Open File/URL...', shortcut="Ctrl+O")
        open_url_action.triggered.connect(self.window.open_url_action)
        menu.addAction(open_url_action)

        menu.addSeparator()

        copy_action = Action(FIF.COPY, 'Copy', shortcut="Ctrl+C")
        copy_action.triggered.connect(self.copy)
        menu.addAction(copy_action)

        paste_action = Action(FIF.PASTE, 'Paste', shortcut="Ctrl+V")
        paste_action.triggered.connect(self.paste)
        menu.addAction(paste_action)

        cut_action = Action(FIF.CUT, 'Cut', shortcut="Ctrl+X")
        cut_action.triggered.connect(self.cut)
        menu.addAction(cut_action)        

        rotate_action = Action(FIF.ROTATE, 'Rotate', shortcut="Ctrl+R")
        rotate_action.triggered.connect(self.rotate_object)
        menu.addAction(rotate_action)     

        menu.addSeparator()      

        properties_action = Action(FIF.INFO, 'Properties', shortcut="Ctrl+P")
        properties_action.triggered.connect(self.properties)
        menu.addAction(properties_action)          

        delete_action = Action(FIF.DELETE, 'Delete', shortcut="Del")
        delete_action.triggered.connect(self.delete)
        menu.addAction(delete_action) 

        if self.current_image_path is None:
            copy_action.setEnabled(False)
            cut_action.setEnabled(False)
            rotate_action.setEnabled(False)
            delete_action.setEnabled(False)
            properties_action.setEnabled(False)
        if self.is_no_local_image_path(self.current_image_path):
            copy_action.setEnabled(False)
            delete_action.setEnabled(False)
            properties_action.setEnabled(False)

        menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def is_no_local_image_path(self, current_image_path=None):
        if current_image_path is None:
            return False
        return (current_image_path.startswith("https://") or current_image_path.startswith("http://") or current_image_path.startswith("file:") or not os.path.isabs(current_image_path))

    def properties(self):
        if self.current_image_path:
            content = self.image_info(self.current_image_path)
            w = MessageBox(self.current_image_path, content, self.window)
            w.cancelButton.hide()
            w.exec()   

    def image_info(self, image_path):
        directory, file_name = os.path.split(image_path)

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                resolution = f"{width}x{height}" 
                image_format = img.format
        except IOError:
            resolution = "Unknown"
            image_format = "Unknown"

        file_size = os.path.getsize(image_path)
        pretty_size = self.pretty_file_size(file_size)

        modification_time = os.path.getmtime(image_path)
        modification_date = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')

        content = (
            f"Directory: {directory}\n"
            f"File Name: {file_name}\n"
            f"Resolution: {resolution}\n"
            f"File Size: {pretty_size}\n"
            f"Format: {image_format}\n"
            f"Last Modified: {modification_date}\n"
        )
        return content

    def pretty_file_size(self, file_size):
        if file_size < 1024:
            return f"{file_size} bytes"
        elif 1024 <= file_size < (1024 * 1024):
            return f"{round(file_size / 1024, 2)} KB"
        else:
            return f"{round(file_size / (1024 * 1024), 2)} MB"

    def rotate_object(self):
        self.rotate_state = (self.rotate_state + 1) % 4
        if self.rotate_state == 1:
            self.rotate(90)
        elif self.rotate_state == 2:
            self.rotate(90)
        elif self.rotate_state == 3:
            self.rotate(90)
        else:
            self.rotate(90)
        self.resizeEvent()

    def show_previous_image(self):
        if self.current_image_path and self.image_files:
            current_index = self.image_files.index(os.path.basename(self.current_image_path))
            if current_index < len(self.image_files) - 1:
                next_file_path = os.path.join(os.path.dirname(self.current_image_path), self.image_files[current_index + 1])
                self.open_image(next_file_path)

    def show_next_image(self):
        if self.current_image_path and self.image_files:
            current_index = self.image_files.index(os.path.basename(self.current_image_path))
            if current_index > 0:
                previous_file_path = os.path.join(os.path.dirname(self.current_image_path), self.image_files[current_index - 1])
                self.open_image(previous_file_path)

    def delete(self):
        if self.is_no_local_image_path(self.current_image_path):
            return
        elif self.current_image_path:
            title = f'Are you sure you want to delete the image?'''
            content = """If you confirm, the program will completely delete the file with no possibility of recovery."""
            w = MessageBox(title, content, self.window)
            if w.exec():
                try:
                    current_index = self.image_files.index(os.path.basename(self.current_image_path))
                    os.remove(self.current_image_path)
                    self.image_files.pop(current_index)

                    InfoBar.success(
                        title='Success!',
                        content=f'The image has been successfully deleted from your computer.',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM_RIGHT,
                        duration=2000,
                        parent=self
                    )

                    if self.image_files:
                        if current_index > 0:
                            previous_file_path = os.path.join(os.path.dirname(self.current_image_path), self.image_files[current_index - 1])
                            self.open_image(previous_file_path)
                        else:
                            next_file_path = os.path.join(os.path.dirname(self.current_image_path), self.image_files[current_index])
                            self.open_image(next_file_path)
                    else:
                        self.cut()
                        self.window.setWindowTitle(self.app_name)
                        self.window.open_image_dialog()

                except Exception as e:
                    InfoBar.error(
                        title='Fatal error',
                        content=f"{e}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM_RIGHT,
                        duration=-1,
                        parent=self
                    )
        else:
            InfoBar.warning(
                title='Warning',
                content="To delete an image, first open it in DLIViewer.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
        
    def copy(self):
        if self.is_no_local_image_path(self.current_image_path):
            return
        elif self.current_image_path:
            image_to_copy = QPixmap(self.current_image_path)
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(image_to_copy)
            InfoBar.success(
                title='Success!',
                content=f'Image has been successfully copied to the clipboard.',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.warning(
                title='Warning',
                content="To copy an image, first open it in DLIViewer.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )

    def paste(self):
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        image_path = clipboard.text()

        if not pixmap.isNull():
            self.cut()
            self.resetTransform()
            self.scene.addPixmap(pixmap)
            self.setSceneRect(0, 0, pixmap.width(), pixmap.height())
            self.resizeEvent()
            self.window.setWindowTitle(f"{image_path} - {self.app_name}")
            self.current_image_path = image_path
        else:
            if os.path.exists(image_path) and image_path.endswith((supported_formats)):
                self.open_image(image_path)
                self.window.setWindowTitle(f"{image_path} - {self.app_name}")
                self.current_image_path = image_path
            else:
                InfoBar.warning(
                    title='Warning',
                    content="To paste an image, first copy the image or its path on your computer.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self
                )

    def cut(self):
        self.current_image_path = None
        self.scene.clear()
        self.window.setWindowTitle(self.app_name)
        self.update_navigation_buttons()