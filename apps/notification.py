from PyQt5.QtWidgets import QApplication, QErrorMessage
from winotify import Notification, audio
from apps.config import Settings
from apps.utils import get_logo
from sys import platform


class ScreenShotNotification:
    # get settings
    __settings = Settings()

    def __init__(self):
        self.notification = None
        if platform.startswith("win"):
            self.notification = Notification(
                app_id=self.__settings.title,
                title="Text extraction",
                msg="Text has been extracted from the selected area",
                icon=get_logo()
            )
            self.notification.set_audio(
                audio.Default,
                loop=False
            )
        elif platform.startswith("linux"):
            # TODO add notifications for linux
            pass

    def show(self):
        self.notification.show()
        # TODO adapt show notifications for linux version


def show_wrong_msg(ex: Exception):
    app = QApplication([])

    error_dialog = QErrorMessage()
    error_dialog.showMessage(f'Error: {ex}')

    return app.exec_()
