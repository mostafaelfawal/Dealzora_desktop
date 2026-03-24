from customtkinter import CTkFrame

from ui.Sales.components.totals_panel import TotalsPanel
from .components.toolbar import Toolbar
from .components.products_section import ProductSection
from .components.cart_panel import CartPanel


class Sale:
    def __init__(self, root, settings_db, sale_state, data_service):
        self.root = root
        self.currency = settings_db.get_setting("currency")
        self.tax_rate = settings_db.get_setting("tax")
        self.sale_state = sale_state
        self.data_service = data_service

        Toolbar(self.root, self.sale_state).pack(fill="x", padx=10, pady=5)
        
        # انشاء مربع البيع
        self._build_sale_section()

    def _build_sale_section(self):
        center_container = CTkFrame(self.root, fg_color="transparent")
        center_container.pack(fill="both", expand=True, padx=10)

        center_container.grid_columnconfigure(0, weight=3)
        center_container.grid_columnconfigure(1, weight=2)

        self.product_section = ProductSection(
            center_container, self.data_service, self.sale_state
        )
        self.product_section.grid(row=0, column=0, sticky="nsew")

        self.totals_panel = TotalsPanel(
            center_container, self.currency, self.tax_rate, self.sale_state, self.data_service
        )
        self.totals_panel.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.cart_panel = CartPanel(
            center_container, self.data_service, self.sale_state
        )
        self.cart_panel.grid(row=0, column=1, sticky="nsew")


