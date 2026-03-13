from customtkinter import (
    CTkToplevel,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkComboBox,
    CTkFrame,
)
from tkinter import messagebox
from utils.center_modal import center_modal
from utils.key_shortcut import key_shortcut
from utils.is_number import is_number
from components.UploadImage import UploadImage


class ProductModal:
    def __init__(
        self,
        root,
        products_db,
        suppliers_db,
        mode="add",
        product_id=None,
        on_success=None,
    ):
        self.root = root
        self.products_db = products_db
        self.suppliers_db = suppliers_db
        self.mode = mode
        self.product_id = product_id
        self.on_success = on_success
        self.categorys = [c[1] for c in self.products_db.get_categorys()]
        self.suppliers = [s[1] for s in self.suppliers_db.get_suppliers()]

        self.selected_product = None
        if self.mode == "edit" and self.product_id:
            self.selected_product = self.products_db.get_product(self.product_id)

        self.build_modal()

    # ================= BUILD =================
    def build_modal(self):
        self.modal = CTkToplevel(self.root)
        self.modal.title(
            "اضافة منتج جديد | Dealzora"
            if self.mode == "add"
            else "تعديل المنتج | Dealzora"
        )
        self.modal.grab_set()
        self.modal.resizable(False, False)
        center_modal(self.modal)

        self.image_frame = CTkFrame(self.modal, fg_color="transparent")
        self.image_frame.grid(row=0, column=0, columnspan=2, pady=10)
        self.upload_widget = UploadImage(self.image_frame)

        # ================= Category =================
        CTkLabel(self.modal, text="الفئة", font=("Cairo", 18, "bold")).grid(
            row=1, column=1, sticky="e", padx=10, pady=8
        )

        self.category_select = CTkComboBox(
            self.modal,
            values=self.categorys,
            width=250,
            font=("Cairo", 16, "bold"),
            dropdown_font=("Cairo", 16),
        )
        self.category_select.set("")
        self.category_select.grid(row=1, column=0)

        # ================= Supplier =================
        CTkLabel(self.modal, text="المورد", font=("Cairo", 18, "bold")).grid(
            row=2, column=1, sticky="e", padx=10, pady=8
        )

        self.supplier_select = CTkComboBox(
            self.modal,
            values=self.suppliers,
            width=250,
            font=("Cairo", 16, "bold"),
            dropdown_font=("Cairo", 16),
        )
        self.supplier_select.set("")
        self.supplier_select.grid(row=2, column=0)

        # ================= Fields =================
        fields = [
            "*الأسم",
            "الباركود",
            "سعر الشراء",
            "سعر البيع",
            "الكمية",
            "حد التنبيه",
        ]

        self.entries = {}

        for i, f in enumerate(fields, 3):
            CTkLabel(self.modal, text=f, font=("Cairo", 18, "bold")).grid(
                row=i, column=1, sticky="e", padx=10, pady=8
            )

            entry = CTkEntry(self.modal, width=250, font=("Cairo", 16, "bold"))
            entry.grid(row=i, column=0, padx=10, pady=8)

            self.entries[f] = entry

        if self.selected_product:
            self.fill_data()

        key_shortcut(self.modal, "<Return>", self.save)

        btn_frame = CTkFrame(self.modal, fg_color="transparent")
        btn_frame.grid(row=len(fields) + 3, column=0, columnspan=2, pady=15)

        CTkButton(
            btn_frame,
            text="حفظ",
            font=("Cairo", 18, "bold"),
            width=150,
            fg_color="#2563eb",
            command=self.save,
        ).pack(side="right", padx=10)

    # ================= Fill Edit Data =================
    def fill_data(self):
        p = self.selected_product

        self.category_select.set(self.products_db.get_category(p[6]))
        self.supplier_select.set(self.suppliers_db.get_supplier(p[9]))

        values = [
            p[1],
            p[2],
            p[3],
            p[4],
            p[5],
            p[8],
        ]

        keys = list(self.entries.keys())

        for k, v in zip(keys, values):
            self.entries[k].insert(0, "" if v is None else str(v))

        self.upload_widget.set_image(p[7])

    # ================= Save =================
    def save(self, event=None):
        name = self.entries["*الأسم"].get().strip()
        barcode = self.entries["الباركود"].get().strip() or None
        buy = self.entries["سعر الشراء"].get() or 0
        sell = self.entries["سعر البيع"].get() or 0
        qty = self.entries["الكمية"].get() or 0
        low = self.entries["حد التنبيه"].get() or 5
        supplier = self.supplier_select.get().strip() or None

        p = self.products_db.get_product(self.product_id)
        diffrent_name = name != p[1]

        if not name:
            return messagebox.showerror("خطأ", "اكتب اسم المنتج")
        if (
            self.products_db.product_exists(name)
            and diffrent_name
            and not messagebox.askokcancel(
                "تأكد", f"هناك منتج موجود بالفعل بهذا الأسم '{name}'\nهل ستضيفه"
            )
        ):
            return

        if not all(is_number(v) for v in [buy, sell, qty, low]):
            return messagebox.showerror("خطأ", "القيم الرقمية غير صحيحة")

        if float(buy) >= float(sell):
            return messagebox.showerror(
                "خطأ", "😏 سعر الشراء اكبر من او يساوي سعر البيع راجع حساباتك"
            )

        try:
            if self.mode == "add":
                self.products_db.add_product(
                    name,
                    barcode,
                    float(buy),
                    float(sell),
                    int(qty),
                    self.upload_widget.get_image(),
                    int(low),
                    category_name=self.category_select.get(),
                    supplier_name=supplier,
                )
                messagebox.showinfo("تم", f"تم اضافة المنتج بنجاح\n'{name}'")
            else:
                self.products_db.update_product(
                    name,
                    barcode,
                    float(buy),
                    float(sell),
                    int(qty),
                    self.upload_widget.get_image(),
                    self.product_id,
                    int(low),
                    category_name=self.category_select.get(),
                    supplier_name=supplier,
                )
                messagebox.showinfo("تم", f"تم تعديل المنتج بنجاح\n'{name}'")

            if self.on_success:
                self.on_success()

            self.modal.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", str(e))
