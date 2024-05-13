from PyQt5.QtGui import QIcon, QPixmap

import qtawesome as qta

def _init_icons(self):
    self.actionOpen_Image.setIcon(qta.icon('ei.file-new'))
    self.actionExit_2.setIcon(qta.icon('fa.close'))
    self.actionFull_Screen.setIcon(qta.icon('ei.resize-full'))
    self.actionSlide_Show.setIcon(qta.icon('ri.slideshow-2-line'))
    self.actionZoom_In.setIcon(qta.icon('ei.zoom-in'))
    self.actionZoom_Out.setIcon(qta.icon('ei.zoom-out'))
    self.actionRotate.setIcon(qta.icon('fa.rotate-left'))
    self.menuSet_As.setIcon(qta.icon('mdi.image-move'))
    self.actionSet_as_Wallpaper.setIcon(qta.icon('mdi.wallpaper'))
    self.actionSettings.setIcon(qta.icon('ri.settings-4-fill'))
    self.actionPrevious.setIcon(qta.icon('ei.chevron-left'))
    self.actionNext.setIcon(qta.icon('ei.chevron-right'))
    self.menuFolder_Contents.setIcon(qta.icon('ei.folder-open'))
    self.actionCheck_Updates.setIcon(qta.icon('ei.search'))
    self.actionAbout.setIcon(qta.icon('ei.info-circle'))
    self.actionAbout_Qt.setIcon(QIcon(f'{self.current_dir}/resources/icons/qt.png'))