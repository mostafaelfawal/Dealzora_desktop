from customtkinter import (
    StringVar,
    CTkLabel,
    CTkFrame,
    CTkEntry,
    CTkButton,
    CTkOptionMenu,
    CTkSegmentedButton,
)
from tkinter import messagebox
from utils.image import image
from utils.key_shortcut import key_shortcut
from components.TreeView import TreeView
from components.CustomerModal import CustomerModal


class Customers:
    def __init__(self, root, customers_db):
        self.root = root
        self.customers_db = customers_db
        self.customers = self.get_all_customers()
        self.customer_selected_phone = ""
        self.search_after_id = None
        self.filter_debt = StringVar(value="الكل")
        
        header = CTkFrame(self.root, fg_color="transparent")
        header.pack(padx=10, pady=10)

        # عنوان الواجهة
        CTkLabel(
            header,
            text="إدارة العملاء",
            image=image("assets/customers.png"),
            font=("Cairo", 40, "bold"),
            compound="left",
        ).pack(side="right", padx=10, pady=10)
        
        message = """
🔹 تحكم أسرع في جدول العملاء:

• Ctrl + A → تحديد كل العملاء
• Ctrl + Shift + A → إزالة تحديد كل العملاء
• Home → الانتقال لأول عميل
• End → الانتقال لآخر عميل
• Insert → إضافة عميل جديد
• Delete أو Ctrl + D → حذف العميل المحدد
• Enter أو ضغطة مزدوجة على العميل → فتح نافذة تعديل العميل
"""
        CTkButton(
            header,
            text="",
            image=image("assets/information.png"),
            width=0,
            corner_radius=50,
            command=lambda: messagebox.showinfo("معلومات | ادارة العملاء", message),
        ).pack(side="right", padx=5, pady=5)

        self.init_search_frame()
        self.init_customers_table()

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

    # ------------------------ Search Frame ------------------------
    def init_search_frame(self):
        frame = CTkFrame(self.root, border_width=1)
        frame.pack(fill="x", padx=10, pady=10)

        CTkButton(
            frame,
            text="اضافة",
            image=image("assets/add_customer.png", (20, 20)),
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
            fg_color=("#f1f5f9", "#1f1f1f"),
            button_color=("#3b82f6", "#2563eb"),
            button_hover_color=("#2563eb", "#1749b6"),
            dropdown_fg_color=("#ffffff", "#1f1f1f"),
            dropdown_hover_color=("#e5e7eb", "#2a2a2a"),
            text_color=("black", "white"),
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
            image=image("assets/edit.png"),
            command=self.edit_customer_modal,
        ).pack(side="left", padx=5)

        CTkButton(
            top_bar,
            text="حذف",
            width=120,
            fg_color="#dc2626",
            hover_color="#a11616",
            font=("Cairo", 20, "bold"),
            image=image("assets/delete.png"),
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
            fg_color=("#f1f5f9", "#1f1f1f"),
            unselected_color=("#c7c7c7", "#2a2a2a"),
            unselected_hover_color=("#e6e6e6", "#3a3a3a"),
            text_color=("black", "white"),
        )
        self.filter_buttons.pack(side="left", padx=5)

        self.tree = TreeView(
            container,
            ("ID", "الدين", "الهاتف", "الأسم"),
            (50, 150, 250, 250),
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
    def add_customer_modal(self):
        CustomerModal(
            self.tree,
            self.add_customer,
            self.edit_customer,
        )

    def edit_customer_modal(self):
        CustomerModal(
            self.tree,
            self.add_customer,
            self.edit_customer,
            "edit",
        )
