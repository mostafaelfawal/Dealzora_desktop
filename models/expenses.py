class ExpensesModel:
    def __init__(self, cur, con):
        self.cur = cur
        self.con = con

        # status = (Paid, Pending, Approved)
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (date('now','localtime')),
                type TEXT NOT NULL,
                beneficiary TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'paid'
            )
            """
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_expense_filters ON expenses(date, type, beneficiary, status)"
        )
        
        self.con.commit()
        
    def add_expense(self, type, beneficiary, amount, description="", date=None):
        self.cur.execute(
            """
            INSERT INTO expenses (date, type, beneficiary, amount, description)
            VALUES (COALESCE(?, date('now','localtime')), ?, ?, ?, ?)
            """,
            (date, type, beneficiary, amount, description),
        )
        self.con.commit()

    def get_expenses(self, from_date=None, to_date=None, type=None, beneficiary=None, status=None):
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
        if status and status != "اختر الحاله":
            query += " AND status = ?"
            params.append(status)
        
        self.cur.execute(query, params)
        return self.cur.fetchall()