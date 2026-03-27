from dataclasses import dataclass

@dataclass
class NavItem:
    """Represents a single sidebar navigation entry."""

    text: str
    icon_path: str
    screen_key: str
    permission: str


@dataclass
class AppDependencies:
    """Groups every external dependency the layout needs."""

    root: object
    customers_db: object
    products_db: object
    user_id: int
    users_db: object
    sale_items_db: object
    sales_db: object
    stock_movements_db: object
    suppliers_db: object
    settings: object
    expenses_db: object
    con: object
    cur: object


# ---------------------------------------------------------------------------
# Navigation registry
# ---------------------------------------------------------------------------

NAV_ITEMS: list[NavItem] = [
    NavItem("بيع", "assets/pos.png", "sale", "cashier_interface"),
    NavItem("منتجات", "assets/products.png", "products", "products_management"),
    NavItem("مستخدم", "assets/users.png", "users", "users_management"),
    NavItem("مخزون", "assets/stock.png", "stock", "inventory_management"),
    NavItem("تقارير", "assets/reports.png", "reports", "reports_view"),
    NavItem("عملاء", "assets/customers.png", "customers", "customers_management"),
    # NavItem("مراكز التكلفة", "assets/cost_center.png", "cost_center", "cost_center_management"),
    NavItem("فواتير", "assets/invoices.png", "invoices", "invoices_management"),
    NavItem("الموردين", "assets/suppliers.png", "suppliers", "suppliers_management"),
    NavItem("المصاريف", "assets/expenses.png", "expenses", "expenses_management"),
    NavItem("الأعدادات", "assets/settings.png", "settings", "settings_edit"),
]