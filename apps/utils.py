from config import Settings, LogoTheme, Theme
import os.path
import darkdetect
import keyboard

get_theme = darkdetect.theme
is_dark = darkdetect.isDark


def get_main_dir():
    file_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(file_path))


def get_default_save_folder():
    screenshot_path = "testpic"
    return os.path.join(get_main_dir(), screenshot_path)


def get_logo():
    # get settings
    __settings = Settings()
    # get main directory
    main_dir = get_main_dir()
    # choose them for logo
    if __settings.logo_theme == LogoTheme.DEFAULT:
        if __settings.theme == Theme.LIGHT:
            return os.path.join(main_dir, r"res\logo_light.svg")
        else:
            return os.path.join(main_dir, r"res\logo.svg")
    elif __settings.logo_theme == LogoTheme.LIGHT:
        return os.path.join(main_dir, r"res\logo_light.svg")
    else:
        return os.path.join(main_dir, r"res\logo.svg")


def get_hotkey():
    hotkey = []
    while True:
        try:
            hotkey_event = keyboard.read_event(suppress=True)
            if hotkey_event.event_type == keyboard.KEY_UP:
                break
            elif hotkey_event.event_type == keyboard.KEY_DOWN:
                hotkey_name: str = hotkey_event.name.lower()
                if "windows" in hotkey_name:
                    hotkey_name = "windows"
                elif "ctrl" in hotkey_name:
                    hotkey_name = "ctrl"
                elif "alt" in hotkey_name:
                    hotkey_name = "alt"
                elif "shift" in hotkey_name:
                    hotkey_name = "shift"
                elif "caps lock" in hotkey_name:
                    hotkey_name = "capslock"
                hotkey.append(hotkey_name)
        except KeyboardInterrupt:
            break
    return "+".join(list(set(hotkey)))
