from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph,
    Image,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utils.format_currency import format_currency
from utils.ar_support import ar
from models.settings import SettingsModel
import subprocess
import os
import tempfile
import threading
from tkinter import messagebox
from num2words import num2words


# ================== Fonts ==================
FONT_BOLD = "assets/fonts/Amiri-Bold.ttf"
FONT_REG = "assets/fonts/Amiri-Regular.ttf"

pdfmetrics.registerFont(TTFont("ArabicBold", FONT_BOLD))
pdfmetrics.registerFont(TTFont("Arabic", FONT_REG))


class A4InvoiceGenerator:

    def __init__(self, sale_data, products_data):
        self.sale = sale_data
        self.products = products_data
        self.settings = SettingsModel()

        # ===== Enhanced Styles =====
        self.shop_title_style = ParagraphStyle(
            name="shop_title",
            fontName="ArabicBold",
            fontSize=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a237e"),
            spaceAfter=5,
        )

        self.shop_info_style = ParagraphStyle(
            name="shop_info",
            fontName="Arabic",
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#455a64"),
            leading=12,
        )

        self.invoice_title_style = ParagraphStyle(
            name="invoice_title",
            fontName="ArabicBold",
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#d32f2f"),
            spaceAfter=10,
            spaceBefore=5,
        )

        self.section_header_style = ParagraphStyle(
            name="section_header",
            fontName="ArabicBold",
            fontSize=14,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#1a237e"),
            spaceAfter=8,
            spaceBefore=5,
        )

        self.normal_style = ParagraphStyle(
            name="n", fontName="Arabic", fontSize=10, alignment=TA_RIGHT, leading=14
        )

        self.bold_style = ParagraphStyle(
            name="b", fontName="ArabicBold", fontSize=11, alignment=TA_RIGHT, leading=14
        )

        self.value_style = ParagraphStyle(
            name="v",
            fontName="ArabicBold",
            fontSize=11,
            alignment=TA_RIGHT,
            leading=14,
            textColor=colors.HexColor("#2c3e50"),
        )

        self.header_style = ParagraphStyle(
            name="h",
            fontName="ArabicBold",
            fontSize=11,
            alignment=TA_CENTER,
            textColor=colors.white,
        )

        self.footer_style = ParagraphStyle(
            name="f",
            fontName="ArabicBold",
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a237e"),
            spaceBefore=15,
        )

    def clean(self, text):
        if text is None:
            return ""
        text = str(text).replace("<", "").replace(">", "")
        return ar(text)

    def A(self, text, style=None):
        if style is None:
            style = self.normal_style
        return Paragraph(self.clean(text), style)

    def generate(self, path):
        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )
        story = []

        # ===== Header with Logo and Shop Info =====
        header_data = []

        # Logo
        logo_path = self.settings.get_setting("logo_path")
        if logo_path and os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.drawHeight = 22 * mm
            logo.drawWidth = 22 * mm
            logo.hAlign = "CENTER"
            header_data.append(logo)

        # Shop Details
        shop_name = self.settings.get_setting("shop_name") or "متجرنا"
        shop_address = self.settings.get_setting("shop_address") or "العنوان"
        shop_phone = self.settings.get_setting("shop_phone") or "الهاتف"

        shop_details = []
        shop_details.append(self.A(shop_name, self.shop_title_style))
        shop_details.append(Spacer(1, 15))
        shop_details.append(self.A(f"{shop_address}", self.shop_info_style))
        shop_details.append(self.A(f"{shop_phone}", self.shop_info_style))

        if header_data:
            header_table = Table(
                [[header_data[0], shop_details]],
                colWidths=[40 * mm, 140 * mm],
                rowHeights=[50 * mm],
            )
        else:
            header_table = Table(
                [[shop_details]],
                colWidths=[180 * mm],
                rowHeights=[50 * mm],
            )

        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 5))

        # Divider Line
        story.append(Paragraph("<hr width='100%' color='#d32f2f'/>", self.normal_style))
        story.append(Spacer(1, 5))

        # Invoice Title
        story.append(self.A("فاتورة بيع", self.invoice_title_style))
        story.append(Spacer(1, 10))

        # ===== Enhanced Info Table =====
        info_data = [
            [
                self.A("رقم الفاتورة", self.bold_style),
                self.A("الوقت", self.bold_style),
                self.A("التاريخ", self.bold_style),
                self.A("العميل", self.bold_style),
            ],
            [
                self.A(self.sale.get("invoice_number", "INV-0000"), self.value_style),
                self.A(self.sale.get("time", "__:__ __"), self.value_style),
                self.A(self.sale.get("date", "____/__/__"), self.value_style),
                self.A(self.sale.get("customer_name", "نقدي"), self.value_style),
            ],
        ]

        info_table = Table(
            info_data, colWidths=[35 * mm, 50 * mm, 35 * mm, 50 * mm], rowHeights=22
        )
        info_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Arabic"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e0e0e0")),
                ]
            )
        )
        story.append(info_table)
        story.append(Spacer(1, 15))

        # ===== Products Section Header =====
        story.append(self.A("المنتجات المشتراة", self.section_header_style))
        story.append(Spacer(1, 5))

        # ===== Enhanced Products Table =====
        data = [
            [
                self.A("الإجمالي", self.header_style),
                self.A("السعر", self.header_style),
                self.A("الكمية", self.header_style),
                self.A("المنتج", self.header_style),
            ]
        ]

        for p in self.products:
            data.append(
                [
                    self.A(format_currency(p.get("total", 0)), self.normal_style),
                    self.A(format_currency(p.get("price", 0)), self.normal_style),
                    self.A(str(p.get("qty", 0)), self.normal_style),
                    self.A(p.get("name", ""), self.bold_style),
                ]
            )

        table = Table(
            data, colWidths=[45 * mm, 40 * mm, 35 * mm, 70 * mm], rowHeights=22
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "ArabicBold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("FONTNAME", (0, 1), (-1, -1), "Arabic"),
                    ("ALIGN", (0, 1), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ffffff")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#fafafa")],
                    ),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 15))

        # ===== Enhanced Summary Table (CLEAN & SIMPLE) =====
        subtotal = self.sale.get("subtotal", 0) or 0
        tax = abs(self.sale.get("tax", 0) or 0)
        discount = abs(self.sale.get("discount", 0) or 0)
        total = abs(self.sale.get("total", 0) or 0)
        paid = self.sale.get("paid", 0) or 0
        remaining = abs(self.sale.get("remaining", 0) or 0)

        summary_data = []

        # ===== Header =====
        summary_data.append([
            self.A("ملخص الفاتورة", ParagraphStyle(
                name="summary_header",
                fontName="ArabicBold",
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.white
            )),
            ""
        ])

        # ===== الإجمالي =====
        summary_data.append([
            self.A(format_currency(subtotal), self.value_style),
            self.A("الإجمالي", self.bold_style)
        ])

        # ===== الخصم =====
        if discount != 0:
            summary_data.append([
                self.A(f"- {format_currency(discount)}", self.value_style),
                self.A("الخصم", self.bold_style)
            ])

        # ===== الضريبة =====
        if tax != 0:
            summary_data.append([
                self.A(format_currency(tax), self.value_style),
                self.A("الضريبة", self.bold_style)
            ])

        # ===== المطلوب =====
        summary_data.append([
            self.A(format_currency(total), self.value_style),
            self.A("المطلوب", self.bold_style)
        ])

        # ===== المدفوع =====
        summary_data.append([
            self.A(format_currency(paid), self.value_style),
            self.A("المدفوع", self.bold_style)
        ])

        # ===== الباقي =====
        if remaining != 0:
            summary_data.append([
                self.A(format_currency(remaining), self.value_style),
                self.A("الباقي", self.bold_style)
            ])

        # ===== Table =====
        row_heights = [28] + [24] * (len(summary_data) - 1)

        summary_table = Table(
            summary_data,
            colWidths=[65 * mm, 65 * mm],
            rowHeights=row_heights
        )

        summary_table.setStyle(
            TableStyle([
                ("SPAN", (0, 0), (-1, 0)),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "ArabicBold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),

                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("GRID", (0, 1), (-1, -1), 0.25, colors.HexColor("#bdbdbd")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),

                # Highlight "المطلوب" (ثابت دايمًا في نفس المكان بعد الترتيب ده)
                ("BACKGROUND", (0, 3 if discount==0 and tax==0 else 4 if (discount!=0 and tax!=0) else 3), (-1, 3 if discount==0 and tax==0 else 4 if (discount!=0 and tax!=0) else 3), colors.HexColor("#fff3e0")),
                ("TEXTCOLOR", (0, 3 if discount==0 and tax==0 else 4 if (discount!=0 and tax!=0) else 3), (-1, 3 if discount==0 and tax==0 else 4 if (discount!=0 and tax!=0) else 3), colors.HexColor("#d32f2f")),
            ])
        )

        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # ===== Amount in Words =====
        amount_words = self.number_to_arabic_words(int(total))

        amount_style = ParagraphStyle(
            name="amount_words",
            fontName="ArabicBold",
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#2c3e50"),
            leading=16,
            spaceBefore=10,
            spaceAfter=10,
        )

        story.append(self.A(amount_words, amount_style))
        story.append(Spacer(1, 5))
        
        # ===== Professional Footer =====
        footer_lines = [
            ("شكرا لزيارتكم", "#1a237e", 14, "ArabicBold"),
            ("Powered By Dealzora", "#727272", 10, "ArabicBold"),
        ]

        for text, color, size, font in footer_lines:
            style = ParagraphStyle(
                name="footer_line",
                fontName=font,
                fontSize=size,
                alignment=TA_CENTER,
                textColor=colors.HexColor(color),
                leading=size+2,
                spaceAfter=3,
            )
            story.append(self.A(text, style))

        story.append(Spacer(1, 10))

        doc.build(story)

    def number_to_arabic_words(self, number):
        try:
            words = num2words(number, lang='ar')
            c = self.settings.get_setting("currency_name") or "جنيهاً"
            return f"مطلوب {words} {c} لا غير"
        except:
            return ""


# ================== Printer ==================
class A4Printer:

    def print(self, sale, products):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                path = f.name

            invoice_generator = A4InvoiceGenerator(sale, products)
            invoice_generator.generate(path)

            printer_name = invoice_generator.settings.get_setting("printer_name")
            sumatra_path = "Dealzora_printer.exe"

            if not os.path.exists(sumatra_path):
                raise Exception("Dealzora_printer.exe غير موجود")

            cmd = [
                sumatra_path,
                "-print-to",
                printer_name,
                path,
                "-silent",
                "-exit-when-done",
            ]

            subprocess.run(cmd, timeout=30)

        except Exception as e:
            messagebox.showerror("خطأ في الطباعة", str(e))


# ================== API ==================
def print_A4(sale_data, products_data):

    def run():
        A4Printer().print(sale_data, products_data)

    threading.Thread(target=run, daemon=True).start()
