from customtkinter import (
    CTkButton,
    CTkRadioButton,
    CTkScrollableFrame,
    CTkToplevel,
    CTkLabel,
    CTkFrame,
    CTkEntry,
)
from tkinter import StringVar
from utils.image import image
from utils.key_shortcut import key_shortcut
from components.CustomerModal import CustomerModal


class CustomerList(CTkScrollableFrame):
    def __init__(self, parent, on_select, on_add):
        super().__init__(parent)
        self.on_select = on_select
        self.on_add = on_add

    def render(self, customers):
        # Clear
        for widget in self.winfo_children():
            widget.destroy()

        # Add Button
        CTkButton(
            self,
            text="إضافة عميل جديد",
            font=("Cairo", 16, "bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            image=image("assets/add_customer.png", (20, 20)),
            compound="left",
            command=self.on_add,
        ).pack(fill="x", pady=3)

        # Cash Button
        cash_customer = {"id": None, "name": "نقدي",}
        CTkButton(
            self,
            text="نقدي",
            font=("Cairo", 16, "bold"),
            command=lambda: self.on_select(cash_customer),
        ).pack(fill="x", pady=3)

        # Customers
        for customer in customers:
            self._add_customer_button(customer)

    def _add_customer_button(self, customer):
        c = {
            "id": customer[0],
            "name": customer[1],
            "phone": customer[2] or "بلا هاتف",
            "debt": customer[3],
        }

        fg, hover = self._color_btn_from_debt(c["debt"])

        CTkButton(
            self,
            text=f"{c['name']} - {c['phone']}",
            font=("Cairo", 16, "bold"),
            text_color="#000000",
            fg_color=fg,
            hover_color=hover,
            command=lambda: self.on_select(c),
        ).pack(fill="x", pady=3)

    @staticmethod
    def _color_btn_from_debt(debt):
        if debt > 0:
            return "#ff6600", "#e95d00"
        elif debt < 0:
            return "#22c55e", "#15803d"
        return "#ffbf00", "#eab308"


class CustomerSearch(CTkFrame):
    def __init__(self, parent, on_search):
        super().__init__(parent)
        self.on_search = on_search
        self._build()

    def _build(self):
        container = CTkFrame(
            self,
            corner_radius=15,
            fg_color=("#f1f5f9", "#0f172a"),
            border_width=1,
            border_color=("#cbd5f5", "#1e293b"),
        )
        container.pack(fill="x", padx=15, pady=15)

        self.search_entry = CTkEntry(
            container,
            placeholder_text="...ابحث عن عميل 🔍",
            font=("Cairo", 14),
            justify="right",
            height=40,
            corner_radius=12,
            fg_color=("#ffffff", "#020617"),
            border_color=("#3b82f6", "#3b82f6"),
            text_color=("#0f172a", "#e2e8f0"),
            placeholder_text_color=("#94a3b8", "#64748b"),
        )
        self.search_entry.pack(fill="x", padx=15, pady=(15, 10))

        self.search_type = StringVar(value="name")

        radio_frame = CTkFrame(container, fg_color="transparent")
        radio_frame.pack(pady=(0, 15))

        self._radio(radio_frame, "بالأسم", "name").pack(side="left", padx=5)
        self._radio(radio_frame, "بالهاتف", "phone").pack(side="left", padx=5)

        key_shortcut(self.search_entry, "<KeyRelease>", self._trigger)

    def _radio(self, parent, text, value):
        return CTkRadioButton(
            parent,
            text=text,
            value=value,
            variable=self.search_type,
            font=("Cairo", 13, "bold"),
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color=("#0f172a", "#e2e8f0"),
            command=self._trigger,
        )

    def _trigger(self):
        keyword = self.search_entry.get().strip()
        self.on_search(keyword, self.search_type.get())


class CustomerDialog(CTkToplevel):
    def __init__(self, parent, data_service, sale_state):
        super().__init__(parent)
        self.data_service = data_service
        self.sale_state = sale_state

        self.all_customers = self.data_service.get_customers()
        self.filtered = self.all_customers.copy()

        self._config_dialog()
        self._build_title()
        self._build_search()
        self._build_legend()
        self._build_list()
        self._render()
        
    def _config_dialog(self):
        self.title("Dealzora | اختيار عميل")
        self.geometry("420x650+200+0")
        self.grab_set()
        self.focus_force()

    def _build_title(self):
        CTkLabel(
            self,
            text="👤 اختيار عميل",
            font=("Cairo", 22, "bold"),
            text_color=("#0f172a", "#4cc9f0"),
        ).pack(pady=(15, 5))

    def _build_search(self):
        self.search = CustomerSearch(self, self._on_search)
        self.search.pack(fill="x")

    def _build_legend(self):
        frame = CTkFrame(
            self,
            fg_color=("#ffffff", "#020617"),
            corner_radius=15,
            border_width=1,
            border_color=("#e2e8f0", "#1e293b"),
        )
        frame.pack(fill="x", padx=15, pady=10)

        self._legend_item(frame, "دائن", "#ffbf00")
        self._legend_item(frame, "مديون", "#ff6600")
        self._legend_item(frame, "غير مديون", "#22c55e")

    def _legend_item(self, parent, text, color):
        CTkLabel(
            parent,
            text=f"{text} ●",
            font=("Cairo", 14, "bold"),
            text_color=color,
        ).pack(anchor="e", padx=10, pady=3)

    def _build_list(self):
        self.list = CustomerList(
            self, on_select=self._on_select, on_add=self._open_add_customer_modal
        )
        self.list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _render(self):
        self.list.render(self.filtered)

    # ================= Events =================

    def _on_search(self, keyword, search_type):
        if not keyword:
            self.filtered = self.all_customers.copy()
        else:
            self.filtered = self.data_service.search_customers_by_query(
                keyword, search_type
            )
        self._render()

    def _on_select(self, customer):
        name = customer["name"]
        id = customer["id"]
        self.sale_state.update_selected_customer(name, id)
        self.destroy()

    def _open_add_customer_modal(self):
        CustomerModal(add_customer=self._add_customer, customers_dialog=self)

    def _add_customer(self, name, phone, debt, modal):
        self.data_service.add_customer(name, phone, debt)
        modal.destroy()

        self.all_customers = self.data_service.get_customers()
        self.filtered = self.all_customers.copy()
        self._render()
