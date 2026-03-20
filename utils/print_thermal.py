import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin
from models.settings import SettingsModel
from utils.format_currency import format_currency
from tkinter.messagebox import showerror
import arabic_reshaper
from bidi.algorithm import get_display

FONT_BOLD = "assets/fonts/NotoNaskhArabic-Bold.ttf"


# تعديل دالة تحويل الأرقام إلى كلمات (إزالة كلمة "جنيه")
def number_to_words_ar(number):
    """Convert number to Arabic words without currency"""
    units = [
        "",
        "واحد",
        "اثنان",
        "ثلاثة",
        "أربعة",
        "خمسة",
        "ستة",
        "سبعة",
        "ثمانية",
        "تسعة",
    ]
    tens = [
        "",
        "عشرة",
        "عشرون",
        "ثلاثون",
        "أربعون",
        "خمسون",
        "ستون",
        "سبعون",
        "ثمانون",
        "تسعون",
    ]
    teens = [
        "عشرة",
        "أحد عشر",
        "اثنا عشر",
        "ثلاثة عشر",
        "أربعة عشر",
        "خمسة عشر",
        "ستة عشر",
        "سبعة عشر",
        "ثمانية عشر",
        "تسعة عشر",
    ]

    if number == 0:
        return "صفر"

    def convert_two_digits(num):
        if num < 10:
            return units[num]
        elif 10 <= num < 20:
            return teens[num - 10]
        else:
            tens_digit = num // 10
            units_digit = num % 10
            if units_digit == 0:
                return tens[tens_digit]
            else:
                return f"{units[units_digit]} و{tens[tens_digit]}"

    if number < 100:
        return convert_two_digits(number)
    elif number < 1000:
        hundreds = number // 100
        remainder = number % 100
        if remainder == 0:
            return f"{units[hundreds]} مئة"
        else:
            return f"{units[hundreds]} مئة و{convert_two_digits(remainder)}"
    elif number < 1000000:
        thousands = number // 1000
        remainder = number % 1000
        if remainder == 0:
            return f"{convert_two_digits(thousands)} ألف"
        else:
            return (
                f"{convert_two_digits(thousands)} ألف و{number_to_words_ar(remainder)}"
            )
    else:
        return str(number)


def draw_ar(draw, x, y, text, font, align="center"):
    # Reshape and reorder Arabic text
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    if align == "right":
        x = x - w - 5
    elif align == "center":
        x = x - w / 2

    draw.text((x, y - h / 2), bidi_text, font=font, fill="black")


