#app_settings.py
from PyQt5.QtWidgets import QFrame, QApplication
from PyQt5 import uic
from qfluentwidgets import (
    setThemeColor, InfoBar, InfoBarPosition, PushButton,
    MessageBox
    )
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, QProcess
import sys

class AppSettings(QFrame):
    def __init__(
        self, 
        current_dir, 
        current_app_color_theme, 
        version,
        current_app_theme, 
        current_scene_theme, 
        current_check_updates,
        current_window_size,
        settings,
        parent=None
        ):
        super().__init__(parent)
        
        self.window = parent
        self.current_app_dir = current_dir
        self.current_app_color_theme = current_app_color_theme
        self.app_version = version
        self.current_app_theme = current_app_theme
        self.current_app_scene_theme = current_scene_theme
        self.current_app_check_updates = current_check_updates
        self.current_app_window_size = current_window_size
        self.app_settings = settings

        uic.loadUi(f'{self.current_app_dir}/core/ui/gui-settings.ui', self)

        color_list =  [
            'Default', 'Red', 'Green', 'Purple',
            'Blue', 'Yellow', 'Orange',
            'Pink', 'Brown'
        ]
        self.ComboBox_2.addItems(color_list)
        color_index = self.ComboBox_2.findText(self.current_app_color_theme)
        self.ComboBox_2.setCurrentIndex(color_index)
        self.ComboBox_2.currentIndexChanged.connect(self.setAppColorTheme)

        self.StrongBodyLabel_2.setText(self.app_version)

        if self.current_app_theme == 'dark':
            self.ScrollArea.setStyleSheet("background-color: rgb(39,39,39); border: none;")
        else:
            self.ScrollArea.setStyleSheet("background-color: rgb(249,249,249); border: none;")

        self.setCheckedFromSettings()
        self.RadioButton.clicked.connect(self.onRadioButtonClicked)
        self.RadioButton_2.clicked.connect(self.onRadioButton2Clicked)
        self.RadioButton_3.clicked.connect(self.onRadioButton3Clicked)
        self.RadioButton_4.clicked.connect(self.onRadioButton4Clicked)

        self.SwitchButton_3.checkedChanged.connect(self.onSwitchButton3Clicked)
        self.SwitchButton_4.checkedChanged.connect(self.onSwitchButton4Clicked)

        self.PushButton.clicked.connect(self.SearchUpdates)

    def setCheckedFromSettings(self):
        if self.current_app_theme == "dark":
            self.RadioButton.setChecked(True)
        else:
            self.RadioButton_2.setChecked(True)

        if self.current_app_scene_theme == "dark":
            self.RadioButton_3.setChecked(True)
        else:
            self.RadioButton_4.setChecked(True)

        if self.current_app_window_size == "true":
            self.SwitchButton_3.setChecked(True)
        if self.current_app_check_updates == "true":
            self.SwitchButton_4.setChecked(True)

    def SearchUpdates(self):
        self.PushButton.setEnabled(False)
        self.window.starter_check_updates(first_update=False)

    def restart_msg_box(self):
        restart_msg = MessageBox(
            f"Restart for application?",
            f"For correct application of new parameters it is necessary to restart the application (Not all parameters are required)",
            self.window
        )
        restart_msg.yesButton.setText('Restart')
        restart_msg.cancelButton.setText("Later")

        if restart_msg.exec():
            QApplication.quit()
            status = QProcess.startDetached(sys.executable, sys.argv) 

    def onSwitchButton3Clicked(self):
        if self.current_app_window_size == "true":
            self.app_settings.setValue("current_window_size", "false")
        else:
            self.app_settings.setValue("current_window_size", "true")

    def onSwitchButton4Clicked(self):
        if self.current_app_check_updates == "true":
            self.app_settings.setValue("current_check_updates", "false")
        else:
            self.app_settings.setValue("current_check_updates", "true")

    def setAppColorTheme(self, index):
        setThemeColor(self.ComboBox_2.itemText(index))
        self.app_settings.setValue("current_app_color_theme", self.ComboBox_2.itemText(index))

    def onRadioButtonClicked(self):
        self.app_settings.setValue("current_app_theme", "dark")
        self.restart_info_bar()

    def onRadioButton2Clicked(self):
        self.app_settings.setValue("current_app_theme", "light")
        self.restart_info_bar()

    def onRadioButton3Clicked(self):
        self.app_settings.setValue("current_scene_theme", "dark")
        self.window.homeInterface.setStyleSheet("background-color: rgb(22,22,22); border-radius: 5px;")

    def onRadioButton4Clicked(self):
        self.app_settings.setValue("current_scene_theme", "light")
        self.window.homeInterface.setStyleSheet("background-color: rgb(230,230,230); border-radius: 5px;")

    def restart_info_bar(self):
        w = InfoBar.new(
            icon=FIF.UPDATE,
            title='Restart for App?',
            content="The App must be restarted to apply the settings",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=3000,
            parent=self.window
        )
        restart_btn = PushButton("Restart")
        restart_btn.clicked.connect(self.restart_msg_box)
        w.addWidget(restart_btn)