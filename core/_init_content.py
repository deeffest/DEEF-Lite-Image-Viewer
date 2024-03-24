from PyQt5.QtWidgets import QAction, QSizePolicy, QWidget
from PyQt5.QtGui import QIcon

def _init_content(self):
	if self.image_path:
		self.open_image(self.image_path)