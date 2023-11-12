import sys
from enum import Enum
from languages import Languages
from PyQt5.QtCore import QSettings
from darkdetect import isDark


class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, Theme):
            return self.name == other.name


class LogoTheme(Enum):
    DARK = "dark"
    LIGHT = "light"
    DEFAULT = "default"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, LogoTheme):
            return self.name == other.name


class Settings:
    # Never change
    title = "Text Extractor App"

    def __init__(self):
        # get settings
        self.__settings = self.__get_setting_values()

        # changeable
        self.theme: Theme | None = None
        self.logo_theme: LogoTheme | None = None
        self.is_notification_enabled: bool | None = None
        self.is_save_photos: bool | None = None
        self.save_folder: str | None = None
        self.languages: list[str] | None = None
        self.hotkey: str | None = None

        # support fields
        self.__run_path = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

        # update values
        self.__update_values()

    def set_values(self, theme: Theme = None,
                   logo_theme: LogoTheme = None,
                   is_notification_enabled: bool = None,
                   is_save_photos: bool = None,
                   save_folder: str | None = None,
                   languages: list[str] = None,
                   hotkey: str = None):
        # set new values if values is not one otherwise set previous values
        self.__set_values(theme, logo_theme, is_notification_enabled, is_save_photos,
                          save_folder, languages, hotkey)

        # update fields of class
        self.__update_values()

    def __set_values(self, theme, logo_theme, is_notification_enabled,
                     is_save_photos, save_folder, languages, hotkey):
        # set new values if values is not one otherwise set previous values
        self.__settings.setValue(
            "theme", theme.value if theme is not None else self.theme
        )
        self.__settings.setValue(
            "logo", logo_theme.value if logo_theme is not None else self.logo_theme
        )
        self.__settings.setValue(
            "notifications",
            is_notification_enabled if is_notification_enabled is not None else self.is_notification_enabled
        )
        self.__settings.setValue(
            "save_photos", is_save_photos if is_save_photos is not None else self.is_save_photos
        )
        self.__settings.setValue(
            "save_folder", save_folder if save_folder is not None else self.save_folder
        )
        self.__settings.setValue(
            "languages", languages if languages is not None else self.languages
        )
        self.__settings.setValue(
            "hotkey", hotkey if hotkey is not None else self.hotkey
        )

    def __update_values(self):
        # update fields
        self.theme: Theme = self.__settings.value("theme", Theme.DARK.value if isDark() else Theme.LIGHT.value)
        self.logo_theme: LogoTheme = self.__settings.value("logo", LogoTheme.DEFAULT.value)
        self.is_notification_enabled: bool = self.__settings.value("notifications", False, bool)
        self.is_save_photos: bool = self.__settings.value("save_photos", False, bool)
        self.save_folder: str | None = self.__settings.value("save_folder", None)
        self.languages: list[str] = self.__settings.value("languages", [
            Languages.English.value,
            Languages.OrientationModule.value
        ])
        self.hotkey: str = self.__settings.value("hotkey", "shift+alt+a")

    def auto_start(self, enable: bool = True):
        autostart = QSettings(self.__run_path, QSettings.NativeFormat)
        if enable:
            autostart.setValue(self.title, sys.argv[0])
        else:
            autostart.remove(self.title)

    def is_auto_started(self):
        autostart = QSettings(self.__run_path, QSettings.NativeFormat)
        return self.title in autostart.allKeys()

    def __get_setting_values(self):
        return QSettings(self.title, "settings")

    def _get_settings(self):
        return self.__settings

    def clear(self):
        self.__settings.clear()
        self.__update_values()

    def __str__(self):
        return (f"Settings(title={self.title}, theme={self.theme}, logo_theme={self.logo_theme}, "
                f"is_notification_disabled={self.is_notification_enabled}, is_save_photos={self.is_save_photos}, "
                f"save_folder={self.save_folder}, languages={self.languages}, hotkey={self.hotkey})")
