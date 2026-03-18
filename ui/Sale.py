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
    ):
        self.root = root

        # قواعد البيانات
        self.products_db = products_db
        self.customers_db = customers_db
        self.sales_db = sales_db
        self.sale_items_db = sale_items_db
        self.stock_movements_db = stock_movements_db
        self.settings_db = settings_db
        self.con = con

        self.c = self.settings_db.get_setting("currency")  # get currency
        self.tax_rate = self.settings_db.get_setting("tax")  # get Tax

        # بيانات
        self.products = self.safe_fetch(self.products_db.get_products)
        self.selected_products = selected_products

        # خصم وضريبة
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.invoice_number = f'INV-{strftime("%Y%m%d%H%M%S")}'

        # العميل والمدفوع
        self.customer_var = customer_var
        self.customer_id = customer_id

        # واجهة المستخدم
        self.build_ui()
        self.refresh_table()

        # تحميل المنتجات المختارة مسبقاً
        self.load_selected_products()

    # =============================
    # Utilities
    # =============================
    def safe_fetch(self, func):
        try:
            return func()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")
            return []

    # =============================
    # UI
    # =============================
    def build_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.build_toolbar()
        self.build_products_section()
        self.build_cart_section()
        self.build_total_section()

    def build_toolbar(self):
        toolbar = CTkFrame(self.root, height=50)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))

        self.invoice_number_label = CTkLabel(
            toolbar,
            text=f"{self.invoice_number} :رقم الفاتوره",
            font=("Cairo", 16, "bold"),
            text_color="#0080e9",
        )
        self.invoice_number_label.pack(side="right", padx=5, pady=5)

        self.date_label = CTkLabel(
            toolbar,
            text=f'التاريخ: {strftime("%Y-%m-%d %H:%M")}',
            font=("Cairo", 16, "bold"),
            text_color="#00bae9",
        )
        self.date_label.pack(side="right", padx=5, pady=5)

        message = """
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
        CTkButton(
            toolbar,
            text="",
            image=image("assets/information.png"),
            width=0,
            corner_radius=50,
            command=lambda: messagebox.showinfo("معلومات | واجهة البيع", message)
        ).pack(side="right", padx=5, pady=5)

    def build_products_section(self):
        container = CTkFrame(
            self.root, border_width=1, border_color="#dddddd", corner_radius=8
        )
        container.grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=5)
        container.grid_rowconfigure(0, weight=1)

        search_frame = CTkFrame(container, fg_color="transparent")
        search_frame.pack(fill="x", padx=5, pady=5)

        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=3)

        self.search_var = StringVar()

        self.search_entry = CTkEntry(
            search_frame,
            textvariable=self.search_var,
            justify="right",
            font=("Cairo", 14),
        )

        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        key_shortcut(self.search_entry, "<Return>", self.handle_enter)
        self.search_var.trace_add("write", lambda *args: self.filter_products())

        self.categorys_menu = CTkOptionMenu(
            search_frame,
            font=("Cairo", 20, "bold"),
            values=["الكل"],
            dropdown_font=("Cairo", 20),
            command=self.filter_products,
        )

        self.categorys_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # وضع كل الفئات في محدد الفئات
        self.fill_categorys()

        frame = CTkFrame(container, fg_color="transparent")
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

        self.tree = TreeView(
            container,
            ("ID", "المنتج", "السعر", "المخزون", "الباركود"),
            (50, 200, 80, 80, 120),
        )
        key_shortcut(
            self.tree.tree, ["<Double-1>", "<Return>"], self.handle_add_product
        )

    def build_cart_section(self):
        self.cart_frame = CTkFrame(
            self.root, border_width=1, border_color="#dddddd", corner_radius=8
        )
        self.cart_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=5)
        CTkLabel(
            self.cart_frame, text="🛒 سلة المشتريات", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        customers_frame = CTkFrame(self.cart_frame, fg_color="transparent")
        customers_frame.pack(pady=5)

        CTkButton(
            customers_frame,
            text="اختر عميل",
            fg_color="#00aeff",
            hover_color="#009be2",
            width=0,
            font=("Cairo", 18, "bold"),
            command=self.show_customer_dialog,
        ).pack(side="right", padx=5)

        self.selected_customer = CTkLabel(
            customers_frame,
            text=self.customer_var.get(),
            font=("Cairo", 16, "bold"),
        )
        self.selected_customer.pack(side="right", padx=5)

        self.cart_count_label = CTkLabel(
            self.cart_frame, text="لم يتم اضافة منتجات بعد", font=("Cairo", 14)
        )
        self.cart_count_label.pack()
        self.cart_frame = CTkScrollableFrame(self.cart_frame, height=400)
        self.cart_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def build_total_section(self):
        def on_discount_change():
            val = self.discount_value_var.get()

            if not val or not is_number(val):
                self.discount_value = 0
            else:
                self.discount_value = float(val)

            self.discount_type = self.discount_type_var.get()
            self.calculate_total()

        def on_tax_change():
            val = self.tax_var.get()

            if not val or not is_number(val):
                self.tax_rate = 0
            else:
                self.tax_rate = float(val)

            self.tax_type = self.tax_type_var.get()
            self.calculate_total()

        frame = CTkFrame(self.root, corner_radius=8)
        frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # الإجمالي الفرعي
        self.subtotal_label = CTkLabel(
            frame, text=f"الإجمالي الفرعي: 0 {self.c}", font=("Cairo", 14)
        )
        self.subtotal_label.pack(anchor="e")

        # =========================
        # الخصم
        # =========================
        discount_frame = CTkFrame(frame, fg_color="transparent")
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
        self.tax_type = "percentage"

        CTkRadioButton(
            discount_frame,
            text=f"{self.c}",
            variable=self.discount_type_var,
            value="amount",
            font=("Cairo", 13),
            command=on_discount_change,
        ).pack(side="right")

        CTkRadioButton(
            discount_frame,
            text="%",
            variable=self.discount_type_var,
            value="percentage",
            font=("Cairo", 13),
            command=on_discount_change,
        ).pack(side="right", padx=5)

        self.discount_value_var.trace_add("write", lambda *args: on_discount_change())

        # =========================
        # الضريبة
        # =========================
        tax_frame = CTkFrame(frame, fg_color="transparent")
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
            text=f"{self.c}",
            variable=self.tax_type_var,
            value="amount",
            font=("Cairo", 13),
            command=on_tax_change,
        ).pack(side="right")

        CTkRadioButton(
            tax_frame,
            text="%",
            variable=self.tax_type_var,
            value="percentage",
            font=("Cairo", 13),
            command=on_tax_change,
        ).pack(side="right", padx=5)

        self.tax_var.trace_add("write", lambda *args: on_tax_change())
        # =========================
        # المطلوب
        # =========================
        self.total_label = CTkLabel(
            frame, text=f"المطلوب: 0 {self.c}", font=("Cairo", 24, "bold")
        )
        self.total_label.pack(anchor="e", pady=5)

        actions_frame = CTkFrame(frame, fg_color="transparent")
        actions_frame.pack(pady=8, fill="x")

        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        # زرار إلغاء العملية (هادئ)
        cancel_btn = CTkButton(
            actions_frame,
            text="❎ إلغاء العملية",
            height=45,
            corner_radius=8,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#111827",
            font=("Cairo", 15, "bold"),
            command=self.cancle_sale,
        )
        cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        finish_btn = CTkButton(
            actions_frame,
            text="✅ إنهاء البيع",
            height=45,
            corner_radius=8,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="white",
            font=("Cairo", 15, "bold"),
            command=self.finish_sale,
        )
        finish_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def handle_enter(self, event=None):
        keyword = self.search_var.get().strip()

        if not keyword:
            return

        results = self.products_db.search_products(keyword)

        if len(results) == 1:
            product_data = results[0]

            status, new_product = self.check_stock(product_data, product_data[0])

            if status == "out_of_stock":
                messagebox.showwarning("تحذير", "هذا المنتج غير متوفر في المخزون")
                return

            elif status == "exceeded":
                messagebox.showwarning("تحذير", "الكمية المطلوبة تتجاوز المخزون")
                return

            elif status == "added" and new_product:
                self.selected_products.append(new_product)
                self.update_product_widget(new_product)

            # تحديث السلة والحسابات
            self.update_cart_count()
            self.calculate_total()
            self.search_var.set("")

    def filter_products(self, event=None):
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

    def fill_categorys(self):
        categorys = self.products_db.get_categorys()

        self.category_map = {"الكل": "all"}

        for c in categorys:
            cid = c[0]
            name = c[1]
            self.category_map[name] = cid

        self.categorys_menu.configure(values=list(self.category_map.keys()))

    # =============================
    # Cart & Products
    # =============================
    def load_selected_products(self):
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
            self.update_product_widget(product)

        self.update_cart_count()
        self.calculate_total()

        if out_of_stock_alert:
            messagebox.showwarning(
                "تحذير",
                "هناك بعض المنتجات المختاره تجاوزت حد المخزون\nتم وضع كمياتها الى اقصى حد",
            )

    def check_stock(self, product_data, pid):
        if product_data[5] <= 0:
            return "out_of_stock", None

        for product in self.selected_products:
            if product["id"] == pid:
                if product["qty"] + 1 > product_data[5]:
                    return "exceeded", None

                product["qty"] += 1
                self.update_product_widget(product)
                return "updated", None

        # منتج جديد
        new_product = {
            "id": product_data[0],
            "name": product_data[1],
            "price": product_data[4],
            "image": product_data[7],
            "qty": 1,
            "widget": None,
            "sub_total_label": None,
            "qty_entry": None,
        }

        return "added", new_product

    def handle_add_product(self, event=None):
        selected_items = self.tree.tree.selection()
        if not selected_items:
            return

        pids = [self.tree.tree.item(i)["values"][0] for i in selected_items]

        has_stock_issue = False
        added_any = False

        for pid in pids:
            product_data = self.products_db.get_product(pid)

            status, new_product = self.check_stock(product_data, pid)

            if status in ("out_of_stock", "exceeded"):
                has_stock_issue = True
                continue

            if status == "added" and new_product:
                self.selected_products.append(new_product)
                self.update_product_widget(new_product)
                added_any = True

            if status == "updated":
                added_any = True

        if has_stock_issue:
            messagebox.showwarning("تنبيه", "بعض المنتجات غير متوفرة أو تجاوزت المخزون")

        if added_any:
            self.update_cart_count()
            self.calculate_total()

    def update_product_widget(self, product):
        container = product["widget"]
        if not container:
            container = CTkFrame(
                self.cart_frame, corner_radius=8, border_width=1, border_color="#e5e5e5"
            )
            container.pack(side="bottom", fill="x", pady=3, padx=3)
            product["widget"] = container

            top_row = CTkFrame(container, fg_color="transparent")
            top_row.pack(fill="x", padx=6, pady=4)

            CTkLabel(top_row, text="", image=image(product["image"]), width=40).pack(
                side="right", padx=(0, 6)
            )

            info_frame = CTkFrame(top_row, fg_color="transparent")
            info_frame.pack(side="right", fill="x", expand=True)

            CTkLabel(
                info_frame,
                text=product["name"],
                font=("Cairo", 11, "bold"),
                text_color=("#167000", "#00a72a"),
                anchor="e",
            ).pack(fill="x", padx=10)

            sub_total = CTkLabel(
                info_frame,
                text="",
                font=("Cairo", 10),
                text_color=("#6d6d6d", "#b4b4b4"),
                anchor="e",
            )
            sub_total.pack(fill="x", padx=10)
            product["sub_total_label"] = sub_total

            qty_frame = CTkFrame(container, fg_color="transparent")
            qty_frame.pack(fill="x", padx=6, pady=(0, 6))

            CTkButton(
                qty_frame,
                text="-",
                width=28,
                height=28,
                font=("Cairo", 14, "bold"),
                command=lambda p=product: self.decrease_qty(p),
            ).pack(side="right", padx=2)

            qty_entry_var = StringVar(value=str(product["qty"]))
            product["qty_entry"] = qty_entry_var

            def on_qty_change(*args):
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
                self.update_product_widget(product)

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

            key_shortcut(
                qty_entry,
                ["<Up>", "<plus>", "<KP_Add>"],
                lambda p=product: self.increase_qty(p),
            )
            key_shortcut(
                qty_entry,
                ["<Down>", "<minus>", "<KP_Subtract>"],
                lambda p=product: self.decrease_qty(p),
            )
            key_shortcut(
                qty_entry,
                ["<Delete>", "<Control-d>", "<Control-D>"],
                lambda p=product: self.remove_from_cart(p),
            )

            CTkButton(
                qty_frame,
                text="+",
                width=28,
                height=28,
                font=("Cairo", 14, "bold"),
                command=lambda p=product: self.increase_qty(p),
            ).pack(side="right", padx=2)

            CTkButton(
                qty_frame,
                text="",
                width=28,
                height=28,
                fg_color=("#b30000", "#8f0000"),
                hover_color=("#8D0000", "#740000"),
                image=image("assets/delete.png", (20, 20)),
                command=lambda p=product: self.remove_from_cart(p),
            ).pack(side="left", padx=10)

        # تحديث السعر الفرعي
        product["sub_total_label"].configure(
            text=f"{product['price']} × {product['qty']} = {format_currency(product['price']*product['qty'])}"
        )
        product["qty_entry"].set(product["qty"])
        self.update_cart_count()
        self.calculate_total()

    def decrease_qty(self, product):
        if product["qty"] - 1 <= 0:
            return self.remove_from_cart(product)
        product["qty"] -= 1
        self.update_product_widget(product)

    def increase_qty(self, product):
        prod_data = self.products_db.get_product(product["id"])
        if product["qty"] + 1 > prod_data[5]:
            messagebox.showwarning("تحذير", "الكمية المطلوبة تتجاوز المخزون")
            return
        product["qty"] += 1
        self.update_product_widget(product)

    def remove_from_cart(self, product):
        if product in self.selected_products:
            self.selected_products.remove(product)
            if product["widget"]:
                product["widget"].destroy()
        self.update_cart_count()
        self.calculate_total()

    def update_cart_count(self):
        count = len(self.selected_products)
        total_items = sum(p["qty"] for p in self.selected_products)
        self.cart_count_label.configure(text=f"{total_items} صنف {count} | قطعة")

    # =============================
    # Calculations
    # =============================
    def calculate_total(self):
        subtotal = sum(p["price"] * p["qty"] for p in self.selected_products)

        # حساب الخصم
        if self.discount_type == "amount":
            discount = self.discount_value
        else:
            discount = subtotal * self.discount_value / 100

        discount = min(discount, subtotal)

        after_discount = subtotal - discount

        # حساب الضريبة
        if self.tax_type == "amount":
            tax = self.tax_rate
        else:
            tax = after_discount * self.tax_rate / 100

        total = after_discount + tax

        self.subtotal_label.configure(
            text=f"الإجمالي الفرعي: {format_currency(subtotal)}"
        )
        self.total_label.configure(text=f"المطلوب: {format_currency(total)}")
        return total

    # =============================
    # Sale Completion
    # =============================
    def cancle_sale(self):
        if messagebox.askokcancel("تأكيد", "هل انت متأكد من الغاء العمليه"):
            self.start_new_sale()
            clear(self.cart_frame)
            self.build_cart_section()

    def finish_sale(self):
        if not self.selected_products:
            messagebox.showwarning("تحذير", "لا توجد منتجات في السلة")
            return

        total = self.calculate_total()
        subtotal = sum(p["price"] * p["qty"] for p in self.selected_products)

        # حساب الخصم
        if self.discount_type == "amount":
            discount = self.discount_value
        else:
            discount = subtotal * self.discount_value / 100
        discount = min(discount, subtotal)

        after_discount = subtotal - discount

        # حساب الضريبة
        if self.tax_type == "amount":
            tax = self.tax_rate
        else:
            tax = after_discount * self.tax_rate / 100

        total = after_discount + tax

        dialog = CTkToplevel(self.root)
        dialog.title("إتمام البيع | Dealzora")
        dialog.geometry("500x700+200+0")
        dialog.grab_set()
        dialog.focus_force()

        # =========================
        # العنوان
        # =========================
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

        # =========================
        # المنتجات
        # =========================
        products_frame = CTkScrollableFrame(dialog, height=200)
        products_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # قاموس لتخزين الأسعار المعدلة
        self.modified_prices = {}
        
        for p in self.selected_products:
            row = CTkFrame(products_frame)
            row.pack(fill="x", pady=2)
            
            # إطار للسعر والمنتج
            product_info_frame = CTkFrame(row, fg_color="transparent")
            product_info_frame.pack(side="right", fill="x", expand=True)
            
            # اسم المنتج والكمية
            CTkLabel(
                product_info_frame,
                text=f"{p['name']}  {p['price']} × {p['qty']}",
                font=("Cairo", 13),
                anchor="e",
            ).pack(fill="x")
            
            # إطار للسعر المعدل
            price_frame = CTkFrame(product_info_frame, fg_color="transparent")
            price_frame.pack(fill="x", pady=(2, 0))
            
            # سعر المنتج الحالي
            CTkLabel(
                price_frame,
                text=":السعر الحالي",
                font=("Cairo", 11),
                text_color="#666666",
                anchor="e",
            ).pack(side="right", padx=(0, 5))
            
            CTkLabel(
                price_frame,
                text=format_currency(p["price"]),
                font=("Cairo", 11, "bold"),
                text_color="#666666",
                anchor="e",
            ).pack(side="right")
            
            # زر تعديل السعر
            def create_price_edit_handler(prod):
                def edit_price():
                    self.show_price_edit_dialog(prod)
                return edit_price
            
            CTkButton(
                row,
                text="تعديل السعر",
                width=60,
                height=25,
                font=("Cairo", 11),
                fg_color="#4b5563",
                hover_color="#374151",
                command=create_price_edit_handler(p)
            ).pack(side="left", padx=5)
            
            # عرض السعر المعدل (إن وجد)
            modified_price_label = CTkLabel(
                row,
                text="",
                font=("Cairo", 11, "bold"),
                text_color="#16A34A",
                anchor="w",
            )
            modified_price_label.pack(side="left", padx=5)
            
            # تخزين مرجع الـ label لتحديثه لاحقاً
            p["modified_price_label"] = modified_price_label
            p["modified_price"] = None

            # السعر الإجمالي
            CTkLabel(
                row,
                text=format_currency(p["price"] * p["qty"]),
                font=("Cairo", 13, "bold"),
                anchor="w",
            ).pack(side="left")

        # =========================
        # الملخص المالي
        # =========================
        summary_frame = CTkFrame(dialog)
        summary_frame.pack(fill="x", padx=15, pady=10)

        def add_summary(text, value):
            row = CTkFrame(summary_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            CTkLabel(
                row,
                text=text,
                font=("Cairo", 14),
                anchor="e",
            ).pack(side="right")

            CTkLabel(
                row,
                text=format_currency(value),
                font=("Cairo", 14, "bold"),
                anchor="w",
            ).pack(side="left")

        add_summary(":الإجمالي الفرعي", subtotal)
        add_summary(":الخصم", discount)
        add_summary(":الضريبة", tax)
        add_summary(":المطلوب", total)

        # =========================
        # المدفوع والباقي
        # =========================
        payment_frame = CTkFrame(dialog)
        payment_frame.pack(fill="x", padx=15, pady=10)

        CTkLabel(
            payment_frame,
            text=":المدفوع",
            font=("Cairo", 14),
        ).pack(anchor="e")

        paid_var = StringVar(value=f"{total:.2f}")

        paid_entry = CTkEntry(
            payment_frame,
            textvariable=paid_var,
            font=("Cairo", 14),
            justify="center",
        )
        paid_entry.pack(fill="x", pady=5, padx=5)

        remaining_label = CTkLabel(
            payment_frame,
            text=f"الباقي: 0 {self.c}",
            font=("Cairo", 14, "bold"),
            text_color="#b91c1c",
        )
        remaining_label.pack(anchor="e")

        def update_remaining(*args):
            if not is_number(paid_var.get()):
                remaining_label.configure(text="الباقي: -")
                return
            paid = float(paid_var.get())
            remaining = paid - total
            remaining_label.configure(text=f"الباقي: {format_currency(remaining)}")

        paid_var.trace_add("write", update_remaining)
        update_remaining()

        # =========================
        # تأكيد
        # =========================
        def print_util():
            try:
                sale_data = {
                    "subtotal": subtotal,
                    "discount": discount,
                    "tax": tax,
                    "total": total,
                    "paid": float(paid_var.get()),
                    "remaining": float(paid_var.get()) - total,
                }
                self.print_invoice(sale_data)
            except Exception as e:
                messagebox.showwarning(
                    "تحذير", f"تم حفظ الفاتورة لكن فشلت الطباعة: {e}"
                )

        def confirm():
            if not is_number(paid_var.get()) or float(paid_var.get()) < 0:
                messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح")
                return

            paid = float(paid_var.get())
            remaining_amount = total - paid

            if self.customer_var.get() != "نقدي":
                self.customers_db.add_debt_to_customer(
                    self.customer_id, f"{remaining_amount:.2f}"
                )

            sold_quantity = {}
            for p in self.selected_products:
                pid = p["id"]
                qty = p["qty"]
                sold_quantity[pid] = sold_quantity.get(pid, 0) + qty

            try:
                # ======================
                # 1️⃣ حساب الفروق من الأسعار المعدلة أولاً
                # ======================
                sale_items_data = []
                total_discount_from_price = 0.0  # استخدام float
                total_increase_from_price = 0.0  # استخدام float
                
                # تأكد من أن جميع المنتجات لديها modified_price معرف
                for p in self.selected_products:
                    if "modified_price" not in p:
                        p["modified_price"] = None

                for p in self.selected_products:
                    qty = p["qty"]
                    # استخدام السعر المعدل إن وجد وكانت قيمته ليست None
                    modified_price = p.get("modified_price")
                    if modified_price is not None:
                        price = modified_price
                    else:
                        price = p["price"]
                    original_price = p["price"]
                                        
                    # حساب الفرق (مع التأكد من أن price ليست None)
                    if price is not None and original_price is not None:
                        if price < original_price:
                            discount_from_price = (original_price - price) * qty
                            total_discount_from_price += discount_from_price
                        elif price > original_price:
                            increase_from_price = (price - original_price) * qty
                            total_increase_from_price += increase_from_price
                                            
                    line_total = price * qty

                    sale_items_data.append(
                        (
                            p["id"],  # product_id
                            qty,  # quantity
                            price,  # price (المعدل أو الأصلي)
                            line_total,  # total
                        )
                    )

                # ======================
                # 2️⃣ حساب الإجمالي المعدل
                # ======================
                modified_total = total
                
                # التأكد من أن القيم ليست None
                if total_discount_from_price is None:
                    total_discount_from_price = 0
                if total_increase_from_price is None:
                    total_increase_from_price = 0
                
                if total_discount_from_price > 0:
                    modified_total -= total_discount_from_price
                if total_increase_from_price > 0:
                    modified_total += total_increase_from_price
                
                change = paid - modified_total  # استخدام modified_total بدلاً من total

                # ======================
                # 3️⃣ حفظ الفاتورة
                # ======================
                sale_id = self.sales_db.add_sale(
                    self.invoice_number,
                    modified_total,  # استخدام الإجمالي المعدل
                    discount + total_discount_from_price,  # إضافة خصم الأسعار المعدلة
                    tax + total_increase_from_price,  # إضافة زيادة الأسعار المعدلة كضريبة إضافية
                    paid,
                    change,
                    self.customer_id,
                )

                # ======================
                # 4️⃣ تسجيل حركات المخزون
                # ======================
                for p in self.selected_products:
                    qty = p["qty"]
                    self.stock_movements_db.add_movement(
                        product_id=p["id"],
                        quantity=-qty,  # سالب للخصم
                        movement_type="بيع",
                        reference_id=sale_id,
                        reference_number=self.invoice_number,
                    )

                # ======================
                # 5️⃣ حفظ عناصر الفاتورة
                # ======================
                self.sale_items_db.add_sale_items(sale_id, sale_items_data)

                # ======================
                # 6️⃣ طباعة الفاتورة
                # ======================
                auto_print = self.settings_db.get_setting("auto_print")
                if auto_print:
                    print_util()

            except Exception as e:
                self.con.rollback()
                messagebox.showerror("خطأ", f"فشل حفظ الفاتورة: {e}")
                return

            self.selected_products.clear()
            clear(self.cart_frame)
            self.update_cart_count()
            self.calculate_total()
            self.start_new_sale()

            dialog.destroy()
            messagebox.showinfo("نجاح", "تمت عملية البيع")
        actions_frame = CTkFrame(dialog, fg_color="transparent")
        actions_frame.pack(fill="x", expand=True, pady=15)

        CTkButton(
            actions_frame,
            text="تأكيد العملية",
            font=("Cairo", 15, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            command=confirm,
        ).pack(side="right", padx=10)

        CTkButton(
            actions_frame,
            text="طباعة",
            font=("Cairo", 15, "bold"),
            fg_color="#1676A3",
            hover_color="#115B7E",
            command=print_util,
        ).pack(side="right", padx=10)
    
    def show_price_edit_dialog(self, product):
        """نافذة تعديل سعر المنتج"""
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
        
        price_var = StringVar(value=str(product['price']))
        price_entry = CTkEntry(
            dialog,
            textvariable=price_var,
            font=("Cairo", 14),
            justify="center",
            width=150,
        )
        price_entry.pack(pady=5)
        price_entry.focus()
        price_entry.select_range(0, 'end')
        
        def save_price():
            if not is_number(price_var.get()):
                messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح")
                return
            
            new_price = float(price_var.get())
            if new_price <= 0:
                messagebox.showerror("خطأ", "يجب أن يكون السعر أكبر من 0")
                return
            
            # حفظ السعر المعدل (تحويل إلى float)
            product['modified_price'] = float(new_price)
            
            # تحديث العرض
            if new_price < product['price']:
                diff_text = f"↓ خصم: {format_currency(product['price'] - new_price)}"
                product['modified_price_label'].configure(
                    text=diff_text,
                    text_color="#16A34A"
                )
            elif new_price > product['price']:
                diff_text = f"↑ زيادة: {format_currency(new_price - product['price'])}"
                product['modified_price_label'].configure(
                    text=diff_text,
                    text_color="#b91c1c"
                )
            else:
                product['modified_price_label'].configure(text="")
            
            dialog.destroy()
        
        CTkButton(
            dialog,
            text="حفظ",
            font=("Cairo", 12, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            command=save_price,
        ).pack(pady=10)
        
        CTkButton(
            dialog,
            text="إلغاء",
            font=("Cairo", 12),
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=dialog.destroy,
        ).pack()
    
    # =============================
    # Customer / Discount / Tax Dialogs
    # =============================
    def show_customer_dialog(self):
        self.customers_dialog = CTkToplevel(self.root)
        self.customers_dialog.title("اختيار العميل | Dealzora")
        self.customers_dialog.geometry("400x500")
        center_modal(self.customers_dialog)

        CTkLabel(
            self.customers_dialog, text="اختر العميل", font=("Cairo", 16, "bold")
        ).pack(pady=5)

        search_frame = CTkFrame(self.customers_dialog, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=5)

        search_var = StringVar()
        search_entry = CTkEntry(
            search_frame,
            textvariable=search_var,
            justify="right",
            font=("Cairo", 14),
        )
        search_entry.pack(side="right", fill="x", expand=True)

        def refresh_results(*args):
            clear(results_frame)

            keyword = search_var.get().strip()
            if keyword:
                if keyword and keyword[0] == "0" and search_type_var.get() == "phone":
                    keyword = keyword[
                        1:
                    ]  # لتخطي 0 في الأرقام المصريه للتعامل مع SQlite3
                customers = self.customers_db.search_customers_by_query(
                    keyword, search_type_var.get()
                )
            else:
                customers = self.customers_db.get_customers()

            CTkButton(
                results_frame,
                text="اضافة عميل جديد",
                font=("Cairo", 13),
                fg_color="#0086a8",
                hover_color="#00718d",
                image=image("assets/add_customer.png", (20, 20)),
                command=lambda: self._add_customer_modal(refresh_results),
            ).pack(fill="x", pady=2)

            CTkButton(
                results_frame,
                text="نقدي",
                command=lambda: self.set_customer("نقدي", self.customers_dialog),
                font=("Cairo", 13),
            ).pack(fill="x", pady=2)

            for c in customers:
                debt = float(c[3])
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
                    results_frame,
                    text=f"{c[1]} - {c[2] or 'بدون هاتف'}",
                    command=lambda name=c[1], cid=c[0]: self.set_customer(
                        name, self.customers_dialog, cid
                    ),
                    fg_color=fg,
                    hover_color=hover,
                    text_color="black",
                    font=("Cairo", 13),
                ).pack(fill="x", pady=2)

        search_type_var = StringVar(value="name")

        CTkRadioButton(
            search_frame,
            text="اسم",
            variable=search_type_var,
            value="name",
            font=("Cairo", 12),
            command=refresh_results,
        ).pack(side="right", padx=5)

        CTkRadioButton(
            search_frame,
            text="هاتف",
            variable=search_type_var,
            value="phone",
            font=("Cairo", 12),
            command=refresh_results,
        ).pack(side="right")

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

        results_frame = CTkScrollableFrame(self.customers_dialog, height=350)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        search_var.trace_add("write", refresh_results)

        refresh_results()

    def set_customer(self, name, dialog, customer_id=None):
        self.customer_var.set(name)
        self.selected_customer.configure(text=f"{self.customer_var.get()}")

        self.customer_id = customer_id if customer_id else None

        dialog.destroy()

    # =============================
    # Table
    # =============================
    def refresh_table(self):
        self.tree.tree.delete(*self.tree.tree.get_children())
        for p in self.products:
            self.tree.tree.insert(
                "",
                "end",
                values=(p[0], p[1], p[4], p[5], p[2]),
                tags=(get_stock_tag(p[5], p[8]),),
            )

    def start_new_sale(self):
        self.products = self.products_db.get_products()
        self.refresh_table()
        self.selected_products = []
        # default data
        self.customer_var.set("نقدي")
        self.selected_customer.configure(text=f"{self.customer_var.get()}")

        self.invoice_number = f'INV-{strftime("%Y%m%d%H%M%S")}'
        self.invoice_number_label.configure(text=f"{self.invoice_number} :رقم الفاتوره")

        self.date_label.configure(text=f'التاريخ: {strftime("%Y-%m-%d %H:%M")}')
        self.search_entry.focus()

    def add_customer(self, name, phone, debt, modal):
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
        CustomerModal(
            self.tree,
            self.add_customer,
            refresh_results=refresh_results,
            customers_dialog=self.customers_dialog,
        )

    def print_invoice(self, sale_data):
        def run_print():
            try:
                from utils.print_thermal import print_shop_invoice

                invoice_data = {
                    "invoice_number": self.invoice_number,
                    "date": strftime("%Y-%m-%d"),
                    "time": strftime("%I:%M %p"),
                    "customer_name": self.customer_var.get(),
                    "subtotal": sale_data["subtotal"],
                    "discount": sale_data["discount"],
                    "tax": sale_data["tax"],
                    "total": sale_data["total"],
                    "paid": sale_data["paid"],
                    "remaining": sale_data["remaining"],
                }

                products = []
                for p in self.selected_products:
                    products.append({
                        "name": p["name"],
                        "price": p["price"],
                        "qty": p["qty"],
                        "total": p["price"] * p["qty"],
                    })

                print_shop_invoice(invoice_data, products)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showwarning("تحذير", str(e)))

        threading.Thread(target=run_print, daemon=True).start()