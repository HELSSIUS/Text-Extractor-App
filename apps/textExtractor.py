import os

from pytesseract import TesseractNotFoundError

from apps.screenshot import ScreenShot
from apps.notification import ScreenShotNotification, show_wrong_msg
from apps.config import Settings
import pyperclip
import cv2
import pytesseract
import keyboard
from multiprocessing import Process


class TextExtractor:
    # get Settings from registry
    __settings = Settings()
    # get languages from settings
    languages = "+".join(__settings.languages)  # eng+rus+ukr for example

    def __init__(self, hotkey: str = __settings.hotkey):
        self.__hotkey = hotkey
        self.__event_loop_process: Process | None = None

    def screenshot_to_clip(self):
        # take screenshot and get its path
        screenshot_img = ScreenShot.make_screenshot()
        img = cv2.imread(screenshot_img.path)

        # if the photo is must not to be saved
        #   and if path to photo exists, delete this photo and its parent directory
        if not self.__settings.is_save_photos and os.path.exists(screenshot_img.path):
            os.remove(screenshot_img.path)
            directory = os.path.dirname(screenshot_img.path)
            try:
                os.rmdir(directory)
            except OSError:  # maybe directory is not empty
                for file in os.listdir(directory):
                    os.remove(os.path.join(directory, file))
                os.rmdir(directory)

        try:
            # extract text from imag
            text = pytesseract.image_to_string(img, self.languages)
            # add text to clipboard
            pyperclip.copy(text)
        except TesseractNotFoundError as tesseract_nf_ex:
            show_wrong_msg(tesseract_nf_ex)
            self.stop_event_loop()

        # Notify user if notifications is enabled
        if self.__settings.is_notification_enabled:
            ScreenShotNotification().show()

    def _event_loop(self):
        keyboard.add_hotkey(self.__hotkey, self.screenshot_to_clip)
        try:
            keyboard.wait()
        # if process is terminate
        except KeyboardInterrupt:
            pass

    def start_event_loop(self) -> Process:
        process = Process(
            target=self._event_loop,
        )
        process.start()
        self.__event_loop_process = process
        return process

    def stop_event_loop(self):
        if self.__event_loop_process:
            self.__event_loop_process.terminate()
            self.__event_loop_process = None

    def restart_event_loop(self):
        self.stop_event_loop()
        self.start_event_loop()

    def update_hotkey(self, new_hotkey: str = __settings.hotkey, auto_restart: bool = False):
        self.__hotkey = new_hotkey
        if auto_restart:
            self.restart_event_loop()
