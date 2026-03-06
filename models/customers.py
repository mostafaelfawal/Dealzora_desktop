class CustomersModel:
    def __init__(self, cur, con):
        self.con = con
        self.cur = cur
        # Create DB
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,
            debt REAL DEFAULT 0,
            created_at TEXT DEFAULT (date('now','localtime'))
            )"""
        )

        # Create Indexs to fast search
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)"
        )

        self.con.commit()

    def search_customers_by_query(self, keyword, search_type):
        if search_type not in ["name", "phone"]:
            return []

        self.cur.execute(
            f"SELECT * FROM customers WHERE {search_type} LIKE ?", (f"%{keyword}%",)
        )
        return self.cur.fetchall()

    def get_customers(self):
        self.cur.execute("SELECT * FROM customers")
        row = self.cur.fetchall()
        return row

    def get_customer(self, cid):
        self.cur.execute("SELECT * FROM customers WHERE id=?", (cid,))
        row = self.cur.fetchone()
        return row

    def add_customer(self, name, phone, debt):
        self.cur.execute(
            "INSERT INTO customers (name, phone, debt) VALUES (?, ?, ?)",
            (name, phone, debt),
        )
        self.con.commit()

    def delete_customer(self, customers_IDs):
        ids_tuble = tuple(customers_IDs)
        self.cur.execute(
            "DELETE FROM customers WHERE id IN (%s)" % ",".join("?" * len(ids_tuble)),
            ids_tuble,
        )
        self.con.commit()

    def update_customer(self, name, phone, debt, customer_id):
        self.cur.execute(
            "UPDATE customers SET name=?, phone=?, debt=? WHERE id=?",
            (name, phone, debt, customer_id),
        )
        self.con.commit()

    def add_debt_to_customer(self, customer_id, amount):
        self.cur.execute(
            "UPDATE customers SET debt = debt + ? WHERE id = ?",
            (amount, customer_id),
        )
        self.con.commit()

    def reduce_debt_from_customer(self, customer_id, amount):
        self.cur.execute(
            "UPDATE customers SET debt = debt - ? WHERE id = ?",
            (amount, customer_id),
        )
        self.con.commit()
