from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

def _init_shortcuts(self):
    shortcuts = {
        Qt.CTRL + Qt.Key_O: self.open_file_dialog,
        Qt.Key_Left: self.previous,
        Qt.Key_Right: self.next,
        Qt.Key_F11: self.full_screen,
        Qt.Key_F10: lambda: self.slide_show_shortcut(self.actionSlide_Show.isChecked()),
        Qt.CTRL + Qt.Key_S: self.open_settings,
        Qt.CTRL + Qt.Key_R: self.rotate_image,
        Qt.CTRL + Qt.Key_W: self.set_wallpaper,
        Qt.CTRL + Qt.Key_E: self.exit_app,
    }

    for key, value in shortcuts.items():
        shortcut = QShortcut(QKeySequence(key), self)
        shortcut.activated.connect(value)