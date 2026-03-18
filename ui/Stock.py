from customtkinter import (
    CTkFrame,
    CTkButton,
    CTkLabel,
    StringVar,
    CTkEntry,
    CTkOptionMenu,
)
from tkinter import messagebox
from components.TreeView import TreeView
from components.ProductModal import ProductModal
from components.BuyInvoiceModal import BuyInvoiceModal
from utils.image import image
from utils.get_stock_tag import get_stock_tag
from utils.key_shortcut import key_shortcut
from utils.format_currency import format_currency


class Stock:
    def __init__(
        self,
        root,
        users_db,
        uid,
        products_db,
        suppliers_db,
        stock_movements_db,
        settings,
    ):
        self.root = root
        self.users_db = users_db
        self.uid = uid
        self.products_model = products_db
        self.supplier_model = suppliers_db
        self.stock_movement_model = stock_movements_db
        self.settings_db = settings

        self.c = self.settings_db.get_setting("currency")

        self.build_header()
        self.build_stats()
        self.build_controls()
        self.build_table()

        self.refresh_categories()
        self.refresh_table()
        self.setup_keyboard_shortcuts()

    # ================= HEADER =================
    def build_header(self):
        header_frame = CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        # إضافة زر تحديث سريع
        CTkButton(
            header_frame,
            text="⟳ تحديث",
            width=100,
            font=("Cairo", 13),
            fg_color="#1f2937",
            hover_color="#2d3a4f",
            command=self.refresh_table,
        ).pack(side="left", padx=5)

        CTkLabel(
            header_frame,
            text="إدارة المخزون",
            image=image("assets/stock.png", (40, 40)),
            font=("Cairo", 32, "bold"),
            compound="left",
            text_color="#2b7de9",
        ).pack(side="right")

        message = """
🔹 تحكم أسرع في جدول المنتجات:

• Ctrl + A → تحديد كل المنتجات
• Ctrl + Shift + A → إزالة تحديد كل المنتجات
• Home → الانتقال لأول منتج
• End → الانتقال لآخر منتج
• Enter أو ضغطة مزدوجة → فتح نافذة تعديل المنتج
• L → عرض المنتجات المنخفضة فقط
• N → فتح نافذة فاتورة شراء جديدة
• T → فتح نافذة حركات المخزون
• Insert → إضافة منتج جديد
"""
        CTkButton(
            header_frame,
            text="",
            image=image("assets/information.png"),
            width=0,
            corner_radius=50,
            command=lambda: messagebox.showinfo("معلومات | ادارة المخزون", message),
        ).pack(side="right", padx=5, pady=5)

    # ================= STATS =================
    def build_stats(self):
        self.stats_frame = CTkFrame(
            self.root, fg_color=("#CCCCCC", "#111827"), corner_radius=15
        )
        self.stats_frame.pack(fill="x", padx=20)

        # إطار داخلي للتوسيط
        inner_frame = CTkFrame(self.stats_frame, fg_color="transparent")
        inner_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # بطاقة إحصائيات منسقة
        self.total_card = self.create_stat_card(
            inner_frame, "📦 إجمالي المنتجات", "0", "#2563eb"
        )
        self.low_card = self.create_stat_card(
            inner_frame, "⚠ منتجات منخفضة", "0", "#dc2626"
        )
        self.value_card = self.create_stat_card(
            inner_frame, "💰 قيمة المخزون", f"0 {self.c}", "#059669"
        )
        self.potential_profit = self.create_stat_card(
            inner_frame, "💲 الربح المتوقع", f"0 {self.c}", "#059605"
        )

    def create_stat_card(self, parent, title, value, color):
        card = CTkFrame(parent, fg_color=color, corner_radius=12, width=200, height=80)
        card.pack(side="left", padx=10, expand=True, fill="both")

        CTkLabel(card, text=title, font=("Cairo", 13), text_color="white").pack(
            pady=(15, 0)
        )

        label = CTkLabel(
            card, text=value, font=("Cairo", 20, "bold"), text_color="white"
        )
        label.pack(pady=(0, 10))

        return label

    # ================= CONTROLS =================
    def build_controls(self):
        control_frame = CTkFrame(
            self.root, fg_color=("#CCCCCC", "#111827"), corner_radius=15
        )
        control_frame.pack(fill="x", padx=20, pady=10)

        # =========================================
        # الصف الأول: البحث + إضافة منتج
        # =========================================
        search_row = CTkFrame(control_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=15, pady=(15, 10))

        search_row.grid_columnconfigure(0, weight=3)
        search_row.grid_columnconfigure(1, weight=0)
        search_row.grid_columnconfigure(2, weight=0)

        self.search_var = StringVar()
        self.search_var.trace("w", lambda *args: self.filter_products())

        self.search_entry = CTkEntry(
            search_row,
            textvariable=self.search_var,
            justify="right",
            height=40,
            font=("Cairo", 14),
            border_width=2,
            border_color="#374151",
        )
        self.search_entry.grid(row=0, column=0, padx=5, sticky="ew")

        CTkButton(
            search_row,
            text="✕ مسح",
            width=80,
            height=40,
            font=("Cairo", 13),
            fg_color=("#acb9ca", "#4b5563"),
            hover_color=("#909cac", "#6b7280"),
            command=self.clear_search,
            text_color=("black", "white"),
        ).grid(row=0, column=1, padx=5)

        CTkButton(
            search_row,
            text="➕ إضافة منتج جديد",
            font=("Cairo", 14, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=40,
            command=self.open_product_window,
        ).grid(row=0, column=2, padx=5)

        # =========================================
        # الصف الثاني: الفلاتر
        # =========================================
        filter_row = CTkFrame(control_frame, fg_color="transparent")
        filter_row.pack(fill="x", padx=15, pady=(0, 10))

        filter_row.grid_columnconfigure(1, weight=1)
        filter_row.grid_columnconfigure(3, weight=1)

        # التصنيف
        CTkLabel(
            filter_row, text="📂 التصنيف:", font=("Cairo", 14), text_color="#78859c"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.category_var = StringVar(value="الكل")
        self.category_var.trace("w", lambda *args: self.filter_products())

        self.category_menu = CTkOptionMenu(
            filter_row,
            variable=self.category_var,
            values=["الكل"],
            font=("Cairo", 13),
            dropdown_font=("Cairo", 13),
            fg_color=("#acb9ca", "#4b5563"),
            button_color=("#acb9ca", "#4b5563"),
            button_hover_color=("#909dad", "#6b7280"),
            height=35,
            text_color=("black", "white"),
        )
        self.category_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # المورد
        CTkLabel(
            filter_row, text="🏭 المورد:", font=("Cairo", 14), text_color="#78859c"
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.supplier_var = StringVar(value="الكل")
        self.supplier_var.trace("w", lambda *args: self.filter_products())

        self.supplier_menu = CTkOptionMenu(
            filter_row,
            variable=self.supplier_var,
            values=["الكل"],
            font=("Cairo", 13),
            dropdown_font=("Cairo", 13),
            fg_color=("#acb9ca", "#4b5563"),
            button_color=("#acb9ca", "#4b5563"),
            button_hover_color=("#909dad", "#6b7280"),
            height=35,
            text_color=("black", "white"),
        )
        self.supplier_menu.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # =========================================
        # الصف الثالث: الأزرار الخاصة
        # =========================================
        action_row = CTkFrame(control_frame, fg_color="transparent")
        action_row.pack(fill="x", padx=15, pady=(0, 15))

        action_row.grid_columnconfigure(0, weight=1)
        action_row.grid_columnconfigure(1, weight=1)
        action_btns = [
            {
                "text": "عرض المنتجات المنخفضة فقط ⚠",
                "fg": "#b45309",
                "hover": "#92400e",
                "cmd": self.show_low_stock,
            },
            {
                "text": "فاتورة شراء جديده 📜",
                "fg": "#098cb4",
                "hover": "#087b9e",
                "cmd": self.open_buy_invoice_window,
            },
            {
                "text": "حركة المخزون 📦",
                "fg": "#5309b4",
                "hover": "#460897",
                "cmd": self.open_stock_movements,
            },
        ]

        for col, btn in enumerate(action_btns):
            CTkButton(
                action_row,
                text=btn["text"],
                font=("Cairo", 13),
                fg_color=btn["fg"],
                hover_color=btn["hover"],
                height=35,
                command=btn["cmd"],
            ).grid(row=0, column=col, padx=5, pady=5, sticky="ew")

    def open_stock_movements(self):
        """فتح نافذة حركات المخزون"""
        from components.StockMovementModal import StockMovementsModal

        StockMovementsModal(
            self.users_db,
            self.uid,
            self.root,
            self.stock_movement_model,
            self.products_model,
        )

    # ================= TABLE محسن =================
    def build_table(self):
        table_frame = CTkFrame(self.root, corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20)

        # عنوان الجدول
        CTkLabel(
            table_frame,
            text="📋 قائمة المنتجات",
            font=("Cairo", 16, "bold"),
            anchor="e",
        ).pack(anchor="e", padx=15, pady=(15, 5))

        # الجدول
        cols = (
            "ID",
            "الاسم",
            "الباركود",
            "سعر الشراء",
            "سعر البيع",
            "الكمية",
            "حد التنبيه",
            "الفئة",
        )

        width = (50, 120, 100, 80, 80, 80, 80, 110)

        self.tree = TreeView(table_frame, cols, width)
        key_shortcut(
            self.tree.tree,
            ["<Double-1>", "<Return>"],
            lambda: self.open_product_window("edit"),
        )

        # تخصيص ألوان الجدول
        self.tree.tree.configure(height=15)

    # ================= SUPPLIER FUNCTIONS =================
    def open_buy_invoice_window(self):
        """فتح نافذة إضافة مورد جديد"""
        BuyInvoiceModal(
            self.users_db,
            self.uid,
            self.root,
            self.products_model,
            self.supplier_model,
            on_success=self.refresh_table,
        )

    def refresh_categories(self):
        categories = self.products_model.get_categorys()
        names = ["الكل"] + [c[1] for c in categories]
        self.category_menu.configure(values=names)

        # تحديث قائمة الموردين أيضاً
        self.refresh_suppliers()

    def refresh_table(self):
        self.search_var.set("")
        self.category_var.set("الكل")
        self.filter_products()

    def filter_products(self):
        keyword = self.search_var.get().strip()
        selected_category = self.category_var.get()
        selected_supplier = self.supplier_var.get()

        for item in self.tree.tree.get_children():
            self.tree.tree.delete(item)

        products = self.products_model.get_products()

        total_products = 0
        low_stock_count = 0
        total_value = 0
        total_sell_value = 0
        potential_profit_value = 0

        for p in products:
            pid, name, barcode, buy, sell, qty, cat_id, _, low, supplier_id, _ = p
            category_name = self.products_model.get_category(cat_id)
            supplier_name = (
                self.supplier_model.get_supplier_by_id(supplier_id)
                if supplier_id
                else "بدون مورد"
            )

            # فلترة البحث
            if keyword:
                if keyword.lower() not in str(name).lower() and keyword not in str(
                    barcode
                ):
                    continue

            # فلترة التصنيف
            if selected_category != "الكل" and category_name != selected_category:
                continue

            # فلترة المورد
            if (
                selected_supplier != "الكل"
                and supplier_name
                and supplier_name[1] != selected_supplier
            ):
                continue

            # تحديد حالة المخزون
            tag = get_stock_tag(qty, low)
            if tag != "success":
                low_stock_count += 1

            total_value += buy * qty
            total_sell_value += sell * qty
            total_products += 1
            potential_profit_value += qty * (sell - buy)

            self.tree.tree.insert(
                "",
                "end",
                values=(
                    pid,
                    name,
                    barcode or "—",
                    f"{buy:.2f}",
                    f"{sell:.2f}",
                    qty,
                    low,
                    category_name or "بدون تصنيف",
                ),
                tags=(tag,),
            )

        # تحديث الإحصائيات
        self.total_card.configure(text=str(total_products))
        self.low_card.configure(text=str(low_stock_count))
        self.value_card.configure(text=format_currency(total_value))
        self.potential_profit.configure(text=format_currency(potential_profit_value))

    def show_low_stock(self):
        self.search_var.set("")
        self.category_var.set("الكل")

        for item in self.tree.tree.get_children():
            self.tree.tree.delete(item)

        products = self.products_model.get_products()
        low_stock_found = False

        for p in products:
            pid, name, barcode, buy, sell, qty, cat_id, _, low, _, _ = p

            if qty <= low:
                low_stock_found = True
                category_name = self.products_model.get_category(cat_id)
                tag = get_stock_tag(qty, low)

                self.tree.tree.insert(
                    "",
                    "end",
                    values=(
                        pid,
                        name,
                        barcode or "—",
                        f"{buy:.2f}",
                        f"{sell:.2f}",
                        qty,
                        low,
                        category_name or "بدون تصنيف",
                    ),
                    tags=(tag,),
                )

        if not low_stock_found:
            messagebox.showinfo("معلومات", "لا توجد منتجات منخفضة حالياً")
            self.refresh_table()

    def clear_search(self):
        self.search_var.set("")
        self.category_var.set("الكل")
        self.supplier_var.set("الكل")
        self.filter_products()

    # ================= Product window =================
    def open_product_window(self, mode="add"):
        pid = None

        if mode == "edit":
            selected = self.tree.tree.selection()
            if not selected:
                return messagebox.showwarning("تنبيه", "اختر منتج")
            pid = self.tree.tree.item(selected[0])["values"][0]

        ProductModal(
            self.root,
            self.products_model,
            self.supplier_model,
            mode,
            pid,
            on_success=self.filter_products,
        )

    def setup_keyboard_shortcuts(self):
        key_shortcut(self.tree.tree, ["<L>", "<l>"], self.show_low_stock)
        key_shortcut(self.tree.tree, "<Insert>", self.open_product_window)
        key_shortcut(self.tree.tree, ["<N>", "<n>"], self.open_buy_invoice_window)
        key_shortcut(self.tree.tree, ["<T>", "<t>"], self.open_stock_movements)
