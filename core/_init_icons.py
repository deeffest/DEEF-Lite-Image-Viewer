from PyQt5.QtGui import QIcon, QPixmap

def _init_icons(self):
    icons = {
        "toolButton": {
            "normal": f'{self.current_dir}/resources/icons/{self.settings.value("app_theme")}/arrow_back_ios.svg',
            "normal_off": None, 
            "disabled": f'{self.current_dir}/resources/icons/disabled/arrow_back_ios.svg', 
            "disabled_off": None,
        },
        "toolButton_2": {
            "normal": f'{self.current_dir}/resources/icons/{self.settings.value("app_theme")}/arrow_forward_ios.svg',
            "normal_off": None, 
            "disabled": f'{self.current_dir}/resources/icons/disabled/arrow_forward_ios.svg', 
            "disabled_off": None,
        },
    }

    for action_name, icon_paths in icons.items():
        action = getattr(self, action_name, None)
        if action:
            icon = QIcon()
            if icon_paths.get("normal"):
                icon.addPixmap(QPixmap(icon_paths["normal"]), QIcon.Normal, QIcon.Off)
            if icon_paths.get("normal_off"):
                icon.addPixmap(QPixmap(icon_paths["normal_off"]), QIcon.Normal, QIcon.On)
            if icon_paths.get("disabled"):
                icon.addPixmap(QPixmap(icon_paths["disabled"]), QIcon.Disabled, QIcon.Off)
            if icon_paths.get("disabled_off"):
                icon.addPixmap(QPixmap(icon_paths["disabled_off"]), QIcon.Disabled, QIcon.On)
            action.setIcon(icon)
        else:
            print(f"Action {action_name} not found in the Window class.")