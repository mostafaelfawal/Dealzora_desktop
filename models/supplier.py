class SupplierModel:
    def __init__(self, cur, con):
        self.cur = cur
        self.con = con
        # Create DB
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS suppliers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE
            )"""
        )

        self.con.commit()

    def get_suppliers(self):
        self.cur.execute("SELECT * FROM suppliers")
        row = self.cur.fetchall()
        return row

    def get_supplier(self, sid):
        self.cur.execute("SELECT * FROM suppliers WHERE id=?", (sid,))
        row = self.cur.fetchone()
        return row[1] if row else ""

    def get_or_create_supplier_id(self, name):
        if not name:
            return None

        self.cur.execute("SELECT id FROM suppliers WHERE name=?", (name,))
        row = self.cur.fetchone()
        if row:
            return row[0]

        # إنشاء مورد جديد لو مش موجود
        self.cur.execute("INSERT INTO suppliers (name) VALUES (?)", (name,))
        self.con.commit()
        return self.cur.lastrowid

    def get_supplier_by_id(self, supplier_id):
        """الحصول على مورد محدد بواسطة ID"""
        self.cur.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,))
        row = self.cur.fetchone()
        return row

    def update_supplier(self, supplier_id, name, phone=None):
        """تحديث بيانات مورد"""
        if phone:
            self.cur.execute(
                "UPDATE suppliers SET name=?, phone=? WHERE id=?",
                (name, phone, supplier_id),
            )
        else:
            self.cur.execute(
                "UPDATE suppliers SET name=?, phone=NULL WHERE id=?",
                (name, supplier_id),
            )
        self.con.commit()

    def delete_supplier(self, supplier_id):
        """حذف مورد"""
        self.cur.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
        self.con.commit()
