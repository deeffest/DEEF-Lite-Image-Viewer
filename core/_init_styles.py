def _init_styles(self):
	if self.settings.value("app_theme", "dark") == "dark":
		self.setStyleSheet("""
			QToolTip {
				background-color: rgb(44,44,44);
				border: 1px solid rgb(93,93,93);
				color: white;
			}
		""")
		self.menubar.setStyleSheet("""
			QMenuBar {
				background-color: rgb(32,32,32);
				border-bottom: 1px solid rgb(29,29,29);
			}
			QFrame {
				color: white;
			}
		""")
		self.statusbar.setStyleSheet("""
			QStatusBar {
				background-color: rgb(32,32,32);
			}
		""")
		self.toolBar.setStyleSheet("""
			QToolBar {
				background-color: rgb(32,32,32);
				border-top: 1px solid rgb(29,29,29);
			}
		""")
	else:
		self.setStyleSheet("""
			QToolTip {
				background-color: rgb(249,249,249);
				border: 1px solid rgb(171,171,171);
				color: black;
			}
		""")
		self.menubar.setStyleSheet("""
			QMenuBar {
				background-color: rgb(243,243,243);
				border-bottom: 1px rgb(230,230,230);
			}
		""")
		self.statusbar.setStyleSheet("""
			QStatusBar {
				background-color: rgb(243,243,243);
			}
		""")
		self.toolBar.setStyleSheet("""
			QToolBar {
				background-color: rgb(243,243,243);
				border-top: 1px solid rgb(230,230,230);
			}
		""")