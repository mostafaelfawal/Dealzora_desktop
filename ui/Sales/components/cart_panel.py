from customtkinter import (
    CTkFrame,
    CTkButton,
    CTkLabel,
    CTkScrollableFrame,
)
from tkinter.messagebox import askyesno

from ui.Sales.components.ProductCard import ProductCard
from .customer_dialog import CustomerDialog
from utils.KeyShortcutsManager import KeyShortcutsManager
from utils.image import image


class CartPanel(CTkFrame):
    def __init__(self, parent, data_service, sale_state):
        super().__init__(parent)
        self.data_service = data_service
        self.sale_state = sale_state
        self.shortcuts = KeyShortcutsManager(self)
        self.product_cards = {}

        # إطار للعنوان
        header_frame = CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)

        CTkLabel(
            header_frame, text="🛒 سلة المشتريات", font=("Cairo", 16, "bold")
        ).pack(side="right", padx=5)

        # زر تفريغ السلة
        CTkButton(
            header_frame,
            text="",
            image=image("assets/clear.png", (20, 20)),
            width=0,
            font=("Cairo", 12),
            fg_color="#FF9100",
            hover_color="#E48100",
            command=self._clear_cart,
        ).pack(side="left", padx=5)

        self._build_selected_customer()
        self._build_total_products_label()

        # إطار قابل للتمرير للمنتجات
        self.cart_container = CTkScrollableFrame(self, fg_color="transparent")
        self.cart_container.pack(fill="both", expand=True, pady=5)

        self.bind_keyboard_shortcuts()

        # التسجيل كمراقب للتغييرات
        self.sale_state.add_observer(self)

        # عرض المنتجات الموجودة إن وجدت
        self.on_state_changed()

    def on_state_changed(self):
        """يتم استدعاؤها عند تغيير حالة البيع"""
        self.refresh_cart()
        # Update Customer label
        customer_name = self.sale_state.selected_customer
        self.selected_customer_label.configure(
            text=customer_name if customer_name else "نقدي"
        )
        # Update total products label
        total_items = self.sale_state.total_items
        count = self.sale_state.total_qty
        self.total_label.configure(text=f"{count} قطعة | {total_items} صنف")

    def refresh_cart(self):
        """تحديث عرض السلة"""
        products = self.sale_state.selected_products
        current_product_ids = set(p["id"] for p in products)
        existing_card_ids = set(self.product_cards.keys())

        # حذف البطاقات التي لم تعد موجودة
        for product_id in existing_card_ids - current_product_ids:
            if product_id in self.product_cards:
                self.product_cards[product_id].destroy()
                del self.product_cards[product_id]

        # تحديث البطاقات الموجودة أو إضافة بطاقات جديدة
        for product in products:
            product_id = product["id"]

            if product_id in self.product_cards:
                # تحديث البطاقة الموجودة
                card = self.product_cards[product_id]
                card.product_data = product
                card.update_display()
            else:
                # إنشاء بطاقة جديدة
                card = ProductCard(
                    self.cart_container,
                    product,
                    self._update_qty,
                    self._remove_product,
                    self.sale_state,
                )
                card.pack(side="bottom", fill="x", pady=3, padx=3)
                self.product_cards[product_id] = card

        # عرض رسالة إذا كانت السلة فارغة
        self._update_empty_label()

    def _update_qty(self, product_id, new_qty):
        """تحديث كمية المنتج"""
        self.sale_state.update_product_qty(product_id, new_qty)

    def _remove_product(self, product_id):
        """حذف منتج من السلة"""
        self.sale_state.remove_product(product_id)

    def _clear_cart(self):
        """تفريغ السلة بالكامل"""
        in_cart = len(self.sale_state.selected_products)
        if in_cart and askyesno("تأكيد", "هل أنت متأكد أنك تريد تفريغ السلة؟"):
            self.sale_state.clear_cart()

    def _build_total_products_label(self):
        self.total_label = CTkLabel(self, font=("Cairo", 12))
        self.total_label.pack()

    def _update_empty_label(self):
        """تحديث عرض رسالة السلة الفارغة"""
        total_items = len(self.sale_state.selected_products)

        # حذف الرسالة الموجودة إذا كانت موجودة
        if hasattr(self, "empty_label") and self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None

        # إضافة رسالة جديدة إذا كانت السلة فارغة
        if total_items == 0:
            self.empty_label = CTkLabel(
                self.cart_container,
                text="🛍️ السلة فارغة",
                font=("Cairo", 14),
                text_color="gray",
            )
            self.empty_label.pack(pady=20)

    def _build_selected_customer(self):
        container = CTkFrame(self, fg_color="transparent")
        container.pack(padx=5, fill="x")

        CTkButton(
            container,
            text="اختر عميل",
            fg_color="#00aeff",
            hover_color="#009be2",
            width=0,
            font=("Cairo", 18, "bold"),
            command=self._show_customer_dialog,
        ).pack(padx=5, side="right")

        self.selected_customer_label = CTkLabel(
            container, text="نقدي", font=("Cairo", 16, "bold")
        )
        self.selected_customer_label.pack(padx=5, side="right")

    def _show_customer_dialog(self):
        CustomerDialog(self, self.data_service, self.sale_state)

    def bind_keyboard_shortcuts(self):
        self.shortcuts.bind("<F2>", self._show_customer_dialog)
        self.shortcuts.bind("<F4>", self._clear_cart)

    def destroy(self):
        self.sale_state.remove_observer(self)
        self.shortcuts.unbind_all()
        super().destroy()
