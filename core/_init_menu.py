from PyQt5.QtWidgets import QMenu

def _init_menu(self, point):
    contextMenu = QMenu(self)

    contextMenu.addAction(self.actionOpen_Image)
    contextMenu.addSeparator()    
    
    contextMenu.addAction(self.actionFull_Screen)
    contextMenu.addAction(self.actionSlide_Show)
    contextMenu.addSeparator()

    contextMenu.addAction(self.actionZoom_In)
    contextMenu.addAction(self.actionZoom_Out)
    contextMenu.addAction(self.actionRotate)
    contextMenu.addSeparator()

    contextMenu.addAction(self.actionPrevious)
    contextMenu.addAction(self.actionNext)
    contextMenu.addSeparator()

    contextMenu.addMenu(self.menuFolder_Contents)
    contextMenu.addSeparator()

    contextMenu.addMenu(self.menuSet_As)
    contextMenu.addSeparator()

    contextMenu.addAction(self.actionSettings)
    contextMenu.addSeparator()

    contextMenu.addAction(self.actionExit_2)

    contextMenu.exec_(self.image_viewer.mapToGlobal(point))