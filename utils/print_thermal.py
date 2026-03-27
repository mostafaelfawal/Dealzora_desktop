import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin
from utils.ar_support import ar
from models.settings import SettingsModel
from utils.format_currency import format_currency
from tkinter.messagebox import showerror
from utils.number_to_arabic_words import number_to_arabic_words

FONT_BOLD = "assets/fonts/NotoNaskhArabic-Bold.ttf"


# ================= PAPER SIZE CONFIGURATION =================
def mm_to_pixels(mm, dpi=203):
    """تحويل الملم إلى بكسل بناءً على DPI (نقطة لكل بوصة) للطابعة الحرارية"""
    inches = mm / 25.4
    pixels = int(inches * dpi)
    return pixels


def get_paper_config(paper_size_mm):
    """الحصول على إعدادات الورق حسب الحجم"""
    if paper_size_mm == 58:
        return {
            "width_mm": 58,
            "width_px": mm_to_pixels(58),
            "font_shop": 24,
            "font_title": 20,
            "font_bold": 16,
            "font_small": 14,
            "row_height": 40,
            "padding": 15,
            "inner_padding": 8,
            "summary_spacing": 22,
            "col_ratio": {"name": 0.35, "qty": 0.20, "price": 0.22, "total": 0.23},
        }
    else:  # 80mm (افتراضي)
        return {
            "width_mm": 80,
            "width_px": mm_to_pixels(80),
            "font_shop": 30,
            "font_title": 22,
            "font_bold": 18,
            "font_small": 16,
            "row_height": 45,
            "padding": 20,
            "inner_padding": 12,
            "summary_spacing": 28,
            "col_ratio": {"name": 0.38, "qty": 0.20, "price": 0.21, "total": 0.21},
        }


# ================= RTL TEXT =================
def draw_ar(draw, x, y, text, font, align="center", fill="black"):
    text = ar(str(text))
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    if align == "right":
        x = x - w
    elif align == "center":
        x = x - w / 2

    # ✅ الإصلاح: طرح bbox[1] لتصحيح offset الخط العربي
    draw.text((x, y - bbox[1]), text, font=font, fill=fill)
    return h


