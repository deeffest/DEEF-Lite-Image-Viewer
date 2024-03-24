from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPalette, QColor
import os
import sys

from core.main_window import MainWindow

name = "DEEF Lite Image Viewer"
version = "2.0"
current_dir = os.path.dirname(os.path.abspath(__file__))

def set_app_palette():
    app_palette = QPalette()

    if app_theme == "dark":
        app_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        app_palette.setColor(QPalette.WindowText, Qt.white)
        app_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        app_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        app_palette.setColor(QPalette.Text, Qt.white)
        app_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        app_palette.setColor(QPalette.ButtonText, Qt.white)
        app_palette.setColor(QPalette.BrightText, Qt.red)
        app_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        app_palette.setColor(QPalette.Highlight, QColor(42, 183, 66))
        app_palette.setColor(QPalette.HighlightedText, Qt.white)
        app_palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
        app_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
        app_palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
        app_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
        app_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))
    else:
        app_palette = QPalette()
        app_palette.setColor(QPalette.Highlight, QColor(109, 215, 123))
        app_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(app_palette)

if __name__ == '__main__':    
    settings = QSettings("deeffest", name)
    app_theme = settings.value("app_theme")  

    app = QApplication(sys.argv + (['-platform', 'windows:darkmode=1'] if app_theme == "dark" else []))
    app.setStyle("Fusion")
    set_app_palette()

    image_path = None
    for arg in sys.argv[1:]:
        image_path = arg
        break

    main_window = MainWindow(
        name,
        version,
        current_dir,
        settings,
        image_path=image_path
        )

    sys.exit(app.exec_())