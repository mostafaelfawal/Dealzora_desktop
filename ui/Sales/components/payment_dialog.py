from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    CTkScrollableFrame,
    CTkToplevel,
    StringVar,
)
from tkinter import StringVar, messagebox
from time import strftime
from utils.key_shortcut import key_shortcut
from utils.format_currency import format_currency
from utils.image import image

# =============================
# Product Item Component with Observer
# =============================


class InvoiceItem(CTkFrame):
    def __init__(self, parent, product, sale_state, on_price_edit, data_service):
        super().__init__(
            parent,
            fg_color=("gray90", "gray25"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray35"),
        )

        self.product = product
        self.sale_state = sale_state
        self.on_price_edit = on_price_edit
        self.data_service = data_service

        # تخزين مراجع للعناصر التي سيتم تحديثها
        self.price_label = None
        self.total_label = None

        # تسجيل هذا العنصر كمراقب للتغييرات
        self.sale_state.add_observer(self)

        self._build()

    def on_state_changed(self):
        """يتم استدعاؤها عند تغيير الحالة في SaleState"""
        self._update_display()

    def _update_display(self):
        """تحديث عرض السعر والإجمالي"""
        if not self.winfo_exists():
            return

        display_price = self.sale_state.get_product_display_price(self.product["id"])
        qty = self.product["qty"]
        total = display_price * qty

        if self.price_label:
            self.price_label.configure(text=format_currency(display_price))

        if self.total_label:
            self.total_label.configure(text=format_currency(total))

    def _build(self):
        name = self.product["name"]
        display_price = self.sale_state.get_product_display_price(self.product["id"])
        qty = self.product["qty"]
        total = display_price * qty

        # اسم المنتج
        CTkLabel(self, text=name, anchor="w", font=("Cairo", 12, "bold")).pack(
            side="right", padx=10, pady=2
        )

        # الكمية
        CTkLabel(self, text=str(qty), font=("Cairo", 12)).pack(
            side="right", padx=5, pady=2
        )

        # السعر المعروض
        self.price_label = CTkLabel(
            self, text=format_currency(display_price), font=("Cairo", 12)
        )
        self.price_label.pack(side="right", padx=5, pady=2)

        # الإجمالي
        self.total_label = CTkLabel(
            self,
            text=format_currency(total),
            font=("Cairo", 12, "bold"),
            text_color=("green", "#00ff00"),
        )
        self.total_label.pack(side="right", padx=5, pady=2)

        price_edit_permission = self.data_service.price_edit_permission
        if price_edit_permission:
            # زر التعديل
            CTkButton(
                self,
                text="",
                image=image("assets/edit.png", (20, 20)),
                width=30,
                height=28,
                corner_radius=6,
                fg_color=("gray75", "gray30"),
                hover_color=("gray65", "gray40"),
                command=self._edit_price,
            ).pack(side="left", padx=5, pady=2)

    def _edit_price(self):
        self.on_price_edit(self.product)

    def destroy(self):
        """إزالة المراقب عند تدمير العنصر"""
        try:
            self.sale_state.remove_observer(self)
        except:
            pass
        super().destroy()


# =============================
# Items List مع رؤوس الأعمدة
# =============================


class InvoiceItemsList(CTkScrollableFrame):
    def __init__(self, parent, sale_state, on_price_edit, data_service):
        super().__init__(
            parent,
            fg_color=("gray95", "gray20"),
            corner_radius=12,
            border_width=1,
            border_color=("gray85", "gray30"),
        )

        self.sale_state = sale_state
        self.on_price_edit = on_price_edit
        self.data_service = data_service
        self.items = {}  # تخزين مراجع العناصر {product_id: InvoiceItem}

        # تسجيل هذا العنصر كمراقب للتغييرات في السلة
        self.sale_state.add_observer(self)

        self._render()

    def on_state_changed(self):
        """يتم استدعاؤها عند تغيير الحالة في SaleState"""
        # التحقق من تغيير قائمة المنتجات (إضافة أو إزالة)
        current_product_ids = set(self.items.keys())
        new_product_ids = set(p["id"] for p in self.sale_state.selected_products)

        if current_product_ids != new_product_ids:
            # إذا تغيرت قائمة المنتجات، نعيد الرندر بالكامل
            self._render()

    def _render(self):
        # مسح المحتوى القديم وإعادة بناء القائمة
        for w in self.winfo_children():
            w.destroy()

        # إعادة تعيين قاموس العناصر
        self.items.clear()

        # إضافة رؤوس الأعمدة
        header_frame = CTkFrame(self, fg_color="transparent", height=35)
        header_frame.pack(fill="x", pady=(0, 2), padx=10)

        # تكوين أعمدة الرأس
        header_frame.grid_columnconfigure(0, weight=3)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)
        header_frame.grid_columnconfigure(4, weight=0)

        CTkLabel(
            header_frame,
            text="⚙️",
            font=("Cairo", 11, "bold"),
            text_color=("gray40", "gray70"),
        ).grid(row=0, column=0, padx=5, pady=2)

        CTkLabel(
            header_frame,
            text="💵 الإجمالي",
            font=("Cairo", 11, "bold"),
            text_color=("gray40", "gray70"),
        ).grid(row=0, column=1, padx=5, pady=2)

        CTkLabel(
            header_frame,
            text="💰 السعر",
            font=("Cairo", 11, "bold"),
            text_color=("gray40", "gray70"),
        ).grid(row=0, column=2, padx=5, pady=2)

        CTkLabel(
            header_frame,
            text="🔢 الكمية",
            font=("Cairo", 11, "bold"),
            text_color=("gray40", "gray70"),
        ).grid(row=0, column=3, padx=5, pady=2)

        # رؤوس الأعمدة
        CTkLabel(
            header_frame,
            text="📦 المنتج",
            font=("Cairo", 11, "bold"),
            text_color=("gray40", "gray70"),
        ).grid(row=0, column=4, sticky="w", padx=10, pady=2)

        # خط فاصل تحت الرؤوس
        separator = CTkFrame(self, height=2, fg_color=("gray75", "gray40"))
        separator.pack(fill="x", padx=10, pady=(0, 2))

        if not self.sale_state.selected_products:
            # عرض رسالة في حالة عدم وجود منتجات
            empty_label = CTkLabel(
                self,
                text="✨ لا توجد منتجات مضافة ✨",
                font=("Cairo", 14, "italic"),
                text_color=("gray50", "gray60"),
            )
            empty_label.pack(expand=True, fill="both", pady=20)
            return

        # عرض المنتجات
        for product in self.sale_state.selected_products:
            item = InvoiceItem(
                self, product, self.sale_state, self.on_price_edit, self.data_service
            )
            item.pack(fill="x", pady=1, padx=10)
            self.items[product["id"]] = item

    def destroy(self):
        """إزالة المراقب عند تدمير العنصر"""
        try:
            self.sale_state.remove_observer(self)
        except:
            pass
        super().destroy()


