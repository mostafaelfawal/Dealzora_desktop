class StockMovementsModel:
    def __init__(self, cur, con):
        self.con = con
        self.cur = cur

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                old_quantity REAL NOT NULL,
                new_quantity REAL NOT NULL,
                movement_type TEXT NOT NULL,
                reference_id INTEGER,
                reference_number TEXT,
                date TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )"""
        )

        self.con.commit()

    # ===============================
    # Add stock movement
    # ===============================
    def add_movement(
        self,
        product_id,
        quantity,
        movement_type,
        reference_id=None,
        reference_number=None,
        old_qty=None,
    ):
        """إضافة حركة مخزون جديدة"""
        try:
            from models.products import ProductsModel

            products_db = ProductsModel(self.cur, self.con)
            if not old_qty:
                old_qty = products_db.get_old_qty(product_id)

            # حساب الكمية الجديدة
            new_quantity = old_qty + quantity

            if new_quantity < 0:
                raise ValueError(f"Insufficient stock for product {product_id}")

            # تحديث كمية المنتج
            self.cur.execute(
                "UPDATE products SET quantity = ? WHERE id = ?",
                (new_quantity, product_id),
            )

            # تسجيل الحركة
            self.cur.execute(
                """INSERT INTO stock_movements 
                (product_id, quantity, old_quantity, new_quantity, movement_type, 
                 reference_id, reference_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    product_id,
                    quantity,
                    old_qty,
                    new_quantity,
                    movement_type,
                    reference_id,
                    reference_number,
                ),
            )

            self.con.commit()
            return self.cur.lastrowid

        except Exception as e:
            self.con.rollback()
            raise e

    # ===============================
    # Get movements
    # ===============================
    def get_movements(self):
        self.cur.execute("SELECT * FROM stock_movements ORDER BY id DESC")
        row = self.cur.fetchall()
        return row

    def filter_by_date(
        self, from_date=None, to_date=None, product_id=None, movement_type=None
    ):
        query = "SELECT * FROM stock_movements WHERE 1=1"
        params = []

        if from_date:
            query += " AND date(date) >= ?"
            params.append(from_date)

        if to_date:
            query += " AND date(date) <= ?"
            params.append(to_date)

        if product_id:
            query += " AND product_id = ?"
            params.append(product_id)

        if movement_type:
            query += " AND movement_type = ?"
            params.append(movement_type)

        query += " ORDER BY id DESC"
        self.cur.execute(query, params)
        return self.cur.fetchall()

    # ===============================
    # Delete movements
    # ===============================
    def delete_movement(self, mIDs: list):
        if not mIDs:
            return
        ids = tuple(mIDs)
        self.cur.execute(
            "DELETE FROM stock_movements WHERE id IN (%s)" % ",".join("?" * len(ids)),
            ids,
        )

        self.con.commit()
