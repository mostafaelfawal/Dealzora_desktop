class DataService:
    def __init__(self, expenses_db) -> None:
        self.expenses_db = expenses_db

    def get_expenses(
        self,
        from_date=None,
        to_date=None,
        type=None,
        beneficiary=None,
        status=None,
        search=None,
    ):
        return self.expenses_db.get_expenses(
            from_date, to_date, type, beneficiary, status, search
        )

    def add_expense(self, date, type, beneficiary, amount, description, status):
        return self.expenses_db.add_expense(
            date, type, beneficiary, amount, description, status
        )

    def update_expense(
        self, expense_id, date, type, beneficiary, amount, description, status
    ):
        return self.expenses_db.update_expense(
            expense_id, date, type, beneficiary, amount, description, status
        )

    def delete_expense(self, expense_id):
        return self.expenses_db.delete_expense(expense_id)
