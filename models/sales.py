class SalesModel:
    def __init__(self, cur, con):
        self.con = con
        self.cur = cur
        # Create DB
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE NOT NULL,
            total REAL NOT NULL,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            paid REAL NOT NULL,
            change REAL DEFAULT 0,
            customer_id INTEGER,
            date TEXT DEFAULT (date('now','localtime')),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
            )"""
        )

        self.con.commit()

    def add_sale(self, number, total, discount, tax, paid, change, customer_id=None):
        self.cur.execute(
            """
            INSERT INTO sales (number, total, discount, tax, paid, change, customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (number, total, discount, tax, paid, change, customer_id),
        )
        r = self.cur.lastrowid
        self.con.commit()
        return r

    def get_sales(self):
        self.cur.execute("SELECT * FROM sales ORDER BY id DESC")
        row = self.cur.fetchall()
        return row

    def get_sale(self, sid):
        self.cur.execute("SELECT * FROM sales WHERE id=?", (sid,))
        row = self.cur.fetchone()
        return row

    def delete_sales(self, saleIDs: list):
        if not saleIDs:
            return

        ids = tuple(saleIDs)
        self.cur.execute(
            "DELETE FROM sales WHERE id IN (%s)" % ",".join("?" * len(ids)),
            ids,
        )
        self.con.commit()

    def update_sale_total(self, sale_id, total):
        self.cur.execute(
            "UPDATE sales SET total=? WHERE id=?",
            (total, sale_id),
        )
        self.con.commit()
