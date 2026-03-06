class SaleItmesModel:
    def __init__(self, cur, con):
        self.con = con
        self.cur = cur
        # Create DB
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS sale_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(id)
            )"""
        )

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id ON sale_items(sale_id)"
        )

        self.con.commit()

    def add_sale_items(self, sale_id, items):
        try:
            self.cur.executemany(
                """
                INSERT INTO sale_items (sale_id, product_id, quantity, price, total)
                VALUES (?, ?, ?, ?, ?)
                """,
                [(sale_id, *item) for item in items],
            )
            self.con.commit()
        except:
            self.con.rollback()

    def get_sale_items(self, sid):
        self.cur.execute("SELECT * FROM sale_items WHERE sale_id=?", (sid,))
        row = self.cur.fetchall()
        return row

    def delete_sale_item(self, item_id):
        self.cur.execute(
            "DELETE FROM sale_items WHERE id=?",
            (item_id,),
        )
        self.con.commit()

    def update_sale_item_quantity(self, item_id, new_quantity, new_total):
        """تحديث كمية المنتج وإجمالي السعر في sale_items"""
        self.cur.execute(
            "UPDATE sale_items SET quantity=?, total=? WHERE id=?",
            (new_quantity, new_total, item_id),
        )
        self.con.commit()
