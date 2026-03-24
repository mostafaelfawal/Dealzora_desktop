from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkRadioButton, CTkEntry, StringVar
from tkinter import messagebox
from utils.KeyShortcutsManager import KeyShortcutsManager
from utils.key_shortcut import key_shortcut
from utils.format_currency import format_currency
from .payment_dialog import InvoiceView

class TotalsPanel(CTkFrame):
    def __init__(self, parent, currency, tax_rate, sale_state):
        super().__init__(parent)

        self.currency = currency
        self.tax_rate = tax_rate
        self.sale_state = sale_state
        # تسجيل كمراقب للتغييرات في حالة البيع
        self.sale_state.add_observer(self)

        self.shortcuts = KeyShortcutsManager(self)
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        self._build_totals_panel()
        self.bind_keyboard_shortcuts()
        self.on_state_changed()

    def _build_totals_panel(self):
        """دالة تجميع العناصر في الواجهه"""
        self._build_subtotal()
        self._build_discount_controls()
        self._build_tax_controls()
        self._build_total()
        self._build_sale_buttons()

    def _build_subtotal(self):
        """Build subtotal display section."""
        # Container for subtotal
        self.subtotal_frame = CTkFrame(self, fg_color="transparent")
        self.subtotal_frame.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        self.subtotal_frame.grid_columnconfigure(0, weight=1)

        # Subtotal label
        self.subtotal_label = CTkLabel(
            self.subtotal_frame,
            text=f"الاجمالي الفرعي: 0.00",
            font=("Cairo", 16, "bold"),
            text_color=("gray10", "gray90"),
        )
        self.subtotal_label.grid(row=0, column=0, sticky="e")

    def _build_discount_controls(self):
        self.discount_type_var = StringVar(value=self.sale_state.discount_type)

        controls = self._build_value_input(
            self,
            ":الخصم",
            row=1,
            variable=self.discount_type_var,
            command=self.on_discount_type_change
        )

        self.discount_entry = controls["entry"]
        key_shortcut(self.discount_entry, "<KeyRelease>", self.on_discount_change)

    def on_discount_change(self):
        value = self.discount_entry.get()
        self.sale_state.discount_amount = value if value else 0

    def on_discount_type_change(self):
        self.sale_state.discount_type = self.discount_type_var.get()
        self.on_state_changed()

    def _build_tax_controls(self):
        self.tax_type_var = StringVar(value=self.sale_state.tax_type)

        controls = self._build_value_input(
            self,
            ":الضريبة",
            row=2,
            variable=self.tax_type_var,
            command=self.on_tax_type_change
        )

        self.tax_entry = controls["entry"]
        self.tax_entry.insert(0, str(self.tax_rate))
        key_shortcut(self.tax_entry, "<KeyRelease>", self.on_tax_change)

    def on_tax_change(self):
        value = self.tax_entry.get()
        self.sale_state.tax_amount = value if value else 0

    def on_tax_type_change(self):
        self.sale_state.tax_type = self.tax_type_var.get()
        self.on_state_changed()
    
    def _build_value_input(self, parent, label_text, row, variable, command):
        frame = CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        # Radio container
        radio_frame = CTkFrame(frame, fg_color="transparent")
        radio_frame.grid(row=0, column=0, padx=10, sticky="e")

        percent_radio = CTkRadioButton(
            radio_frame,
            text="%",
            variable=variable,
            command=command,
            value="percent",
            font=("Cairo", 14, "bold"),
            fg_color="#0078da",
            hover_color="#0060b0",
            border_color="#0078da",
        )
        percent_radio.grid(row=0, column=0, padx=5)

        currency_radio = CTkRadioButton(
            radio_frame,
            text=self.currency,
            variable=variable,
            command=command,
            value="fixed",
            font=("Cairo", 14, "bold"),
            fg_color="#0078da",
            hover_color="#0060b0",
            border_color="#0078da",
        )
        currency_radio.grid(row=0, column=1, padx=5)

        entry = CTkEntry(
            frame,
            placeholder_text="0.00",
            justify="center",
            width=120,
            height=35,
            font=("Cairo", 14),
            border_color="#0078da",
        )
        entry.grid(row=0, column=1, padx=10, sticky="e")

        label = CTkLabel(
            frame,
            text=label_text,
            font=("Cairo", 14, "bold"),
            text_color=("gray10", "gray90"),
        )
        label.grid(row=0, column=2, padx=(10, 0), sticky="e")

        return {
            "frame": frame,
            "entry": entry,
            "percent_radio": percent_radio,
            "currency_radio": currency_radio,
        }

    def _build_total(self):
        """Build total amount display with professional styling."""
        # Separator line
        self.separator = CTkFrame(self, height=2, fg_color="#0078da")
        self.separator.grid(row=3, column=0, padx=20, sticky="ew")

        # Container for total
        self.total_frame = CTkFrame(self, fg_color="transparent")
        self.total_frame.grid(row=4, column=0, padx=20, sticky="ew")
        self.total_frame.grid_columnconfigure(0, weight=1)

        # Total amount (bold and prominent)
        self.total_amount_label = CTkLabel(
            self.total_frame,
            text=f"0.00 {self.currency}",
            font=("Cairo", 24, "bold"),
            text_color="#0078da",
        )
        self.total_amount_label.grid(row=0, column=0, padx=5, sticky="e")

        # Total label
        self.total_label = CTkLabel(
            self.total_frame,
            text=":المبلغ المطلوب",
            font=("Cairo", 18, "bold"),
            text_color=("gray10", "gray90"),
        )
        self.total_label.grid(row=0, column=1, sticky="e")

    def _build_sale_buttons(self):
        """Build action buttons for sale completion."""
        # Buttons container
        self.buttons_frame = CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=5, column=0, padx=20, pady=(10, 15), sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        # Cancel sale button
        self.cancel_button = CTkButton(
            self.buttons_frame,
            text="الغاء عملية البيع (Esc)",
            font=("Cairo", 13, "bold"),
            fg_color="transparent",
            hover_color=("#E0E0E0", "#2E2E2E"),
            border_width=2,
            border_color="#FF6B6B",
            text_color="#FF6B6B",
            height=38,
            corner_radius=8,
            command=self.on_cancel_sale,
        )
        self.cancel_button.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        # Complete sale button
        self.complete_button = CTkButton(
            self.buttons_frame,
            text="اتمام البيع (F12)",
            font=("Cairo", 13, "bold"),
            fg_color="#0078da",
            hover_color="#0060b0",
            height=38,
            corner_radius=8,
            command=self.on_finish_sale,
        )
        self.complete_button.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def on_finish_sale(self):
        if not self.sale_state.selected_products:
            messagebox.showwarning("تحذير", "لا يوجد منتجات لإتمام البيع")
            return
        InvoiceView(self, self.sale_state, self.reset_inputs)

    def on_cancel_sale(self):
        in_cart = len(self.sale_state.selected_products)
        if in_cart and messagebox.askyesno(
            "تأكيد", "هل أنت متأكد أنك تريد إلغاء عملية البيع؟"
        ):
            self.sale_state.reset_sale()
            self.reset_inputs()
    
    def reset_inputs(self):
        self.discount_entry.delete(0, "end")
        self.tax_entry.delete(0, "end")
        self.tax_entry.insert(0, self.tax_rate)

    def on_state_changed(self):
        self.total_amount_label.configure(
            text=format_currency(self.sale_state.total)
        )
        self.subtotal_label.configure(
            text=f"الاجمالي الفرعي: {format_currency(self.sale_state.subtotal)}"
        )

    def bind_keyboard_shortcuts(self):
        self.shortcuts.bind("<F12>", self.on_finish_sale)
        self.shortcuts.bind("<Escape>", self.on_cancel_sale)

    def destroy(self):
        self.shortcuts.unbind_all()
        # إزالة هذا المكون كمراقب لحالة البيع قبل تدميره
        self.sale_state.remove_observer(self)
        
        super().destroy()
