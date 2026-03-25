class ExpensesState:
    def __init__(self, expenses_service) -> None:
        self.expenses_service = expenses_service
        self._expenses = []
        self._filters = {
            "from_date": None,
            "to_date": None,
            "type": None,
            "beneficiary": None,
            "status": None,
            "search": None,
        }

    @property
    def expenses(self):
        self._expenses = self.expenses_service.get_expenses(
            from_date=self._filters["from_date"],
            to_date=self._filters["to_date"],
            type=self._filters["type"],
            beneficiary=self._filters["beneficiary"],
            status=self._filters["status"],
            search=self._filters["search"],
        )
        return self._expenses

    def set_filter(self, filter_name, value):
        if filter_name in self._filters:
            # إذا كانت القيمة "اختر..." أو فارغة، قم بتعيينها إلى None
            if value in ["اختر المستفيد", "اختر نوع", "اختر حالة", ""]:
                self._filters[filter_name] = None
            else:
                self._filters[filter_name] = value
            return True
        return False

    def clear_filters(self):
        self._filters = {
            "from_date": None,
            "to_date": None,
            "type": None,
            "beneficiary": None,
            "status": None,
            "search": None,
        }

    def refresh(self):
        """تحديث البيانات"""
        self._expenses = []
