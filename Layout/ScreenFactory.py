from ui.Sales.sale_screen import Sale
from ui.Products import Products
from ui.Users import UsersManagement
from ui.Stock import Stock
from ui.Reports import Reports
from ui.Customers import Customers
from ui.Invoices import Invoices
from ui.Settings import Settings
from ui.Suppliers import Suppliers
from ui.Expenses.Expenses import Expenses
from Layout.data_structures import AppDependencies
from ui.Sales.services.DataService import DataService
from typing import Callable
from ui.Sales.SaleState import SaleState


class ScreenFactory:
    """
    Knows how to build every screen from its string key.
    Receives all dependencies at construction time so the
    caller never has to worry about them.
    """

    def __init__(
        self, deps: AppDependencies, sale_state: SaleState, data_service: DataService
    ) -> None:
        self._deps = deps
        self._sale_state = sale_state
        self._data_service = data_service

    def build(self, parent, screen_key: str) -> None:
        builder = self._registry.get(screen_key)
        if builder:
            builder(self, parent)

    # ------------------------------------------------------------------
    # Individual builders (private)
    # ------------------------------------------------------------------

    def _build_sale(self, parent) -> None:
        Sale(parent, self._deps.settings, self._sale_state, self._data_service)

    def _build_products(self, parent) -> None:
        Products(parent, self._deps.products_db, self._deps.suppliers_db)

    def _build_users(self, parent) -> None:
        UsersManagement(parent, self._deps.users_db)

    def _build_stock(self, parent) -> None:
        Stock(
            parent,
            self._deps.users_db,
            self._deps.user_id,
            self._deps.products_db,
            self._deps.suppliers_db,
            self._deps.stock_movements_db,
            self._deps.settings,
        )

    def _build_reports(self, parent) -> None:
        Reports(parent, self._deps.cur)

    def _build_customers(self, parent) -> None:
        Customers(parent, self._deps.customers_db)

    def _build_invoices(self, parent) -> None:
        Invoices(
            parent,
            self._deps.con,
            self._deps.sales_db,
            self._deps.sale_items_db,
            self._deps.customers_db,
            self._deps.products_db,
            self._deps.stock_movements_db,
            self._deps.settings,
        )

    def _build_suppliers(self, parent) -> None:
        Suppliers(
            parent, self._deps.suppliers_db, self._deps.user_id, self._deps.users_db
        )

    def _build_expenses(self, parent) -> None:
        Expenses(parent, self._deps.expenses_db)
    
    def _build_settings(self, parent) -> None:
        Settings(parent, self._deps.settings)

    # Mapping kept inside the class to stay self-contained
    @property
    def _registry(self) -> dict[str, Callable]:
        return {
            "sale": ScreenFactory._build_sale,
            "products": ScreenFactory._build_products,
            "users": ScreenFactory._build_users,
            "stock": ScreenFactory._build_stock,
            "reports": ScreenFactory._build_reports,
            "customers": ScreenFactory._build_customers,
            "invoices": ScreenFactory._build_invoices,
            "suppliers": ScreenFactory._build_suppliers,
            "expenses": ScreenFactory._build_expenses,
            "settings": ScreenFactory._build_settings,
        }

