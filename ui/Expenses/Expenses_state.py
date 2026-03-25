class ExpensesState:
    def __init__(self, expenses_service) -> None:
        self.expenses_service = expenses_service
        self._expenses = []