# =============================
# Totals Section - مع مراقبة التغييرات
# =============================


class TotalsBox(CTkFrame):
    def __init__(self, parent, sale_state):
        super().__init__(
            parent,
            fg_color=("gray90", "gray25"),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", "gray35"),
        )
        self.sale_state = sale_state

        # تخزين مراجع للعناصر
        self.subtotal_label = None
        self.discount_label = None
        self.tax_label = None
        self.total_label = None

        self._build()

        # تسجيل كمراقب للتغييرات
        self.sale_state.add_observer(self)
        self.fill_fields()

    def on_state_changed(self):
        """يتم استدعاؤها عند تغيير الحالة في SaleState"""
        self.fill_fields()

    def _row(self, label_text, is_total=False):
        frame = CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=2)

        # التسمية
        CTkLabel(
            frame, text=label_text, font=("Cairo", 12, "bold" if is_total else "normal")
        ).pack(side="right")

        # قيمة
        value = CTkLabel(
            frame,
            text="0",
            font=("Cairo", 13, "bold" if is_total else "normal"),
            text_color=("blue", "#00aaff") if is_total else None,
        )
        value.pack(side="right", padx=(10, 0))

        return value

    def _build(self):
        self.subtotal_label = self._row(" :الاجمالي الفرعي")
        self.discount_label = self._row(" :الخصم")
        self.tax_label = self._row(" :الضريبة")
        self.total_label = self._row(" :المطلوب", is_total=True)

    def fill_fields(self):
        if self.subtotal_label:
            self.subtotal_label.configure(
                text=format_currency(self.sale_state.subtotal)
            )
        if self.discount_label:
            self.discount_label.configure(
                text=format_currency(self.sale_state.discount_amount)
            )
        if self.tax_label:
            self.tax_label.configure(text=format_currency(self.sale_state.tax_amount))
        if self.total_label:
            self.total_label.configure(text=format_currency(self.sale_state.total))

    def destroy(self):
        """إزالة المراقب عند تدمير العنصر"""
        try:
            self.sale_state.remove_observer(self)
        except:
            pass
        super().destroy()


# =============================
# Payment Section
# =============================


