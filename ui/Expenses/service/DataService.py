class DataService:
    def __init__(self, expenses_db) -> None:
        self.expenses_db = expenses_db
    
    def get_expenses(self, from_date=None, to_date=None, type=None, beneficiary=None, status=None):
        return self.expenses_db.get_expenses(from_date, to_date, type, beneficiary, status)