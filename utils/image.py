from PIL import Image
from customtkinter import CTkImage
from pathlib import Path


def image(path, size=(40, 40)):
    """تحميل صورة للأستخدام في Customtkinter Widgets"""
    if not path or not Path(path).is_file():
        path = "assets/icon.png"

    img = Image.open(path)
    return CTkImage(img, size=size)
