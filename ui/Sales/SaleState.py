import threading
from time import strftime
from tkinter import messagebox
from utils.is_number import is_number
from tkinter.messagebox import showwarning


class SaleState:
    def __init__(self, tax_rate, data_service):
        self.tax_rate = tax_rate
        self.data_service = data_service
        self._reset_sale()
        self._observers = []  # قائمة للمراقبين

    def add_observer(self, observer):
        """إضافة مراقب للتغييرات"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """إزالة مراقب"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self):
        """إخطار جميع المراقبين بتغيير الحالة"""
        for observer in self._observers:
            observer.on_state_changed()

    def _reset_sale(self):
        self._invoice_number = self._generate_invoice_number()
        self._selected_products = {}
        self._selected_customer = "نقدي"
        self._customer_id = None
        self._discount_type = "percent"  # or fixed
        self._discount_value = 0
        self._tax_type = "percent"  # or fixed
        self._tax_value = self._get_default_tax()

        # تخزين تأثير كل منتج على الخصم والضريبة
        # {product_id: {'discount_effect': value, 'tax_effect': value, 'adjusted_price': price}}
        self._product_effects = {}

        if hasattr(self, "_observers"):
            self._notify_observers()

    def _generate_invoice_number(self):
        "انشاء رقم فاتورة فريد"
        unique_id = strftime("%Y%m%d%H%M%S")
        return f"INV-{unique_id}"

    def _get_default_tax(self):
        return self.tax_rate if self.tax_rate else 0

    @property
    def invoice_number(self):
        return self._invoice_number

    @property
    def selected_customer(self):
        return self._selected_customer

    @property
    def customer_id(self):
        return self._customer_id

    def update_selected_customer(self, c_name, c_id):
        self._selected_customer = c_name if c_name else None
        self._customer_id = c_id if c_id else None
        self._notify_observers()

    @property
    def total_qty(self):
        return sum(item["qty"] for item in self.selected_products)

    @property
    def total_items(self):
        return len(self.selected_products)

    @property
    def subtotal(self):
        """حساب الإجمالي الفرعي باستخدام الأسعار الأصلية"""
        result = sum(
            item["original_price"] * item["qty"] for item in self.selected_products
        )
        return round(result, 2)

    @property
    def total(self):
        result = self.subtotal - self.discount_amount + self.tax_amount
        return round(result, 2)        

    # ======= Discount =============
    @property
    def discount_amount(self):
        result = 0
        if self._discount_type == "percent":
            result = self.subtotal * (self._discount_value / 100)
        else:
            result = self._discount_value
        return round(result, 2)
    
    @discount_amount.setter
    def discount_amount(self, value):
        if not is_number(value):
            return

        self._discount_value = float(value)
        self._notify_observers()

    @property
    def discount_type(self):
        return self._discount_type

    @discount_type.setter
    def discount_type(self, discount_type):
        self._discount_type = discount_type
        self._notify_observers()

    # ======= Tax =============
    @property
    def tax_amount(self):
        base = self.subtotal - self.discount_amount
        result = 0
        if self._tax_type == "percent":
            result = base * (self._tax_value / 100)
        else:
            result = self._tax_value
        return round(result, 2)
    
    @tax_amount.setter
    def tax_amount(self, value):
        if not is_number(value):
            return

        self._tax_value = float(value)
        self._notify_observers()

    @property
    def tax_type(self):
        return self._tax_type

    @tax_type.setter
    def tax_type(self, tax_type):
        self._tax_type = tax_type
        self._notify_observers()

    def reset_sale(self):
        return self._reset_sale()

    @property
    def selected_products(self):
        """إرجاع قائمة المنتجات مع السعر المعروض"""
        products = []
        for product_id, product in self._selected_products.items():
            product_copy = product.copy()
            # استخدام السعر المعدل إذا وجد
            if product_id in self._product_effects:
                product_copy["price"] = self._product_effects[product_id][
                    "adjusted_price"
                ]
            else:
                product_copy["price"] = product_copy["original_price"]
            products.append(product_copy)
        return products

    def get_product_display_price(self, product_id):
        """الحصول على السعر المعروض للمنتج"""
        if product_id in self._product_effects:
            return self._product_effects[product_id]["adjusted_price"]
        elif product_id in self._selected_products:
            return self._selected_products[product_id]["original_price"]
        return 0

    def add_product(self, product):
        """
        إضافة منتج إلى السلة مع التحقق من المخزون.
        """
        product_id = product["id"]
        qty_to_add = product["qty"]
        stock = product["stock"]

        # الكمية الحالية في السلة
        current_qty = self._selected_products.get(product_id, {}).get("qty", 0)
        new_qty = current_qty + qty_to_add

        checked = self.check_out_of_stock(product_id, new_qty)

        if checked:
            new_qty = stock

        if product_id in self._selected_products:
            self._selected_products[product_id]["qty"] = new_qty
        else:
            product_copy = product.copy()
            product_copy["qty"] = new_qty
            product_copy["original_price"] = product["price"]
            self._selected_products[product_id] = product_copy

    def add_products(self, products):
        """إضافة مجموعة منتجات مع التحقق من المخزون لكل منتج"""
        for product in products:
            self.add_product(product)
        self._notify_observers()

    @selected_products.setter
    def selected_products(self, products):
        self._selected_products.clear()
        self._product_effects.clear()

        for product in products:
            if not is_number(product["price"]) or not is_number(product["qty"]):
                raise ValueError("سعر المنتج او كميته يجب ان تكون رقماً")

            product_copy = product.copy()
            product_copy["original_price"] = product["price"]
            self._selected_products[product["id"]] = product_copy

        self._notify_observers()

    def remove_product(self, product_id):
        if product_id in self._selected_products:
            # قبل حذف المنتج، نقوم بإلغاء تأثيره على الخصم والضريبة
            self._remove_product_effect(product_id)
            del self._selected_products[product_id]
            self._notify_observers()

    def _remove_product_effect(self, product_id):
        """إزالة تأثير منتج معين من الخصم والضريبة"""
        if product_id not in self._product_effects:
            return
        
        effect = self._product_effects.pop(product_id)
        
        # فقط للنوع fixed — للنسبة المئوية إعادة حساب كاملة أضمن
        if self._discount_type == "fixed":
            self._discount_value = max(0, self._discount_value - effect.get("discount_effect", 0))
        
        if self._tax_type == "fixed":
            self._tax_value = max(0, self._tax_value - effect.get("tax_effect", 0))

    def update_product_qty(self, product_id, new_qty):
        if product_id not in self._selected_products:
            return

        if new_qty <= 0:
            self.remove_product(product_id)
            return

        check = self.check_out_of_stock(product_id, new_qty)
        if check:
            self._selected_products[product_id]["qty"] = self._selected_products[
                product_id
            ]["stock"]
        else:
            self._selected_products[product_id]["qty"] = new_qty

        # إذا كان هناك تعديل سعر لهذا المنتج، نحتاج لإعادة حساب تأثيره
        if product_id in self._product_effects:
            current_adjusted_price = self._product_effects[product_id]["adjusted_price"]
            self.update_product_price(product_id, current_adjusted_price)

        self._notify_observers()

    def update_product_price(self, product_id, new_price):
        """
        تعديل سعر المنتج:
        - يتم إزالة التأثير السابق لهذا المنتج
        - يتم حساب التأثير الجديد وإضافته
        - لا يتم تعديل سعر المنتج في السلة
        """
        if product_id not in self._selected_products:
            return

        if not is_number(new_price):
            raise ValueError("سعر المنتج يجب أن يكون رقماً")

        product = self._selected_products[product_id]
        original_price = product["original_price"]
        new_price = float(new_price)

        # إذا كان السعر الجديد هو نفس السعر الأصلي، قم بإزالة التأثير فقط
        if abs(new_price - original_price) < 0.01:
            if product_id in self._product_effects:
                self._remove_product_effect(product_id)
            return

        # إزالة التأثير السابق لهذا المنتج إن وجد
        if product_id in self._product_effects:
            self._remove_product_effect(product_id)

        # حساب التأثير الجديد
        qty = product["qty"]
        total_diff = (new_price - original_price) * qty

        discount_effect = 0
        tax_effect = 0

        if total_diff < 0:
            # السعر الجديد أقل -> خصم
            discount_effect = abs(total_diff)
            if self._discount_type == "fixed":
                self._discount_value += discount_effect
            else:
                if self.subtotal > 0:
                    additional_discount_percent = (
                        abs(total_diff) / self.subtotal
                    ) * 100
                    self._discount_value += additional_discount_percent
        elif total_diff > 0:
            # السعر الجديد أكبر -> ضريبة
            tax_effect = total_diff
            if self._tax_type == "fixed":
                self._tax_value += tax_effect
            else:
                base = self.subtotal - self.discount_amount
                if base > 0:
                    additional_tax_percent = (total_diff / base) * 100
                    self._tax_value += additional_tax_percent

        # تخزين التأثير الجديد
        self._product_effects[product_id] = {
            "adjusted_price": new_price,
            "discount_effect": discount_effect,
            "tax_effect": tax_effect,
        }

        self._notify_observers()

    def check_out_of_stock(self, product_id, new_qty):
        selected_product = self._selected_products.get(product_id)
        if not selected_product:
            return False

        max_qty = selected_product["stock"]

        if new_qty > max_qty:
            showwarning(
                "كمية غير متوفرة",
                f"الكمية المطلوبة تتجاوز المخزون\nتم تحديد كمية المنتج = {max_qty}",
            )
            return True

        return False

    def clear_cart(self):
        """تفريغ السلة بالكامل"""
        self._selected_products.clear()
        self._product_effects.clear()
        self._notify_observers()

    def complete_sale(self, amount_paid):
        invoice_data = self._prepare_invoice_data(amount_paid)
        products_data = self._prepare_products_for_printing()

        self._handle_customer_debt(amount_paid)
        sale_id = self._record_invoice(amount_paid)
        self._record_stock_movements(sale_id)

        self._print_invoice(invoice_data, products_data)

        self._reset_sale()

    def _handle_customer_debt(self, amount_paid):
        remaining_amount = self._calculate_remaining(amount_paid)
        if self.selected_customer != "نقدي" and remaining_amount > 0:
            self.data_service.update_customer_debt(
                self.customer_id, f"{remaining_amount:.2f}"
            )

    def _record_invoice(self, amount_paid):
        remaining_amount = self._calculate_remaining(amount_paid)
        sale_id = self.data_service.record_invoice(
            self.invoice_number,
            self.total,
            self.discount_amount,
            self.tax_amount,
            self.total,
            remaining_amount,
            self.customer_id
        )

        self._record_invoice_item(sale_id)
        return sale_id

    def _record_invoice_item(self, sale_id):
        sale_items_data = self._prepare_sale_items_data()
        self.data_service.record_invoice_item(sale_id, sale_items_data)
    
    def _prepare_sale_items_data(self):
        sale_items_data = []
        for product in self.selected_products:
            qty = product["qty"]
            price = product["price"]

            sale_items_data.append(
                (
                    product["id"], 
                    qty,  
                    price, 
                    self.total,  
                )
            )

        return sale_items_data
    
    def _record_stock_movements(self, sale_id):
        for product in self.selected_products:
            product_id = product["id"]
            qty_sold = float(product["qty"])
            self.data_service.add_movement(product_id, -qty_sold, self.invoice_number, sale_id)
            
    def _calculate_remaining(self, amount_paid):
        if not is_number(amount_paid):
            raise ValueError("المبلغ المدفوع يجب أن يكون رقماً")
        remaining = self.total - float(amount_paid)
        return round(remaining, 2)
    
    def _print_invoice(self, invoice_data, products_data):
        try:
            from utils.print_thermal import print_shop_invoice
            from utils.print_A4 import print_A4

            printer_type = self.data_service.get_setting("printer_type") or "حرارية"

            if printer_type == "A4":
                print_A4(invoice_data, products_data)
            else:
                print_shop_invoice(invoice_data, products_data)

        except Exception as e:
            messagebox.showwarning("تحذير", f"فشل الطباعة: {e}")
    
    def print_current_invoice(self, amount_paid=0):
        """طباعة الفاتورة بدون تسجيل البيع"""
        try:
            invoice_data = self._prepare_invoice_data(amount_paid)
            products_data = self._prepare_products_for_printing()
            self._print_invoice(invoice_data, products_data)
        except Exception as e:
            messagebox.showwarning("تحذير", f"فشل الطباعة: {e}")
    
    def _prepare_invoice_data(self, amount_paid):
        """Prepare invoice data for printing."""
        amount_paid = float(amount_paid) if is_number(amount_paid) else 0
        remaining = self._calculate_remaining(amount_paid)
        
        return {
            "invoice_number": self.invoice_number,
            "date": strftime("%Y-%m-%d"),
            "time": strftime("%I:%M %p"),
            "customer_name": self.selected_customer,
            "subtotal": self.subtotal,
            "discount": self.discount_amount,
            "tax": self.tax_amount,
            "total": self.total,
            "paid": round(amount_paid, 2),
            "remaining": remaining,
        }
    
    def _prepare_products_for_printing(self):
        products = []
        for product in self.selected_products:
            total = product["price"] * product["qty"]

            products.append(
                {
                    "name": product["name"],
                    "price": product["price"],
                    "qty": product["qty"],
                    "total": round(total, 2),
                }
            )
        return products