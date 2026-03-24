from customtkinter import CTkFrame, CTkEntry, CTkOptionMenu
from tkinter import messagebox
from utils.get_stock_tag import get_stock_tag
from utils.key_shortcut import key_shortcut
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
        # إطار أفقي لتوزيع العناصر
        search_container = CTkFrame(self, fg_color="transparent")
        search_container.pack(fill="x", padx=20, pady=5)

        # توزيع المسافات
        search_container.grid_columnconfigure(0, weight=1)  # قائمة الفئات
        search_container.grid_columnconfigure(1, weight=3)  # حقل البحث

        # إنشاء العناصر داخل الإطار
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
        """إنشاء حقل البحث"""
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

        # تأثير التركيز
        def on_focus():
            search_entry.configure(border_color="#0099ff")

        def on_blur():
            search_entry.configure(border_color=("#E0E0E0", "#3E3E3E"))

        key_shortcut(search_entry, "<FocusIn>", on_focus)
        key_shortcut(search_entry, "<FocusOut>", on_blur)

        return search_entry

    def _create_category_menu(self, parent):
        """إنشاء قائمة الفئات"""
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

        # ارجاع القائمة لتمكين التحديث لاحقًا
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

        # لو مفيش نتائج
        if not items:
            return

        # لو نتيجة واحدة → أضف مباشرة
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

        self.refresh_table()
        self.add_shortcuts()

    def load_products(self):
        products = self.data_service.get_products()
        return products

    def refresh_table(self):
        tree = self.tree.tree
        # تنظيف البيانات في الجدول
        tree.delete(*tree.get_children())
        # ملأ الجدول بالبيانات الجديدة
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
            if not product_data:
                continue
            
            if product_data[5] <= 0:  # لو المخزون صفر أو أقل
                self.is_out_of_stock = True
                continue

            # جهز المنتج
            product = {
                "id": (product_data[0]),
                "name": product_data[1],
                "price": float(product_data[4]),
                "image_path": product_data[7],
                "stock": int(product_data[5]),
                "low_stock": int(product_data[8]),
                "qty": 1,
            }
            products.append(product)

        if self.is_out_of_stock:
            messagebox.showwarning(
                "منتج غير متوفر",
                f"بعض المنتجات المحددة غير متوفرة في المخزون وتم تخطيها.",
            )

        self.sale_state.add_products(products)

    def update_products(self, products):
        self.products = products
        self.refresh_table()


class ProductSection(CTkFrame):
    def __init__(self, parent, data_service, sale_state):
        super().__init__(parent)

        self.search = SearchSection(self, data_service)
        self.search.pack(fill="x")

        self.table = ProductTable(self, data_service, sale_state)
        self.table.pack(fill="both", expand=True, padx=20)
        self.search.product_table = self.table

        # ربط البحث بالجدول
        self.search.on_search_callback = self.table.update_products
