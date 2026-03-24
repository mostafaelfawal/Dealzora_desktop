from customtkinter import CTkFrame, CTkLabel, CTkButton
from tkinter.messagebox import showinfo
from time import strftime
from utils.image import image

class Toolbar(CTkFrame):
    def __init__(self, parent, sale_state):
        super().__init__(parent)

        self.sale_state = sale_state
        self.date = self._get_current_date()
        self.main_font = ("Cairo", 16, "bold")

        self._build_toolbar()
        self._update_time()

    def _build_toolbar(self):
        # عرض رقم الفاتورة
        self.invoice_number_label = CTkLabel(
            self,
            text=f"{self.sale_state.invoice_number} :رقم الفاتورة",
            font=self.main_font,
            text_color=("#008f83", "#00bbab"),
        )
        self.invoice_number_label.pack(pady=10, padx=10, side="right")
        # عرض التاريخ و الوقت
        self.date_label = CTkLabel(
            self,
            text=f"{self.date} :التاريخ",
            font=self.main_font,
            text_color=("#008cc4", "#009ddb"),
        )
        self.date_label.pack(padx=10, pady=10, side="right")
        # زر المساعدة
        CTkButton(
            self,
            text="",
            image=image("assets/information.png"),
            corner_radius=20,
            command=self._show_help,
        ).pack(padx=10, pady=10, side="right")

    def _get_current_date(self):
        "الحصول على التاريخ الحالي"
        date = strftime("%d/%m/%Y")
        time = strftime("%H:%M:%S")
        
        return f"⏰ {time} | 📅 {date}"

    def _update_time(self):
        self.date = self._get_current_date()

        self.date_label.configure(text=f"{self.date} :التاريخ")

        self.after(1000, self._update_time)

    def _show_help(self):
        showinfo("مساعدة | واجهة البيع", self._get_help_message())

    def _get_help_message(self):
        return """
━━━━━━━━━━━━━━━━━━
🧾 دليل استخدام واجهة البيع
━━━━━━━━━━━━━━━━━━

⌨️ اختصارات سريعة:
───────────────
F4        → لتفريغ السلة
F3        → البحث عن منتج
F2        → اختيار عميل
F12        → اتمام البيع
Esc       → الغاء العملية

🛒 إدارة المنتجات:
───────────────
• امسح الباركود أو اكتب اسم المنتج للبحث
• استخدم الفئات لتصفية المنتجات بسرعة

📦 التحكم في الجدول:
───────────────
Enter / Double Click → إضافة المنتج
Ctrl + A            → تحديد الكل
Ctrl + Shift + A    → إلغاء التحديد
Home                → أول منتج
End                 → آخر منتج

➕➖ تعديل الكمية:
───────────────
+ أو ↑   → زيادة الكمية
- أو ↓   → تقليل الكمية

🗑️ الحذف:
───────────────
Delete أو Ctrl + D → حذف المنتج من السلة

💰 النظام المالي:
───────────────
• يتم تسجيل المديونية تلقائيًا عند عدم الدفع الكامل
• يتم خصم الرصيد تلقائيًا إذا كان العميل دائن

━━━━━━━━━━━━━━━━━━
⚡ نصيحة:
استخدم الكيبورد بدل الماوس لسرعة أعلى في الكاشير
━━━━━━━━━━━━━━━━━━
"""
