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
        tr,
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
        self.tr = tr

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

        language_list = [
            'en_EN', 'ru_RU', 'es_ES', 'zh_CN', 
            'fr_FR', 'de_DE', 'ja_JP', 'uk_UA'
        ]
        self.ComboBox.setEnabled(True)
        self.ComboBox.addItems(language_list)
        language_index = self.ComboBox.findText(self.app_settings.value("current_app_language", "en_EN"))
        self.ComboBox.setCurrentIndex(language_index)
        self.ComboBox.currentIndexChanged.connect(self.setAppLanguage)

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

        self._set_translations()

    def _set_translations(self):
        self.TitleLabel_2.setText(self.tr["9"])
        self.HyperlinkButton.setText(self.tr["42"])
        self.SubtitleLabel_5.setText(self.tr["43"])
        self.BodyLabel_7.setText(self.tr["44"])
        self.BodyLabel_19.setText(self.tr["45"])
        self.SubtitleLabel_6.setText(self.tr["46"])
        self.BodyLabel_8.setText(self.tr["47"])
        self.BodyLabel_14.setText(self.tr["48"])
        self.BodyLabel_9.setText(self.tr["49"])
        self.SubtitleLabel_7.setText(self.tr["50"])
        self.BodyLabel_10.setText(self.tr["51"])
        self.BodyLabel_11.setText(self.tr["52"])
        self.PushButton.setText(self.tr["53"])
        self.BodyLabel_13.setText(self.tr["54"])
        self.BodyLabel_12.setText(self.tr["55"])
        self.RadioButton.setText(self.tr["56"])
        self.RadioButton_2.setText(self.tr["57"])
        self.RadioButton_3.setText(self.tr["56"])
        self.RadioButton_4.setText(self.tr["57"])
        self.SubtitleLabel_8.setText(self.tr["58"])

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
        else:
            self.SwitchButton_3.setChecked(False)

        if self.current_app_check_updates == "true":
            self.SwitchButton_4.setChecked(True)
        else:
            self.SwitchButton_4.setChecked(False)

    def SearchUpdates(self):
        self.PushButton.setEnabled(False)
        self.window.starter_check_updates(first_update=False)

    def restart_msg_box(self):
        restart_msg = MessageBox(
            self.tr["38"],
            self.tr["41"],
            self.window
        )
        restart_msg.yesButton.setText(self.tr["40"])
        restart_msg.cancelButton.setText(self.tr["5"])

        if restart_msg.exec():
            QApplication.quit()
            status = QProcess.startDetached(sys.executable, sys.argv) 

    def setAppLanguage(self, index):
        current_language = self.ComboBox.itemText(index)
        self.app_settings.setValue("current_app_language", current_language)
        self.restart_info_bar()

    def onSwitchButton3Clicked(self):
        if self.current_app_window_size == "true":
            self.app_settings.setValue("current_window_size", "false")
            self.current_app_window_size = "false"
        else:
            self.app_settings.setValue("current_window_size", "true")
            self.current_app_window_size = "true"

    def onSwitchButton4Clicked(self):
        if self.current_app_check_updates == "true":
            self.app_settings.setValue("current_check_updates", "false")
            self.current_app_check_updates = "false"
        else:
            self.app_settings.setValue("current_check_updates", "true")
            self.current_app_check_updates = "true"

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
            title=self.tr['38'],
            content=self.tr['39'],
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=3000,
            parent=self.window
        )
        restart_btn = PushButton(self.tr["40"])
        restart_btn.clicked.connect(self.restart_msg_box)
        w.addWidget(restart_btn)