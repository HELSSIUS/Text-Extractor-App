from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QFileDialog, QWidget, QLabel, QWidgetAction
from pytesseract import get_languages

from apps.languages import Languages
from apps.textExtractor import TextExtractor
from apps.utils import get_logo, get_default_save_folder, get_hotkey
from apps.config import Settings, Theme, LogoTheme


class TrayApp(QSystemTrayIcon):
    def __init__(self, settings: Settings):
        super().__init__()
        # get settings
        self.__settings = settings
        # setup UI
        self.__setup_ui()
        # create text extractor
        self.extractor = TextExtractor()
        # start extractor
        self.extractor.start_event_loop()
        # TODO add autoreload for extractor if pc was slept and now is working
        #  or just add auto check is extractor running each 5 or 10 secs

    def __setup_ui(self):
        self.setToolTip(self.__settings.title)
        self.__set_icon()
        self.__set_menu()

    def __set_icon(self):
        icon = QIcon(get_logo())
        self.setIcon(icon)

    def __set_menu(self):
        self.menu = QMenu()
        self.__set_style()
        self.__set_title_action()
        self.menu.addSeparator()
        self.__set_items()
        self.setContextMenu(self.menu)

    def __set_style(self):
        self.menu.setObjectName("QMenu")

        # set menu stylesheet
        bg_color, color, selected_bg_color = self.__get_colors()

        self.menu.setStyleSheet(f"""
            QMenu{{
                background-color: #{bg_color};
                color: #{color};
            }}
            QMenu::item{{
                background-color: #{bg_color};
                color: #{color};
                padding: 10px;
                padding-left: 4px;
                padding-right: 20px;
                margin-left: 6px;
                margin-right: 16px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: #{selected_bg_color};
            }}
        """)

    def __set_title_action(self):
        # set title action 3f4042
        self.title_action = QAction(self.icon(), self.__settings.title, self)
        self.title_action.setEnabled(False)
        self.menu.addAction(self.title_action)

    def __set_items(self):
        # Create the main menu items
        self.hotkey_action = QAction(f"HotKey {self.__settings.hotkey}", self)
        self.hotkey_action.triggered.connect(self.change_hotkey)

        # action (Enable notifications/Disable notifications)
        self.notifications_action = QAction(
            "Disable notifications" if self.__settings.is_notification_enabled else "Enable notifications",
            self)
        self.notifications_action.triggered.connect(self.toggle_notifications)

        # action (Enable notifications/Disable notifications)
        self.autostart_action = QAction(
            "Disable autostart" if self.__settings.is_auto_started() else "Enable autostart",
            self)
        self.autostart_action.triggered.connect(self.toggle_autostart)

        # action (don`t save screenshots/save screenshots)
        self.is_save_action = QAction(
            "don`t save screenshots" if self.__settings.is_save_photos else "save screenshots",
            self)
        self.is_save_action.triggered.connect(self.toggle_save_photos)

        # set save folder if save is enable
        if self.__settings.is_save_photos:
            self.__set_action_save_folder()

        # create menu for set languages
        self.languages_menu = self.menu.addMenu("Languages")
        self.__set_lang_menu()

        # Create logo submenu items
        self.logo_menu = self.menu.addMenu("Logo")
        self.__add_actions_logo_menu()

        # Create theme submenu items
        self.theme_menu = self.menu.addMenu("Theme")
        self.__add_actions_theme_menu()

        # create and set quit action
        self.action_quit = QAction("Quit", self)
        self.action_quit.triggered.connect(self.quit_application)

        # Add main menu items and the submenu to the main menu
        self.__set_items_menu()

    def __add_actions_logo_menu(self):
        for logo_theme in LogoTheme:
            logo_theme_action = QAction(logo_theme.value.capitalize(), self)
            logo_theme_action.triggered.connect(self.toggle_logo_theme)
            if logo_theme.value == self.__settings.logo_theme:
                logo_theme_action.setVisible(False)
            self.logo_menu.addAction(logo_theme_action)

    def __set_action_save_folder(self):
        self.save_folder_action = QAction("Save Folder")
        self.save_folder_action.triggered.connect(self.select_folder)

    def __set_lang_menu(self):
        self.languages_menu.clear()
        tesseract_langs = get_languages()
        for language in Languages:
            if language.value in tesseract_langs:
                # lang_action = QAction(language.name, self)
                lang_action = QWidgetAction(self)
                lang_label = QLabel(language.name)
                lang_action.setDefaultWidget(lang_label)

                # set stylesheet for items
                lang_label.setStyleSheet(self.__get_lang_label_style(False))
                if language.value in self.__settings.languages:
                    lang_label.setStyleSheet(self.__get_lang_label_style(True))

                # set action
                lang_action.triggered.connect(self.select_languages)
                # add to menu
                self.languages_menu.addAction(lang_action)

    def __set_items_menu(self):
        if hasattr(self, "save_folder_action"):
            self.menu.addActions([
                self.hotkey_action,
                self.notifications_action,
                self.autostart_action,
                self.is_save_action,
                self.save_folder_action,
                self.languages_menu.menuAction(),
                self.logo_menu.menuAction(),
                self.theme_menu.menuAction(),
                self.action_quit
            ])
        else:
            self.menu.addActions([
                self.hotkey_action,
                self.notifications_action,
                self.autostart_action,
                self.is_save_action,
                self.languages_menu.menuAction(),
                self.logo_menu.menuAction(),
                self.theme_menu.menuAction(),
                self.action_quit
            ])

    def __add_actions_theme_menu(self):
        self.theme_menu.clear()
        for theme in Theme:
            theme_action = QAction(theme.value.capitalize(), self)
            theme_action.triggered.connect(self.toggle_theme)
            if theme.value == self.__settings.theme:
                theme_action.setVisible(False)
            self.theme_menu.addAction(theme_action)

    def __get_colors(self, select_prev_select: bool = False)\
            -> tuple[str, str, str] | tuple[str, str, str, str]:
        if self.__settings.theme == Theme.LIGHT:
            bg_color = "f2f2f2"
            color = "000000"
            selected_bg_color = "90c8f6"
            selected_bg_previous_color = "6389a9"
        else:
            bg_color = "292a2d"
            color = "e8eaed"
            selected_bg_color = "3f4042"
            selected_bg_previous_color = "333335"
        if select_prev_select:
            return bg_color, color, selected_bg_color, selected_bg_previous_color
        return bg_color, color, selected_bg_color

    def __get_lang_label_style(self, selected: bool):
        bg_color, color, selected_bg_color, selected_bg_previous_color = self.__get_colors(
            select_prev_select=True
        )
        if selected:
            return f"""
                QLabel{{
                    background-color: #{selected_bg_color};
                    color: #{color};
                    padding: 10px;
                    padding-left: 4px;
                    padding-right: 20px;
                    margin-left: 6px;
                    margin-right: 16px;
                    font-size: 13px;
                }}
                QLabel::Hover {{
                    background-color: #{selected_bg_previous_color};
                }}
            """
        return f"""
            QLabel{{
                background-color: #{bg_color};
                color: #{color};
                padding: 10px;
                padding-left: 4px;
                padding-right: 20px;
                margin-left: 6px;
                margin-right: 16px;
                font-size: 13px;
            }}
            QLabel::Hover {{
                background-color: #{selected_bg_color};
            }}"""

    # TODO add method update UI to update all menu for DRY principle

    def change_hotkey(self):
        hotkey = get_hotkey()
        self.__settings.set_values(
           hotkey=hotkey
        )
        self.sender().setText(f"HotKey {self.__settings.hotkey}")
        self.extractor.update_hotkey(
            new_hotkey=self.__settings.hotkey,
            auto_restart=True
        )

    def select_folder(self):
        save_dir = QFileDialog.getExistingDirectory(QWidget(), "select directory", get_default_save_folder())
        self.__settings.set_values(save_folder=save_dir if len(save_dir) > 0 else self.__settings.save_folder)

    def select_languages(self):
        lang: Languages = Languages.get_item_by_name(
            self.sender().defaultWidget().text()
        )
        if lang.value in self.__settings.languages:
            self.__settings.languages.remove(lang.value)
            self.__settings.set_values(
                languages=self.__settings.languages
            )
        else:
            self.__settings.languages.append(lang.value)
            self.__settings.set_values(
                languages=self.__settings.languages
            )
        self.extractor.restart_event_loop()
        self.__set_lang_menu()

    def toggle_notifications(self):
        if self.__settings.is_notification_enabled:
            self.sender().setText("Enable notifications")
        else:
            self.sender().setText("Disable notifications")

        self.extractor.restart_event_loop()

        self.__settings.set_values(
            is_notification_enabled=not self.__settings.is_notification_enabled
        )

    def toggle_autostart(self):
        is_auto_started = self.__settings.is_auto_started()
        if is_auto_started:
            self.sender().setText("Enable autostart")
        else:
            self.sender().setText("Disable autostart")

        self.__settings.auto_start(not is_auto_started)

    def toggle_save_photos(self):
        if self.__settings.is_save_photos:
            self.sender().setText("save screenshots")
            self.menu.removeAction(self.save_folder_action)

        else:
            self.sender().setText("don`t save screenshots")
            for action in self.menu.actions():
                self.theme_menu.removeAction(action)
            self.__set_action_save_folder()
            # self.menu.addAction(self.save_folder_action)
            self.__set_items_menu()

        self.extractor.restart_event_loop()

        self.__settings.set_values(
            is_save_photos=not self.__settings.is_save_photos
        )

    def toggle_logo_theme(self):
        # get selected theme
        theme: LogoTheme = LogoTheme(self.sender().text().lower())
        # set
        self.__settings.set_values(logo_theme=theme)
        # update logo menu
        for action in self.logo_menu.actions():
            self.logo_menu.removeAction(action)
        # update GUI
        self.__add_actions_logo_menu()
        self.__set_icon()
        self.title_action.setIcon(self.icon())

    def toggle_theme(self):
        # get selected theme
        theme: Theme = Theme(self.sender().text().lower())  # e.g Dark -> Theme.dark
        # set
        self.__settings.set_values(theme=theme)
        # update theme menu
        for action in self.theme_menu.actions():
            self.theme_menu.removeAction(action)
        # update GUI where use theme
        self.__add_actions_theme_menu()
        self.__set_style()
        self.__set_icon()
        self.__set_lang_menu()
        self.title_action.setIcon(self.icon())

    def quit_application(self):
        # stop event loop for extractor
        self.extractor.stop_event_loop()
        # stop app
        QApplication.quit()
