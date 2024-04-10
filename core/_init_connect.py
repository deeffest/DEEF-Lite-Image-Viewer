import sys

from PyQt5.QtWidgets import qApp

def _init_connect(self):
    self.actionOpen_Image.triggered.connect(self.open_file_dialog)
    self.actionFull_Screen.triggered.connect(self.full_screen)
    self.toolButton_3.clicked.connect(self.full_screen)
    self.actionDark_Theme.triggered.connect(self.toggle_dark_theme)
    self.actionPrevious.triggered.connect(self.previous)
    self.toolButton.clicked.connect(self.previous)
    self.actionNext.triggered.connect(self.next)
    self.toolButton_2.clicked.connect(self.next)
    self.actionCheck_Updates.triggered.connect(self.check_for_updates)
    self.actionAbout.triggered.connect(self.about)
    self.actionAbout_Qt.triggered.connect(lambda: qApp.aboutQt())

    self.image_viewer.customContextMenuRequested.connect(self.show_context_menu)
    self.scrollArea.installEventFilter(self)