from customtkinter import (
    CTkLabel,
    CTkFrame,
    CTkButton,
    CTkEntry,
    CTkOptionMenu,
)
from tkinter import messagebox
from components.BarcodePrinter import BarcodePrinter
from utils.check_limit import check_limit
from utils.image import image
from utils.key_shortcut import key_shortcut
from utils.is_number import is_number
from utils.import_products import import_products
from utils.export_products import export_products
from utils.get_stock_tag import get_stock_tag
from components.TreeView import TreeView
from components.ProductModal import ProductModal


class Products:
    def __init__(self, root, products_db, suppliers_db):
        self.root = root
        self.products_db = products_db
        self.suppliers_db = suppliers_db

        self.search_after_id = None
        self.products = []
        self.categorys = []
        self.suppliers = [s[1] for s in self.suppliers_db.get_suppliers()]
        self.category_map = {"الكل": "all"}

        self.reload_products_view()

        header = CTkFrame(self.root, fg_color="transparent")
        header.pack(padx=10, pady=10)

        CTkLabel(
            header,
            text="إدارة المنتجات",
            image=image("assets/products.png"),
            font=("Cairo", 40, "bold"),
            compound="left",
        ).pack(side="right", padx=10, pady=10)

        message = """
🔹 تحكم أسرع في جدول المنتجات:

• Ctrl + A → تحديد كل المنتجات
• Ctrl + Shift + A → إزالة تحديد كل المنتجات
• Home → الانتقال لأول منتج
• End → الانتقال لآخر منتج
• Insert → إضافة منتج جديد
• Delete أو Ctrl + D → حذف المنتج المحدد
• Enter أو ضغطة مزدوجة على المنتج → فتح نافذة تعديل المنتج
"""
        CTkButton(
            header,
            text="",
            image=image("assets/information.png"),
            width=0,
            corner_radius=50,
            command=lambda: messagebox.showinfo("معلومات | ادارة المنتجات", message),
        ).pack(side="right", padx=5, pady=5)

        self.init_search_frame()
        self.init_products_table()
        self.init_action_buttons()

    # ---------- Helpers ----------
    def reload_products_view(self):
        self.products = self.get_all_products()
        if hasattr(self, "tree"):
            self.refresh_table()
        self.refresh_categorys()

    def validate_numbers(self, *vals):
        return all(is_number(v) for v in vals)

    # ---------- Search ----------
    def init_search_frame(self):
        frame = CTkFrame(self.root, border_width=1)
        frame.pack(fill="x", padx=10, pady=10)

        CTkButton(
            frame,
            text="اضافة",
            image=image("assets/add_product.png", (20, 20)),
            font=("Cairo", 20, "bold"),
            fg_color="#197c00",
            hover_color="#155c03",
            border_width=1,
            border_color="#123509",
            command=self.add_product_modal,
        ).pack(side="right", padx=10, pady=10)

        self.search_entry = CTkEntry(
            frame,
            font=("Cairo", 20, "bold"),
            justify="right",
            placeholder_text="...ابحث عن منتج",
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
            values=["الأسم", "الباركود"],
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
        self.search_after_id = self.root.after(300, self.apply_search)

    def apply_search(self):
        keyword = self.search_entry.get().strip()
        search_map = {"الأسم": "name", "الباركود": "barcode"}
        search_type = search_map.get(self.search_type.get(), "name")

        selected_category = (
            self.category_filter.get() if hasattr(self, "category_filter") else "الكل"
        )
        category_id = self.category_map.get(selected_category, "all")

        if keyword:
            self.products = self.products_db.search_products_by_query(
                keyword, search_type
            )
        else:
            self.products = self.products_db.get_products_by_category(category_id)

        self.refresh_table()

    # ---------- Table ----------
    def init_products_table(self):
        container = CTkFrame(self.root, border_width=1)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        top = CTkFrame(container, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        self.products_count = CTkLabel(top, font=("Cairo", 20, "bold"))
        self.products_count.pack(side="right", padx=10)

        CTkButton(
            top,
            text="تعديل",
            width=120,
            fg_color="#2563eb",
            hover_color="#1749b6",
            font=("Cairo", 20, "bold"),
            image=image("assets/edit.png"),
            command=self.edit_product_modal,
        ).pack(side="left", padx=5)

        CTkButton(
            top,
            text="حذف",
            width=120,
            fg_color="#dc2626",
            hover_color="#a11616",
            font=("Cairo", 20, "bold"),
            image=image("assets/delete.png"),
            command=self.delete_selected_products,
        ).pack(side="left", padx=5)

        self.category_filter = CTkOptionMenu(
            top,
            values=list(self.category_map.keys()),
            command=self.handle_category_filter,
            font=("Cairo", 16, "bold"),
            dropdown_font=("Cairo", 16),
            width=150,
            height=38,
            corner_radius=10,
            fg_color=("#f1f5f9", "#1f1f1f"),
            button_color=("#3b82f6", "#2563eb"),
            button_hover_color=("#2563eb", "#1749b6"),
            dropdown_fg_color=("#ffffff", "#1f1f1f"),
            dropdown_hover_color=("#e5e7eb", "#2a2a2a"),
            text_color=("black", "white"),
        )
        self.category_filter.set("الكل")
        self.category_filter.pack(side="left", padx=5)

        self.tree = TreeView(
            container,
            ("ID", "الأسم", "الباركود", "الكمية", "سعر البيع"),
            (50, 250, 200, 100, 100),
        )

        # Key Shortcuts
        key_shortcut(
            self.tree.tree,
            ["<Delete>", "<Control-d>", "<Control-D>"],
            self.delete_selected_products,
        )
        key_shortcut(
            self.tree.tree,
            ["<Double-1>", "<Return>", "<Control-e>", "<Control-E>"],
            self.edit_product_modal,
        )
        key_shortcut(self.tree.tree, "<Insert>", self.add_product_modal)

        self.refresh_table()

    def refresh_table(self):
        self.tree.tree.delete(*self.tree.tree.get_children())
        for p in self.products:
            self.tree.tree.insert(
                "",
                "end",
                values=(p[0], p[1], p[2] or "—", p[5], p[4]),
                tags=(get_stock_tag(p[5], p[8]),),
            )
        self.products_count.configure(text=f"عدد المنتجات: {len(self.products)}")

    def handle_category_filter(self, selected):
        cid = self.category_map.get(selected, "all")
        self.products = self.products_db.get_products_by_category(cid)
        self.refresh_table()

    # ---------- CRUD ----------
    def get_all_products(self):
        try:
            return self.products_db.get_products()
        except Exception as e:
            messagebox.showerror("خطأ", str(e))
            return []

    def get_all_categorys(self):
        try:
            return self.products_db.get_categorys()
        except Exception as e:
            messagebox.showerror("خطأ", str(e))
            return []

    def refresh_categorys(self):
        raw = self.get_all_categorys()
        self.categorys.clear()
        self.category_map = {"الكل": "all"}

        for cid, cname in raw:
            self.categorys.append(cname)
            self.category_map[cname] = cid

        if hasattr(self, "category_filter"):
            self.category_filter.configure(values=list(self.category_map.keys()))

    def delete_selected_products(self):
        selected = self.tree.tree.selection()
        if not selected:
            return messagebox.showwarning("تنبيه", "اختر منتج")

        ids = [self.tree.tree.item(i)["values"][0] for i in selected]
        if messagebox.askokcancel("تأكد", "هل انت متأكد؟"):
            self.products_db.delete_products(ids)
            self.reload_products_view()

    # ---------- Modals ----------
    def add_product_modal(self):
        current = len(self.get_all_products())
        if not check_limit("اضافة المنتجات", current):
            return
        ProductModal(
            self.root,
            self.products_db,
            self.suppliers_db,
            mode="add",
            on_success=self.reload_products_view,
        )

    def edit_product_modal(self):
        selected = self.tree.tree.selection()
        if not selected:
            return messagebox.showwarning("تنبيه", "اختر منتج")

        pid = self.tree.tree.item(selected[0])["values"][0]

        ProductModal(
            self.root,
            self.products_db,
            self.suppliers_db,
            mode="edit",
            product_id=pid,
            on_success=self.reload_products_view,
        )

    # ---------- Buttons ----------
    def init_action_buttons(self):
        frame = CTkFrame(self.root, border_width=1)
        frame.pack(padx=10, pady=10)

        CTkButton(
            frame,
            text="Excel/CVS استيراد",
            fg_color="#af6300",
            hover_color="#854b00",
            font=("Cairo", 20, "bold"),
            image=image("assets/import_products.png"),
            command=lambda: import_products(self),
        ).pack(side="left", padx=5)

        CTkButton(
            frame,
            text="Excel/CVS تصدير",
            fg_color="#af7800",
            hover_color="#946500",
            font=("Cairo", 20, "bold"),
            image=image("assets/export_products.png"),
            command=lambda: export_products(
                self.products, self.products_db.get_category
            ),
        ).pack(side="left", padx=5, pady=10)

        CTkButton(
            frame,
            text="انشاء باركود",
            fg_color="#008caf",
            hover_color="#00728f",
            image=image("assets/barcode.png"),
            font=("Cairo", 20, "bold"),
            command=self.print_barcode,
        ).pack(side="left", padx=5, pady=10)

    def print_barcode(self):
        BarcodePrinter(self.root, self.products)