def draw_cell(draw, x, y, w, h, text, font, align="center", is_header=False):
    # Draw cell border
    draw.rectangle((x, y, x + w, y + h), outline="black", width=1)

    # ONLY header cells get background (removed product row coloring)
    if is_header:
        draw.rectangle((x + 1, y + 1, x + w - 1, y + h - 1), fill="lightgray")

    # Reshape and reorder Arabic text
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # التأكد من أن النص لا يتعدى حدود الخلية
    if tw > w - 10:
        # تصغير الخط مؤقتاً للنصوص الطويلة
        temp_font = ImageFont.truetype(FONT_BOLD, font.size - 2)
        bbox = draw.textbbox((0, 0), bidi_text, font=temp_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        font_to_use = temp_font
    else:
        font_to_use = font

    if align == "right":
        tx = x + w - tw - 5
    elif align == "left":
        tx = x + 5
    else:
        tx = x + (w - tw) / 2

    ty = y + (h - th) / 2

    draw.text((tx, ty), bidi_text, font=font_to_use, fill="black")


def generate_invoice(sale_data, products_data, width=400):  # تصغير العرض شوية
    settings = SettingsModel()
    shop = settings.get_setting("shop_name")

    # تعديل حجم الخطوط لتكون مناسبة
    f_shop = ImageFont.truetype(FONT_BOLD, 32)
    f_title = ImageFont.truetype(FONT_BOLD, 24)
    f_bold = ImageFont.truetype(FONT_BOLD, 18)
    f_small = ImageFont.truetype(FONT_BOLD, 16)
    f_amount_words = ImageFont.truetype(FONT_BOLD, 16)

    img = Image.new("1", (width, 2000), "white")
    draw = ImageDraw.Draw(img)

    y = 20
    center = width // 2

    # ===== Header =====

    # اسم المحل
    draw_ar(draw, center, y, shop, f_shop)
    y += 45

    # عنوان الفاتورة
    draw_ar(draw, center, y, "فاتورة بيع", f_title)
    y += 35

    # خط فاصل
    draw.line((10, y, width - 10, y), fill="black", width=2)
    y += 15

    # تفاصيل الفاتورة - تعديل التنسيق عشان ما يلتصقوش
    # السطر الأول
    draw_ar(draw, width - 10, y, f"رقم: {sale_data['invoice_number']}", f_bold, "right")
    draw_ar(draw, 10, y, f"تاريخ: {sale_data['date']}", f_bold, "left")
    y += 28

    # السطر الثاني
    draw_ar(draw, width - 10, y, f"وقت: {sale_data['time']}", f_bold, "right")

    # تقليل اسم العميل إذا كان طويل
    customer = sale_data["customer_name"]
    if len(customer) > 12:
        customer = customer[:12] + ".."
    draw_ar(draw, 10, y, f"عميل: {customer}", f_bold, "left")
    y += 28

    # خط فاصل
    draw.line((10, y, width - 10, y), fill="black", width=1)
    y += 15

    # ===== Table =====

    # تعديل عرض الأعمدة لتناسب الطابعة الحرارية
    col_name = 150
    col_qty = 55
    col_price = 85
    col_total = 70
    row_h = 32

    x = 10

    # التحقق من أن مجموع الأعمدة لا يتعدى عرض الفاتورة
    total_width = col_name + col_qty + col_price + col_total
    if total_width > width - 20:
        # تعديل تلقائي إذا كان العرض كبير
        col_name = width - 20 - (col_qty + col_price + col_total)

    # صف العناوين (فقط هذه الخلايا لها خلفية)
    draw_cell(
        draw,
        x + col_name + col_qty + col_price,
        y,
        col_total,
        row_h,
        "الإجمالي",
        f_bold,
        is_header=True,
    )
    draw_cell(
        draw,
        x + col_name + col_qty,
        y,
        col_price,
        row_h,
        "السعر",
        f_bold,
        is_header=True,
    )
    draw_cell(draw, x + col_name, y, col_qty, row_h, "الكمية", f_bold, is_header=True)
    draw_cell(draw, x, y, col_name, row_h, "المنتج", f_bold, is_header=True)

    y += row_h

    # المنتجات (بدون تلوين alternating rows)
    for p in products_data:
        # تقليل اسم المنتج ليناسب العرض
        name = p["name"]
        if len(name) > 14:
            name = name[:14] + "."

        draw_cell(draw, x, y, col_name, row_h, name, f_bold, "right")
        draw_cell(draw, x + col_name, y, col_qty, row_h, f'{p["qty"]}', f_bold)

        # تنسيق السعر بدون كسور عشرية إذا كانت .00
        price = (
            f'{int(p["price"])}' if p["price"] == int(p["price"]) else f'{p["price"]}'
        )
        draw_cell(draw, x + col_name + col_qty, y, col_price, row_h, price, f_bold)

        total = (
            f'{int(p["total"])}' if p["total"] == int(p["total"]) else f'{p["total"]}'
        )
        draw_cell(
            draw,
            x + col_name + col_qty + col_price,
            y,
            col_total,
            row_h,
            total,
            f_bold,
        )

        y += row_h

    y += 10

    # خط فاصل بعد المنتجات
    draw.line((10, y, width - 10, y), fill="black", width=2)
    y += 15

    # ===== Summary Section =====

    def summary(label, value, is_bold=False):
        nonlocal y
        font_to_use = f_bold if is_bold else f_small
        draw_ar(draw, width - 10, y, label, font_to_use, "right")
        # تنسيق القيمة
        formatted_value = f"{int(value)}" if value == int(value) else f"{value}"
        draw_ar(draw, 10, y, formatted_value, font_to_use, "left")
        y += 25

    # الملخص
    summary("الإجمالي الفرعي", sale_data["subtotal"])

    if sale_data["discount"] > 0:
        summary("الخصم", sale_data["discount"])

    if sale_data["tax"] > 0:
        summary("الضريبة", sale_data["tax"])

    # خط فاصل خفيف
    draw.line((10, y, width - 10, y), fill="black", width=1)
    y += 12

    # المجاميع النهائية
    summary("الإجمالي", sale_data["total"], True)
    summary("المدفوع", sale_data["paid"], True)
    summary("الباقي", sale_data["remaining"], True)

    # المبلغ بالكلمات (بدون كلمة "جنيه")
    y += 5
    total_in_words = number_to_words_ar(int(sale_data["total"]))

    # تقسيم النص إذا كان طويلاً
    words_text = f"فقط {total_in_words} لا غير"
    if len(total_in_words) > 30:
        # للأسف النص طويل جداً، هنكتبه في سطرين
        parts = total_in_words.split(" و")
        if len(parts) > 1:
            middle = len(parts) // 2
            part1 = " و".join(parts[:middle])
            part2 = " و".join(parts[middle:])
            draw_ar(draw, center, y, f"فقط {part1}", f_amount_words)
            y += 20
            draw_ar(draw, center, y, f"{part2} لا غير", f_amount_words)
        else:
            draw_ar(draw, center, y, words_text, f_amount_words)
    else:
        draw_ar(draw, center, y, words_text, f_amount_words)
    y += 25

    # خط فاصل
    draw.line((10, y, width - 10, y), fill="black", width=2)
    y += 20

    # ===== Footer =====

    draw_ar(draw, center, y, "شكراً لزيارتكم", f_bold)
    y += 25

    draw_ar(draw, center, y, "Powered By Dealzora", f_small)
    y += 20

    # قص الصورة
    img = img.crop((0, 0, width, y + 30))

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
