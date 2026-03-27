from customtkinter import (
    CTkFrame,
    CTkEntry,
    CTkOptionMenu,
    CTkSegmentedButton,
    CTkScrollableFrame,
    CTkLabel,
    CTkButton,
)
from tkinter import messagebox
from utils.get_stock_tag import get_stock_tag
from utils.key_shortcut import key_shortcut
from utils.image import image
from utils.KeyShortcutsManager import KeyShortcutsManager
from components.TreeView import TreeView


class SearchSection(CTkFrame):
    def __init__(self, parent, data_service):
        super().__init__(parent)
        self.data_service = data_service

        self.shortcuts = KeyShortcutsManager(self)

        self._build_search_section()
        self.bind_keyboard_shortcuts()

    def _build_search_section(self):
        """قسم البحث والفئات في صف واحد"""
        search_container = CTkFrame(self, fg_color="transparent")
        search_container.pack(fill="x", padx=20, pady=5)

        search_container.grid_columnconfigure(0, weight=1)
        search_container.grid_columnconfigure(1, weight=3)

        self.category_menu = self._create_category_menu(search_container)
        self.category_menu.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.fill_categorys()

        self.search_box = self._create_search_box(search_container)
        self.search_box.grid(row=0, column=1, sticky="ew")

        self._bind_events()

    def fill_categorys(self):
        categorys = self.data_service.get_categorys()
        self.category_menu.configure(values=["جميع الفئات"] + categorys)

    def _create_search_box(self, parent):
        search_entry = CTkEntry(
            parent,
            placeholder_text="...ابحث بالاسم أو الباركود 🔍",
            font=("Cairo", 14),
            height=45,
            corner_radius=25,
            border_width=2,
            border_color=("#E0E0E0", "#3E3E3E"),
            fg_color=("#F5F5F5", "#2B2B2B"),
            justify="right",
        )

        def on_focus():
            search_entry.configure(border_color="#0099ff")

        def on_blur():
            search_entry.configure(border_color=("#E0E0E0", "#3E3E3E"))

        key_shortcut(search_entry, "<FocusIn>", on_focus)
        key_shortcut(search_entry, "<FocusOut>", on_blur)

        return search_entry

    def _create_category_menu(self, parent):
        category_menu = CTkOptionMenu(
            parent,
            values=["جميع الفئات"],
            font=("Cairo", 13),
            dropdown_font=("Cairo", 13),
            height=45,
            corner_radius=25,
            fg_color=("#FFFFFF", "#4B4B4B"),
            button_color=("#E0E0E0", "#3E3E3E"),
            button_hover_color="#0078da",
            text_color=("#1A1A1A", "#FFFFFF"),
            command=lambda _: self._on_search(),
        )
        return category_menu

    def _focus_search(self):
        self.search_box.focus_force()

    def bind_keyboard_shortcuts(self):
        self.shortcuts.bind("<F3>", self._focus_search)

    def _bind_events(self):
        key_shortcut(self.search_box, "<Return>", self._barcode_scan_add)
        key_shortcut(self.search_box, "<KeyRelease>", self._on_search)

    def _barcode_scan_add(self):
        if not hasattr(self, "product_table"):
            return
        self._on_search()
        tree = self.product_table.tree.tree
        items = tree.get_children()

        if not items:
            return

        if len(items) == 1:
            tree.selection_set(items[0])
            self.product_table._on_add_product()
            self.search_box.delete(0, "end")
            return

    def _on_search(self):
        keyword = self.search_box.get()
        category = self.category_menu.get()

        results = self.data_service.search_product(keyword, category)

        if hasattr(self, "on_search_callback"):
            self.on_search_callback(results)

    def destroy(self):
        self.shortcuts.unbind_all()
        super().destroy()


