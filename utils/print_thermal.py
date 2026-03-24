from escpos.printer import Win32Raw
from utils.ar_support import ar
from models.settings import SettingsModel
from utils.format_currency import format_currency
from tkinter.messagebox import showerror
from utils.number_to_arabic_words import number_to_arabic_words


# ================= BUILDER =================
class InvoiceBuilder:
    def __init__(self, width=32):
        self.width = width
        self.lines = []

    def add(self, text=""):
        self.lines.append(ar(str(text)))
    
    def line(self, char="-"):
        self.lines.append(char * self.width)

    def center(self, text):
        text = ar(str(text))
        self.lines.append(text.center(self.width))

    def build(self):
        return "\n".join(self.lines)


# ================= ESC/POS PRINTER =================
class EscposInvoicePrinter:
    def __init__(self, printer_name):
        self.printer = Win32Raw(printer_name)

    def print_text(self, text):
        try:
            self.printer._raw((text + "\n").encode("cp864"))
            self.printer.cut()
        except:
            self.printer._raw((text + "\n").encode("utf-8"))
            self.printer.cut()


# ================= MAIN =================
def build_invoice_text(sale_data, products_data):
    settings = SettingsModel()

    paper_size = settings.get_setting("paper_size")
    width = 32 if paper_size == "58" else 48

    b = InvoiceBuilder(width)

    shop = settings.get_setting("shop_name") or "متجرنا"
    phone = settings.get_setting("shop_phone") or ""
    address = settings.get_setting("shop_address") or ""
    currency = settings.get_setting("currency_name")
    sub_currency = settings.get_setting("sub_currency_name")

    # ===== HEADER =====
    b.center(shop)
    if address:
        b.center(address)
    if phone:
        b.center(phone)

    b.line()
    b.center("فاتورة بيع")
    b.line()

    # ===== INFO =====
    b.add(f"رقم الفاتورة: {sale_data['invoice_number']}")
    b.add(f"التاريخ: {sale_data['date']}")
    b.add(f"الوقت: {sale_data['time']}")
    b.add(f"العميل: {sale_data['customer_name']}")

    b.line()

    # ===== PRODUCTS =====
    for p in products_data:
        b.add(p["name"])
        b.add(f"{p['qty']} × {format_currency(p['price'])}")
        b.add(f"= {format_currency(p['total'])}")
        b.line()

    # ===== SUMMARY =====
    b.add(f"الإجمالي: {format_currency(sale_data['subtotal'])}")

    if sale_data["discount"] > 0:
        b.add(f"الخصم: {format_currency(sale_data['discount'])}")

    if sale_data["tax"] > 0:
        b.add(f"الضريبة: {format_currency(sale_data['tax'])}")

    b.line()

    b.add(f"المطلوب: {format_currency(sale_data['total'])}")
    b.add(f"المدفوع: {format_currency(sale_data['paid'])}")
    b.add(f"الباقي: {format_currency(sale_data['remaining'])}")

    # ===== AMOUNT IN WORDS =====
    try:
        words = number_to_arabic_words(
            sale_data["total"], currency, sub_currency
        )
        b.line()
        b.center(words)
    except:
        pass

    # ===== FOOTER =====
    b.line()
    b.center("شكراً لزيارتكم")
    b.center("Powered By Dealzora")

    return b.build()

# ================= CASH DRAWER =================
def open_cash_drawer(printer_name):
    from escpos.printer import Win32Raw

    p = Win32Raw(printer_name)

    try:
        # أمر فتح الدرج
        p._raw(b'\x1b\x70\x00\x19\xfa')
    except Exception as e:
        print("Drawer Error:", e)

# ================= PRINT =================
def print_shop_invoice(sale_data, products_data, preview=False):
    settings = SettingsModel()
    printer_name = settings.get_setting("printer_name")

    try:
        invoice_text = build_invoice_text(sale_data, products_data)

        # 👀 Preview
        if preview:
            print("\n" + "="*40)
            print(invoice_text)
            print("="*40 + "\n")
            return True

        # 🖨️ Print
        printer = EscposInvoicePrinter(printer_name)
        printer.print_text(invoice_text)
        open_cash_drawer(printer_name)

        return True

    except Exception as e:
        showerror("خطأ في الطباعة", str(e))
        return False