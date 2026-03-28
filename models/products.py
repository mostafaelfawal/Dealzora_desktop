from models.supplier import SupplierModel
from models.stock_movements import StockMovementsModel
from utils.alter_column_type import alter_column_type
from utils.column_exists import column_exists

class ProductsModel:
    def __init__(self, cur, con):
        self.con = con
        self.cur = cur
        self.suppliers_db = SupplierModel(self.cur, self.con)
        self.stock_movements_db = StockMovementsModel(self.cur, self.con)

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS units(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            small_unit_name TEXT,
            conversion_factor REAL
            )
            """
        )
        self.create_default_units()
        
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS category(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
            )"""
        )

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            barcode TEXT UNIQUE,
            buy_price REAL DEFAULT 0,
            sell_price REAL NOT NULL,
            quantity REAL DEFAULT 0,
            category_id INTEGER,
            image_path TEXT,
            low_stock INTEGER DEFAULT 5,
            supplier_id INTEGER,
            created_at TEXT DEFAULT (date('now','localtime')),
            unit_id INTEGER,
            FOREIGN KEY(category_id) REFERENCES category(id),
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY(unit_id) REFERENCES units(id)
            )"""
        )
        
        alter_column_type(cur, con, "products", "quantity", "REAL")
        
        if not column_exists(self.cur, "products", "unit_id"):
            self.cur.execute("ALTER TABLE products ADD COLUMN unit_id INTEGER")
            self.con.commit()

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)"
        )

        self.con.commit()

    def create_default_units(self):
        """إنشاء وحدات افتراضية إذا لم تكن موجودة"""
        # التحقق من وجود أي وحدات في قاعدة البيانات
        self.cur.execute("SELECT COUNT(*) FROM units")
        count = self.cur.fetchone()[0]
        
        if count == 0:
            default_units = [
                ("قطعة", None, 1),
                ("لتر", None, 1),
                ("كجم", "جرام", 1000),
                ("متر", "سنتيمتر", 100),
                ("سنتيمتر", None, 1),
                ("جرام", None, 1),
            ]
            
            self.cur.executemany(
                "INSERT INTO units (name, small_unit_name, conversion_factor) VALUES (?, ?, ?)",
                default_units
            )
            self.con.commit()
    
    def finalize_changes(self):
        self.clean_empty_categorys()
        self.con.commit()

    def clean_empty_categorys(self):
        self.cur.execute(
            """
            DELETE FROM category
            WHERE id NOT IN (
                SELECT DISTINCT category_id
                FROM products
                WHERE category_id IS NOT NULL
            )
        """
        )

    def search_products_by_query(self, keyword, search_type):
        if search_type not in ["name", "barcode"]:
            return []
        self.cur.execute(
            f"SELECT * FROM products WHERE {search_type} LIKE ?", (f"%{keyword}%",)
        )
        return self.cur.fetchall()

    def search_products(self, keyword):
        keyword = keyword.strip()

        self.cur.execute(
            "SELECT * FROM products WHERE barcode LIKE ?",
            (f"{keyword}%",),
        )
        result = self.cur.fetchall()
        if result:
            return result

        # fallback بحث بالاسم
        self.cur.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            (f"%{keyword}%",),
        )
        return self.cur.fetchall()
    
    def search_products_advanced(self, keyword="", category_id=None):
        keyword = keyword.strip()

        query = """
            SELECT *
            FROM products
            WHERE 1=1
        """
        params = []

        # فلترة بالفئة
        if category_id and category_id != "all":
            query += " AND category_id = ?"
            params.append(category_id)

        # فلترة بالكلمة
        if keyword:
            query += " AND (barcode LIKE ? OR name LIKE ?)"
            params.extend([f"{keyword}%", f"%{keyword}%"])

        query += " ORDER BY id DESC"

        self.cur.execute(query, params)
        return self.cur.fetchall()

    def product_exists(self, p_name):
        self.cur.execute(
            "SELECT name FROM products WHERE name LIKE ?",
            (f"{p_name}",),
        )
        row = self.cur.fetchone()
        return True if row else False

    def get_products(self):
        self.cur.execute("SELECT * FROM products ORDER BY id DESC")
        return self.cur.fetchall()

    def get_product(self, pid):
        self.cur.execute("SELECT * FROM products WHERE id=?", (pid,))
        return self.cur.fetchone()

    def get_old_qty(self, pid):
        self.cur.execute("SELECT quantity FROM products WHERE id=?", (pid,))
        qty = self.cur.fetchone()
        return qty[0] if qty else 0

    def get_categorys(self):
        self.cur.execute("SELECT * FROM category")
        return self.cur.fetchall()

    def get_category(self, cid):
        self.cur.execute("SELECT name FROM category WHERE id=?", (cid,))
        row = self.cur.fetchone()
        return row[0] if row else ""
    
    def get_units(self):
        self.cur.execute("SELECT * FROM units")
        return self.cur.fetchall()
    
    def get_unit(self, uid):
        self.cur.execute("SELECT * FROM units WHERE id=?", (uid,))
        row = self.cur.fetchone()
        return row

    def get_products_by_category(self, category_id):
        if category_id == "all":
            self.cur.execute("SELECT * FROM products")
        else:
            self.cur.execute(
                "SELECT * FROM products WHERE category_id=?", (category_id,)
            )
        return self.cur.fetchall()

    def get_or_create_category_id(self, name):
        self.cur.execute("SELECT id FROM category WHERE name=?", (name,))
        row = self.cur.fetchone()
        if row:
            return row[0]

        self.cur.execute("INSERT INTO category (name) VALUES (?)", (name,))
        self.con.commit()
        return self.cur.lastrowid

    def search_products_by_category(self, keyword, category_name):
        keyword = keyword.strip()

        self.cur.execute(
            """
            SELECT p.*
            FROM products p
            JOIN category c ON p.category_id = c.id
            WHERE c.name = ?
            AND (p.barcode LIKE ? OR p.name LIKE ?)
            """,
            (category_name, f"{keyword}%", f"%{keyword}%"),
        )

        return self.cur.fetchall()
    
    def delete_products(self, products_IDs: list):
        if not products_IDs:
            return
        ids = tuple(products_IDs)
        self.cur.execute(
            "DELETE FROM products WHERE id IN (%s)" % ",".join("?" * len(ids)),
            ids,
        )
        self.finalize_changes()

    def add_product(
        self,
        name,
        barcode,
        buy_price,
        sell_price,
        quantity,
        image_path,
        low_stock=5,
        supplier_id=None,
        category_id=None,
        supplier_name=None,
        category_name=None,
        unit_id=None,  # Add unit_id parameter
    ):
        if category_name and not category_id:
            category_id = self.get_or_create_category_id(category_name)
        if supplier_name and not supplier_id:
            supplier_id = self.suppliers_db.get_or_create_supplier_id(supplier_name)

        if barcode:
            self.cur.execute(
                "SELECT id, quantity FROM products WHERE barcode=?", (barcode,)
            )
            row = self.cur.fetchone()

            if row:
                product_id, old_qty = row
                new_qty = old_qty + quantity

                self.cur.execute(
                    "UPDATE products SET quantity=? WHERE id=?", (new_qty, product_id)
                )

                self.con.commit()
                return

        self.cur.execute(
            """INSERT INTO products
            (name,barcode,buy_price,sell_price,quantity,category_id,image_path,low_stock,supplier_id,unit_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                name,
                barcode,
                buy_price,
                sell_price,
                quantity,
                category_id,
                image_path,
                low_stock,
                supplier_id,
                unit_id,  # Add unit_id
            ),
        )
        product_id = self.cur.lastrowid
        
        self.stock_movements_db.add_movement(
            product_id=product_id,
            quantity=quantity,
            movement_type="رصيد افتتاحي",
        )
        self.finalize_changes()

    def update_product(
        self,
        name,
        barcode,
        buy_price,
        sell_price,
        quantity,
        image_path,
        product_id,
        low_stock=5,
        supplier_id=None,
        category_id=None,
        supplier_name=None,
        category_name=None,
        unit_id=None,  # Add unit_id parameter
    ):
        if category_name and not category_id:
            category_id = self.get_or_create_category_id(category_name)
        if supplier_name and not supplier_id:
            supplier_id = self.suppliers_db.get_or_create_supplier_id(supplier_name)

        old_quantity = self.get_old_qty(product_id)

        self.cur.execute(
            """UPDATE products SET
            name=?,barcode=?,buy_price=?,sell_price=?,
            quantity=?,image_path=?,low_stock=?,supplier_id=?,category_id=?,unit_id=?
            WHERE id=?""",
            (
                name,
                barcode,
                buy_price,
                sell_price,
                quantity,
                image_path,
                low_stock,
                supplier_id,
                category_id,
                unit_id,  # Add unit_id
                product_id,
            ),
        )

        if old_quantity != quantity:
            quantity_diff = quantity - old_quantity
            movement_type = "يدوي"

            self.stock_movements_db.add_movement(
                product_id=product_id,
                quantity=quantity_diff,
                movement_type=movement_type,
                reference_id=product_id,
                old_qty=old_quantity,
            )

        self.finalize_changes()