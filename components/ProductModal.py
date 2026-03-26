from customtkinter import (
    CTkToplevel,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkComboBox,
    CTkFrame,
    CTkOptionMenu,
)
from tkinter import messagebox, StringVar
from utils.center_modal import center_modal
from utils.key_shortcut import key_shortcut
from utils.is_number import is_number
from utils.image import image
from components.UploadImage import UploadImage
import string
import random


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
        self.units = self.get_units()  # Get units list
        self.units_dict = self.get_units_dict()  # Get units with IDs

        self.selected_product = None
        if self.mode == "edit" and self.product_id:
            self.selected_product = self.products_db.get_product(self.product_id)

        self.build_modal()

    def get_units(self):
        """Get all units from database"""
        try:
            self.products_db.cur.execute("SELECT id, name FROM units")
            units = self.products_db.cur.fetchall()
            return [u[1] for u in units]
        except:
            return []

    def get_units_dict(self):
        """Get units dictionary with name as key and id as value"""
        try:
            self.products_db.cur.execute("SELECT id, name FROM units")
            units = self.products_db.cur.fetchall()
            return {u[1]: u[0] for u in units}
        except:
            return {}

    def get_unit_id_by_name(self, unit_name):
        """Get unit ID by name"""
        return self.units_dict.get(unit_name)

    # ================= BUILD =================
    def build_modal(self):
        self.modal = CTkToplevel(self.root)
        self.modal.title(
            "اضافة منتج جديد | Dealzora"
            if self.mode == "add"
            else "تعديل المنتج | Dealzora"
        )
        self.modal.grab_set()
        self.modal.focus_force()
        self.modal.geometry("+200+0")
        self.modal.resizable(False, False)

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

        # ================= Unit Row =================
        # Unit Label
        CTkLabel(self.modal, text="الوحدة", font=("Cairo", 18, "bold")).grid(
            row=3, column=1, padx=(0, 10), sticky="e"
        )
        
        unit_frame = CTkFrame(self.modal, fg_color="transparent")
        unit_frame.grid(row=3, column=0, pady=10, padx=10)

        # Add Unit Button
        CTkButton(
            unit_frame,
            text="",
            image=image("assets/add.png", (20, 20)),
            width=40,
            font=("Cairo", 14, "bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.show_add_unit_modal,
        ).pack(side="right", padx=10)

        # Unit OptionMenu
        self.unit_var = StringVar()

        self.unit_select = CTkOptionMenu(
            unit_frame,
            values=self.units,
            variable=self.unit_var,
            width=200,
            font=("Cairo", 16, "bold"),
            dropdown_font=("Cairo", 16),
            fg_color="#1f538d",
            button_color="#1f538d",
            button_hover_color="#2b6aaf",
        )
        self.unit_select.pack(side="right", padx=5)

        # ================= Fields =================
        fields = [
            "*الأسم",
            "الباركود",
            "سعر الشراء",
            "*سعر البيع",
            "الكمية",
            "حد التنبيه",
        ]

        self.entries = {}

        for i, f in enumerate(fields, 4):  # Start from row 4
            CTkLabel(self.modal, text=f, font=("Cairo", 18, "bold")).grid(
                row=i, column=1, sticky="e", padx=10, pady=8
            )
            if f == "الباركود":
                frame = CTkFrame(self.modal, fg_color="transparent")
                frame.grid(row=i, column=0, padx=10, pady=8)

                entry = CTkEntry(frame, width=200, font=("Cairo", 16, "bold"))
                entry.pack(side="left", padx=(0, 5))

                CTkButton(
                    frame,
                    text="🎲",
                    width=0,
                    font=("Cairo", 16, "bold"),
                    fg_color="#10b981",
                    hover_color="#059669",
                    command=self.generate_barcode,
                ).pack(side="left")

            else:
                entry = CTkEntry(self.modal, width=250, font=("Cairo", 16, "bold"))
                entry.grid(row=i, column=0, padx=10, pady=8)

            self.entries[f] = entry

        if self.selected_product:
            self.fill_data()

        key_shortcut(self.modal, "<Return>", self.save)

        btn_frame = CTkFrame(self.modal, fg_color="transparent")
        btn_frame.grid(row=len(fields) + 5, column=0, columnspan=2, pady=15)

        CTkButton(
            btn_frame,
            text="حفظ",
            font=("Cairo", 18, "bold"),
            width=150,
            fg_color="#2563eb",
            command=self.save,
        ).pack(side="right", padx=10)

    def show_add_unit_modal(self):
        """Show modal to add new unit with small unit and conversion factor"""
        add_unit_modal = CTkToplevel(self.modal)
        add_unit_modal.title("اضافة وحدة جديدة | Dealzora")
        add_unit_modal.grab_set()
        add_unit_modal.resizable(False, False)
        add_unit_modal.geometry("450x400")
        center_modal(add_unit_modal)

        # Unit Name
        CTkLabel(add_unit_modal, text="اسم الوحدة", font=("Cairo", 16, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        unit_name_entry = CTkEntry(add_unit_modal, width=250, font=("Cairo", 14))
        unit_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Small Unit Name
        CTkLabel(add_unit_modal, text="الوحدة الصغرى", font=("Cairo", 16, "bold")).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        small_unit_entry = CTkEntry(add_unit_modal, width=250, font=("Cairo", 14))
        small_unit_entry.grid(row=1, column=1, padx=10, pady=10)
        CTkLabel(
            add_unit_modal,
            text="(اختياري - الوحدة الأصغر مثل 'جم' لو الوحدة الأساسية 'كجم')",
            font=("Cairo", 10),
            text_color="gray",
        ).grid(row=2, column=0, columnspan=2, pady=2)

        # Conversion Factor
        CTkLabel(add_unit_modal, text="معامل التحويل", font=("Cairo", 16, "bold")).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        conversion_entry = CTkEntry(add_unit_modal, width=250, font=("Cairo", 14))
        conversion_entry.grid(row=3, column=1, padx=10, pady=10)

        CTkLabel(
            add_unit_modal,
            text="(كم مرة تساوي الوحدة الصغرى؟ مثال: 1000 يعني 1 كجم = 1000 جم)",
            font=("Cairo", 10),
            text_color="gray",
        ).grid(row=4, column=0, columnspan=2, pady=2)

        def save_unit():
            unit_name = unit_name_entry.get().strip()
            small_unit = small_unit_entry.get().strip() or None
            conversion = conversion_entry.get().strip()

            if not unit_name:
                messagebox.showerror("خطأ", "اكتب اسم الوحدة")
                return

            if not conversion:
                messagebox.showerror("خطأ", "اكتب معامل التحويل")
                return

            try:
                conversion = float(conversion)
                if conversion <= 0:
                    messagebox.showerror("خطأ", "معامل التحويل يجب أن يكون أكبر من صفر")
                    return
            except ValueError:
                messagebox.showerror("خطأ", "معامل التحويل يجب أن يكون رقماً")
                return

            try:
                # Check if unit already exists
                self.products_db.cur.execute(
                    "SELECT id FROM units WHERE name=?", (unit_name,)
                )
                if self.products_db.cur.fetchone():
                    messagebox.showerror("خطأ", f"الوحدة '{unit_name}' موجودة بالفعل")
                    return

                # Add unit to database with all fields
                self.products_db.cur.execute(
                    """INSERT INTO units (name, small_unit_name, conversion_factor) 
                       VALUES (?, ?, ?)""",
                    (unit_name, small_unit, conversion),
                )
                self.products_db.con.commit()

                # Refresh units list
                self.units = self.get_units()
                self.units_dict = self.get_units_dict()
                self.unit_select.configure(values=self.units)

                # Auto-select the newly added unit
                self.unit_var.set(unit_name)

                messagebox.showinfo("تم", f"تم اضافة الوحدة '{unit_name}' بنجاح")
                add_unit_modal.destroy()

            except Exception as e:
                messagebox.showerror("خطأ", str(e))

        # Save Button
        button_frame = CTkFrame(add_unit_modal, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        CTkButton(
            button_frame,
            text="حفظ",
            font=("Cairo", 16, "bold"),
            width=100,
            fg_color="#2563eb",
            command=save_unit,
        ).pack(side="left", padx=10)

        CTkButton(
            button_frame,
            text="إلغاء",
            font=("Cairo", 16, "bold"),
            width=100,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=add_unit_modal.destroy,
        ).pack(side="left", padx=10)

    # ================= Fill Edit Data =================
    def generate_barcode(self):
        chars = string.ascii_uppercase + string.digits
        code = "".join(random.choice(chars) for _ in range(15))

        self.entries["الباركود"].delete(0, "end")
        self.entries["الباركود"].insert(0, code)

    def fill_data(self):
        p = self.selected_product

        self.category_select.set(self.products_db.get_category(p[6]))
        self.supplier_select.set(self.suppliers_db.get_supplier(p[9]))

        # Fill unit data if exists
        if len(p) > 11 and p[11]:  # unit_id exists
            self.products_db.cur.execute(
                "SELECT name FROM units WHERE id=?",
                (p[11],),
            )
            unit_data = self.products_db.cur.fetchone()
            if unit_data:
                self.unit_var.set(unit_data[0])

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
        sell = self.entries["*سعر البيع"].get() or 0
        qty = self.entries["الكمية"].get() or 0
        low = self.entries["حد التنبيه"].get() or 5
        supplier = self.supplier_select.get().strip() or None

        # Get unit ID from selected unit name
        unit_name = self.unit_var.get().strip()
        unit_id = None

        if unit_name:
            # Get unit ID from the units dictionary
            unit_id = self.get_unit_id_by_name(unit_name)
            if not unit_id:
                # If unit doesn't exist in dictionary, try to get from database
                try:
                    self.products_db.cur.execute(
                        "SELECT id FROM units WHERE name=?", (unit_name,)
                    )
                    row = self.products_db.cur.fetchone()
                    if row:
                        unit_id = row[0]
                        # Update dictionary
                        self.units_dict[unit_name] = unit_id
                except:
                    pass

        p = self.selected_product
        diffrent_name = True

        if p:
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
                    float(qty),
                    self.upload_widget.get_image(),
                    int(low),
                    category_name=self.category_select.get(),
                    supplier_name=supplier,
                    unit_id=unit_id,  # Pass unit_id
                )
                messagebox.showinfo("تم", f"تم اضافة المنتج بنجاح\n'{name}'")
            else:
                self.products_db.update_product(
                    name,
                    barcode,
                    float(buy),
                    float(sell),
                    float(qty),
                    self.upload_widget.get_image(),
                    self.product_id,
                    int(low),
                    category_name=self.category_select.get(),
                    supplier_name=supplier,
                    unit_id=unit_id,  # Pass unit_id
                )
                messagebox.showinfo("تم", f"تم تعديل المنتج بنجاح\n'{name}'")

            if self.on_success:
                self.on_success()

            self.modal.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", str(e))
