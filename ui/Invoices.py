from time import strftime

from customtkinter import (
    CTkLabel,
    CTkFrame,
    CTkEntry,
    CTkSegmentedButton,
    CTkButton,
    CTkToplevel,
    StringVar,
    CTkScrollableFrame,
)
from tkinter import messagebox
from components.TreeView import TreeView
from utils.image import image
from utils.format_currency import format_currency
from utils.key_shortcut import key_shortcut
from utils.is_number import is_number
from tkcalendar import DateEntry
from datetime import date


class Invoices:
    def __init__(
        self,
        root,
        con,
        invoices_db,
        sale_items_db,
        customers_db,
        products_db,
        stock_movements_db,
    ):
        self.root = root
        self.con = con

        # قواعد البيانات
        self.invoices_db = invoices_db
        self.sale_items_db = sale_items_db
        self.customers_db = customers_db
        self.products_db = products_db
        self.stock_movements_db = stock_movements_db

        # البيانات
        self.invoices = self.get_invoices_with_details()

        # العنوان
        CTkLabel(
            self.root,
            text="الفواتير",
            image=image("assets/invoices.png", (40, 40)),
            font=("Cairo", 40, "bold"),
            compound="left",
        ).pack(padx=10, pady=10)

        self.init_search_bar()
        self.init_invoices_table()

        # ربط أحداث البحث
        self.bind_search_events()
        self.refresh_table()

    def get_invoices_with_details(self):
        """جلب الفواتير مع تفاصيل العميل وحساب الحالة"""
        try:
            sales = self.invoices_db.get_sales()
            invoices_with_details = []

            for sale in sales:
                # sale: (id, number, total, discount, tax, paid, change, customer_id, date)
                sale_id = sale[0]
                number = sale[1]
                total = float(sale[2])
                paid = float(sale[5])
                change = float(sale[6])
                customer_id = sale[7]
                date = sale[8]

                # جلب اسم العميل
                customer_name = "نقدي"
                if customer_id:
                    customer = self.customers_db.get_customer(customer_id)
                    if customer:
                        customer_name = customer[1]  # اسم العميل

                if paid >= total:
                    status = "مدفوعة"
                elif 0 < paid < total:
                    status = "مدفوعة جزئياً"
                else:
                    status = "آجل"

                invoices_with_details.append(
                    (
                        sale_id,  # ID
                        number,  # رقم الفاتورة
                        date,  # التاريخ
                        customer_name,  # العميل
                        status,  # الحالة
                        format_currency(total),  # الإجمالي
                        format_currency(paid),  # المدفوع
                        format_currency(change),  # الباقي
                    )
                )

            return invoices_with_details

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل جلب الفواتير: {e}")
            return []

    def bind_search_events(self):
        """ربط أحداث البحث"""
        key_shortcut(
            self.from_date,
            ["<KeyRelease>", "<<DateEntrySelected>>"],
            self.filter_invoices,
        )
        key_shortcut(
            self.to_date,
            ["<KeyRelease>", "<<DateEntrySelected>>"],
            self.filter_invoices,
        )
        key_shortcut(self.customer_entry, "<KeyRelease>", self.filter_invoices)
        key_shortcut(self.invoice_number_entry, "<KeyRelease>", self.filter_invoices)
        self.payment_status.configure(command=self.filter_invoices)

    def init_search_bar(self):
        """شريط البحث والفلترة مع DateEntry"""

        search_card = CTkFrame(
            self.root,
            corner_radius=15,
            border_width=1,
            border_color=("#AFAFAF", "#3f3f46"),
            fg_color=("#DDDDDD", "#1f1f1f"),
        )
        search_card.pack(fill="x", padx=20, pady=15)

        # Grid System
        for i in range(3):
            search_card.grid_columnconfigure(i, weight=1)

        # العنوان
        title = CTkLabel(
            search_card,
            text="🔎 بحث وفلترة الفواتير",
            font=("Cairo", 20, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, sticky="e", padx=20, pady=(15, 20))

        # 📅 من تاريخ
        from_label = CTkLabel(
            search_card,
            text="📅 من تاريخ",
            font=("Cairo", 14, "bold"),
        )
        from_label.grid(row=0, column=0, sticky="w", padx=10, pady=(0, 2))

        self.from_date = DateEntry(
            search_card,
            date_pattern="yyyy-mm-dd",
            font=("Cairo", 16),
            background="#262626",
            foreground="#f3f4f6",
            bordercolor="#555555",
            width=12,
            relief="flat",
        )
        self.from_date.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # 📅 إلى تاريخ
        to_label = CTkLabel(
            search_card,
            text="📅 إلى تاريخ",
            font=("Cairo", 14, "bold"),
        )
        to_label.grid(row=0, column=1, sticky="w", padx=10, pady=(0, 2))

        self.to_date = DateEntry(
            search_card,
            date_pattern="yyyy-mm-dd",
            font=("Cairo", 16),
            background="#262626",
            foreground="#f3f4f6",
            bordercolor="#555555",
            width=12,
            relief="flat",
        )
        self.to_date.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # ------------------------
        # 👤 العميل + رقم الفاتورة
        # ------------------------
        self.customer_entry = CTkEntry(
            search_card,
            placeholder_text="👤 اسم العميل",
            height=42,
            font=("Cairo", 18),
            corner_radius=10,
        )
        self.customer_entry.grid(row=2, column=0, padx=10, pady=8, sticky="ew")

        self.invoice_number_entry = CTkEntry(
            search_card,
            placeholder_text="🔢 رقم الفاتورة",
            height=42,
            font=("Cairo", 18),
            corner_radius=10,
        )
        self.invoice_number_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        # ------------------------
        # 💰 حالة الدفع
        # ------------------------
        self.payment_status = CTkSegmentedButton(
            search_card,
            values=["الكل", "مدفوعة", "مدفوعة جزئياً", "آجل"],
            font=("Cairo", 16, "bold"),
            height=45,
            corner_radius=15,
            selected_color="#26dc96",
            selected_hover_color="#1dbe81",
        )
        self.payment_status.set("الكل")
        self.payment_status.grid(
            row=3, column=0, columnspan=3, padx=10, pady=15, sticky="ew"
        )

        # ------------------------
        # الأزرار
        # ------------------------
        actions_frame = CTkFrame(search_card, fg_color="transparent")
        actions_frame.grid(row=4, column=0, columnspan=3, pady=15, padx=10, sticky="ew")

        for i in range(3):
            actions_frame.grid_columnconfigure(i, weight=1)

        CTkButton(
            actions_frame,
            text="عرض الفاتورة",
            fg_color="#26dc96",
            hover_color="#1dbe81",
            font=("Cairo", 18, "bold"),
            height=45,
            corner_radius=12,
            command=self.show_invoice_details,
        ).grid(row=0, column=1, padx=5, sticky="ew")

        CTkButton(
            actions_frame,
            text="إعادة تعيين",
            fg_color="#6b7280",
            hover_color="#4b5563",
            font=("Cairo", 18, "bold"),
            height=45,
            corner_radius=12,
            command=self.reset_filters,
        ).grid(row=0, column=2, padx=5, sticky="ew")

    def init_invoices_table(self):
        """جدول الفواتير"""
        self.tree = TreeView(
            self.root,
            (
                "ID",
                "رقم الفاتورة",
                "التاريخ",
                "العميل",
                "الحالة",
                "الإجمالي",
                "المدفوع",
                "الباقي",
            ),
            (30, 120, 120, 100, 70, 100, 100, 100),
        )

        # ربط double-click لعرض التفاصيل
        key_shortcut(
            self.tree.tree, ["<Double-1>", "<Return>"], self.show_invoice_details
        )

    def get_state_tag(self, status):
        """تحديد لون الحالة"""
        if status == "مدفوعة":
            return "success"
        elif status == "مدفوعة جزئياً":
            return "warning"
        else:
            return "danger"

    def refresh_table(self, data=None):
        """تحديث الجدول"""
        if data is None:
            data = self.invoices

        self.tree.tree.delete(*self.tree.tree.get_children())
        for inv in data:
            self.tree.tree.insert(
                "",
                "end",
                values=inv,
                tags=(self.get_state_tag(inv[4]),),
            )

    def filter_invoices(self, event=None):
        """تصفية الفواتير حسب معايير البحث"""
        filtered = []

        # جلب قيم البحث
        from_date = str(self.from_date.get_date()).strip()
        to_date = str(self.to_date.get_date()).strip()
        customer = self.customer_entry.get().strip()
        invoice_num = self.invoice_number_entry.get().strip()
        status = self.payment_status.get()

        for inv in self.invoices:
            # فلترة حسب رقم الفاتورة
            if invoice_num and invoice_num not in str(inv[1]):
                continue

            # فلترة حسب العميل
            if customer and customer.lower() not in inv[3].lower():
                continue

            # فلترة حسب التاريخ
            current_date = from_date == to_date and from_date == str(date.today())
            if from_date and inv[2] < from_date and not current_date:
                continue
            if to_date and inv[2] > to_date and not current_date:
                continue

            # فلترة حسب الحالة
            if status != "الكل" and inv[4] != status:
                continue

            filtered.append(inv)

        self.refresh_table(filtered)

    def reset_filters(self):
        """إعادة تعيين الفلاتر"""
        today = date.today()
        self.from_date.set_date(today)
        self.to_date.set_date(today)
        self.customer_entry.delete(0, "end")
        self.invoice_number_entry.delete(0, "end")
        self.payment_status.set("الكل")
        self.refresh_table()

    def show_invoice_details(self, event=None):
        """عرض تفاصيل الفاتورة في نافذة منبثقة"""

        selected = self.tree.tree.selection()
        if not selected:
            return messagebox.showwarning("تنبيه", "الرجاء اختيار فاتورة")

        invoice_data = self.tree.tree.item(selected[0])["values"]
        invoice_id = invoice_data[0]
        invoice_number = invoice_data[1]

        sale = self.invoices_db.get_sale(invoice_id)
        if not sale:
            return messagebox.showerror("خطأ", "الفاتورة غير موجودة")

        # بيانات الفاتورة من جدول sales
        total = float(sale[2])
        discount = float(sale[3])
        tax = float(sale[4])
        paid = float(sale[5])
        change = float(sale[6])
        customer_id = sale[7]
        date = sale[8]

        # اسم العميل
        customer_name = "نقدي"
        if customer_id:
            customer = self.customers_db.get_customer(customer_id)
            if customer:
                customer_name = customer[1]

        # المنتجات
        items = self.sale_items_db.get_sale_items(invoice_id)

        # =========================
        # إنشاء النافذة
        # =========================
        dialog = CTkToplevel(self.root)
        dialog.title(f"تفاصيل الفاتورة - {invoice_number}")
        dialog.geometry("520x700+200+0")

        dialog.grab_set()
        dialog.focus_force()

        container = CTkFrame(dialog, corner_radius=15)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # عنوان
        CTkLabel(
            container,
            text=f"🧾 فاتورة رقم {invoice_number}",
            font=("Arial", 22, "bold"),
        ).pack(pady=(10, 5))

        CTkLabel(
            container,
            text=f"التاريخ: {date}",
            font=("Arial", 16),
        ).pack()

        CTkLabel(
            container,
            text=f"العميل: {customer_name}",
            font=("Arial", 18, "bold"),
            text_color="#2563eb",
        ).pack(pady=(5, 15))

        # =========================
        # جدول المنتجات
        # =========================
        items_frame = CTkScrollableFrame(container, height=250)
        items_frame.pack(fill="x", padx=5, pady=5)

        self.row_frames = {}

        if not items:
            CTkLabel(
                items_frame,
                text="لا توجد منتجات",
                font=("Cairo", 16),
            ).pack(pady=10)
        else:
            for item in items:
                product_id = item[2]
                quantity = item[3]
                price = float(item[4])
                item_total = float(item[5])

                product = self.products_db.get_product(product_id)
                product_name = product[1] if product else "منتج محذوف"

                row = CTkFrame(items_frame, corner_radius=10)
                row.pack(fill="x", pady=4, padx=5)
                self.row_frames[product_id] = row

                frame = CTkFrame(row, fg_color="transparent")
                frame.pack(fill="x")

                # زر حذف المنتج
                CTkButton(
                    frame,
                    text="",
                    image=image("assets/delete.png", (20, 20)),
                    fg_color="transparent",
                    width=0,
                    command=lambda single_item=item, pid=product_id: self.return_product(
                        single_item,
                        invoice_number,
                        pid,
                        invoice_id,
                        customer_id,
                        dialog,
                    ),
                ).pack(side="left")

                # اسم المنتج
                CTkLabel(
                    frame,
                    text=f"{product_name}",
                    font=("Arial", 16, "bold"),
                ).pack(side="right", padx=10, pady=(5, 0))

                CTkLabel(
                    row,
                    text=f"× {price} = {format_currency(item_total)}",
                    font=("Arial", 15),
                ).pack(side="right", padx=5)

                # الكمية + السعر + الإجمالي
                quantity_var = StringVar(value=str(quantity))

                quantity_entry = CTkEntry(
                    row,
                    textvariable=quantity_var,
                    width=60,
                    font=("Arial", 15),
                    justify="center",
                    corner_radius=5,
                )
                quantity_entry.pack(side="right", padx=(0, 5))

                # زر تحديث الكمية
                CTkButton(
                    row,
                    text="تحديث",
                    font=("Arial", 14),
                    fg_color="#2563eb",
                    hover_color="#1e40af",
                    command=lambda pid=product_id, q_var=quantity_var, old_total=item_total: self.update_item_quantity(
                        invoice_id,
                        invoice_number,
                        pid,
                        q_var,
                        old_total,
                        customer_id,
                        dialog,
                    ),
                ).pack(side="left", padx=5, pady=5)

        # =========================
        # الملخص المالي
        # =========================
        summary = CTkFrame(container, corner_radius=12)
        summary.pack(fill="x", pady=10, padx=5)

        def summary_row(label, value, color=None):
            row = CTkFrame(summary, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)

            CTkLabel(
                row,
                text=value,
                font=("Arial", 16, "bold"),
                text_color=color if color else ("black", "white"),
            ).pack(side="left")
            CTkLabel(row, text=label, font=("Arial", 16)).pack(side="right")

        summary_row(":الخصم", format_currency(discount))
        summary_row(":الضريبة", format_currency(tax))
        summary_row(":المطلوب", format_currency(total))
        summary_row(":المدفوع", format_currency(paid), "#2563eb")
        summary_row(
            ":الباقي",
            format_currency(change),
            "#059669" if change > 0 else "#dc2626",
        )

        # اطار الأزرار
        action_frame = CTkFrame(container, border_width=1, border_color="#bebebe")
        action_frame.pack(pady=10)

        CTkButton(
            action_frame,
            text="إغلاق",
            font=("Arial", 18, "bold"),
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=dialog.destroy,
        ).grid(row=0, column=0, pady=3, padx=5)
        CTkButton(
            action_frame,
            text="طباعة",
            font=("Arial", 18, "bold"),
            fg_color="#00A5A5",
            hover_color="#008A8A",
            command=self.print_invoice,
        ).grid(row=0, column=1, pady=3, padx=5)
        CTkButton(
            action_frame,
            text="ارجاع الفاتورة",
            font=("Arial", 18, "bold"),
            fg_color="#CF0000",
            hover_color="#9E0000",
            command=lambda: self.return_full_invoice(
                invoice_id, invoice_number, items, customer_id, dialog
            ),
        ).grid(row=1, columnspan=2, pady=3, padx=5)

    def get_sale_items(self, sale_id):
        """جلب عناصر الفاتورة - دالة مساعدة"""
        try:
            return self.sale_items_db.get_sale_items(sale_id)
        except Exception as e:
            return []

    def update_item_quantity(
        self,
        sale_id,
        invoice_number,
        product_id,
        quantity_var,
        old_total,
        customer_id,
        dialog,
    ):
        """تحديث كمية المنتج في الفاتورة"""
        try:
            if not is_number(quantity_var.get()):
                return messagebox.showerror("خطأ", "يجب ادخال رقم صحيح")

            new_qty = float(quantity_var.get())

            if new_qty <= 0:
                items = self.sale_items_db.get_sale_items(sale_id)
                item = next((i for i in items if i[2] == product_id), None)
                if item:
                    return self.return_product(
                        item, invoice_number, product_id, sale_id, customer_id, dialog
                    )
                return

            # =========================
            # جلب بيانات العنصر الأصلي
            # =========================
            items = self.sale_items_db.get_sale_items(sale_id)
            item = next((i for i in items if i[2] == product_id), None)

            if not item:
                return messagebox.showerror("خطأ", "المنتج غير موجود")

            old_qty = float(item[3])
            price = float(item[4])
            new_total = new_qty * price

            # =========================
            # التحقق من المخزون
            # =========================
            product = self.products_db.get_product(product_id)
            if not product:
                return messagebox.showerror("خطأ", "المنتج غير موجود بالمخزن")

            stock_qty = float(product[5])  # quantity في جدول products

            # المتاح الحقيقي
            available_qty = stock_qty + old_qty

            if new_qty > available_qty:
                return messagebox.showerror(
                    "Out Of Stock",
                    f"الكمية غير متوفرة بالمخزن.\nالمتاح: {available_qty}",
                )

            # =========================
            # تحديث item في قاعدة البيانات
            # =========================
            self.sale_items_db.update_sale_item_quantity(item[0], new_qty, new_total)

            # تحديث إجمالي الفاتورة
            sale = self.invoices_db.get_sale(sale_id)
            if sale:
                old_sale_total = float(sale[2])
                diff = new_total - old_total
                new_sale_total = old_sale_total + diff
                self.invoices_db.update_sale_total(sale_id, new_sale_total)

            # =========================
            # تحديث المخزون
            # =========================
            diff_qty = old_qty - new_qty

            if diff_qty > 0:
                self.stock_movements_db.add_movement(
                    product_id=product_id,
                    quantity=abs(diff_qty),
                    movement_type="ارجاع",
                    reference_id=sale_id,
                    reference_number=invoice_number,
                )
            elif diff_qty < 0:
                # رجع فرق للمخزن
                self.stock_movements_db.add_movement(
                    product_id=product_id,
                    quantity=diff_qty,
                    movement_type="بيع",
                    reference_id=sale_id,
                    reference_number=invoice_number,
                )

            # تحديث الجدول
            self.invoices = self.get_invoices_with_details()
            self.refresh_table()

            messagebox.showinfo("نجاح", "تم تحديث الكمية بنجاح ✅")

        except Exception as e:
            self.con.rollback()
            messagebox.showerror("خطأ", f"فشل تحديث الكمية: {e}")

    def return_full_invoice(self, sid, invoice_number, items, customer_id, dialog):
        """إرجاع الفاتورة كاملة"""
        if not messagebox.askyesno("تأكيد", "هل أنت متأكد من إرجاع الفاتورة كاملة؟"):
            return

        try:
            sale = self.invoices_db.get_sale(sid)
            if not sale:
                return

            total = float(sale[2])
            paid = float(sale[5])

            remaining = total - paid  # الدين الفعلي

            # -----------------------
            # 1️⃣ تجميع المنتجات
            # -----------------------
            products_to_return = {}

            for item in items:
                product_id = item[2]
                quantity = item[3]

                if product_id in products_to_return:
                    products_to_return[product_id] += quantity
                else:
                    products_to_return[product_id] = quantity

            # -----------------------
            # 2️⃣ إعادة المخزون
            # -----------------------
            for product_id, quantity in products_to_return.items():
                self.stock_movements_db.add_movement(
                    product_id=product_id,
                    quantity=quantity,
                    movement_type="ارجاع",
                    reference_id=sid,
                    reference_number=invoice_number,
                )

            # -----------------------
            # 3️⃣ تقليل دين العميل
            # -----------------------
            if customer_id and remaining > 0:
                self.customers_db.reduce_debt_from_customer(customer_id, remaining)

            # -----------------------
            # 4️⃣ حذف الفاتورة
            # -----------------------
            self.invoices_db.delete_sales([sid])

            # تحديث الجدول
            self.invoices = self.get_invoices_with_details()
            self.refresh_table()

            dialog.destroy()
            messagebox.showinfo("نجاح", "تم إرجاع الفاتورة و تحديث المخزون بنجاح ✅")

        except Exception as e:
            self.con.rollback()
            messagebox.showerror("خطأ", f"فشل الإرجاع: {e}")

    def return_product(self, item, invoice_number, pid, sale_id, customer_id, dialog):
        """
        item: (id, sale_id, product_id, quantity, price, total)
        """

        if not messagebox.askyesno(
            "تأكيد", "هل أنت متأكد من إرجاع هذا المنتج من الفاتورة؟"
        ):
            return

        try:
            # نجيب كل عناصر الفاتورة من DB
            items = self.sale_items_db.get_sale_items(sale_id)

            # لو المنتج ده هو الوحيد في الفاتورة
            if len(items) == 1:
                return self.return_full_invoice(
                    sale_id, invoice_number, items, customer_id, dialog
                )

            # ==============================
            # غير كده → نحذف المنتج عادي
            # ==============================

            item_id = item[0]
            product_id = item[2]
            quantity = item[3]
            item_total = float(item[5])

            # حذف الصف من الواجهة
            if pid in self.row_frames:
                self.row_frames[pid].destroy()
                del self.row_frames[pid]

            # إعادة الكمية للمخزون
            self.stock_movements_db.add_movement(
                product_id=product_id,
                quantity=quantity,
                movement_type="ارجاع",
                reference_id=sale_id,
                reference_number=invoice_number,
            )

            # حذف العنصر من قاعدة البيانات
            self.sale_items_db.delete_sale_item(item_id)

            # تحديث إجمالي الفاتورة
            sale = self.invoices_db.get_sale(sale_id)
            if not sale:
                return

            old_total = float(sale[2])
            paid = float(sale[5])

            new_total = old_total - item_total
            if new_total < 0:
                new_total = 0

            self.invoices_db.update_sale_total(sale_id, new_total)

            # تحديث الدين لو فيه
            remaining = new_total - paid
            if customer_id and remaining < 0:
                self.customers_db.reduce_debt_from_customer(customer_id, abs(remaining))

            messagebox.showinfo("نجاح", "تم إرجاع المنتج بنجاح ✅")

            # تحديث الجدول الرئيسي
            self.invoices = self.get_invoices_with_details()
            self.refresh_table()

        except Exception as e:
            self.con.rollback()
            messagebox.showerror("خطأ", f"فشل إرجاع المنتج: {e}")

    def print_invoice(self, event=None):
        """طباعة الفاتورة بعد اختيارها من الجدول"""
        selected = self.tree.tree.selection()
        if not selected:
            return messagebox.showwarning("تنبيه", "الرجاء اختيار فاتورة")

        invoice_data = self.tree.tree.item(selected[0])["values"]
        invoice_id = invoice_data[0]

        sale = self.invoices_db.get_sale(invoice_id)
        if not sale:
            return messagebox.showerror("خطأ", "الفاتورة غير موجودة")

        # بيانات الفاتورة
        total = float(sale[2])
        discount = float(sale[3])
        tax = float(sale[4])
        paid = float(sale[5])
        change = float(sale[6])
        customer_id = sale[7]
        date_str = sale[8]
        

        customer_name = "نقدي"
        if customer_id:
            customer = self.customers_db.get_customer(customer_id)
            if customer:
                customer_name = customer[1]

        # المنتجات
        items = self.sale_items_db.get_sale_items(invoice_id)
        products = []
        for item in items:
            product_id = item[2]
            product = self.products_db.get_product(product_id)
            product_name = product[1] if product else "منتج محذوف"
            qty = item[3]
            price = float(item[4])
            total_item = float(item[5])
            products.append({
                "name": product_name,
                "qty": qty,
                "price": price,
                "total": total_item
            })

        # فصل الوقت عن التاريخ
        try:
            # نفترض التنسيق HH:MM:SS DD-MM-YYYY
            date_part, time_part = date_str.split(" ", 1)
        except Exception:
            # لو التنسيق غريب نخليهم فارغين
            time_part = ""
            date_part = date_str

        # بيانات جاهزة للطباعة
        sale_data = {
            "invoice_number": sale[1],
            "date": date_part,     # DD-MM-YYYY
            "time": time_part,     # HH:MM:SS
            "customer_name": customer_name,
            "subtotal": total - discount - tax,
            "discount": discount,
            "tax": tax,
            "total": total,
            "paid": paid,
            "remaining": change,
        }

        from utils.print_thermal import print_shop_invoice

        try:
            print_shop_invoice(sale_data, products)
            messagebox.showinfo("نجاح", "تم إرسال الفاتورة للطابعة ✅")
        except Exception as e:
            messagebox.showwarning("تحذير", f"حدث خطأ في الطباعة: {e}")
