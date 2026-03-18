import win32print
import win32ui
from PIL import ImageWin
from tkinter import messagebox
from models.settings import SettingsModel 

def print_barcode_to_printer(img):
    """
    يطبع الصورة على الطابعة المحددة في الإعدادات
    """

    settings = SettingsModel()
    printer_name = settings.get_setting("printer_name")

    if not printer_name:
        messagebox.showerror("خطأ", "لم يتم تحديد طابعة")
        return

    try:
        # فتح الطابعة
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            printer_size = hDC.GetDeviceCaps(110), hDC.GetDeviceCaps(111)  # PHYSICALWIDTH, PHYSICALHEIGHT
            hDC.StartDoc("Barcode Print")
            hDC.StartPage()

            # تحويل الصورة لتناسب الطابعة
            bmp = img.convert("RGB")
            dib = ImageWin.Dib(bmp)
            # حساب موضع وطول/عرض الصورة
            x = int((printer_size[0] - bmp.width) / 2)
            y = int((printer_size[1] - bmp.height) / 2)
            dib.draw(hDC.GetHandleOutput(), (x, y, x + bmp.width, y + bmp.height))

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل الطباعة: {e}")