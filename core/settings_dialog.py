from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

import qtawesome as qta

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = parent
        self.settings = self.window.settings
        self.temp_settings = {}

        loadUi(
            f'{self.window.current_dir}/core/ui/settings_dialog.ui', self
        )

        self._init_window()
        self._init_content()
        self._init_connect()

    def _init_content(self):
        self.temp_settings["save_last_window_size"] = self.settings.value("save_last_window_size", "true") == "true"
        self.temp_settings["check_for_updates_at_startup"] = self.settings.value("check_for_updates_at_startup", "true") == "true"
        self.temp_settings["app_theme"] = self.settings.value("app_theme", "dark")
        
        self.apply_settings()

    def _init_connect(self):
        self.pushButton.clicked.connect(self.save_and_close)
        self.pushButton_2.clicked.connect(self.close)

        self.checkBox.stateChanged.connect(self.set_temp_save_last_window_size)
        self.checkBox_2.stateChanged.connect(self.set_temp_check_for_updates_at_startup)
        self.radioButton.toggled.connect(lambda: self.set_temp_app_theme("light") if self.radioButton.isChecked() else None)
        self.radioButton_2.toggled.connect(lambda: self.set_temp_app_theme("dark") if self.radioButton_2.isChecked() else None)
        
    def apply_settings(self):
        self.checkBox.setChecked(self.temp_settings["save_last_window_size"])
        self.checkBox_2.setChecked(self.temp_settings["check_for_updates_at_startup"])
        if self.temp_settings["app_theme"] == "dark":
            self.radioButton_2.setChecked(True)
        else:
            self.radioButton.setChecked(True)

    def save_settings(self):
        self.settings.setValue("save_last_window_size", "true" if self.temp_settings["save_last_window_size"] else "false")
        self.settings.setValue("check_for_updates_at_startup", "true" if self.temp_settings["check_for_updates_at_startup"] else "false")
        self.settings.setValue("app_theme", self.temp_settings["app_theme"])

    def set_temp_save_last_window_size(self, state):
        self.temp_settings["save_last_window_size"] = state

    def set_temp_check_for_updates_at_startup(self, state):
        self.temp_settings["check_for_updates_at_startup"] = state

    def set_temp_app_theme(self, theme):
        self.temp_settings["app_theme"] = theme

    def _init_window(self):
        self.setWindowTitle("Settings")
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(self.size())
        self.setWindowIcon(qta.icon('ri.settings-4-fill'))

    def save_and_close(self):
        self.save_settings()
        self.close()