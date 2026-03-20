import threading

from customtkinter import (
    StringVar,
    CTkFrame,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkOptionMenu,
    CTkScrollableFrame,
    CTkRadioButton,
    CTkToplevel,
)
from tkinter import messagebox

# ========= Utils ==============
from utils.clear import clear
from utils.is_number import is_number
from utils.key_shortcut import key_shortcut
from utils.center_modal import center_modal
from utils.get_stock_tag import get_stock_tag
from utils.image import image
from utils.format_currency import format_currency

from time import strftime
from components.TreeView import TreeView
from components.CustomerModal import CustomerModal


class Sale:
    """
    Main sales interface for processing customer transactions.
    Handles product selection, cart management, discounts, taxes, and payment.
    """

    def __init__(
        self,
        root,
        products_db,
        customers_db,
        sales_db,
        sale_items_db,
        stock_movements_db,
        settings_db,
        selected_products,
        customer_var,
        customer_id,
        discount_type,
        discount_value,
        con,
        uid,
        users_db,
    ):
        # Store root window reference
        self.root = root

        # Database connections
        self._init_databases(
            products_db,
            customers_db,
            sales_db,
            sale_items_db,
            stock_movements_db,
            settings_db,
            con,
            uid,
            users_db,
        )

        # Initialize settings and data
        self._init_settings_and_data(
            selected_products, customer_var, customer_id, discount_type, discount_value
        )

        # Build user interface
        self.build_ui()
        self.refresh_table()

        # Load any pre-selected products
        self._load_selected_products()

    # =========================================================================
    # Initialization Methods
    # =========================================================================

    def _init_databases(
        self,
        products_db,
        customers_db,
        sales_db,
        sale_items_db,
        stock_movements_db,
        settings_db,
        con,
        uid,
        users_db,
    ):
        """Initialize all database connections."""
        self.products_db = products_db
        self.customers_db = customers_db
        self.sales_db = sales_db
        self.sale_items_db = sale_items_db
        self.stock_movements_db = stock_movements_db
        self.settings_db = settings_db
        self.con = con
        self.uid = uid
        self.users_db = users_db

    def _init_settings_and_data(
        self,
        selected_products,
        customer_var,
        customer_id,
        discount_type,
        discount_value,
    ):
        """Load settings and initialize data structures."""
        self.currency = self.settings_db.get_setting("currency")
        self.tax_rate = self.settings_db.get_setting("tax")

        # Product data
        self.products = self._safe_fetch(self.products_db.get_products)
        self.selected_products = selected_products

        # Discount and tax
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.tax_type = "percentage"  # Default tax type

        # Invoice data
        self.invoice_number = self._generate_invoice_number()

        # Customer data
        self.customer_var = customer_var
        self.customer_id = customer_id

        # UI state tracking
        self.category_map = {}
        self.modified_prices = {}

    def _safe_fetch(self, fetch_function):
        """Safely fetch data from database with error handling."""
        try:
            return fetch_function()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")
            return []

    def _generate_invoice_number(self):
        """Generate a unique invoice number based on timestamp."""
        return f'INV-{strftime("%Y%m%d%H%M%S")}'

    # =========================================================================
    # UI Building Methods
    # =========================================================================

    def build_ui(self):
        """Build the complete user interface."""
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self._build_toolbar()
        self._build_products_section()
        self._build_cart_section()
        self._build_total_section()

    def _build_toolbar(self):
        """Build the top toolbar with invoice info and help."""
        toolbar = CTkFrame(self.root, height=50)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))

        # Invoice number display
        self.invoice_number_label = CTkLabel(
            toolbar,
            text=f"{self.invoice_number} :رقم الفاتوره",
            font=("Cairo", 16, "bold"),
            text_color="#0080e9",
        )
        self.invoice_number_label.pack(side="right", padx=5, pady=5)

        # Date display
        self.date_label = CTkLabel(
            toolbar,
            text=f'التاريخ: {strftime("%Y-%m-%d %H:%M")}',
            font=("Cairo", 16, "bold"),
            text_color="#00bae9",
        )
        self.date_label.pack(side="right", padx=5, pady=5)

        # Help button
        self._add_help_button(toolbar)

    def _add_help_button(self, parent):
        """Add help button with information message."""
        help_message = self._get_help_message()
        CTkButton(
            parent,
            text="",
            image=image("assets/information.png"),
            width=0,
            corner_radius=50,
            command=lambda: messagebox.showinfo("معلومات | واجهة البيع", help_message),
        ).pack(side="right", padx=5, pady=5)

    def _get_help_message(self):
        """Return the help message text."""
        return """
🔹 استخدام مربع البحث وإدارة المنتجات:

• إضافة منتجات عن طريق قارئ الباركود أو البحث باسم المنتج
• تصفية جدول المنتجات حسب الفئة عبر مربع الفئات

🔹 تحكم أسرع في جدول المنتجات:

• Enter أو ضغطة مزدوجة → إضافة المنتج
• Ctrl + A → تحديد كل المنتجات
• Ctrl + Shift + A → إزالة تحديد كل المنتجات
• Home → الانتقال لأول منتج
• End → الانتقال لآخر منتج
• Delete أو Ctrl + D → حذف المنتج من السلة
• + أو ↑ → زيادة كمية المنتج
• - أو ↓ → تقليل كمية المنتج

🔹 معلومات إضافية:

• يتم إضافة الديون تلقائيًا للعملاء الذين لم يسددوا الفاتورة بالكامل
• إذا كان العميل دائن وليس مديون، سيتم خصم المطلوب من رصيده المسجل
"""

    def _build_products_section(self):
        """Build the products list section with search and filtering."""
        container = CTkFrame(
            self.root, border_width=1, border_color="#dddddd", corner_radius=8
        )
        container.grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=5)
        container.grid_rowconfigure(0, weight=1)

        self._build_search_frame(container)
        self._build_products_header(container)
        self._build_products_table(container)

    def _build_search_frame(self, parent):
        """Build the search and filter controls."""
        search_frame = CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=3)

        # Search entry
        self.search_var = StringVar()
        self.search_entry = CTkEntry(
            search_frame,
            textvariable=self.search_var,
            justify="right",
            font=("Cairo", 14),
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Bind search events
        key_shortcut(self.search_entry, "<Return>", self._handle_search_enter)
        self.search_var.trace_add("write", lambda *args: self.filter_products())

        # Category dropdown
        self.categorys_menu = CTkOptionMenu(
            search_frame,
            font=("Cairo", 20, "bold"),
            values=["الكل"],
            dropdown_font=("Cairo", 20),
            command=self.filter_products,
        )
        self.categorys_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Populate categories
        self._fill_categories()

    def _build_products_header(self, parent):
        """Build the header for products section."""
        frame = CTkFrame(parent, fg_color="transparent")
        frame.pack(anchor="e", padx=5, pady=5, fill="x")

        CTkLabel(frame, text="قائمة المنتجات", font=("Cairo", 16, "bold")).pack(
            side="right"
        )
        CTkLabel(
            frame,
            text="امسح الباركود — اكتب اسم المنتج — اختر الفئة",
            font=("Cairo", 16, "bold"),
            text_color="#919191",
        ).pack(side="left")

    def _build_products_table(self, parent):
        """Build the products table."""
        self.tree = TreeView(
            parent,
            ("ID", "المنتج", "السعر", "المخزون", "الباركود"),
            (50, 200, 80, 80, 120),
            11,
        )
        key_shortcut(
            self.tree.tree, ["<Double-1>", "<Return>"], self._handle_add_product
        )

    def _build_cart_section(self):
        """Build the shopping cart section."""
        self.cart_frame = CTkFrame(
            self.root, border_width=1, border_color="#dddddd", corner_radius=8
        )
        self.cart_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=5)

        # Cart header
        CTkLabel(
            self.cart_frame, text="🛒 سلة المشتريات", font=("Cairo", 16, "bold")
        ).pack(pady=5)

        # Customer selection
        self._build_customer_selection()

        # Cart counter
        self.cart_count_label = CTkLabel(
            self.cart_frame, text="لم يتم اضافة منتجات بعد", font=("Cairo", 14)
        )
        self.cart_count_label.pack()

        # Scrollable cart area
        self.cart_scrollable = CTkScrollableFrame(self.cart_frame, height=400)
        self.cart_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

    def _build_customer_selection(self):
        """Build the customer selection controls."""
        customers_frame = CTkFrame(self.cart_frame, fg_color="transparent")
        customers_frame.pack(pady=5)

        CTkButton(
            customers_frame,
            text="اختر عميل",
            fg_color="#00aeff",
            hover_color="#009be2",
            width=0,
            font=("Cairo", 18, "bold"),
            command=self._show_customer_dialog,
        ).pack(side="right", padx=5)

        self.selected_customer = CTkLabel(
            customers_frame,
            text=self.customer_var.get(),
            font=("Cairo", 16, "bold"),
        )
        self.selected_customer.pack(side="right", padx=5)

    def _build_total_section(self):
        """Build the totals and actions section."""
        frame = CTkFrame(self.root, corner_radius=8)
        frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Subtotal
        self.subtotal_label = CTkLabel(
            frame, text=f"الإجمالي الفرعي: 0 {self.currency}", font=("Cairo", 14)
        )
        self.subtotal_label.pack(anchor="e")

        # Discount controls
        self._build_discount_controls(frame)

        # Tax controls
        self._build_tax_controls(frame)

        # Total
        self.total_label = CTkLabel(
            frame, text=f"المطلوب: 0 {self.currency}", font=("Cairo", 24, "bold")
        )
        self.total_label.pack(anchor="e", pady=5)

        # Action buttons
        self._build_action_buttons(frame)

    def _build_discount_controls(self, parent):
        """Build discount input controls."""
        discount_frame = CTkFrame(parent, fg_color="transparent")
        discount_frame.pack(anchor="e", pady=2)

        CTkLabel(discount_frame, text=":الخصم", font=("Cairo", 14)).pack(side="right")

        self.discount_value_var = StringVar(value="0")
        discount_entry = CTkEntry(
            discount_frame,
            width=80,
            font=("Cairo", 14),
            textvariable=self.discount_value_var,
            justify="center",
        )
        discount_entry.pack(side="right", padx=5)

        self.discount_type_var = StringVar(value="amount")

        CTkRadioButton(
            discount_frame,
            text=f"{self.currency}",
            variable=self.discount_type_var,
            value="amount",
            font=("Cairo", 13),
            command=self._on_discount_change,
        ).pack(side="right")

        CTkRadioButton(
            discount_frame,
            text="%",
            variable=self.discount_type_var,
            value="percentage",
            font=("Cairo", 13),
            command=self._on_discount_change,
        ).pack(side="right", padx=5)

        self.discount_value_var.trace_add(
            "write", lambda *args: self._on_discount_change()
        )

    def _build_tax_controls(self, parent):
        """Build tax input controls."""
        tax_frame = CTkFrame(parent, fg_color="transparent")
        tax_frame.pack(anchor="e", pady=2)

        CTkLabel(tax_frame, text=":الضريبة", font=("Cairo", 14)).pack(side="right")

        self.tax_var = StringVar(value=str(self.tax_rate))
        tax_entry = CTkEntry(
            tax_frame,
            width=80,
            font=("Cairo", 14),
            textvariable=self.tax_var,
            justify="center",
        )
        tax_entry.pack(side="right", padx=5)

        self.tax_type_var = StringVar(value="percentage")

        CTkRadioButton(
            tax_frame,
            text=f"{self.currency}",
            variable=self.tax_type_var,
            value="amount",
            font=("Cairo", 13),
            command=self._on_tax_change,
        ).pack(side="right")

        CTkRadioButton(
            tax_frame,
            text="%",
            variable=self.tax_type_var,
            value="percentage",
            font=("Cairo", 13),
            command=self._on_tax_change,
        ).pack(side="right", padx=5)

        self.tax_var.trace_add("write", lambda *args: self._on_tax_change())

    def _build_action_buttons(self, parent):
        """Build the cancel and finish buttons."""
        actions_frame = CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(pady=8, fill="x")
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        # Cancel button
        cancel_btn = CTkButton(
            actions_frame,
            text="❎ إلغاء العملية",
            height=45,
            corner_radius=8,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#111827",
            font=("Cairo", 15, "bold"),
            command=self._cancel_sale,
        )
        cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        # Finish button
        finish_btn = CTkButton(
            actions_frame,
            text="✅ إنهاء البيع",
            height=45,
            corner_radius=8,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="white",
            font=("Cairo", 15, "bold"),
            command=self._finish_sale,
        )
        finish_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def _on_discount_change(self):
        """Handle discount value or type change."""
        val = self.discount_value_var.get()

        if not val or not is_number(val):
            self.discount_value = 0
        else:
            self.discount_value = float(val)

        self.discount_type = self.discount_type_var.get()
        self._calculate_total()

    def _on_tax_change(self):
        """Handle tax value or type change."""
        val = self.tax_var.get()

        if not val or not is_number(val):
            self.tax_rate = 0
        else:
            self.tax_rate = float(val)

        self.tax_type = self.tax_type_var.get()
        self._calculate_total()

    def _handle_search_enter(self, event=None):
        """Handle Enter key in search field."""
        keyword = self.search_var.get().strip()

        if not keyword:
            return

        results = self.products_db.search_products(keyword)

        if len(results) == 1:
            self._add_single_product_from_search(results[0])

    def _add_single_product_from_search(self, product_data):
        """Add a single product from search results."""
        status, new_product = self._check_stock(product_data, product_data[0])

        if status == "out_of_stock":
            messagebox.showwarning("تحذير", "هذا المنتج غير متوفر في المخزون")
            return
        elif status == "exceeded":
            messagebox.showwarning("تحذير", "الكمية المطلوبة تتجاوز المخزون")
            return
        elif status == "added" and new_product:
            self.selected_products.append(new_product)
            self._update_product_widget(new_product)

        # Update cart and calculations
        self._update_cart_count()
        self._calculate_total()
        self.search_var.set("")

    def _handle_add_product(self, event=None):
        """Handle adding selected products from table."""
        selected_items = self.tree.tree.selection()
        if not selected_items:
            return

        pids = [self.tree.tree.item(i)["values"][0] for i in selected_items]
        has_stock_issue = False
        added_any = False

        for pid in pids:
            product_data = self.products_db.get_product(pid)
            status, new_product = self._check_stock(product_data, pid)

            if status in ("out_of_stock", "exceeded"):
                has_stock_issue = True
                continue

            if status == "added" and new_product:
                self.selected_products.append(new_product)
                self._update_product_widget(new_product)
                added_any = True
            elif status == "updated":
                added_any = True

        if has_stock_issue:
            messagebox.showwarning("تنبيه", "بعض المنتجات غير متوفرة أو تجاوزت المخزون")

        if added_any:
            self._update_cart_count()
            self._calculate_total()

    # =========================================================================
    # Cart Management Methods
    # =========================================================================

    def _load_selected_products(self):
        """Load previously selected products into cart."""
        if not self.selected_products:
            return

        out_of_stock_alert = False
        for product in self.selected_products:
            product_from_db = self.products_db.get_product(product["id"])
            product["widget"] = None
            product["name"] = product_from_db[1]
            product["price"] = product_from_db[4]
            product["image"] = product_from_db[7]

            if product_from_db[5] < product["qty"]:
                product["qty"] = product_from_db[5]
                out_of_stock_alert = True

            self._update_product_widget(product)

        self._update_cart_count()
        self._calculate_total()

        if out_of_stock_alert:
            messagebox.showwarning(
                "تحذير",
                "هناك بعض المنتجات المختاره تجاوزت حد المخزون\nتم وضع كمياتها الى اقصى حد",
            )

    def _check_stock(self, product_data, product_id):
        """
        Check stock availability and update or create cart item.
        Returns: (status, new_product)
        """
        if product_data[5] <= 0:
            return "out_of_stock", None

        # Check if product already in cart
        for product in self.selected_products:
            if product["id"] == product_id:
                if product["qty"] + 1 > product_data[5]:
                    return "exceeded", None

                product["qty"] += 1
                self._update_product_widget(product)
                return "updated", None

        # Create new product
        new_product = {
            "id": product_data[0],
            "name": product_data[1],
            "price": product_data[4],
            "image": product_data[7],
            "qty": 1,
            "widget": None,
            "sub_total_label": None,
            "qty_entry": None,
            "modified_price": None,
            "modified_price_label": None,
        }

        return "added", new_product

    def _update_product_widget(self, product):
        """Create or update a product widget in the cart."""
        container = product["widget"]

        if not container:
            container = self._create_product_widget_container(product)
            product["widget"] = container

        # Update product display
        self._update_product_display(product)

    def _create_product_widget_container(self, product):
        """Create a new product widget container."""
        container = CTkFrame(
            self.cart_scrollable,
            corner_radius=8,
            border_width=1,
            border_color="#e5e5e5",
        )
        container.pack(side="bottom", fill="x", pady=3, padx=3)

        # Top row with product info
        top_row = self._create_product_info_row(container, product)
        top_row.pack(fill="x", padx=6, pady=4)

        # Quantity controls row
        qty_frame = self._create_quantity_controls(container, product)
        qty_frame.pack(fill="x", padx=6, pady=(0, 6))

        return container

    def _create_product_info_row(self, container, product):
        """Create the top row with product image, name, and subtotal."""
        top_row = CTkFrame(container, fg_color="transparent")

        # Product image
        CTkLabel(top_row, text="", image=image(product["image"]), width=40).pack(
            side="right", padx=(0, 6)
        )

        # Info frame
        info_frame = CTkFrame(top_row, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True)

        # Product name
        CTkLabel(
            info_frame,
            text=product["name"],
            font=("Cairo", 11, "bold"),
            text_color=("#167000", "#00a72a"),
            anchor="e",
        ).pack(fill="x", padx=10)

        # Subtotal label
        sub_total = CTkLabel(
            info_frame,
            text="",
            font=("Cairo", 10),
            text_color=("#6d6d6d", "#b4b4b4"),
            anchor="e",
        )
        sub_total.pack(fill="x", padx=10)
        product["sub_total_label"] = sub_total

        return top_row

    def _create_quantity_controls(self, container, product):
        """Create quantity control buttons and entry."""
        qty_frame = CTkFrame(container, fg_color="transparent")

        # Decrease button
        CTkButton(
            qty_frame,
            text="-",
            width=28,
            height=28,
            font=("Cairo", 14, "bold"),
            command=lambda p=product: self._decrease_quantity(p),
        ).pack(side="right", padx=2)

        # Quantity entry
        qty_entry_var = StringVar(value=str(product["qty"]))
        product["qty_entry"] = qty_entry_var

        def on_qty_change(*args):
            self._handle_quantity_change(product, qty_entry_var)

        qty_entry_var.trace_add("write", on_qty_change)

        qty_entry = CTkEntry(
            qty_frame,
            width=40,
            height=28,
            justify="center",
            textvariable=qty_entry_var,
            font=("Cairo", 12, "bold"),
        )
        qty_entry.pack(side="right", padx=2)

        # Bind keyboard shortcuts
        self._bind_quantity_shortcuts(qty_entry, product)

        # Increase button
        CTkButton(
            qty_frame,
            text="+",
            width=28,
            height=28,
            font=("Cairo", 14, "bold"),
            command=lambda p=product: self._increase_quantity(p),
        ).pack(side="right", padx=2)

        # Delete button
        CTkButton(
            qty_frame,
            text="",
            width=28,
            height=28,
            fg_color=("#b30000", "#8f0000"),
            hover_color=("#8D0000", "#740000"),
            image=image("assets/delete.png", (20, 20)),
            command=lambda p=product: self._remove_from_cart(p),
        ).pack(side="left", padx=10)

        return qty_frame

    def _bind_quantity_shortcuts(self, entry, product):
        """Bind keyboard shortcuts to quantity entry."""
        key_shortcut(
            entry,
            ["<Up>", "<plus>", "<KP_Add>"],
            lambda p=product: self._increase_quantity(p),
        )
        key_shortcut(
            entry,
            ["<Down>", "<minus>", "<KP_Subtract>"],
            lambda p=product: self._decrease_quantity(p),
        )
        key_shortcut(
            entry,
            ["<Delete>", "<Control-d>", "<Control-D>"],
            lambda p=product: self._remove_from_cart(p),
        )

    def _handle_quantity_change(self, product, qty_entry_var):
        """Handle manual quantity entry changes."""
        val = qty_entry_var.get()
        if not val:
            qty_entry_var.set("1")
            return

        if not is_number(val):
            qty_entry_var.set(str(product["qty"]))
            return

        try:
            qty = int(val)
        except ValueError:
            qty = float(val)

        prod_data = self.products_db.get_product(product["id"])
        max_qty = prod_data[5]
        if qty > max_qty:
            qty = max_qty
            qty_entry_var.set(str(max_qty))

        product["qty"] = qty
        self._update_product_display(product)

    def _update_product_display(self, product):
        """Update product display with current values."""
        product["sub_total_label"].configure(
            text=f"{product['price']} × {product['qty']} = {format_currency(product['price'] * product['qty'])}"
        )
        product["qty_entry"].set(product["qty"])
        self._update_cart_count()
        self._calculate_total()

    def _decrease_quantity(self, product):
        """Decrease product quantity by 1."""
        if product["qty"] - 1 <= 0:
            self._remove_from_cart(product)
            return
        product["qty"] -= 1
        self._update_product_widget(product)

    def _increase_quantity(self, product):
        """Increase product quantity by 1."""
        prod_data = self.products_db.get_product(product["id"])
        if product["qty"] + 1 > prod_data[5]:
            messagebox.showwarning("تحذير", "الكمية المطلوبة تتجاوز المخزون")
            return
        product["qty"] += 1
        self._update_product_widget(product)

    def _remove_from_cart(self, product):
        """Remove product from cart."""
        if product in self.selected_products:
            self.selected_products.remove(product)
            if product["widget"]:
                product["widget"].destroy()
        self._update_cart_count()
        self._calculate_total()

    def _update_cart_count(self):
        """Update the cart counter display."""
        count = len(self.selected_products)
        total_items = sum(p["qty"] for p in self.selected_products)
        self.cart_count_label.configure(text=f"{total_items} صنف {count} | قطعة")

    # =========================================================================
    # Calculation Methods
    # =========================================================================

    def _calculate_total(self):
        subtotal = self._calculate_subtotal()

        # 🧠 حساب فروقات تعديل السعر
        modified = self._calculate_modified_totals()

        # الخصم الأساسي + خصم من تعديل السعر
        discount = self._calculate_discount(subtotal)
        discount += modified["discount_from_price"]
        discount = min(discount, subtotal)

        after_discount = subtotal - discount

        # الضريبة الأساسية + زيادة من تعديل السعر
        tax = self._calculate_tax(after_discount)
        tax += modified["increase_from_price"]

        total = after_discount + tax

        self._update_total_displays(subtotal, total)
        return total

    def _calculate_subtotal(self):
        """Calculate subtotal from cart items."""
        return sum(p["price"] * p["qty"] for p in self.selected_products)

    def _calculate_discount(self, subtotal):
        """Calculate discount based on type and value."""
        if self.discount_type == "amount":
            return self.discount_value
        else:
            return subtotal * self.discount_value / 100

    def _calculate_tax(self, amount):
        """Calculate tax based on type and value."""
        if self.tax_type == "amount":
            return self.tax_rate
        else:
            return amount * self.tax_rate / 100

    def _update_total_displays(self, subtotal, total):
        """Update subtotal and total labels."""
        self.subtotal_label.configure(
            text=f"الإجمالي الفرعي: {format_currency(subtotal)}"
        )
        self.total_label.configure(text=f"المطلوب: {format_currency(total)}")

    # =========================================================================
    # Sale Completion Methods
    # =========================================================================

    def _cancel_sale(self):
        """Cancel the current sale and start a new one."""
        if messagebox.askokcancel("تأكيد", "هل انت متأكد من الغاء العمليه"):
            self._start_new_sale()
            clear(self.cart_scrollable)
            self._build_cart_section()

    def _finish_sale(self):
        """Finish the sale and show payment dialog."""
        if not self.selected_products:
            messagebox.showwarning("تحذير", "لا توجد منتجات في السلة")
            return

        # Calculate totals
        subtotal = self._calculate_subtotal()
        discount = self._calculate_discount(subtotal)
        discount = min(discount, subtotal)
        after_discount = subtotal - discount
        tax = self._calculate_tax(after_discount)
        total = after_discount + tax

        # Show payment dialog
        self._show_payment_dialog(subtotal, discount, tax, total)

    def _show_payment_dialog(self, subtotal, discount, tax, total):
        """Show the payment completion dialog."""
        dialog = CTkToplevel(self.root)
        dialog.title("إتمام البيع | Dealzora")
        dialog.geometry("500x700+200+0")
        dialog.grab_set()
        dialog.focus_force()

        # Build dialog sections
        self._build_payment_dialog_header(dialog)
        self._build_payment_dialog_products(dialog)
        self._build_payment_dialog_summary(dialog, subtotal, discount, tax, total)
        self._build_payment_dialog_payment(dialog, total)
        self._build_payment_dialog_actions(dialog, subtotal, discount, tax, total)

    def _build_payment_dialog_header(self, dialog):
        """Build the header section of payment dialog."""
        CTkLabel(
            dialog,
            text="تفاصيل الفاتورة",
            font=("Cairo", 18, "bold"),
            text_color="#0080e9",
        ).pack(pady=10)

        info_frame = CTkFrame(dialog)
        info_frame.pack(fill="x", padx=15, pady=5)

        CTkLabel(
            info_frame,
            text=f"{self.invoice_number} :رقم الفاتورة",
            font=("Cairo", 14),
            anchor="e",
        ).pack(fill="x")

        CTkLabel(
            info_frame,
            text=f"العميل: {self.customer_var.get()}",
            font=("Cairo", 14),
            anchor="e",
        ).pack(fill="x")

    def _build_payment_dialog_products(self, dialog):
        """Build the products section of payment dialog."""
        products_frame = CTkScrollableFrame(dialog, height=200)
        products_frame.pack(fill="both", expand=True, padx=15, pady=10)

        for product in self.selected_products:
            self._build_payment_product_row(products_frame, product)

    def _build_payment_product_row(self, parent, product):
        """Build a single product row in payment dialog."""
        row = CTkFrame(parent)
        row.pack(fill="x", pady=2)

        # Product info frame
        product_info_frame = CTkFrame(row, fg_color="transparent")
        product_info_frame.pack(side="right", fill="x", expand=True)

        # Product name and quantity
        CTkLabel(
            product_info_frame,
            text=f"{product['name']}  {product['price']} × {product['qty']}",
            font=("Cairo", 13),
            anchor="e",
        ).pack(fill="x")

        # Price info frame
        price_frame = CTkFrame(product_info_frame, fg_color="transparent")
        price_frame.pack(fill="x", pady=(2, 0))

        CTkLabel(
            price_frame,
            text=":السعر الحالي",
            font=("Cairo", 11),
            text_color="#666666",
            anchor="e",
        ).pack(side="right", padx=(0, 5))

        CTkLabel(
            price_frame,
            text=format_currency(product["price"]),
            font=("Cairo", 11, "bold"),
            text_color="#666666",
            anchor="e",
        ).pack(side="right")

        # Price edit button (if permitted)
        if self.users_db.check_permission(self.uid, "edit_price_in_invoice"):
            CTkButton(
                row,
                text="تعديل السعر",
                width=60,
                height=25,
                font=("Cairo", 11),
                fg_color="#4b5563",
                hover_color="#374151",
                command=lambda p=product: self._show_price_edit_dialog(p),
            ).pack(side="left", padx=5)

        # Modified price label
        modified_price_label = CTkLabel(
            row,
            text="",
            font=("Cairo", 11, "bold"),
            text_color="#16A34A",
            anchor="w",
        )
        modified_price_label.pack(side="left", padx=5)
        product["modified_price_label"] = modified_price_label

        # Total price
        CTkLabel(
            row,
            text=format_currency(product["price"] * product["qty"]),
            font=("Cairo", 13, "bold"),
            anchor="w",
        ).pack(side="left")

    def _build_payment_dialog_summary(self, dialog, subtotal, discount, tax, total):
        """Build the financial summary section."""
        summary_frame = CTkFrame(dialog)
        summary_frame.pack(fill="x", padx=15, pady=10)
        self.summary_labels = {
            "subtotal": None,
            "discount": None,
            "tax": None,
            "total": None,
        }

        self._add_summary_row(summary_frame, "subtotal", ":الإجمالي الفرعي", subtotal)
        self._add_summary_row(summary_frame, "discount", ":الخصم", discount)
        self._add_summary_row(summary_frame, "tax", ":الضريبة", tax)
        self._add_summary_row(summary_frame, "total", ":المطلوب", total)

    def _refresh_payment_modal(self):
        if not hasattr(self, "summary_labels"):
            return

        subtotal = self._calculate_subtotal()

        modified = self._calculate_modified_totals()

        discount = self._calculate_discount(subtotal)
        discount += modified["discount_from_price"]

        after_discount = subtotal - discount

        tax = self._calculate_tax(after_discount)
        tax += modified["increase_from_price"]

        total = after_discount + tax

        self.summary_labels["subtotal"].configure(text=format_currency(subtotal))
        self.summary_labels["discount"].configure(text=format_currency(discount))
        self.summary_labels["tax"].configure(text=format_currency(tax))
        self.summary_labels["total"].configure(text=format_currency(total))

    def _add_summary_row(self, parent, key, label, value):
        """Add a row to the summary frame."""
        row = CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        CTkLabel(
            row,
            text=label,
            font=("Cairo", 14),
            anchor="e",
        ).pack(side="right")

        val_label = CTkLabel(
            row,
            text=format_currency(value),
            font=("Cairo", 14, "bold"),
            anchor="w",
        )
        val_label.pack(side="left")
        self.summary_labels[key] = val_label

    def _build_payment_dialog_payment(self, dialog, total):
        """Build the payment input section."""
        payment_frame = CTkFrame(dialog)
        payment_frame.pack(fill="x", padx=15, pady=10)

        CTkLabel(
            payment_frame,
            text=":المدفوع",
            font=("Cairo", 14),
        ).pack(anchor="e")

        self.paid_var = StringVar(value=f"{total:.2f}")

        paid_entry = CTkEntry(
            payment_frame,
            textvariable=self.paid_var,
            font=("Cairo", 14),
            justify="center",
        )
        paid_entry.pack(fill="x", pady=5, padx=5)

        self.remaining_label = CTkLabel(
            payment_frame,
            text=f"الباقي: 0 {self.currency}",
            font=("Cairo", 14, "bold"),
            text_color="#b91c1c",
        )
        self.remaining_label.pack(anchor="e")

        self.paid_var.trace_add("write", lambda *args: self._update_remaining())
        self._update_remaining()

    def _update_remaining(self):
        """Update remaining amount based on paid value."""
        if not is_number(self.paid_var.get()):
            self.remaining_label.configure(text="الباقي: -")
            return
        paid = float(self.paid_var.get())
        remaining = paid - self._calculate_total()
        self.remaining_label.configure(
            text=f"الباقي: {format_currency(remaining)}",
            text_color="#16A34A" if remaining >= 0 else "#b91c1c",
        )

    def _build_payment_dialog_actions(self, dialog, subtotal, discount, tax, total):
        """Build the action buttons for payment dialog."""
        actions_frame = CTkFrame(dialog, fg_color="transparent")
        actions_frame.pack(fill="x", expand=True, pady=15)

        CTkButton(
            actions_frame,
            text="تأكيد العملية",
            font=("Cairo", 15, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            command=lambda: self._confirm_sale(dialog, subtotal, discount, tax, total),
        ).pack(side="right", padx=10)

        CTkButton(
            actions_frame,
            text="طباعة",
            font=("Cairo", 15, "bold"),
            fg_color="#1676A3",
            hover_color="#115B7E",
            command=lambda: self._print_invoice_with_data(
                subtotal, discount, tax, total
            ),
        ).pack(side="right", padx=10)

    def _show_price_edit_dialog(self, product):
        """Show dialog for editing product price."""
        dialog = CTkToplevel(self.root)
        dialog.title("تعديل السعر")
        dialog.geometry("300x250")
        center_modal(dialog)
        dialog.grab_set()

        CTkLabel(
            dialog,
            text=f"تعديل سعر: {product['name']}",
            font=("Cairo", 14, "bold"),
        ).pack(pady=10)

        CTkLabel(
            dialog,
            text=f"السعر الأصلي: {format_currency(product['price'])}",
            font=("Cairo", 12),
        ).pack()

        CTkLabel(
            dialog,
            text="السعر الجديد:",
            font=("Cairo", 12),
        ).pack(pady=(10, 0))

        price_var = StringVar(value=str(product["price"]))
        price_entry = CTkEntry(
            dialog,
            textvariable=price_var,
            font=("Cairo", 14),
            justify="center",
            width=150,
        )
        price_entry.pack(pady=5)
        price_entry.focus()
        price_entry.select_range(0, "end")

        CTkButton(
            dialog,
            text="حفظ",
            font=("Cairo", 12, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            command=lambda: self._save_price_edit(dialog, product, price_var),
        ).pack(pady=10)

        CTkButton(
            dialog,
            text="إلغاء",
            font=("Cairo", 12),
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=dialog.destroy,
        ).pack()

    def _save_price_edit(self, dialog, product, price_var):
        """Save edited price for product."""
        if not is_number(price_var.get()):
            messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح")
            return

        new_price = float(price_var.get())
        if new_price <= 0:
            messagebox.showerror("خطأ", "يجب أن يكون السعر أكبر من 0")
            return

        # Save modified price
        product["modified_price"] = float(new_price)

        # Update display
        if new_price < product["price"]:
            diff_text = f"↓ خصم: {format_currency(product['price'] - new_price)}"
            product["modified_price_label"].configure(
                text=diff_text, text_color="#16A34A"
            )
        elif new_price > product["price"]:
            diff_text = f"↑ زيادة: {format_currency(new_price - product['price'])}"
            product["modified_price_label"].configure(
                text=diff_text, text_color="#b91c1c"
            )
        else:
            product["modified_price_label"].configure(text="")

        dialog.destroy()
        self._calculate_total()
        self._refresh_payment_modal()
        self._update_remaining()

    def _confirm_sale(self, dialog, subtotal, discount, tax, total):
        """Confirm and process the sale."""
        if not is_number(self.paid_var.get()) or float(self.paid_var.get()) < 0:
            messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح")
            return

        paid = float(self.paid_var.get())
        remaining_amount = total - paid

        # Add debt if customer is not cash
        self._handle_customer_debt(remaining_amount)

        try:
            # Process sale with modified prices
            self._process_sale_transaction(discount, tax, total, paid)

            # Print invoice if auto-print is enabled
            auto_print = self.settings_db.get_setting("auto_print")
            if auto_print:
                sale_data = self._prepare_sale_data(
                    subtotal, discount, tax, total, paid
                )
                self._print_invoice(sale_data)

        except Exception as e:
            self.con.rollback()
            messagebox.showerror("خطأ", f"فشل حفظ الفاتورة: {e}")
            return

        # Reset for new sale
        self._reset_after_sale()
        dialog.destroy()
        messagebox.showinfo("نجاح", "تمت عملية البيع")

    def _handle_customer_debt(self, remaining_amount):
        """Handle customer debt if applicable."""
        if self.customer_var.get() != "نقدي" and remaining_amount > 0:
            self.customers_db.add_debt_to_customer(
                self.customer_id, f"{remaining_amount:.2f}"
            )

    def _process_sale_transaction(self, discount, tax, total, paid):
        """Process the complete sale transaction."""
        # Calculate price modifications
        modified_totals = self._calculate_modified_totals()

        # Use modified totals
        modified_total = total
        modified_discount = discount + modified_totals["discount_from_price"]
        modified_tax = tax + modified_totals["increase_from_price"]

        change = paid - modified_total

        # Save sale
        sale_id = self.sales_db.add_sale(
            self.invoice_number,
            modified_total,
            modified_discount,
            modified_tax,
            paid,
            change,
            self.customer_id,
        )

        # Record stock movements
        self._record_stock_movements(sale_id)

        # Save sale items with modified prices
        sale_items_data = self._prepare_sale_items_data()
        self.sale_items_db.add_sale_items(sale_id, sale_items_data)

        return sale_id

    def _calculate_modified_totals(self):
        """Calculate totals with modified prices."""
        total_discount_from_price = 0.0
        total_increase_from_price = 0.0

        for product in self.selected_products:
            modified_price = product.get("modified_price")
            if modified_price is not None:
                original_price = product["price"]
                qty = product["qty"]

                if modified_price < original_price:
                    discount_from_price = (original_price - modified_price) * qty
                    total_discount_from_price += discount_from_price
                elif modified_price > original_price:
                    increase_from_price = (modified_price - original_price) * qty
                    total_increase_from_price += increase_from_price

        return {
            "discount_from_price": total_discount_from_price,
            "increase_from_price": total_increase_from_price,
        }

    def _prepare_sale_items_data(self):
        """Prepare sale items data with modified prices."""
        sale_items_data = []

        for product in self.selected_products:
            qty = product["qty"]
            modified_price = product.get("modified_price")
            price = modified_price if modified_price is not None else product["price"]
            line_total = price * qty

            sale_items_data.append(
                (
                    product["id"],  # product_id
                    qty,  # quantity
                    price,  # price (modified or original)
                    line_total,  # total
                )
            )

        return sale_items_data

    def _record_stock_movements(self, sale_id):
        """Record stock movements for sold products."""
        for product in self.selected_products:
            qty = product["qty"]
            self.stock_movements_db.add_movement(
                product_id=product["id"],
                quantity=-qty,  # Negative for sale
                movement_type="بيع",
                reference_id=sale_id,
                reference_number=self.invoice_number,
            )

    def _prepare_sale_data(self, subtotal, discount, tax, total, paid):
        """Prepare sale data for printing."""
        return {
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total,
            "paid": paid,
            "remaining": paid - total,
        }

    def _reset_after_sale(self):
        """Reset the interface after successful sale."""
        self.selected_products.clear()
        clear(self.cart_scrollable)
        self._update_cart_count()
        self._calculate_total()
        self._start_new_sale()

    def _print_invoice_with_data(self, subtotal, discount, tax, total):
        """Print invoice with current sale data."""
        try:
            sale_data = self._prepare_sale_data(
                subtotal, discount, tax, total, float(self.paid_var.get())
            )
            self._print_invoice(sale_data)
        except Exception as e:
            messagebox.showwarning("تحذير", f"تم حفظ الفاتورة لكن فشلت الطباعة: {e}")

    # =========================================================================
    # Customer Selection Methods
    # =========================================================================

    def _show_customer_dialog(self):
        """Show customer selection dialog."""
        self.customers_dialog = CTkToplevel(self.root)
        self.customers_dialog.title("اختيار العميل | Dealzora")
        self.customers_dialog.geometry("400x500")
        center_modal(self.customers_dialog)

        CTkLabel(
            self.customers_dialog, text="اختر العميل", font=("Cairo", 16, "bold")
        ).pack(pady=5)

        # Search frame
        search_frame, search_var, search_type_var = self._build_customer_search()
        search_frame.pack(fill="x", padx=10, pady=5)

        # Legend
        self._build_customer_legend()

        # Results frame
        results_frame = CTkScrollableFrame(self.customers_dialog, height=350)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Bind search
        search_var.trace_add(
            "write",
            lambda *args: self._refresh_customer_results(
                results_frame, search_var, search_type_var
            ),
        )

        # Initial load
        self._refresh_customer_results(results_frame, search_var, search_type_var)

    def _build_customer_search(self):
        """Build customer search controls."""
        search_frame = CTkFrame(self.customers_dialog, fg_color="transparent")

        search_var = StringVar()
        search_entry = CTkEntry(
            search_frame,
            textvariable=search_var,
            justify="right",
            font=("Cairo", 14),
        )
        search_entry.pack(side="right", fill="x", expand=True)

        search_type_var = StringVar(value="name")

        CTkRadioButton(
            search_frame,
            text="اسم",
            variable=search_type_var,
            value="name",
            font=("Cairo", 12),
        ).pack(side="right", padx=5)

        CTkRadioButton(
            search_frame,
            text="هاتف",
            variable=search_type_var,
            value="phone",
            font=("Cairo", 12),
        ).pack(side="right")

        return search_frame, search_var, search_type_var

    def _build_customer_legend(self):
        """Build customer status legend."""
        CTkLabel(
            self.customers_dialog, text="دآئن", font=("Cairo", 16), text_color="#dac400"
        ).pack(anchor="e", padx=2)
        CTkLabel(
            self.customers_dialog,
            text="مديون",
            font=("Cairo", 16),
            text_color="#c50000",
        ).pack(anchor="e", padx=2)
        CTkLabel(
            self.customers_dialog,
            text="غير مديون",
            font=("Cairo", 16),
            text_color="#69da00",
        ).pack(anchor="e", padx=2)

    def _refresh_customer_results(self, results_frame, search_var, search_type_var):
        """Refresh customer results based on search."""
        clear(results_frame)

        keyword = search_var.get().strip()
        search_type = search_type_var.get()

        if keyword:
            if keyword and keyword[0] == "0" and search_type == "phone":
                keyword = keyword[1:]  # Remove leading 0 for SQLite
            customers = self.customers_db.search_customers_by_query(
                keyword, search_type
            )
        else:
            customers = self.customers_db.get_customers()

        # Add new customer button
        CTkButton(
            results_frame,
            text="اضافة عميل جديد",
            font=("Cairo", 13),
            fg_color="#0086a8",
            hover_color="#00718d",
            image=image("assets/add_customer.png", (20, 20)),
            command=lambda: self._add_customer_modal(
                lambda: self._refresh_customer_results(
                    results_frame, search_var, search_type_var
                )
            ),
        ).pack(fill="x", pady=2)

        # Cash option
        CTkButton(
            results_frame,
            text="نقدي",
            command=lambda: self._set_customer("نقدي", self.customers_dialog),
            font=("Cairo", 13),
        ).pack(fill="x", pady=2)

        # Customer buttons
        for customer in customers:
            self._create_customer_button(results_frame, customer)

    def _create_customer_button(self, parent, customer):
        """Create a button for a single customer."""
        debt = float(customer[3])
        if debt == 0:
            fg = "#69da00"
            hover = "#5cbe00"
        elif debt < 0:
            fg = "#dac400"
            hover = "#c4b000"
        else:
            fg = "#c50000"
            hover = "#af0000"

        CTkButton(
            parent,
            text=f"{customer[1]} - {customer[2] or 'بدون هاتف'}",
            command=lambda name=customer[1], cid=customer[0]: self._set_customer(
                name, self.customers_dialog, cid
            ),
            fg_color=fg,
            hover_color=hover,
            text_color="black",
            font=("Cairo", 13),
        ).pack(fill="x", pady=2)

    def _set_customer(self, name, dialog, customer_id=None):
        """Set the selected customer."""
        self.customer_var.set(name)
        self.selected_customer.configure(text=f"{self.customer_var.get()}")
        self.customer_id = customer_id if customer_id else None
        dialog.destroy()

    # =========================================================================
    # Table and Filter Methods
    # =========================================================================

    def filter_products(self, event=None):
        """Filter products based on search and category."""
        keyword = self.search_var.get().strip()
        category_name = self.categorys_menu.get()
        category_id = self.category_map.get(category_name)

        if category_id == "all":
            if keyword:
                self.products = self.products_db.search_products(keyword)
            else:
                self.products = self.products_db.get_products()
        else:
            if keyword:
                self.products = self.products_db.search_products_by_category(
                    keyword, category_name
                )
            else:
                self.products = self.products_db.get_products_by_category(category_id)

        self.refresh_table()

    def _fill_categories(self):
        """Populate the category dropdown."""
        categories = self.products_db.get_categorys()

        self.category_map = {"الكل": "all"}

        for category in categories:
            cid = category[0]
            name = category[1]
            self.category_map[name] = cid

        self.categorys_menu.configure(values=list(self.category_map.keys()))

    def refresh_table(self):
        """Refresh the products table."""
        self.tree.tree.delete(*self.tree.tree.get_children())
        for product in self.products:
            self.tree.tree.insert(
                "",
                "end",
                values=(product[0], product[1], product[4], product[5], product[2]),
                tags=(get_stock_tag(product[5], product[8]),),
            )

    # =========================================================================
    # New Sale Methods
    # =========================================================================

    def _start_new_sale(self):
        """Reset for a new sale."""
        self.products = self.products_db.get_products()
        self.refresh_table()
        self.selected_products = []

        # Reset customer
        self.customer_var.set("نقدي")
        self.selected_customer.configure(text=f"{self.customer_var.get()}")

        # New invoice number
        self.invoice_number = self._generate_invoice_number()
        self.invoice_number_label.configure(text=f"{self.invoice_number} :رقم الفاتوره")

        # Update date
        self.date_label.configure(text=f'التاريخ: {strftime("%Y-%m-%d %H:%M")}')

        # Focus search
        self.search_entry.focus()

    # =========================================================================
    # Customer Addition Methods
    # =========================================================================

    def _add_customer(self, name, phone, debt, modal):
        """Add a new customer."""
        try:
            self.customers_db.add_customer(name, phone, debt)
            messagebox.showinfo("تم", "تم اضافة العميل بنجاح")
            modal.destroy()
        except Exception as e:
            if "UNIQUE constraint failed: customers.phone" in str(e):
                messagebox.showerror("خطأ", "رقم الهاتف مستخدم بالفعل")
            else:
                messagebox.showerror("خطأ", str(e))

    def _add_customer_modal(self, refresh_results):
        """Show add customer modal."""
        CustomerModal(
            self.tree,
            self._add_customer,
            refresh_results=refresh_results,
            customers_dialog=self.customers_dialog,
        )

    # =========================================================================
    # Printing Methods
    # =========================================================================

    def _print_invoice(self, sale_data):
        """Print invoice in a separate thread."""
        
        def run_print():
            try:
                from utils.print_thermal import print_shop_invoice
                from utils.print_A4 import print_A4
                
                invoice_data = self._prepare_invoice_data(sale_data)
                products_data = self._prepare_products_for_printing()
                
                # التحقق من نوع الطباعة المطلوب
                printer_type = self.settings_db.get_setting("printer_type") or "حرارية"
                
                if printer_type == "A4":
                    print_A4(invoice_data, products_data)
                else:
                    print_shop_invoice(invoice_data, products_data)
                    
            except Exception as e:
                error_message = f"تم حفظ الفاتورة لكن فشلت الطباعة: {e}"
                self.root.after(0, lambda: messagebox.showwarning("تحذير", error_message))
        
        threading.Thread(target=run_print, daemon=True).start()

    def _prepare_invoice_data(self, sale_data):
        """Prepare invoice data for printing."""
        return {
            "invoice_number": self.invoice_number,
            "date": strftime("%Y-%m-%d"),
            "time": strftime("%I:%M %p"),
            "customer_name": self.customer_var.get(),
            "subtotal": round(sale_data["subtotal"], 2),
            "discount": round(sale_data["discount"], 2),
            "tax": round(sale_data["tax"], 2),
            "total": round(sale_data["total"], 2),
            "paid": round(sale_data["paid"], 2),
            "remaining": round(sale_data["remaining"], 2),
        }

    def _prepare_products_for_printing(self):
        """Prepare products data for printing."""
        products = []
        for product in self.selected_products:
            modified_price = product.get("modified_price")
            price = modified_price if modified_price is not None else product["price"]

            products.append(
                {
                    "name": product["name"],
                    "price": price,
                    "qty": product["qty"],
                    "total": price * product["qty"],
                }
            )
        return products
