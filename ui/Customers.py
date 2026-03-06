from customtkinter import (
    StringVar,
    CTkLabel,
    CTkFrame,
    CTkEntry,
    CTkButton,
    CTkOptionMenu,
    CTkSegmentedButton,
    CTkToplevel,
)
from tkinter import messagebox
from utils.image import image
from utils.is_number import is_number
from utils.key_shortcut import key_shortcut
from utils.center_modal import center_modal
from components.TreeView import TreeView
from components.BackupButton import BackupButton


class Customers:
    def __init__(self, root, customers_db):
        self.root = root
        self.customers_db = customers_db
        self.customers = self.get_all_customers()
        self.customer_selected_phone = ""
        self.search_after_id = None
        self.filter_debt = StringVar(value="الكل")

        # عنوان الواجهة
        CTkLabel(
            self.root,
            text="إدارة العملاء",
            image=image("assets/عملاء.png"),
            font=("Cairo", 40, "bold"),
            compound="left",
        ).pack(padx=10, pady=10)

        self.init_search_frame()
        self.init_customers_table()
        self.init_action_buttons()

    # ------------------------ Helpers ------------------------
    def get_all_customers(self):
        try:
            return self.customers_db.get_customers()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ اثناء جلب بيانات العملاء: \n{e}")
            return []

    def get_debt_tag(self, debt):
        if debt < 0:
            return "warning"  # دائن
        elif debt == 0:
            return "success"  # غير مديون
        else:
            return "danger"  # مديون

    def validate_customer_fields(self, name, debt):
        if not name:
            messagebox.showerror("خطأ", "اكتب اسم العميل اولاً!")
            return False
        if not is_number(debt):
            messagebox.showerror("خطأ", "يجب ادخال حجم الدين بشكل صحيح")
            return False
        return True

    # ------------------------ Search Frame ------------------------
    def init_search_frame(self):
        frame = CTkFrame(self.root, border_width=1)
        frame.pack(fill="x", padx=10, pady=10)

        CTkButton(
            frame,
            text="اضافة",
            image=image("assets/اضافة_عميل.png", (20, 20)),
            font=("Cairo", 20, "bold"),
            fg_color="#197c00",
            hover_color="#155c03",
            border_width=1,
            border_color="#123509",
            command=self.add_customer_modal,
        ).pack(side="right", padx=10, pady=10)

        self.search_entry = CTkEntry(
            frame,
            font=("Cairo", 20, "bold"),
            justify="right",
            placeholder_text="...ابحث عن عميل",
            border_width=1,
            width=250,
        )
        self.search_entry.pack(side="right", padx=10)
        key_shortcut(self.search_entry, "<KeyRelease>", self.handle_search)

        CTkLabel(frame, text="بحث عن طريق ال", font=("Cairo", 24, "bold")).pack(
            side="right", padx=10
        )

        self.search_type = CTkOptionMenu(
            frame,
            values=["الأسم", "الهاتف"],
            font=("Cairo", 16, "bold"),
            dropdown_font=("Cairo", 16),
            width=140,
            height=38,
            corner_radius=10,
            fg_color="#1f1f1f",
            button_color="#2563eb",
            button_hover_color="#1749b6",
            dropdown_fg_color="#1f1f1f",
            dropdown_hover_color="#2a2a2a",
            text_color="white",
        )
        self.search_type.pack(side="right", padx=10, pady=10)

    def handle_search(self, event=None):
        if self.search_after_id:
            self.root.after_cancel(self.search_after_id)
        self.search_after_id = self.root.after(300, self.apply_filters)

    def apply_filters(self):
        keyword = self.search_entry.get().strip()
        search_map = {"الأسم": "name", "الهاتف": "phone"}
        search_type = search_map.get(self.search_type.get(), "name")

        if keyword and keyword[0] == "0" and search_type == "phone":
            keyword = keyword[1:]  # لتخطي 0 في الأرقام المصريه للتعامل مع SQlite3

        filter_type = self.filter_debt.get()

        customers = self.get_all_customers()

        if keyword:
            customers = [
                c
                for c in customers
                if keyword.lower()
                in str(c[1] if search_type == "name" else c[2]).lower()
            ]

        if filter_type == "مدينين":
            customers = [c for c in customers if float(c[3]) > 0]
        elif filter_type == "غير مدينين":
            customers = [c for c in customers if float(c[3]) == 0]
        elif filter_type == "دائنين":
            customers = [c for c in customers if float(c[3]) < 0]

        self.customers = customers
        self.refresh_table()

    # ------------------------ Table ------------------------
    def init_customers_table(self):
        container = CTkFrame(self.root, border_width=1)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top bar
        top_bar = CTkFrame(container, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.customers_count = CTkLabel(
            top_bar,
            text="",
            font=("Cairo", 20, "bold"),
        )
        self.customers_count.pack(side="right", padx=10)

        CTkButton(
            top_bar,
            text="تعديل",
            width=120,
            fg_color="#2563eb",
            hover_color="#1749b6",
            font=("Cairo", 20, "bold"),
            image=image("assets/تعديل.png"),
            command=self.edit_customer_modal,
        ).pack(side="left", padx=5)

        CTkButton(
            top_bar,
            text="حذف",
            width=120,
            fg_color="#dc2626",
            hover_color="#a11616",
            font=("Cairo", 20, "bold"),
            image=image("assets/حذف.png"),
            command=self.delete_selected_customers,
        ).pack(side="left", padx=5)

        self.filter_buttons = CTkSegmentedButton(
            top_bar,
            values=["الكل", "مدينين", "غير مدينين", "دائنين"],
            variable=self.filter_debt,
            command=lambda v: self.apply_filters(),
            font=("Cairo", 18, "bold"),
            height=40,
            corner_radius=12,
            border_width=1,
            fg_color="#1f1f1f",
            selected_color="#2563eb",
            selected_hover_color="#1749b6",
            unselected_color="#2a2a2a",
            unselected_hover_color="#3a3a3a",
            text_color="white",
        )
        self.filter_buttons.pack(side="left", padx=5)

        self.tree = TreeView(
            container,
            ("ID", "الدين", "الهاتف", "الأسم"),
            (50, 150, 250, 300),
        )

        self.refresh_table()

        # Key Shortcuts
        key_shortcut(self.tree.tree, ["<Delete>", "<Control-d>"], self.on_delete_key)
        key_shortcut(
            self.tree.tree,
            ["<Double-1>", "<Return>", "<Control-e>"],
            self.edit_customer_modal,
        )
        key_shortcut(self.tree.tree, "<Insert>", self.add_customer_modal)

    def refresh_table(self):
        self.tree.tree.delete(*self.tree.tree.get_children())
        for c in self.customers:
            debt = float(c[3])
            self.tree.tree.insert(
                "",
                "end",
                values=(c[0], debt, c[2] or "—", c[1]),
                tags=(self.get_debt_tag(debt),),
            )
        self.customers_count.configure(text=f"عدد العملاء: {len(self.customers)}")

    def on_delete_key(self):
        self.delete_selected_customers()

    # ------------------------ CRUD ------------------------
    def delete_selected_customers(self):
        selected = self.tree.tree.selection()
        if not selected:
            return messagebox.showwarning("تنبيه", "اختر عميل واحد على الأقل")
        ids = [self.tree.tree.item(i)["values"][0] for i in selected]
        if messagebox.askokcancel("تأكد", "هل انت متأكد من الحذف؟"):
            try:
                self.customers_db.delete_customer(ids)
                messagebox.showinfo("تم", "تم حذف العملاء بنجاح")
                self.apply_filters()
            except Exception as e:
                messagebox.showerror("خطأ", str(e))

    def add_customer(self, name, phone, debt, modal):
        try:
            self.customers_db.add_customer(name, phone, debt)
            messagebox.showinfo("تم", "تم اضافة العميل بنجاح")
            modal.destroy()
            self.apply_filters()
        except Exception as e:
            if "UNIQUE constraint failed: customers.phone" in str(e):
                messagebox.showerror("خطأ", "رقم الهاتف مستخدم بالفعل")
            else:
                messagebox.showerror("خطأ", str(e))

    def edit_customer(self, name, phone, debt, id, modal):
        try:
            self.customers_db.update_customer(name, phone, debt, id)
            messagebox.showinfo("تم", "تم تعديل العميل بنجاح")
            modal.destroy()
            self.apply_filters()
        except Exception as e:
            if (
                "UNIQUE constraint failed: customers.phone" in str(e)
                and self.customer_selected_phone != phone
            ):
                messagebox.showerror("خطأ", "رقم الهاتف مستخدم بالفعل")
            else:
                messagebox.showerror("خطأ", str(e))

    # ------------------------ Modals ------------------------
    def _customer_modal(self, mode="add"):
        selected_data = None
        if mode == "edit":
            selected = self.tree.tree.selection()
            if not selected:
                return messagebox.showwarning("تنبيه", "اختر عميل")
            selected_data = self.tree.tree.item(selected[0])["values"]
            self.customer_selected_phone = selected_data[2]

        modal = CTkToplevel()
        modal.title(
            "اضافة عميل | Dealzora" if mode == "add" else "تعديل العميل | Dealzora"
        )
        center_modal(modal)

        fields = ["*الأسم", "الهاتف", "حجم الدين"]
        self.entries = {}
        for i, f in enumerate(fields):
            CTkLabel(modal, text=f, font=("Cairo", 18, "bold")).grid(
                row=i, column=1, sticky="e", padx=10, pady=8
            )
            entry = CTkEntry(
                modal, border_width=1, width=250, font=("Cairo", 16, "bold")
            )
            entry.grid(row=i, column=0, sticky="w", padx=10, pady=8)
            if selected_data:
                if f == "حجم الدين":
                    entry.insert(0, selected_data[1])
                elif f == "الهاتف":
                    entry.insert(0, "" if selected_data[2] == "—" else selected_data[2])
                elif f == "*الأسم":
                    entry.insert(0, selected_data[3])
            self.entries[f] = entry

        def clear_fields():
            for e in self.entries.values():
                e.delete(0, "end")

        def save(event=None):
            name = self.entries["*الأسم"].get().strip()
            phone = self.entries["الهاتف"].get().strip() or None
            debt = self.entries["حجم الدين"].get().strip() or 0
            if not self.validate_customer_fields(name, debt):
                return
            if mode == "add":
                self.add_customer(name, phone, debt, modal)
            else:
                self.edit_customer(name, phone, debt, selected_data[0], modal)

        key_shortcut(modal, "<Return>", save)

        btn_frame = CTkFrame(modal, fg_color="transparent")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        CTkButton(
            btn_frame,
            text="اضافة العميل" if mode == "add" else "تعديل العميل",
            font=("Cairo", 18, "bold"),
            width=150,
            fg_color="#2563eb",
            hover_color="#1749b6",
            image=image("assets/اضافة.png" if mode == "add" else "assets/تعديل.png"),
            command=save,
        ).pack(side="right", padx=10)

        CTkButton(
            btn_frame,
            text="تنظيف الحقول",
            font=("Cairo", 18, "bold"),
            width=150,
            fg_color="#dc2626",
            hover_color="#a11616",
            image=image("assets/تنظيف_الحقول.png"),
            command=clear_fields,
        ).pack(side="right", padx=10)

    def add_customer_modal(self):
        self._customer_modal("add")

    def edit_customer_modal(self):
        self._customer_modal("edit")

    # ------------------------ Buttons ------------------------
    def init_action_buttons(self):
        frame = CTkFrame(self.root, border_width=1)
        frame.pack(padx=10, pady=10)

        BackupButton(frame)
