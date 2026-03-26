from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    StringVar,
    CTkOptionMenu,
)
from utils.format_currency import format_currency
from utils.image import image
from utils.is_number import is_number
from utils.key_shortcut import key_shortcut


class ProductCard(CTkFrame):
    def __init__(self, parent, product_data, on_qty_change, on_remove, sale_state):
        super().__init__(
            parent, corner_radius=8, border_width=1, border_color=("#e5e5e5", "#4D4D4D")
        )
        self.product_data = product_data
        self.on_qty_change = on_qty_change
        self.on_remove = on_remove
        self.product_id = product_data["id"]
        self.sale_state = sale_state
        self._updating = False  # منع الحلقات اللانهائية

        # بيانات الوحدة
        self.unit = product_data["unit"]
        self.sub_unit = product_data["sub_unit"]
        self.conversion_factor = product_data["conversion_factor"]
        
        # تحديد قائمة الوحدات المتاحة
        if self.sub_unit:
            self.units_list = [self.unit, self.sub_unit]
            self.current_unit = StringVar(value=self.unit)
            self.unit_enabled = True
        else:
            self.units_list = [self.unit]
            self.current_unit = StringVar(value=self.unit)
            self.unit_enabled = False
        
        self._build_card()

    def _build_card(self):
        """بناء بطاقة المنتج المصغرة"""
        # Top row with product info
        top_row = self._create_product_info_row()
        top_row.pack(fill="x", padx=6, pady=4)

        # Bottom row with unit selection and quantity controls
        bottom_row = self._create_bottom_row()
        bottom_row.pack(fill="x", padx=6, pady=(0, 6))

    def _create_product_info_row(self):
        """Create the top row with product image, name, and subtotal."""
        top_row = CTkFrame(self, fg_color="transparent")

        # Product image
        img = image(self.product_data["image_path"])
        CTkLabel(top_row, text="", image=img, width=40, height=40).pack(
            side="right", padx=(0, 6)
        )

        # Info frame
        info_frame = CTkFrame(top_row, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True)

        # Product name
        name = self.product_data["name"]
        MAX_NAME_LENGTH = 28
        if len(name) > MAX_NAME_LENGTH:
            name = name[:MAX_NAME_LENGTH] + "\n" + name[MAX_NAME_LENGTH:]

        CTkLabel(
            info_frame,
            text=name,
            font=("Cairo", 11, "bold"),
            text_color=("#167000", "#00a72a"),
            anchor="e",
        ).pack(fill="x", padx=10)

        # Subtotal label (السعر × الكمية = الإجمالي)
        self.sub_total_label = CTkLabel(
            info_frame,
            text=self._get_details_text(),
            font=("Cairo", 10),
            text_color=("#6d6d6d", "#b4b4b4"),
            anchor="e",
        )
        self.sub_total_label.pack(fill="x", padx=10)

        return top_row

    def _create_bottom_row(self):
        """Create bottom row with unit selection and quantity controls"""
        bottom_row = CTkFrame(self, fg_color="transparent")

        # Unit selection (OptionMenu)
        self.unit_menu = CTkOptionMenu(
            bottom_row,
            values=self.units_list,
            variable=self.current_unit,
            width=70,
            height=28,
            font=("Cairo", 10),
            dropdown_font=("Cairo", 10),
            fg_color="#2b6aaf",
            button_color="#2b6aaf",
            button_hover_color="#1f538d",
            command=self._on_unit_change,  # ربط التغيير بالدالة
        )
        self.unit_menu.pack(side="right", padx=2)
        
        # تعطيل القائمة إذا لم توجد وحدة صغرى
        if not self.unit_enabled:
            self.unit_menu.configure(state="disabled")

        # Quantity controls frame
        qty_frame = CTkFrame(bottom_row, fg_color="transparent")
        qty_frame.pack(side="right")

        # Decrease button
        CTkButton(
            qty_frame,
            text="-",
            width=28,
            height=28,
            font=("Cairo", 14, "bold"),
            command=self._decrease_qty,
        ).pack(side="right", padx=2)

        # Quantity entry
        self.qty_entry_var = StringVar(value=str(self.product_data["qty"]))

        self.qty_entry = CTkEntry(
            qty_frame,
            width=40,
            height=28,
            justify="center",
            textvariable=self.qty_entry_var,
            font=("Cairo", 12, "bold"),
        )
        self.qty_entry.pack(side="right", padx=2)

        self._bind_qty_entry_events()
        self._bind_shortcuts_qty()

        # Increase button
        CTkButton(
            qty_frame,
            text="+",
            width=28,
            height=28,
            font=("Cairo", 14, "bold"),
            command=self._increase_qty,
        ).pack(side="right", padx=2)

        # Delete button
        CTkButton(
            bottom_row,
            text="",
            width=28,
            height=28,
            fg_color=("#b30000", "#8f0000"),
            hover_color=("#8D0000", "#740000"),
            image=image("assets/delete.png", (20, 20)),
            command=self._on_remove,
        ).pack(side="left", padx=2)

        return bottom_row

    def _on_unit_change(self, selected_unit):
        """معالجة تغيير الوحدة"""
        if self._updating:
            return
        
        self._updating = True
        try:
            # تحديث الكمية في product_data
            current_qty = self.product_data["qty"]
            
            # إعادة حساب السعر بناءً على الوحدة المختارة
            self._update_subtotal()
            
            # استدعاء callback لتحديث الإجمالي العام - إزالة unit_changed
            self.on_qty_change(self.product_id, current_qty)
            
        finally:
            self._updating = False

    def _calculate_effective_price(self):
        """حساب السعر الفعلي بناءً على الوحدة المختارة"""
        base_price = self.product_data["price"]
        selected_unit = self.current_unit.get()
        self.sale_state.change_current_unit(self.product_id, selected_unit)

        if selected_unit == self.sub_unit and self.sub_unit:
            # إذا اختار الوحدة الصغرى: السعر الفعلي = السعر الأساسي ÷ معامل التحويل
            effective_price = base_price / self.conversion_factor
        else:
            # إذا اختار الوحدة الرئيسية: السعر الفعلي = السعر الأساسي
            effective_price = base_price
            
        return effective_price

    def _get_details_text(self):
        """الحصول على نص التفاصيل مع مراعاة الوحدة"""
        qty = self.product_data["qty"]
        effective_price = self._calculate_effective_price()
        total = effective_price * qty
        
        return f"{effective_price:.2f} × {qty} = {format_currency(total)}"

    def _bind_qty_entry_events(self):
        # عند أي تغيير في Entry، حاول تحديث الكمية
        def on_entry_change(*args):
            if self._updating:
                return

            value = self.qty_entry_var.get()
            if is_number(value):
                new_qty = float(value)
                self._updating = True
                try:
                    self.on_qty_change(self.product_id, new_qty)
                finally:
                    self._updating = False
            elif value == "":
                # السماح بمسح مؤقت
                return
            else:
                if self.qty_entry_var.get()[-1] != ".":
                    self.qty_entry_var.set("1")
                else:
                    return

        self.qty_entry_var.trace_add("write", on_entry_change)

    def _bind_shortcuts_qty(self):
        key_shortcut(
            self.qty_entry,
            ["<Up>", "<plus>", "<KP_Add>"],
            self._increase_qty,
        )
        key_shortcut(
            self.qty_entry,
            ["<Down>", "<minus>", "<KP_Subtract>"],
            self._decrease_qty,
        )
        key_shortcut(
            self.qty_entry, ["<Delete>", "<Control-d>", "<Control-D>"], self._on_remove
        )

    def _increase_qty(self):
        """زيادة الكمية"""
        if self._updating:
            return
        current_qty = self.product_data["qty"]
        if current_qty == 0.5:
            new_qty = 1
        else:
            new_qty = current_qty + 1
        self._updating = True
        try:
            self.on_qty_change(self.product_id, new_qty)
        finally:
            self._updating = False

    def _decrease_qty(self):
        """نقصان الكمية"""
        if self._updating:
            return
        current_qty = self.product_data["qty"]
        # لو الكميه 1 و عمل انقاص تكون نصف
        if current_qty == 1:
            new_qty = 0.5
        else:
            new_qty = current_qty - 1
        self._updating = True

        try:
            self.on_qty_change(self.product_id, new_qty)
        finally:
            self._updating = False

    def _on_remove(self):
        """حذف المنتج"""
        if self._updating:
            return
        self._updating = True
        try:
            self.on_remove(self.product_id)
        finally:
            self._updating = False

    def update_display(self):
        """تحديث عرض الكمية والإجمالي"""
        self._updating = True
        try:
            self.qty_entry_var.set(str(self.product_data["qty"]))
            self.sub_total_label.configure(text=self._get_details_text())
        finally:
            self._updating = False
    
    def _update_subtotal(self):
        """تحديث الإجمالي فقط دون تغيير الكمية"""
        self.sub_total_label.configure(text=self._get_details_text())