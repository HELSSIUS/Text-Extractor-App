# PyQt5 (QApplication for start app)
import pytesseract
from PyQt5.QtWidgets import QApplication
from apps.config import Settings
from apps.notification import show_wrong_msg
# applications
from apps.tray import TrayApp
# default python modules
from multiprocessing import freeze_support
import sys


def main():
    # create pyqt5 app
    app = QApplication(sys.argv)
    settings = Settings()

    # set options
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")

    # start tray
    tray = TrayApp(settings)
    tray.show()
    # execute dynamic app code and get status code when app is finished
    # stop python interpolator with status code of app
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        # check is tesseract exist(if not trow exception)
        pytesseract.get_tesseract_version()
        # To use pyinstaller with multiprocessing
        if sys.platform.startswith('win'):
            # On Windows calling this function is necessary.
            freeze_support()
        main()
    except Exception as ex:
        sys.exit(show_wrong_msg(ex))