class ProductTable(CTkFrame):
    def __init__(self, parent, data_service, sale_state):
        super().__init__(parent)
        self.data_service = data_service
        self.sale_state = sale_state
        self.products = self.load_products()

        self.tree = TreeView(
            self,
            cols=("ID", "باركود", "مخزون", "السعر", "المنتج"),
            width=(20, 130, 80, 80, 200),
        )

        self.refresh_table(self.products)
        self.add_shortcuts()

    def load_products(self):
        return self.data_service.get_products()

    def refresh_table(self, products=None):
        tree = self.tree.tree
        self.products = products if products else self.load_products()
        tree.delete(*tree.get_children())
        for product in self.products:
            p = {
                "id": product[0],
                "name": product[1],
                "barcode": product[2],
                "price": product[4],
                "stock": product[5],
                "low_stock": product[8],
            }
            tree.insert(
                "",
                "end",
                values=(p["id"], p["barcode"], p["stock"], p["price"], p["name"]),
                tags=get_stock_tag(p["stock"], p["low_stock"]),
            )

    def add_shortcuts(self):
        key_shortcut(self.tree.tree, ["<Return>", "<Double-1>"], self._on_add_product)

    def _on_add_product(self):
        tree = self.tree.tree
        selected_rows = tree.selection()
        products = []
        self.is_out_of_stock = False
        if not selected_rows:
            return

        for row in selected_rows:
            values = tree.item(row)["values"]
            product_id = values[0]

            product_data = self.data_service.get_product(product_id)
            unit_id = product_data[11] if len(product_data) > 11 else None
            unit_info = self.data_service.get_unit(unit_id) if unit_id else None

            if not product_data:
                continue

            if product_data[5] <= 0:
                self.is_out_of_stock = True
                continue

            product = {
                "id": product_data[0],
                "name": product_data[1],
                "price": float(product_data[4]),
                "image_path": product_data[7],
                "stock": int(product_data[5]),
                "low_stock": int(product_data[8]),
                "qty": 1,
                "unit": unit_info["unit_name"] if unit_info else "قطعة",
                "sub_unit": unit_info["sub_unit_name"] if unit_info else None,
                "conversion_factor": unit_info["conversion_factor"] if unit_info else 1,
                "current_unit": unit_info["unit_name"] if unit_info else "قطعة",
            }
            products.append(product)

        if self.is_out_of_stock:
            messagebox.showwarning(
                "منتج غير متوفر",
                "بعض المنتجات المحددة غير متوفرة في المخزون وتم تخطيها.",
            )

        self.sale_state.add_products(products)

    def update_products(self, products):
        self.products = products
        self.refresh_table(products)


