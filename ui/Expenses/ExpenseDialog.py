from customtkinter import (
    CTkToplevel,
    CTkEntry,
    CTkLabel,
    CTkFrame,
    CTkComboBox,
    CTkOptionMenu,
    CTkButton,
)
from tkcalendar import DateEntry
import tkinter.messagebox as messagebox


class ExpenseDialog(CTkToplevel):
    def __init__(self, parent, expense_data=None, on_save_callback=None):
        super().__init__(parent)
        self.expense_data = expense_data
        self.on_save_callback = on_save_callback
        self._setup_window()
        self._build_form()

        if expense_data:
            self._populate_form()

    def _setup_window(self):
        """تكوين خصائص النافذة"""
        self.title("➕ إضافة مصروف" if not self.expense_data else "✏️ تعديل مصروف")
        self.geometry("400x550")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        # توسيط النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        """بناء النموذج بشكل مضغوط"""
        # الإطار الرئيسي
        main = CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=15)

        # حقول الإدخال
        fields = [
            ("📅 التاريخ", self._create_date_field),
            ("📂 النوع", self._create_type_field),
            ("👤 المستفيد", self._create_beneficiary_field),
            ("💰 المبلغ", self._create_amount_field),
            ("🏷️ الحالة", self._create_status_field),
        ]

        for label, creator in fields:
            frame = CTkFrame(main, fg_color="transparent")
            frame.pack(fill="x", pady=5)

            CTkLabel(frame, text=label, font=("Cairo", 13, "bold")).pack(anchor="w")
            creator(frame)

        # حقل الوصف (منفصل)
        desc_frame = CTkFrame(main, fg_color="transparent")
        desc_frame.pack(fill="x", pady=5)

        CTkLabel(desc_frame, text="📝 الوصف", font=("Cairo", 13, "bold")).pack(
            anchor="w"
        )
        self.desc_entry = CTkEntry(
            desc_frame, font=("Cairo", 12), placeholder_text="اختياري", height=35
        )
        self.desc_entry.pack(fill="x", pady=(2, 0))

        # الأزرار
        btn_frame = CTkFrame(main, fg_color="transparent")
        btn_frame.pack(pady=(15, 0))

        CTkButton(
            btn_frame,
            text="حفظ",
            font=("Cairo", 14, "bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            width=100,
            height=35,
            corner_radius=8,
            command=self._save_expense,
        ).pack(side="left", padx=5)

        CTkButton(
            btn_frame,
            text="إلغاء",
            font=("Cairo", 14, "bold"),
            fg_color="#757575",
            hover_color="#616161",
            width=100,
            height=35,
            corner_radius=8,
            command=self.destroy,
        ).pack(side="left", padx=5)

        # اختصارات
        self.bind("<Return>", lambda e: self._save_expense())
        self.bind("<Escape>", lambda e: self.destroy())

    def _create_date_field(self, parent):
        """إنشاء حقل التاريخ"""
        self.date_entry = DateEntry(
            parent,
            font=("Cairo", 12),
            date_pattern="yyyy-mm-dd",
            width=20,
            background="#4CAF50",
            foreground="white",
            borderwidth=1,
        )
        self.date_entry.pack(fill="x", pady=(2, 0))

    def _create_type_field(self, parent):
        """إنشاء حقل النوع"""
        self.type_menu = CTkComboBox(
            parent,
            values=[
                "مصاريف منزلية",
                "مصاريف ايجار",
                "مصاريف طعام",
                "مصاريف مواصلات",
                "مصاريف تعليم",
                "مصاريف صحية",
                "مصاريف ترفيه",
            ],
            font=("Cairo", 12),
            height=35,
            dropdown_font=("Cairo", 12),
        )
        self.type_menu.pack(fill="x", pady=(2, 0))
        if not self.expense_data:
            self.type_menu.set("مصاريف منزلية")

    def _create_beneficiary_field(self, parent):
        """إنشاء حقل المستفيد"""
        self.beneficiary_entry = CTkEntry(
            parent, font=("Cairo", 12), placeholder_text="أدخل اسم المستفيد", height=35
        )
        self.beneficiary_entry.pack(fill="x", pady=(2, 0))

    def _create_amount_field(self, parent):
        """إنشاء حقل المبلغ"""
        self.amount_entry = CTkEntry(
            parent, font=("Cairo", 12), placeholder_text="0.00", height=35
        )
        self.amount_entry.pack(fill="x", pady=(2, 0))

    def _create_status_field(self, parent):
        """إنشاء حقل الحالة"""
        self.status_menu = CTkOptionMenu(
            parent,
            values=["مدفوع", "معلق", "موافق عليه"],
            font=("Cairo", 12),
            height=35,
            dropdown_font=("Cairo", 12),
        )
        self.status_menu.pack(fill="x", pady=(2, 0))
        if not self.expense_data:
            self.status_menu.set("مدفوع")

    def _populate_form(self):
        """تعبئة البيانات للتعديل"""
        if isinstance(self.expense_data, (tuple, list)):
            # (id, date, type, beneficiary, amount, description, status)
            self.date_entry.set_date(self.expense_data[1])
            self.type_menu.set(self.expense_data[2])
            self.beneficiary_entry.insert(0, self.expense_data[3])
            self.amount_entry.insert(0, str(self.expense_data[4]))
            if len(self.expense_data) > 5 and self.expense_data[5]:
                self.desc_entry.insert(0, self.expense_data[5])
            if len(self.expense_data) > 6:
                self.status_menu.set(self.expense_data[6])
        elif isinstance(self.expense_data, dict):
            self.date_entry.set_date(self.expense_data.get("date", ""))
            self.type_menu.set(self.expense_data.get("type", ""))
            self.beneficiary_entry.insert(0, self.expense_data.get("beneficiary", ""))
            self.amount_entry.insert(0, str(self.expense_data.get("amount", 0)))
            self.desc_entry.insert(0, self.expense_data.get("description", ""))
            self.status_menu.set(self.expense_data.get("status", "مدفوع"))

    def _save_expense(self):
        """حفظ البيانات"""
        try:
            # التحقق من البيانات المطلوبة
            beneficiary = self.beneficiary_entry.get().strip()
            if not beneficiary:
                messagebox.showwarning(
                    "تنبيه", "الرجاء إدخال اسم المستفيد", parent=self
                )
                self.beneficiary_entry.focus()
                return

            amount_text = self.amount_entry.get().strip()
            if not amount_text:
                messagebox.showwarning("تنبيه", "الرجاء إدخال المبلغ", parent=self)
                self.amount_entry.focus()
                return

            try:
                amount = float(amount_text)
                if amount <= 0:
                    messagebox.showwarning(
                        "تنبيه", "الرجاء إدخال مبلغ أكبر من صفر", parent=self
                    )
                    self.amount_entry.focus()
                    return
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح", parent=self)
                self.amount_entry.focus()
                return

            # تجهيز البيانات
            expense_data = {
                "date": self.date_entry.get_date(),
                "type": self.type_menu.get(),
                "beneficiary": beneficiary,
                "amount": amount,
                "description": self.desc_entry.get().strip(),
                "status": self.status_menu.get(),
            }

            # إضافة ID للتعديل
            if self.expense_data:
                if isinstance(self.expense_data, (tuple, list)):
                    expense_data["id"] = self.expense_data[0]
                elif isinstance(self.expense_data, dict):
                    expense_data["id"] = self.expense_data.get("id")

            if self.on_save_callback:
                self.on_save_callback(expense_data)

            self.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}", parent=self)
