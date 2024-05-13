from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import QStatusTipEvent
from PyQt5.QtCore import QObject, QEvent

class StatusTipFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if isinstance(event, QStatusTipEvent):
            return True
        return super().eventFilter(watched, event)

def _init_connect(self):
    self.actionOpen_Image.triggered.connect(self.open_file_dialog)
    self.actionExit_2.triggered.connect(self.exit_app)
    self.folder_contents_widget.lineEdit.textChanged.connect(self.filter_list_items)
    self.actionFull_Screen.triggered.connect(self.full_screen)
    self.actionSlide_Show.triggered.connect(self.slide_show)
    self.actionZoom_In.triggered.connect(self.zoom_in)
    self.actionZoom_Out.triggered.connect(self.zoom_out)
    self.actionRotate.triggered.connect(self.rotate_image)
    self.actionSet_as_Wallpaper.triggered.connect(self.set_wallpaper)
    self.actionSettings.triggered.connect(self.open_settings)
    self.actionPrevious.triggered.connect(self.previous)
    self.actionNext.triggered.connect(self.next)
    self.actionCheck_Updates.triggered.connect(self.check_for_updates)
    self.actionAbout.triggered.connect(self.about)
    self.actionAbout_Qt.triggered.connect(lambda: qApp.aboutQt())

    self.image_viewer.customContextMenuRequested.connect(self.show_context_menu)
    self.image_viewer.installEventFilter(self)
    self.installEventFilter(StatusTipFilter(self))