class ExpensesModel:
    def __init__(self, cur, con):
        self.cur = cur
        self.con = con

        # status = (مدفوع, معلق, موافق عليه)
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (date('now','localtime')),
                type TEXT NOT NULL,
                beneficiary TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'مدفوع'
            )
            """
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_expense_filters ON expenses(date, type, beneficiary, status)"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_expense_search ON expenses(description, amount)"
        )

        self.con.commit()

    def add_expense(
        self, date, type, beneficiary, amount, description="", status="مدفوع"
    ):
        """إضافة مصروف جديد"""
        self.cur.execute(
            """
            INSERT INTO expenses (date, type, beneficiary, amount, description, status)
            VALUES (COALESCE(?, date('now','localtime')), ?, ?, ?, ?, ?)
            """,
            (date, type, beneficiary, amount, description, status),
        )
        self.con.commit()
        return self.cur.lastrowid

    def update_expense(
        self, expense_id, date, type, beneficiary, amount, description, status
    ):
        """تحديث مصروف موجود"""
        self.cur.execute(
            """
            UPDATE expenses 
            SET date = ?, type = ?, beneficiary = ?, amount = ?, description = ?, status = ?
            WHERE id = ?
            """,
            (date, type, beneficiary, amount, description, status, expense_id),
        )
        self.con.commit()
        return self.cur.rowcount > 0

    def delete_expense(self, expense_id):
        """حذف مصروف"""
        self.cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.con.commit()
        return self.cur.rowcount > 0

    def get_expenses(
        self,
        from_date=None,
        to_date=None,
        type=None,
        beneficiary=None,
        status=None,
        search=None,
    ):
        query = "SELECT id, date, type, beneficiary, amount, description, status FROM expenses WHERE 1=1"
        params = []

        if from_date:
            query += " AND date >= ?"
            params.append(from_date)
        if to_date:
            query += " AND date <= ?"
            params.append(to_date)
        if type and type != "اختر نوع":
            query += " AND type = ?"
            params.append(type)
        if beneficiary and beneficiary != "اختر المستفيد":
            query += " AND beneficiary = ?"
            params.append(beneficiary)
        if status and status != "اختر حالة":
            query += " AND status = ?"
            params.append(status)
        if search:
            query += (
                " AND (description LIKE ? OR CAST(amount AS TEXT) LIKE ? OR id LIKE ?)"
            )
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        query += " ORDER BY date DESC, id DESC"
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def get_unique_beneficiaries(self):
        """الحصول على قائمة المستفيدين الفريدة"""
        self.cur.execute(
            "SELECT DISTINCT beneficiary FROM expenses ORDER BY beneficiary"
        )
        return [row[0] for row in self.cur.fetchall()]

    def get_unique_types(self):
        """الحصول على قائمة الأنواع الفريدة"""
        self.cur.execute("SELECT DISTINCT type FROM expenses ORDER BY type")
        return [row[0] for row in self.cur.fetchall()]
