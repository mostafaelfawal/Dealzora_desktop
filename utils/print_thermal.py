import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin
from utils.ar_support import ar
from models.settings import SettingsModel
from utils.format_currency import format_currency
from tkinter.messagebox import showerror

FONT_BOLD = "assets/fonts/NotoNaskhArabic-Bold.ttf"


def draw_ar(draw, x, y, text, font, align="center"):
    bbox = draw.textbbox((0, 0), ar(text), font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    if align == "right":
        x = x - w - 5
    elif align == "center":
        x = x - w / 2

    draw.text((x, y - h / 2), ar(text), font=font, fill="black")


def draw_cell(draw, x, y, w, h, text, font, align="center"):
    draw.rectangle((x, y, x + w, y + h), outline="black", width=1)

    bbox = draw.textbbox((0, 0), ar(text), font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    if align == "right":
        tx = x + w - tw - 5
    elif align == "left":
        tx = x + 5
    else:
        tx = x + (w - tw) / 2

    ty = y + (h - th) / 2

    draw.text((tx, ty), ar(text), font=font, fill="black")


def generate_invoice(sale_data, products_data, width=440):

    settings = SettingsModel()

    shop = settings.get_setting("shop_name")

    f_shop = ImageFont.truetype(FONT_BOLD, 28)
    f_title = ImageFont.truetype(FONT_BOLD, 18)
    f_bold = ImageFont.truetype(FONT_BOLD, 16)

    img = Image.new("1", (width, 2000), "white")
    draw = ImageDraw.Draw(img)

    y = 20
    center = width // 2

    # ===== Header =====

    draw_ar(draw, center, y, shop, f_shop)
    y += 40

    draw_ar(draw, center, y, "فاتورة بيع", f_title)
    y += 30

    draw.line((20, y, width - 20, y), fill="black", width=2)
    y += 20

    draw_ar(
        draw,
        width - 20,
        y,
        f"رقم الفاتورة: {sale_data['invoice_number']}",
        f_bold,
        "right",
    )
    draw_ar(draw, 20, y, f"التاريخ: {sale_data['date']}", f_bold, "left")
    y += 25

    draw_ar(draw, width - 20, y, f"الوقت: {sale_data['time']}", f_bold, "right")

    draw_ar(draw, 20, y, f"العميل: {sale_data['customer_name']}", f_bold, "left")
    y += 25

    draw.line((20, y, width - 20, y), fill="black", width=1)
    y += 15

    # ===== Table =====

    col_name = 180
    col_qty = 60
    col_price = 100
    col_total = 60
    row_h = 28

    x = 20

    # Header row
    
    draw_cell(
        draw,
        x + col_name + col_qty + col_price,
        y,
        col_total,
        row_h,
        "الإجمالي",
        f_bold,
    )
    draw_cell(draw, x + col_name + col_qty, y, col_price, row_h, "السعر", f_bold)
    draw_cell(draw, x + col_name, y, col_qty, row_h, "الكمية", f_bold)
    draw_cell(draw, x, y, col_name, row_h, "المنتج", f_bold)

    y += row_h

    # Products
    for p in products_data:

        name = p["name"][:18]

        draw_cell(draw, x, y, col_name, row_h, name, f_bold, "right")

        draw_cell(draw, x + col_name, y, col_qty, row_h, f'{p["qty"]}', f_bold)

        draw_cell(
            draw,
            x + col_name + col_qty,
            y,
            col_price,
            row_h,
            f'{p["price"]}',
            f_bold,
        )

        draw_cell(
            draw,
            x + col_name + col_qty + col_price,
            y,
            col_total,
            row_h,
            f'{p["total"]}',
            f_bold,
        )

        y += row_h

    y += 10

    draw.line((20, y, width - 20, y), fill="black", width=2)
    y += 20

    # ===== Summary =====

    def summary(label, value):
        nonlocal y
        draw_ar(draw, width - 20, y, label, f_bold, "right")
        draw_ar(draw, 20, y, format_currency(value), f_bold, "left")
        y += 25

    summary("الإجمالي الفرعي", sale_data["subtotal"])

    if sale_data["discount"] > 0:
        summary("الخصم", sale_data["discount"])

    if sale_data["tax"] > 0:
        summary("الضريبة", sale_data["tax"])

    draw.line((20, y, width - 20, y), fill="black", width=1)
    y += 15

    summary("الإجمالي", sale_data["total"])
    summary("المدفوع", sale_data["paid"])
    summary("الباقي", sale_data["remaining"])

    draw.line((20, y, width - 20, y), fill="black", width=2)
    y += 25

    draw_ar(draw, center, y, "شكراً لزيارتكم", f_bold)
    y += 30
    draw_ar(draw, center, y, "Powred By Dealzora", f_bold)

    img = img.crop((0, 0, width, y + 40))

    return img


def print_image_to_printer(img, printer_name):

    hprinter = win32print.OpenPrinter(printer_name)
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    hdc.StartDoc("Thermal Invoice")
    hdc.StartPage()

    if img.mode != "1":
        img = img.convert("1")

    dib = ImageWin.Dib(img)
    dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))

    hdc.EndPage()
    hdc.EndDoc()

    win32print.ClosePrinter(hprinter)


def print_shop_invoice(sale_data, products_data):

    settings = SettingsModel()

    printer_name = settings.get_setting("printer_name")
    copies = int(settings.get_setting("invoices_per_print") or 1)

    try:

        for _ in range(copies):

            img = generate_invoice(sale_data, products_data)

            print_image_to_printer(img, printer_name)
        return True
    except Exception as e:
        if "StartDoc failed" in str(e):
            showerror("خطأ في الطباعة", "فشل في بدء عملية الطباعة")
            return False
        showerror("خطأ في الطباعة", str(e))
        return False