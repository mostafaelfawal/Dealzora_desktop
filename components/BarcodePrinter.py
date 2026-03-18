from customtkinter import (
    CTkToplevel,
    CTkFrame,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkScrollableFrame,
)
from tkinter import messagebox
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import tempfile
from models.settings import SettingsModel
from utils.format_currency import format_currency
from utils.is_number import is_number
from utils.ar_support import ar
from utils.key_shortcut import key_shortcut
import win32print
import win32ui
from PIL import ImageWin
import string
import random

class BarcodePrinter:
    def __init__(self, root, products):
        self.root = root
        self.products = products
        self.filtered_products = products
        self.selected_product = None
        self.build_modal()

    # ---------- UI ----------
    def build_modal(self):
        self.modal = CTkToplevel(self.root)
        self.modal.title("طباعة باركود")
        self.modal.geometry("900x700+0+0")
        self.modal.grab_set()
        self.modal.focus_force()
        self.build_layout()

    def build_layout(self):
        container = CTkFrame(self.modal)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT (Search + List)
        left = CTkFrame(container, width=300)
        left.pack(side="left", fill="y", padx=(0, 10))

        self.search_entry = CTkEntry(
            left,
            placeholder_text="بحث بالاسم أو الباركود...",
            justify="right",
            font=("Cairo", 16, "bold"),
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)
        key_shortcut(self.search_entry, "<KeyRelease>", self.handle_search)

        self.products_list = CTkScrollableFrame(left)
        self.products_list.pack(fill="both", expand=True, padx=10, pady=10)

        # RIGHT (Fields + Preview)
        right = CTkFrame(container)
        right.pack(side="left", fill="both", expand=True)

        self.build_fields(right)
        self.build_preview(right)
        self.render_products()

    # ---------- Search ----------
    def handle_search(self, event=None):
        if not len(self.filtered_products):
            self.filtered_products = self.products
            return
        keyword = self.search_entry.get().lower()
        self.filtered_products = [
            p
            for p in self.products
            if keyword in (p[1] or "").lower() or keyword in (p[2] or "").lower()
        ]
        self.render_products()

    # ---------- Products List ----------
    def render_products(self):
        for widget in self.products_list.winfo_children():
            widget.destroy()
        if len(self.filtered_products):
            for p in self.filtered_products:
                CTkButton(
                    self.products_list,
                    text=f"{p[1]}",
                    anchor="e",
                    font=("Cairo", 12, "bold"),
                    command=lambda prod=p: self.select_product(prod),
                ).pack(fill="x", pady=2)
        else:
            CTkLabel(
                self.products_list,
                text="لا يوجد منتجات",
                text_color="gray",
                anchor="center",
                font=("Cairo", 16, "bold"),
            ).pack(expand=True)

    def select_product(self, product):
        self.selected_product = product
        # Fill fields
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, product[1])
        self.barcode_entry.delete(0, "end")
        self.barcode_entry.insert(0, product[2] or "")
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(product[4]))
        self.copies_entry.delete(0, "end")
        c = str(product[5])
        if product[5] <= 0:
            c = "1"
        self.copies_entry.insert(0, c)
        self.update_preview()

    # ---------- Fields ----------
    def build_fields(self, parent):
        frame = CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        self.name_entry = self.create_field(frame, "اسم المنتج")
        self.barcode_entry = self.create_field(frame, "*الباركود")
        self.price_entry = self.create_field(frame, "السعر")
        self.copies_entry = self.create_field(frame, "عدد النسخ")
        CTkButton(
            frame,
            text="تحديث المعاينة",
            font=("Cairo", 16, "bold"),
            command=self.update_preview,
        ).pack(pady=10)

    def create_field(self, parent, label):
        if label == "*الباركود":            
            barcode_frame = CTkFrame(parent, fg_color="transparent")
            barcode_frame.pack(fill="x", padx=10, pady=5)
            CTkLabel(barcode_frame, text=label, font=("Cairo", 16, "bold")).pack(
                side="right", padx=10
            )
            CTkButton(
                    barcode_frame,
                    text="🎲",
                    width=0,
                    font=("Cairo", 16, "bold"),
                    fg_color="#10b981",
                    hover_color="#059669",
                    command=lambda: self.generate_barcode(entry)
            ).pack(side="left", padx=10, pady=8)
        else:
            CTkLabel(parent, text=label, anchor="e", font=("Cairo", 16, "bold")).pack(
                fill="x", padx=10
            )
        entry = CTkEntry(parent, justify="right", font=("Cairo", 16, "bold"))
        entry.pack(fill="x", padx=10, pady=5)
        
        key_shortcut(entry, "<Return>", self.update_preview)
        return entry

    # ---------- Preview ----------
    def generate_barcode(self, entry):
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(15))

        entry.delete(0, "end")
        entry.insert(0, code)
        
    def build_preview(self, parent):
        frame = CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.preview_label = CTkLabel(
            frame, text="المعاينه", font=("Cairo", 16, "bold")
        )
        self.preview_label.pack(expand=True)
        CTkButton(
            parent,
            text="طباعة",
            fg_color="#16a34a",
            font=("Cairo", 16, "bold"),
            command=self.print_barcode,
        ).pack(pady=10)

    def generate_barcode_image(self, code, name="", price=""):
        if not code:
            return None

        # Use Arial font to support Arabic
        try:
            name_font = ImageFont.truetype("arial.ttf", 24)
            price_font = ImageFont.truetype("arial.ttf", 20)
        except:
            name_font = ImageFont.load_default()
            price_font = ImageFont.load_default()

        EAN = barcode.get_barcode_class("code128")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        ean = EAN(code, writer=ImageWriter())
        filename = ean.save(temp_file.name)

        img = Image.open(filename)

        # Resize barcode smaller
        img = img.resize((img.width // 2, img.height // 2))

        # Calculate extra height dynamically
        extra_height = 0
        if name:
            extra_height += 30
        if price.strip():
            extra_height += 25

        # Canvas size
        canvas_width = img.width + 40
        canvas_height = img.height + extra_height + 10  # 10px margin
        new_img = Image.new("RGB", (canvas_width, canvas_height), "white")
        draw = ImageDraw.Draw(new_img)

        y = 5
        # draw name
        if name:
            text_bbox = draw.textbbox((0,0), name, font=name_font)
            text_width = text_bbox[2] - text_bbox[0]
            x = (canvas_width - text_width) // 2
            draw.text((x, y), ar(name), font=name_font, fill="black")
            y += 30

        # draw barcode
        x_barcode = (canvas_width - img.width) // 2
        new_img.paste(img, (x_barcode, y))
        y += img.height + 5

        # draw price
        if price.strip() and is_number(price):
            text_bbox = draw.textbbox((0, 0), price, font=price_font)
            text_width = text_bbox[2] - text_bbox[0]
            x_price = (canvas_width - text_width) // 2
            draw.text((x_price, y), f"{format_currency(float(price))}", font=price_font, fill="black")
        elif price.strip():
            messagebox.showerror("خطأ", "السعر غير صالح، سيتم تجاهله في المعاينة والطباعة")

        return new_img

    def update_preview(self):
        code = self.barcode_entry.get()
        name = self.name_entry.get()
        price = self.price_entry.get()
        self.img = self.generate_barcode_image(code, name, price)
        if self.img:
            from customtkinter import CTkImage

            preview = CTkImage(light_image=self.img, size=(250, 120))
            self.preview_label.configure(image=preview, text="")
            self.preview_label.image = preview
    
    def print_barcode_to_printer(self, img):
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
    # ---------- Print ----------
    def print_barcode(self):
        copies = self.copies_entry.get()
        try:
            copies = int(round(float(copies)))
            if not self.img:
                raise ValueError
            for _ in range(copies):
                self.print_barcode_to_printer(self.img)
        except ValueError:
            return messagebox.showerror("خطأ", "عدد النسخ غير صالح أو لا توجد صورة للطباعة")
        messagebox.showinfo("تم", f"تم ارسال {copies} نسخة للطباعة (تجريبي حالياً)")
