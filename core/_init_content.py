from PyQt5.QtWidgets import QWidget, QSizePolicy, QLabel

def _init_content(self):
	self.zoom_label = QLabel(self)
	self.statusbar.addPermanentWidget(self.zoom_label)

	self.create_folder_contents_menu()
	self.actionFolder_Contents_3.setVisible(False)
	
	self.toolBar.addAction(self.actionOpen_Image)
	self.toolBar.addSeparator()

	self.toolBar.addAction(self.actionPrevious)
	self.toolBar.addAction(self.actionNext)
	self.toolBar.addSeparator()

	self.toolBar.addAction(self.actionZoom_In)
	self.toolBar.addAction(self.actionZoom_Out)
	self.toolBar.addAction(self.actionRotate)
	self.toolBar.addSeparator()
    
	spacer = QWidget()
	spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
	self.toolBar.addWidget(spacer)
	
	self.toolBar.addAction(self.actionSlide_Show)
	self.toolBar.addSeparator()
	self.toolBar.addAction(self.actionFull_Screen)

	self.set_timer()

	if self.image_path:
		self.open_image(self.image_path)