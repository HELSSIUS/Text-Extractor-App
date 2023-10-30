# PyQt5 imports
import PIL.Image
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
# work with images (PIL/Pillow)
from PIL import ImageGrab
# my modules
from apps.utils import get_default_save_folder
from apps.config import Settings
# default modules
import datetime
import os.path


class SnippingWidget(QtWidgets.QMainWindow):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None, screenshot_path: str = None, file_name: str = None):
        super(SnippingWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # variable for store last screenshot
        self.last_screenshot = None
        # settings
        self.__settings = Settings()

        # path of photos
        self.screenshot_path = self.__get_screenshot_path(screenshot_path, file_name)

        # settings of square
        self.outsideSquareColor = "red"
        self.squareThickness = 2

        # points
        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

        # start
        #   On top of all other applications
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        #   overrides the keyboard handler on an empty method 'keyPressEvent'
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        #   full screen
        self.showFullScreen()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        self.hide()

    def __get_screenshot_path(self, screenshot_path, file_name):
        # generates filename
        if file_name is None:
            file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        # check if we got screenshot_path
        if screenshot_path is None or not self.__settings.is_save_photos:
            default_dir = get_default_save_folder()
            # check if folder is not exists
            if not os.path.exists(default_dir):
                os.mkdir(default_dir)

            # create path with file
            screenshot_path = os.path.join(default_dir, file_name)
        else:
            # if we got path from user
            if not os.path.exists(screenshot_path):
                os.mkdir(screenshot_path)

            # create path with file
            screenshot_path = os.path.join(screenshot_path, file_name)
        return screenshot_path

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.update()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        pass

    def mouseReleaseEvent(self, mouse_event):
        # get coordinates
        r = QtCore.QRect(self.start_point, self.end_point).normalized()
        self.hide()
        # grab image from coordinates
        img = ImageGrab.grab(bbox=r.getCoords())
        # saving image
        try:
            img.save(self.screenshot_path)
            self.last_screenshot = img
        except ValueError:  # if trying to save empty image
            self.last_screenshot = ScreenShot(self.screenshot_path)
            self.last_screenshot.image.save(self.screenshot_path)
        # The cursor is reset to its default state before the window is closed.
        QtWidgets.QApplication.restoreOverrideCursor()
        self.closed.emit()
        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()
        self.close()

    def paintEvent(self, event):
        trans = QtGui.QColor(22, 100, 233)
        r = QtCore.QRectF(self.start_point, self.end_point).normalized()
        qp = QtGui.QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)
        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)


class ScreenShot:
    def __init__(self, path: str, image: PIL.Image.Image = None):
        self.path = path
        if not image:
            # if path doesn't exist
            try:
                image = PIL.Image.open(path)
            except FileNotFoundError:
                image = self.__default_image()
        self.image: PIL.Image.Image = image

    def show(self):
        # show image
        self.image.show(os.path.basename(self.path))

    def __default_image(self) -> PIL.Image.Image:
        """
        Getting default image without any text
        :return: PIL image
        """
        width, height = 400, 300
        white_image = PIL.Image.new('RGB', (width, height), 'white')
        white_image.save(self.path)
        return white_image

    @classmethod
    def make_screenshot(cls):
        app = QApplication([])
        # get config
        settings = Settings()
        # create and start app
        widget = SnippingWidget(screenshot_path=settings.save_folder)
        widget.show()
        # execute app and exit app after execute
        app.exec_()
        # create instance of ScreenShot class for return user
        screen = cls(widget.screenshot_path, widget.last_screenshot)
        return screen
