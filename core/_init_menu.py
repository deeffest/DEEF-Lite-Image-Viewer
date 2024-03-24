from PyQt5.QtWidgets import QMenu

def _init_menu(self, point):
    contextMenu = QMenu(self)

    for action in self.menuFile.actions():
        if isinstance(action, QMenu):
            contextMenu.addMenu(action.menu())
        else:
            contextMenu.addAction(action)
    contextMenu.addSeparator()

    for action in self.menuView.actions():
        if isinstance(action, QMenu):
            contextMenu.addMenu(action.menu())
        else:
            contextMenu.addAction(action)
    contextMenu.addSeparator()         

    for action in self.menuNavigate.actions():
        if isinstance(action, QMenu):
            contextMenu.addMenu(action.menu())
        else:
            contextMenu.addAction(action)
    contextMenu.addSeparator()

    contextMenu.addMenu(self.menuHelp)
    contextMenu.addSeparator()

    contextMenu.exec_(self.image_viewer.mapToGlobal(point))