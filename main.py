from core.main_window import Window
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
import os
import sys
from qfluentwidgets import setTheme, setThemeColor, Theme

name = "DEEF Lite Image Viewer"
version = "1.0"
current_dir = os.path.dirname(os.path.abspath(__file__))

supported_formats = [str(fmt, 'utf-8') for fmt in QImageReader.supportedImageFormats()]
filter_ = "Images ({})".format(' '.join('*.' + fmt for fmt in supported_formats))

def is_image_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension[1:] 

    return file_extension in supported_formats

if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = QSettings("deeffest", name)

    current_app_theme = settings.value("current_app_theme", "dark")
    current_app_color_theme = settings.value("current_app_color_theme", "Default")
    current_scene_theme = settings.value("current_scene_theme", "dark")
    current_window_size = settings.value("current_window_size", "true")
    current_check_updates = settings.value("current_check_updates", "true")

    image_path = sys.argv[1] if len(sys.argv) > 1 and is_image_file(sys.argv[1]) else None

    setThemeColor(str(current_app_color_theme))
    setTheme(Theme.DARK if current_app_theme == "dark" else Theme.LIGHT)

    ImgViewer = Window(
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
        image_path
    )
    
    sys.exit(app.exec_())