def wrap_text(draw, text, font, max_width):
    """تقسيم النص إلى أسطر متعددة حسب العرض المتاح"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]

        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def draw_cell(
    draw, x, y, w, h, text, font, align="center", fill=None, draw_border=True
):
    if fill:
        draw.rectangle((x, y, x + w, y + h), fill=fill)
    if draw_border:
        draw.rectangle((x, y, x + w, y + h), outline="black", width=1)

    max_text_width = w - 10
    lines = wrap_text(draw, str(text), font, max_text_width)
    if not lines:
        lines = [""]

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        # ✅ الإصلاح: استخدم الارتفاع الفعلي مش bbox[3] فقط
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights)

    # ✅ الإصلاح: توسيط حقيقي مع مراعاة offset الخط
    start_y = y + (h - total_height) // 2

    current_y = start_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        # ✅ الإصلاح: طرح bbox[1] عشان تصحح offset الخط العربي
        text_y = current_y - bbox[1]

        if align == "right":
            tx = x + w - tw - 5
        elif align == "left":
            tx = x + 5
        else:
            tx = x + (w - tw) / 2

        draw.text((tx, text_y), ar(line), font=font, fill="black")
        current_y += line_heights[i]

    return max(h, total_height + 10)


# ================= MAIN GENERATOR =================
def generate_invoice(sale_data, products_data, width=None):
    settings = SettingsModel()
    shop = settings.get_setting("shop_name") or "متجرنا"
    phone = settings.get_setting("shop_phone") or ""
    address = settings.get_setting("shop_address") or ""
    currency = settings.get_setting("currency_name")
    sub_currency = settings.get_setting("sub_currency_name")
    paper_size = settings.get_setting("paper_size") or "80"

    # تحويل إلى int إذا كانت string
    if isinstance(paper_size, str):
        paper_size = int(paper_size) if paper_size.isdigit() else 80

    # الحصول على إعدادات الورق
    paper_config = get_paper_config(paper_size)

    # تحديد العرض
    if width is None:
        width = paper_config["width_px"]

    # تحميل الخطوط
    f_shop = ImageFont.truetype(FONT_BOLD, paper_config["font_shop"])
    f_title = ImageFont.truetype(FONT_BOLD, paper_config["font_title"])
    f_bold = ImageFont.truetype(FONT_BOLD, paper_config["font_bold"])
    f_small = ImageFont.truetype(FONT_BOLD, paper_config["font_small"])

    margin = paper_config["padding"]
    inner_padding = paper_config["inner_padding"]
    content_width = width - (margin * 2)

    img = Image.new("1", (width, 3000), "white")
    draw = ImageDraw.Draw(img)

    y = margin
    center = width // 2

    # ===== HEADER =====
    draw_ar(draw, center, y, shop, f_shop, "center")
    y += paper_config["font_shop"] + 10

    if address:
        draw_ar(draw, center, y, address, f_small, "center")
        y += paper_config["font_small"] + 5
    if phone:
        draw_ar(draw, center, y, phone, f_small, "center")
        y += paper_config["font_small"] + 10

    # عنوان الفاتورة - إصلاح مشكلة الرؤية
    # حساب عرض النص أولاً لمعرفة المساحة المطلوبة
    temp_text = "فاتورة بيع"
    temp_bbox = draw.textbbox((0, 0), ar(temp_text), font=f_title)
    text_height = temp_bbox[3] - temp_bbox[1]

    # حساب ارتفاع الخلفية (إضافة مسافة أعلى وأسفل النص)
    title_padding = 12
    title_height = text_height + (title_padding * 2)
    title_y = y

    # رسم الخلفية السوداء
    draw.rectangle(
        (margin, title_y, width - margin, title_y + title_height), fill="black"
    )

    # رسم النص في المنتصف تماماً
    text_x = center
    text_y = title_y + title_height // 2

    # رسم النص مع إزاحة بسيطة لضمان ظهوره كاملاً
    draw_ar(draw, text_x, text_y, "فاتورة بيع", f_title, "center", "white")

    y += title_height + 15

    # ===== INFO =====
    info_spacing = paper_config["font_bold"] + 5
    draw_ar(
        draw,
        width - margin,
        y,
        f"رقم الفاتورة: {sale_data['invoice_number']}",
        f_bold,
        "right",
    )
    draw_ar(draw, margin, y, f"التاريخ: {sale_data['date']}", f_bold, "left")
    y += info_spacing
    draw_ar(draw, width - margin, y, f"الوقت: {sale_data['time']}", f_bold, "right")
    draw_ar(draw, margin, y, f"العميل: {sale_data['customer_name']}", f_bold, "left")
    y += info_spacing + 5

    # ===== TABLE =====
    total_width = content_width

    # حساب عرض الأعمدة - تصحيح ترتيب الأعمدة ليكون المنتج أولاً
    col_ratio = paper_config["col_ratio"]
    col_name = int(total_width * col_ratio["name"])
    col_qty = int(total_width * col_ratio["qty"])
    col_price = int(total_width * col_ratio["price"])
    col_total = total_width - (col_name + col_qty + col_price)

    # التأكد من الحد الأدنى
    min_width = 40 if paper_size == 58 else 50
    if col_name < min_width:
        col_name = min_width
        remaining = total_width - col_name
        col_qty = int(remaining * 0.3)
        col_price = int(remaining * 0.35)
        col_total = remaining - (col_qty + col_price)

    x = margin
    row_h = paper_config["row_height"]

    # رأس الجدول - ترتيب صحيح: المنتج | الكمية | السعر | الإجمالي
    header_y = y
    draw.rectangle((x, header_y, width - margin, header_y + row_h), fill="black")

    draw_cell(
        draw, x, header_y, col_name, row_h, "المنتج", f_bold, "center", "white", True
    )
    draw_cell(
        draw,
        x + col_name,
        header_y,
        col_qty,
        row_h,
        "الكمية",
        f_bold,
        "center",
        "white",
        True,
    )
    draw_cell(
        draw,
        x + col_name + col_qty,
        header_y,
        col_price,
        row_h,
        "السعر",
        f_bold,
        "center",
        "white",
        True,
    )
    draw_cell(
        draw,
        x + col_name + col_qty + col_price,
        header_y,
        col_total,
        row_h,
        "الإجمالي",
        f_bold,
        "center",
        "white",
        True,
    )

    y += row_h

    # المنتجات
    for p in products_data:
        temp_draw = ImageDraw.Draw(Image.new("1", (width, 100), "white"))
        max_text_width = col_name - 10
        lines = wrap_text(temp_draw, p["name"], f_bold, max_text_width)

        if lines:
            total_height = 0
            for line in lines:
                bbox = temp_draw.textbbox((0, 0), line, font=f_bold)
                total_height += bbox[3] - bbox[1]
            required_height = max(row_h, total_height + 10)
        else:
            required_height = row_h

        draw_cell(
            draw,
            x,
            y,
            col_name,
            required_height,
            p["name"],
            f_bold,
            "right",
            None,
            True,
        )
        draw_cell(
            draw,
            x + col_name,
            y,
            col_qty,
            required_height,
            str(p["qty"]),
            f_bold,
            "center",
            None,
            True,
        )
        draw_cell(
            draw,
            x + col_name + col_qty,
            y,
            col_price,
            required_height,
            format_currency(p["price"]),
            f_bold,
            "center",
            None,
            True,
        )
        draw_cell(
            draw,
            x + col_name + col_qty + col_price,
            y,
            col_total,
            required_height,
            format_currency(p["total"]),
            f_bold,
            "center",
            None,
            True,
        )

        y += required_height

    y += 10

    # ===== SUMMARY BOX =====
    box_x = margin
    box_w = content_width
    header_height = 35
    box_start_y = y  # ✅ احفظ بداية الصندوق


    # حساب عدد العناصر في الملخص
    summary_items = 1  # العنوان
    summary_items += 1  # الإجمالي
    if sale_data.get("discount", 0) > 0:
        summary_items += 1
    if sale_data.get("tax", 0) > 0:
        summary_items += 1
    summary_items += 1  # الخط الفاصل
    summary_items += 3  # المطلوب، المدفوع، الباقي

    # حساب ارتفاع الصندوق
    header_height = 35
    content_height = summary_items * paper_config["summary_spacing"]
    box_height = header_height + content_height + 40

    # رسم الصندوق الخارجي
    draw.rectangle((box_x, y, box_x + box_w, y + box_height), outline="black", width=2)

    # رسم رأس الصندوق
    draw.rectangle((box_x, box_start_y, box_x + box_w, box_start_y + header_height), fill="black")
    title_bbox = draw.textbbox((0, 0), ar("ملخص الفاتورة"), font=f_bold)
    title_h = title_bbox[3] - title_bbox[1]
    title_y = box_start_y + (header_height - title_h) // 2
    draw_ar(draw, box_x + box_w / 2, title_y, "ملخص الفاتورة", f_bold, "center", "white")

    # بداية المحتوى مع مسافات داخلية
    y += header_height + inner_padding

    def draw_summary_row(label, value, is_bold=False, is_total=False):
        nonlocal y
        font_used = f_bold if is_bold else f_bold

        # الرسم الأيمن (التسمية) مع مسافة من اليمين
        right_x = width - margin - inner_padding
        draw_ar(draw, right_x, y, label, font_used, "right")

        # الرسم الأيسر (القيمة) مع مسافة من اليسار
        left_x = margin + inner_padding
        value_text = format_currency(value)
        draw_ar(draw, left_x, y, value_text, font_used, "left")

        # خط سميك تحت المجموع النهائي
        if is_total:
            line_y = y + paper_config["summary_spacing"] - 5
            draw.line(
                (
                    margin + inner_padding,
                    line_y,
                    width - margin - inner_padding,
                    line_y,
                ),
                fill="black",
                width=2,
            )

        y += paper_config["summary_spacing"]

    # عرض البيانات
    draw_summary_row("الإجمالي", sale_data["subtotal"])
    if sale_data.get("discount", 0) > 0:
        draw_summary_row("الخصم", sale_data["discount"])
    if sale_data.get("tax", 0) > 0:
        draw_summary_row("الضريبة", sale_data["tax"])

    # خط فاصل
    y += 5
    draw.line((margin + inner_padding, y, width - margin - inner_padding, y), fill="black", width=1)
    y += paper_config["summary_spacing"] - 10

    draw_summary_row("المطلوب", sale_data["total"], is_bold=True, is_total=True)
    draw_summary_row("المدفوع", sale_data["paid"])
    draw_summary_row("الباقي", sale_data["remaining"])

    y += inner_padding

    # ===== AMOUNT IN WORDS =====
    try:
        box_end_y = y + 5
        draw.rectangle((box_x, box_start_y, box_x + box_w, box_end_y), outline="black", width=2)
        words = number_to_arabic_words(sale_data["total"], currency, sub_currency)
        # تقسيم النص الطويل
        max_word_width = content_width - (inner_padding * 2)
        word_lines = wrap_text(draw, words, f_small, max_word_width)

        y += 10
        for line in word_lines:
            draw_ar(draw, center, y, line, f_small, "center")
            y += paper_config["font_small"] + 5
        y += 10
    except Exception as e:
        print(f"Error in number to words: {e}")
        pass

    # ===== FOOTER =====
    y += 15
    draw_ar(draw, center, y, "شكراً لزيارتكم", f_bold, "center")
    y += 25 if paper_size == 80 else 20
    draw_ar(draw, center, y, "Powered By Dealzora", f_small, "center")

    # اقتصاص الصورة
    img = img.crop((0, 0, width, y + margin))
    return img


# ================= PRINT =================
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
    try:
        img = generate_invoice(sale_data, products_data)
        print_image_to_printer(img, printer_name)
        return True
    except Exception as e:
        showerror("خطأ في الطباعة", str(e))
        return False

