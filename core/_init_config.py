from PyQt5.QtCore import QByteArray

def _init_config(self):        
	if self.settings.value("app_theme", "dark") == "dark":
		self.actionDark_Theme.setChecked(True)
	else:
		self.actionDark_Theme.setChecked(False)

	self.restoreState(self.settings.value('window_state', QByteArray()))