class PaymentBox(CTkFrame):
    def __init__(self, parent, sale_state, dialog, on_finish_callback):
        super().__init__(
            parent,
            fg_color=("gray90", "gray25"),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", "gray35"),
        )

        self.sale_state = sale_state
        self.dialog = dialog
        self.on_finish_callback = on_finish_callback
        self.paid_var = StringVar(value=self.sale_state.total)

        self._build()

        # تسجيل كمراقب للتغييرات
        self.sale_state.add_observer(self)
        self._bind_events()

    def on_state_changed(self):
        """يتم استدعاؤها عند تغيير الحالة في SaleState"""
        # تحديث قيمة المدفوع الافتراضية
        self.paid_var.set(str(self.sale_state.total))
        self._update_change()

    def _build(self):
        # عنوان
        title = CTkLabel(self, text="💳 معلومات الدفع", font=("Cairo", 13, "bold"))
        title.pack(pady=(4, 2))

        # حقل المدفوع
        paid_frame = CTkFrame(self, fg_color="transparent")
        paid_frame.pack(fill="x", padx=15, pady=2)

        CTkLabel(paid_frame, text=":المدفوع", font=("Cairo", 11)).pack(
            side="right", padx=10
        )

        self.paid_entry = CTkEntry(
            paid_frame,
            justify="center",
            textvariable=self.paid_var,
            font=("Cairo", 13),
            height=35,
            corner_radius=8,
        )
        self.paid_entry.pack(side="right", padx=10)

        # الباقي
        self.change_label = CTkLabel(self, font=("Cairo", 11, "bold"))
        self.change_label.pack(pady=2)
        self._update_change()

        # أزرار
        button_frame = CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=4)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.print_btn = CTkButton(
            button_frame,
            text="🖨️ طباعة",
            font=("Cairo", 12, "bold"),
            height=35,
            corner_radius=8,
            fg_color=("blue", "#2c3e66"),
            hover_color=("darkblue", "#1e2b4f"),
            command=self._print_invoice,
        )
        self.print_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.confirm_btn = CTkButton(
            button_frame,
            text="✅ تأكيد",
            font=("Cairo", 12, "bold"),
            height=35,
            corner_radius=8,
            fg_color=("green", "#00aa55"),
            hover_color=("darkgreen", "#008844"),
            command=self._confirm_payment,
        )
        self.confirm_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

    def _print_invoice(self):
        amount_paid = self.paid_var.get()
        try:
            self.sale_state.print_current_invoice(amount_paid)
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def _confirm_payment(self):
        amount_paid = self.paid_var.get()
        self.sale_state.complete_sale(amount_paid)

        self.dialog.destroy()
        messagebox.showinfo(
            "تم البيع", "Dealzora تمت عملية البيع بنجاح! شكراً لاستخدامك"
        )
        # اعادة حقول الخصم و الضريبه
        self.on_finish_callback()

    def _bind_events(self):
        self._paid_trace_id = self.paid_var.trace_add(
            "write", lambda *_: self._update_change()
        )

    def destroy(self):
        # إزالة المراقب قبل تدمير العنصر
        try:
            self.sale_state.remove_observer(self)
        except:
            pass
        # إزالة الاستماع
        if hasattr(self, "_paid_trace_id"):
            self.paid_var.trace_remove("write", self._paid_trace_id)
        super().destroy()

    def _update_change(self):
        try:
            paid = float(self.paid_var.get().replace(",", ""))
        except:
            paid = 0

        change = paid - self.sale_state.total

        if change >= 0:
            color = ("green", "#00ff00")
            status = "✅ الباقي"
        else:
            color = ("red", "#ff5555")
            status = "⚠️ الباقي"

        self.change_label.configure(
            text=f"{status}: {format_currency(abs(change))}", text_color=color
        )


# =============================
# Header
# =============================


class InvoiceHeader(CTkFrame):
    def __init__(self, parent, sale_state):
        super().__init__(
            parent,
            fg_color=("gray90", "gray25"),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", "gray35"),
        )

        self.sale_state = sale_state

        # تخزين مراجع للعناصر
        self.customer_label = None

        # تسجيل كمراقب للتغييرات
        self.sale_state.add_observer(self)

        self._build()

    def on_state_changed(self):
        """يتم استدعاؤها عند تغيير الحالة في SaleState"""
        if self.customer_label:
            customer_name = self.sale_state.selected_customer
            self.customer_label.configure(text=f"العميل: {customer_name}")

    def _build(self):
        # عنوان
        title = CTkLabel(
            self,
            text="🧾 فاتورة البيع",
            font=("Cairo", 16, "bold"),
            text_color=("blue", "#00aaff"),
        )
        title.pack(pady=(4, 2))

        # إطار المعلومات
        info_frame = CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=2)

        invoice_number = self.sale_state.invoice_number
        self.invoice_label = CTkLabel(
            info_frame,
            text=f"{invoice_number} :رقم الفاتورة",
            font=("Cairo", 11),
            anchor="e",
        )
        self.invoice_label.pack(anchor="e", pady=1)

        customer_name = self.sale_state.selected_customer
        self.customer_label = CTkLabel(
            info_frame, text=f"العميل: {customer_name}", font=("Cairo", 11), anchor="e"
        )
        self.customer_label.pack(anchor="e", pady=1)

        self.date_label = CTkLabel(
            info_frame,
            text=self.get_current_date(),
            font=("Cairo", 10),
            text_color=("gray50", "gray60"),
            anchor="e",
        )
        self.date_label.pack(anchor="e", pady=1)

    def get_current_date(self):
        date = strftime("%d/%m/%Y")
        time = strftime("%H:%M:%S")
        return f"⏰ {time} | 📅 {date}"

    def destroy(self):
        """إزالة المراقب عند تدمير العنصر"""
        try:
            self.sale_state.remove_observer(self)
        except:
            pass
        super().destroy()


