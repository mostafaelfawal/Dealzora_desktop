from utils.check_limit import check_limit


class DataService:
    def __init__(
        self,
        products_db,
        customers_db,
        stock_movements_db,
        sales_db,
        sale_itmes_db,
        settings_db,
        price_edit_permission,
    ):
        self.products_db = products_db
        self.customers_db = customers_db
        self.stock_movements_db = stock_movements_db
        self.sales_db = sales_db
        self.sale_itmes_db = sale_itmes_db
        self.settings_db = settings_db
        self._price_edit_permission = price_edit_permission

    @property
    def price_edit_permission(self):
        return self._price_edit_permission

    # ======== Settings ========
    def get_setting(self, key: str):
        return self.settings_db.get_setting(key)

    # ========= Products =========
    def get_products(self):
        return self.products_db.get_products()

    def get_product(self, pid):
        return self.products_db.get_product(pid)

    def search_product(self, keyword="", category_name="جميع الفئات"):
        category_id = None

        if category_name != "جميع الفئات":
            for c in self.products_db.get_categorys():
                if c[1] == category_name:
                    category_id = c[0]
                    break

        return self.products_db.search_products_advanced(keyword, category_id)

    # ========= categorys =========
    def get_categorys(self):
        return [c[1] for c in self.products_db.get_categorys()]

    # ========= units =========
    def get_unit(self, unit_id):
        unit = self.products_db.get_unit(unit_id)
        return {
            "unit_name": unit[1],
            "sub_unit_name": unit[2],
            "conversion_factor": unit[3]
        }

    # ========= Customers =========
    def get_customers(self):
        return self.customers_db.get_customers()

    def add_customer(self, name, phone, debt):
        current = len(self.get_customers())
        if not check_limit("اضافة العملاء", current):
            return None
        return self.customers_db.add_customer(name, phone, debt)

    def search_customers_by_query(self, keyword, search_type):
        return self.customers_db.search_customers_by_query(keyword, search_type)

    def update_customer_debt(self, cid, new_debt):
        self.customers_db.update_customer_debt(cid, new_debt)

    # ========= Stock Movements =========
    def add_movement(
        self,
        product_id,
        qty,
        reference_number,
        reference_id,
        movement_type="بيع",
    ):
        self.stock_movements_db.add_movement(
            product_id,
            qty,
            movement_type,
            reference_id,
            reference_number=reference_number,
        )

    # ========= Invoices =========
    def get_sales(self):
        return self.sales_db.get_sales()
    
    def record_invoice(self, number, total, discount, tax, paid, change, customer_id):
        current = len(self.get_sales())
        if not check_limit("انشاء الفواتير", current):
            return None
        
        return self.sales_db.add_sale(
            number, total, discount, tax, paid, change, customer_id
        )

    def record_invoice_item(self, sale_id, products):
        self.sale_itmes_db.add_sale_items(sale_id, products)
