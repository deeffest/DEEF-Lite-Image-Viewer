from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

def _init_shortcuts(self):
    shortcuts = {
        Qt.CTRL + Qt.Key_O: self.open_file_dialog,
        Qt.Key_Left: self.previous,
        Qt.Key_Right: self.next,
        Qt.Key_F11: self.full_screen,
    }

    for key, value in shortcuts.items():
        shortcut = QShortcut(QKeySequence(key), self)
        shortcut.activated.connect(value)