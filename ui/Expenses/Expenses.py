from customtkinter import CTkButton, CTkComboBox, CTkEntry, CTkLabel, CTkFrame, CTkOptionMenu
from tkcalendar import DateEntry
from .Expenses_state import ExpensesState
from .service.DataService import DataService
from utils.image import image
from components.TreeView import TreeView


class Expenses:
    def __init__(self, root, expenses_db) -> None:
        self.root = root
        
        self.expenses_service = DataService(expenses_db)
        self.expenses_state = ExpensesState(self.expenses_service)
        
        self._build_title()
        self._build_actions_frame()
        self._build_row_summary()
        self._build_expenses_table()

    # ---------------- Title ----------------
    def _build_title(self) -> None:
        CTkLabel(
            self.root,
            text="ادارة المصروفات",
            image=image("assets/expenses.png"),
            font=("Cairo", 40, "bold"),
            compound="left",
        ).pack(padx=10, pady=10)

    # ---------------- Actions Frame ----------------
    def _build_actions_frame(self) -> None:
        self.actions_frame = CTkFrame(
            self.root, fg_color=("#FFFFFF", "#000000"), corner_radius=10
        )
        self.actions_frame.pack(padx=10, pady=10, fill="x")

        # إعداد أعمدة Grid لتتمدد بشكل متساوي
        for i in range(5):
            self.actions_frame.grid_columnconfigure(i, weight=1)

        # إنشاء الصفوف
        self._build_row_dates()
        self._build_row_filters()
        self._build_row_search()

    # ---------------- Row 0: Dates + Add ----------------
    def _build_row_dates(self) -> None:
        self.to_date = DateEntry(
            self.actions_frame,
            font=("Cairo", 20),
            date_pattern="yyyy-mm-dd",
        )
        self.to_date.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        CTkLabel(
            self.actions_frame,
            text="←",
            font=("Cairo", 20),
            compound="left",
        ).grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.from_date = DateEntry(
            self.actions_frame,
            font=("Cairo", 20),
            date_pattern="yyyy-mm-dd",
        )
        self.from_date.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        CTkLabel(
            self.actions_frame,
            text="من تاريخ",
            font=("Cairo", 20),
            compound="left",
        ).grid(row=0, column=3, padx=5, pady=10, sticky="ew")

        self.add_expense_btn = CTkButton(
            self.actions_frame,
            text="اضافة مصروف",
            image=image("assets/add.png"),
            font=("Cairo", 20),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            corner_radius=30,
        )
        self.add_expense_btn.grid(row=0, column=4, padx=5, pady=10, sticky="ew")

    # ---------------- Row 1: Filters ----------------
    def _build_row_filters(self) -> None:
        self.beneficiary_cb = CTkComboBox(
            self.actions_frame,
            values=["اختر المستفيد", "احمد", "محمد", "علي"],
            font=("Cairo", 20, "bold"),
            dropdown_font=("Cairo", 20),
            fg_color=("#D6D6D6", "#2E2E2E"),
            corner_radius=10,
        )
        self.beneficiary_cb.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.type_menu = CTkOptionMenu(
            self.actions_frame,
            values=["اختر نوع", "مصاريف منزلية", "مصاريف سيارة", "مصاريف طعام", "مصاريف أخرى"],
            font=("Cairo", 20, "bold"),
            dropdown_font=("Cairo", 20),
            fg_color=("#D6D6D6", "#3F3F3F"),
            text_color=("#000000", "#FFFFFF"),
            corner_radius=10,
        )
        self.type_menu.grid(row=1, column=2, columnspan=2, padx=5, pady=10, sticky="ew")

        self.status_menu = CTkOptionMenu(
            self.actions_frame,
            values=["اختر حالة", "مدفوع", "معلق", "موافق عليه"],
            font=("Cairo", 20, "bold"),
            dropdown_font=("Cairo", 20),
            fg_color=("#D6D6D6", "#3F3F3F"),
            text_color=("#000000", "#FFFFFF"),
            corner_radius=10,
        )
        self.status_menu.grid(row=1, column=4, padx=5, pady=10, sticky="ew")

    # ---------------- Row 2: Search + Clear ----------------
    def _build_row_search(self) -> None:
        self.search_entry = CTkEntry(
            self.actions_frame,
            placeholder_text="ابحث برقم المستند, الأسم, المبلغ...",
            font=("Cairo", 20),
            fg_color=("#D6D6D6", "#2E2E2E"),
            corner_radius=10,
        )
        self.search_entry.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

        self.clear_btn = CTkButton(
            self.actions_frame,
            text="مسح ❌",
            fg_color=("#ADADAD", "#4B4B4B"),
            hover_color=("#A0A0A0", "#3B3B3B"),
            font=("Cairo", 20),
        )
        self.clear_btn.grid(row=2, column=3, columnspan=2, padx=5, pady=10, sticky="ew")
        
    # ---------------- Row 3: Summary Cards ----------------
    def build_summary_card(self, text, value, fg_color) -> None:
        card = CTkFrame(
            self.summary_frame, fg_color=fg_color, corner_radius=15
        )
        card.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        CTkLabel(
            card,
            text=text,
            font=("Cairo", 18, "bold"),
            fg_color=fg_color,
        ).pack(padx=10, pady=(10, 5))
        CTkLabel(
            card,
            text=value,
            font=("Cairo", 24, "bold"),
            fg_color=fg_color,
        ).pack(padx=10, pady=(0, 10))

    def _build_row_summary(self) -> None:
        # Container للملخص
        self.summary_frame = CTkFrame(
            self.root, fg_color=("#FFFFFF", "#1E1E1E"), corner_radius=10
        )
        self.summary_frame.pack(padx=10, fill="x")

        # إعداد 3 أعمدة متساوية
        for i in range(3):
            self.summary_frame.grid_columnconfigure(i, weight=1)

        self.build_summary_card("المصروف السنوي", "0.00", ("#FF9800", "#F57C00"))
        self.build_summary_card("المصروف الشهري", "0.00", ("#2196F3", "#1976D2"))
        self.build_summary_card("المصروف اليومي", "0.00", ("#4CAF50", "#388E3C"))
        
    def _build_expenses_table(self) -> None:
        cols = ("ID", "رقم المستند", "التاريخ", "النوع", "المستفيد", "المبلغ", "الحاله")
        widths = (30, 150, 120, 150, 150, 100, 120)
        self.tree = TreeView(self.root, cols, widths, 10)
        