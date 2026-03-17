import ctypes
import os

def load_font(font_path):
    FR_PRIVATE = 0x10

    path = os.path.abspath(font_path)

    if os.name == "nt":
        ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)