# =============================
# Main Invoice UI
# =============================


class InvoiceView(CTkToplevel):
    def __init__(self, parent, sale_state, on_finish_callback, data_service):
        super().__init__(parent)

        self.sale_state = sale_state
        self.on_finish_callback = on_finish_callback
        self.data_service = data_service

        # تكوين النافذة
        self._config_dialog()
        self._build()

    def _build(self):
        # تعيين لون الخلفية
        self.configure(fg_color=("gray97", "gray15"))

        # إطار رئيسي مع مسافات أقل
        main_frame = CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=6, pady=4)

        # Header
        self.header = InvoiceHeader(main_frame, self.sale_state)
        self.header.pack(fill="x", pady=(0, 4))

        # Items List
        self.items = InvoiceItemsList(
            main_frame, self.sale_state, self._on_price_edit, self.data_service
        )
        self.items.pack(fill="both", expand=True, pady=(0, 4))

        # Totals
        self.totals = TotalsBox(main_frame, self.sale_state)
        self.totals.pack(fill="x", pady=(0, 4))

        # Payment
        self.payment = PaymentBox(
            main_frame, self.sale_state, self, self.on_finish_callback
        )
        self.payment.pack(fill="x")

    def _on_price_edit(self, product):
        """فتح نافذة تعديل السعر"""
        edit_dialog = CTkToplevel(self)
        edit_dialog.title("تعديل السعر")
        edit_dialog.geometry("350x250")
        edit_dialog.grab_set()

        edit_dialog.transient(self)

        # المحتوى
        CTkLabel(
            edit_dialog, text=f"تعديل سعر {product['name']}", font=("Cairo", 13, "bold")
        ).pack(pady=8)

        # عرض السعر الأصلي
        CTkLabel(
            edit_dialog,
            text=f"السعر الأصلي: {format_currency(product['original_price'])}",
            font=("Cairo", 10),
            text_color=("gray", "gray60"),
        ).pack(pady=2)

        # عرض السعر الحالي
        current_price = self.sale_state.get_product_display_price(product["id"])
        CTkLabel(
            edit_dialog,
            text=f"السعر الحالي: {format_currency(current_price)}",
            font=("Cairo", 10),
            text_color=("blue", "#00aaff"),
        ).pack(pady=2)

        def save_price():
            try:
                new_price = float(price_var.get())
                if new_price < 0:
                    raise ValueError("السعر لا يمكن أن يكون سالباً")
                self.sale_state.update_product_price(product["id"], new_price)
                edit_dialog.destroy()
            except ValueError as e:
                error_label = CTkLabel(
                    edit_dialog,
                    text=f"⚠️ {str(e) if str(e) else 'يرجى إدخال رقم صحيح'}",
                    text_color="red",
                    font=("Cairo", 10),
                )
                error_label.pack(pady=2)
                edit_dialog.after(2000, error_label.destroy)

        # حقل السعر
        price_var = StringVar(value=str(current_price))
        price_entry = CTkEntry(
            edit_dialog, textvariable=price_var, font=("Cairo", 13), width=200
        )
        price_entry.pack(pady=8)
        key_shortcut(price_entry, "<Return>", save_price)
        key_shortcut(edit_dialog, "<Escape>", edit_dialog.destroy)

        # أزرار
        button_frame = CTkFrame(edit_dialog, fg_color="transparent")
        button_frame.pack(pady=12)

        CTkButton(
            button_frame, text="حفظ", command=save_price, font=("Cairo", 11), width=80
        ).pack(side="left", padx=5)

        CTkButton(
            button_frame,
            text="إلغاء",
            command=edit_dialog.destroy,
            font=("Cairo", 11),
            fg_color="gray",
            width=80,
        ).pack(side="left", padx=5)

    def _config_dialog(self):
        """تكوين خصائص النافذة"""
        self.title("🧾 Dealzora | فاتورة البيع")
        self.geometry("500x700+200+0")
        self.minsize(400, 500)
        self.grab_set()
        self.focus_force()
        self.lift()
