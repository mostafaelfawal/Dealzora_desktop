from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkLabel,
    CTkFrame,
    CTkOptionMenu,
)
from tkcalendar import DateEntry
from .Expenses_state import ExpensesState
from .service.DataService import DataService
from .ExpenseDialog import ExpenseDialog
from utils.image import image
from utils.format_currency import format_currency
from utils.key_shortcut import key_shortcut
from components.TreeView import TreeView
from datetime import datetime
import tkinter.messagebox as messagebox

from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkLabel,
    CTkFrame,
    CTkOptionMenu,
)
from tkcalendar import DateEntry
import tkinter.messagebox as messagebox

class Expenses:
    def __init__(self, root, expenses_db) -> None:
        self.root = root
        self._search_after_id = None  # For debouncing search
        self._is_updating = False  # Prevent recursive updates

        self.expenses_service = DataService(expenses_db)
        self.expenses_state = ExpensesState(self.expenses_service)

        self._build_title()
        self._build_actions_frame()
        self._build_row_summary()
        self._build_expenses_table()
        self._setup_filter_events()
        self._load_unique_values()  # تحميل القيم الفريدة
        self.refresh_expenses_table(self.expenses_state.expenses)

    # ---------------- تحميل القيم الفريدة ----------------
    def _load_unique_values(self) -> None:
        """تحميل قيم المستفيدين والأنواع الفريدة من قاعدة البيانات"""
        try:
            # تحديث قائمة المستفيدين
            beneficiaries = self.expenses_service.expenses_db.get_unique_beneficiaries()
            if beneficiaries:
                self.beneficiary_cb.configure(values=["اختر المستفيد"] + beneficiaries)
                self.beneficiary_cb.set("اختر المستفيد")
            
            # تحديث قائمة الأنواع
            types = self.expenses_service.expenses_db.get_unique_types()
            if types:
                self.type_menu.configure(values=["اختر نوع"] + types)
                self.type_menu.set("اختر نوع")
        except Exception as e:
            print(f"Error loading unique values: {e}")

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
        for i in range(7):
            self.actions_frame.grid_columnconfigure(i, weight=1)

        # إنشاء الصفوف
        self._build_row_dates()
        self._build_row_filters()
        self._build_row_search()
        self._build_row_actions()

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

    # ---------------- Row for Edit/Delete Buttons ----------------
    def _build_row_actions(self) -> None:
        """Build row with edit and delete buttons."""
        CTkLabel(
            self.actions_frame,
            text="",
            font=("Cairo", 20),
        ).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.edit_btn = CTkButton(
            self.actions_frame,
            text="تعديل",
            image=image("assets/edit.png"),
            font=("Cairo", 20),
            fg_color=("#00B7FF", "#00B7FF"),
            hover_color=("#00A0E0", "#00A0E0"),
            corner_radius=30,
            command=self._edit_expense,
        )
        self.edit_btn.grid(row=3, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        self.delete_btn = CTkButton(
            self.actions_frame,
            text="حذف",
            image=image("assets/delete.png"),
            font=("Cairo", 20),
            fg_color=("#F44336", "#D32F2F"),
            hover_color=("#E53935", "#C62828"),
            corner_radius=30,
            command=self._delete_expense,
        )
        self.delete_btn.grid(row=3, column=4, columnspan=2, padx=5, pady=5, sticky="ew")

    # ---------------- Row 1: Filters ----------------
    def _build_row_filters(self) -> None:
        self.beneficiary_cb = CTkOptionMenu(
            self.actions_frame,
            values=["اختر المستفيد"],
            font=("Cairo", 20, "bold"),
            dropdown_font=("Cairo", 20),
            fg_color=("#D6D6D6", "#2E2E2E"),
            corner_radius=10,
            command=self._on_filter_change,
        )
        self.beneficiary_cb.grid(
            row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew"
        )

        self.type_menu = CTkOptionMenu(
            self.actions_frame,
            values=["اختر نوع"],
            font=("Cairo", 20, "bold"),
            dropdown_font=("Cairo", 20),
            fg_color=("#D6D6D6", "#3F3F3F"),
            text_color=("#000000", "#FFFFFF"),
            corner_radius=10,
            command=self._on_filter_change,
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
            command=self._on_filter_change,
        )
        self.status_menu.grid(
            row=1, column=4, columnspan=2, padx=5, pady=10, sticky="ew"
        )

    # ---------------- Row 2: Search + Clear ----------------
    def _build_row_search(self) -> None:
        self.search_entry = CTkEntry(
            self.actions_frame,
            placeholder_text="ابحث بالمبلغ, الوصف...",
            font=("Cairo", 20),
            fg_color=("#D6D6D6", "#2E2E2E"),
            corner_radius=10,
        )
        self.search_entry.grid(
            row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew"
        )

        self.clear_btn = CTkButton(
            self.actions_frame,
            text="مسح ❌",
            fg_color=("#ADADAD", "#4B4B4B"),
            hover_color=("#A0A0A0", "#3B3B3B"),
            font=("Cairo", 20),
        )
        self.clear_btn.grid(row=2, column=3, columnspan=3, padx=5, pady=10, sticky="ew")

    # ---------------- Summary Cards ----------------
    def build_summary_card(self, text, fg_color) -> None:
        card = CTkFrame(self.summary_frame, fg_color=fg_color, corner_radius=15)
        card.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        title_label = CTkLabel(
            card,
            text=text,
            font=("Cairo", 18, "bold"),
            fg_color=fg_color,
        )
        title_label.pack(padx=10, pady=(10, 5))

        value_label = CTkLabel(
            card,
            text="00.0",
            font=("Cairo", 24, "bold"),
            fg_color=fg_color,
        )
        value_label.pack(padx=10, pady=(0, 10))

        return value_label

    def _build_row_summary(self) -> None:
        self.summary_frame = CTkFrame(
            self.root, fg_color=("#FFFFFF", "#1E1E1E"), corner_radius=10
        )
        self.summary_frame.pack(padx=10, fill="x")

        for i in range(3):
            self.summary_frame.grid_columnconfigure(i, weight=1)

        self.yearly_label = self.build_summary_card(
            "المصروف السنوي", ("#FF9800", "#F57C00")
        )
        self.monthly_label = self.build_summary_card(
            "المصروف الشهري", ("#2196F3", "#1976D2")
        )
        self.daily_label = self.build_summary_card(
            "المصروف اليومي", ("#4CAF50", "#388E3C")
        )

        self._update_summary()

    # ---------------- إعداد أحداث الفلترة ----------------
    def _setup_filter_events(self) -> None:
        """Setup filter events with optimization."""
        # For date pickers - immediate update
        key_shortcut(self.from_date, "<<DateEntrySelected>>", self._on_filter_change)
        key_shortcut(self.to_date, "<<DateEntrySelected>>", self._on_filter_change)
        
        # For dropdowns - immediate update
        key_shortcut(self.beneficiary_cb, "<<OptionMenuSelected>>", self._on_filter_change)
        key_shortcut(self.type_menu, "<<OptionMenuSelected>>", self._on_filter_change)
        key_shortcut(self.status_menu, "<<OptionMenuSelected>>", self._on_filter_change)
        
        # For search - with debouncing
        key_shortcut(self.search_entry, "<KeyRelease>", self._on_search_change)
        
        self.clear_btn.configure(command=self._clear_filters)
        self.add_expense_btn.configure(command=self._add_expense)

    # ---------------- معالجة تغيير الفلاتر ----------------
    def _on_filter_change(self, value=None) -> None:
        """Handle filter changes with prevention of recursive updates."""
        if self._is_updating:
            return
        
        self._is_updating = True
        try:
            self.expenses_state.set_filter("from_date", self.from_date.get_date())
            self.expenses_state.set_filter("to_date", self.to_date.get_date())
            self.expenses_state.set_filter("type", self.type_menu.get())
            self.expenses_state.set_filter("beneficiary", self.beneficiary_cb.get())
            self.expenses_state.set_filter("status", self.status_menu.get())
            
            self._update_display()
        finally:
            self._is_updating = False

    # ---------------- معالجة البحث مع تأخير ----------------
    def _on_search_change(self, event=None) -> None:
        """Handle search with debouncing."""
        if self._search_after_id:
            self.root.after_cancel(self._search_after_id)
        
        self._search_after_id = self.root.after(300, self._apply_search_filter)

    def _apply_search_filter(self) -> None:
        """Apply search filter after debouncing delay."""
        if self._is_updating:
            return
        
        self._is_updating = True
        try:
            self.expenses_state.set_filter("search", self.search_entry.get())
            self._update_display()
        finally:
            self._is_updating = False
            self._search_after_id = None

    # ---------------- تحديث العرض ----------------
    def _update_display(self) -> None:
        """Unified method to update table and summary."""
        filtered_expenses = self.expenses_state.expenses
        self._refresh_table(filtered_expenses)
        self._update_summary()

    def _get_tag_for_status(self, status) -> str:
        if status == "مدفوع":
            return "success"
        elif status == "معلق":
            return "danger"
        elif status == "موافق عليه":
            return "warning"
    
    def _refresh_table(self, expenses) -> None:
        """Refresh table with new data."""
        self.tree.tree.delete(*self.tree.tree.get_children())
        for expense in expenses:
            # expense format: (id, date, type, beneficiary, amount, description, status)
            expense = list(expense)
            expense[4] = format_currency(expense[4])
            expense[5] = expense[6]
            tag = self._get_tag_for_status(expense[5])
            self.tree.tree.insert("", "end", values=expense, tags=(tag,))


    # ---------------- مسح جميع الفلاتر ----------------
    def _clear_filters(self) -> None:
        """Clear all filters with optimized update."""
        if self._is_updating:
            return
        
        self._is_updating = True
        try:
            self.expenses_state.clear_filters()
            
            self.from_date.set_date(None)
            self.to_date.set_date(None)
            self.beneficiary_cb.set("اختر المستفيد")
            self.type_menu.set("اختر نوع")
            self.status_menu.set("اختر حالة")
            self.search_entry.delete(0, "end")
            
            if self._search_after_id:
                self.root.after_cancel(self._search_after_id)
                self._search_after_id = None
            
            self._update_display()
        finally:
            self._is_updating = False

    # ---------------- تحديث الملخصات ----------------
    def _update_summary(self) -> None:
        """Update daily, monthly, and yearly expense summaries."""
        expenses = self.expenses_state.expenses
        
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.strftime("%Y-%m-%d")
        
        daily_total = 0
        monthly_total = 0
        yearly_total = 0
        
        for expense in expenses:
            expense_date = datetime.strptime(expense[1], "%Y-%m-%d")
            expense_amount = expense[4]
            
            if expense[1] == current_day:
                daily_total += expense_amount
            
            if expense_date.year == current_year and expense_date.month == current_month:
                monthly_total += expense_amount
            
            if expense_date.year == current_year:
                yearly_total += expense_amount
        
        self.daily_label.configure(text=format_currency(daily_total))
        self.monthly_label.configure(text=format_currency(monthly_total))
        self.yearly_label.configure(text=format_currency(yearly_total))

    # ---------------- إضافة مصروف ----------------
    def _add_expense(self) -> None:
        """فتح نافذة إضافة مصروف جديد"""
        ExpenseDialog(self.root, on_save_callback=self._save_expense)

    # ---------------- تعديل مصروف ----------------
    def _edit_expense(self) -> None:
        """فتح نافذة تعديل المصروف"""
        if not self.selected_expense_id:
            messagebox.showwarning("تحذير", "الرجاء تحديد مصروف للتعديل")
            return
        
        # البحث عن المصروف المحدد
        selected_expense = None
        for expense in self.expenses_state.expenses:
            if expense[0] == self.selected_expense_id:
                selected_expense = expense
                break
        
        if selected_expense:
            ExpenseDialog(
                self.root,
                expense_data=selected_expense,
                on_save_callback=self._update_expense,
            )
        else:
            messagebox.showerror("خطأ", "لم يتم العثور على المصروف المحدد")

    # ---------------- حذف مصروف ----------------
    def _delete_expense(self) -> None:
        """حذف المصروف المحدد"""
        if not self.tree.tree.selection():
            messagebox.showwarning("تحذير", "الرجاء تحديد مصروف للحذف")
            return
        
        # تأكيد الحذف
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا المصروف؟\nلا يمكن التراجع عن هذا الإجراء."):
            try:
                if self.expenses_service.delete_expense(self.selected_expense_id):
                    # تحديث القوائم المنسدلة
                    self._load_unique_values()
                    # تحديث البيانات
                    self.expenses_state.refresh()
                    self._update_display()
                    self.selected_expense_id = None
                    messagebox.showinfo("نجاح", "تم حذف المصروف بنجاح")
                else:
                    messagebox.showerror("خطأ", "فشل حذف المصروف")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الحذف: {str(e)}")

    # ---------------- حفظ مصروف جديد ----------------
    def _save_expense(self, expense_data: dict) -> None:
        """حفظ مصروف جديد"""
        try:
            self.expenses_service.add_expense(
                date=expense_data["date"],
                type=expense_data["type"],
                beneficiary=expense_data["beneficiary"],
                amount=expense_data["amount"],
                description=expense_data.get("description", ""),
                status=expense_data["status"]
            )
            # تحديث القوائم المنسدلة
            self._load_unique_values()
            # تحديث البيانات
            self.expenses_state.refresh()
            self._update_display()
            messagebox.showinfo("نجاح", "تم إضافة المصروف بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الإضافة: {str(e)}")

    # ---------------- تحديث مصروف موجود ----------------
    def _update_expense(self, expense_data: dict) -> None:
        """تحديث مصروف موجود"""
        try:
            if self.expenses_service.update_expense(
                expense_id=expense_data["id"],
                date=expense_data["date"],
                type=expense_data["type"],
                beneficiary=expense_data["beneficiary"],
                amount=expense_data["amount"],
                description=expense_data.get("description", ""),
                status=expense_data["status"]
            ):
                # تحديث القوائم المنسدلة
                self._load_unique_values()
                # تحديث البيانات
                self.expenses_state.refresh()
                self._update_display()
                self.selected_expense_id = None
                messagebox.showinfo("نجاح", "تم تعديل المصروف بنجاح")
            else:
                messagebox.showerror("خطأ", "فشل تعديل المصروف")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التعديل: {str(e)}")

    # ---------------- معالجة اختيار صف في الجدول ----------------
    def _on_row_select(self, event):
        selected = self.tree.tree.selection()
        if not selected:
            self.selected_expense_id = None
            return

        item = self.tree.tree.item(selected[0])
        values = item["values"]

        if values:
            self.selected_expense_id = values[0]  # أول عمود هو الـ ID
            
    # ---------------- بناء جدول المصروفات ----------------
    def _build_expenses_table(self) -> None:
        """بناء جدول عرض المصروفات"""
        cols = ("ID", "التاريخ", "النوع", "المستفيد", "المبلغ", "الحاله")
        widths = (50, 150, 120, 150, 150, 100)
        self.tree = TreeView(self.root, cols, widths, 10)
        self.tree.tree.bind("<<TreeviewSelect>>", self._on_row_select)
        key_shortcut(self.tree.tree, ["<Double-1>", "<Return>"], self._edit_expense)
        key_shortcut(self.tree.tree, "<Delete>", self._delete_expense)

    # ---------------- تحديث الجدول (للتوافق) ----------------
    def refresh_expenses_table(self, expenses):
        """تحديث جدول المصروفات (للتوافق مع الإصدارات السابقة)"""
        self._refresh_table(expenses)