class ProductCardsView(CTkScrollableFrame):
    """عرض المنتجات على شكل بطاقات صغيرة في Grid"""

    COLUMNS = 4  # عدد الأعمدة في الـ Grid

    def __init__(self, parent, data_service, sale_state):
        super().__init__(parent, height=300)
        self.data_service = data_service
        self.sale_state = sale_state
        self.products = []
        self._image_cache = {}  # تخزين الصور لمنع garbage collection

    def update_products(self, products):
        """تحديث البطاقات بقائمة منتجات جديدة"""
        self.products = products if products else []
        self._render_cards()

    def _render_cards(self):
        """مسح البطاقات القديمة وإعادة الرسم"""
        for widget in self.winfo_children():
            widget.destroy()
        self._image_cache.clear()

        for col in range(self.COLUMNS):
            self.grid_columnconfigure(col, weight=1)

        for idx, product in enumerate(self.products):
            row = idx // self.COLUMNS
            col = idx % self.COLUMNS
            card = self._build_card(product)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _build_card(self, product):
        """بناء بطاقة منتج واحدة"""
        p_id = product[0]
        name = product[1]
        price = product[4]
        stock = product[5]
        low_stock = product[8]
        img_path = product[7] if len(product) > 7 else None

        # تحديد لون الإطار بناءً على المخزون
        if stock <= 0:
            border_color = "#FF4444"
        elif low_stock and stock <= low_stock:
            border_color = "#FFA500"
        else:
            border_color = ("#E0E0E0", "#3E3E3E")

        card = CTkFrame(
            self,
            corner_radius=10,
            border_width=1,
            border_color=border_color,
            fg_color=("#FFFFFF", "#2B2B2B"),
        )

        # ── صورة المنتج ──
        img_label = CTkLabel(
            card,
            text="",
            image=image(img_path, (50, 50)),
            font=("Cairo", 22),
            width=50,
            height=50,
        )
        img_label.pack(pady=(6, 2))

        # ── اسم المنتج ──
        CTkLabel(
            card,
            text=("..." if len(name) > 20 else "") + name[:20],
            font=("Cairo", 11, "bold"),
            text_color=("#1A1A1A", "#FFFFFF"),
            wraplength=110,
            justify="center",
        ).pack(padx=4)

        # ── السعر ──
        CTkLabel(
            card,
            text=f"💰 {price}",
            font=("Cairo", 10, "bold"),
            text_color="#0099ff",
        ).pack()

        # ── زر الإضافة ──
        CTkButton(
            card,
            text="+ إضافة",
            font=("Cairo", 10),
            height=26,
            corner_radius=8,
            fg_color="#0078da",
            hover_color="#005fa3",
            command=lambda pid=p_id: self._add_product_by_id(pid),
        ).pack(side="bottom", padx=6, pady=(0, 6), fill="x")

        return card

    def _add_product_by_id(self, product_id):
        """إضافة منتج بالضغط على زر البطاقة"""
        product_data = self.data_service.get_product(product_id)
        if not product_data:
            return

        if product_data[5] <= 0:
            messagebox.showwarning("منتج غير متوفر", "هذا المنتج غير متوفر في المخزون.")
            return

        unit_id = product_data[11] if len(product_data) > 11 else None
        unit_info = self.data_service.get_unit(unit_id) if unit_id else None

        product = {
            "id": product_data[0],
            "name": product_data[1],
            "price": float(product_data[4]),
            "image_path": product_data[7],
            "stock": int(product_data[5]),
            "low_stock": int(product_data[8]),
            "qty": 1,
            "unit": unit_info["unit_name"] if unit_info else "قطعة",
            "sub_unit": unit_info["sub_unit_name"] if unit_info else None,
            "conversion_factor": unit_info["conversion_factor"] if unit_info else 1,
            "current_unit": unit_info["unit_name"] if unit_info else "قطعة",
        }

        self.sale_state.add_products([product])


class ProductSection(CTkFrame):
    def __init__(self, parent, data_service, sale_state):
        super().__init__(parent)
        self.data_service = data_service
        self.sale_state = sale_state

        # ── شريط التحكم (بحث + زر التبديل) ──
        top_bar = CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x")

        self.search = SearchSection(top_bar, data_service)
        self.search.pack(side="right", fill="x", expand=True)

        self.view_toggle = CTkSegmentedButton(
            top_bar,
            values=["🗂 جدول", "🃏 بطاقات"],
            font=("Cairo", 13),
            selected_color="#0078da",
            selected_hover_color="#005fa3",
            unselected_color=("#E0E0E0", "#3E3E3E"),
            unselected_hover_color=("#CCCCCC", "#4A4A4A"),
            fg_color=("#F0F0F0", "#2B2B2B"),
            text_color=("#1A1A1A", "#FFFFFF"),
            height=38,
            corner_radius=10,
            command=self._on_view_change,
        )
        self.view_toggle.set("🗂 جدول")
        self.view_toggle.pack(side="left", padx=(20, 5), pady=5)

        # ── عرض الجدول ──
        self.table = ProductTable(self, data_service, sale_state)
        self.table.pack(fill="both", expand=True, padx=20)

        # ── عرض البطاقات (مخفي في البداية) ──
        self.cards_view = ProductCardsView(self, data_service, sale_state)
        # لا نعرضه الآن

        # ربط البحث بالعرض الحالي
        self.search.product_table = self.table
        self.search.on_search_callback = self._on_search_results

        # تحميل البطاقات بالبيانات الأولية
        self.cards_view.update_products(self.table.products)

    def _on_view_change(self, value):
        """التبديل بين عرض الجدول والبطاقات"""
        if value == "🗂 جدول":
            self.cards_view.pack_forget()
            self.table.pack(fill="both", expand=True, padx=20)
        else:
            self.table.pack_forget()
            self.cards_view.pack(fill="both", expand=True, padx=20)

    def _on_search_results(self, results):
        """تمرير نتائج البحث لكلا العرضين"""
        self.table.update_products(results)
        self.cards_view.update_products(results)
