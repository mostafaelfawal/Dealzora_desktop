import shutil
import os
from time import strftime
from tkinter import messagebox


def backup_database(backup_path=None, return_message=False):
    """
    عمل نسخة احتياطية من قاعدة البيانات
    :param backup_path: المسار المخصص لحفظ النسخ الاحتياطية (اختياري)
    """
    # إذا لم يتم تحديد مسار، استخدم المسار الافتراضي
    if backup_path is None:
        backup_path = "backup"

    try:
        # محاولة إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(backup_path, exist_ok=True)

        # إنشاء اسم الملف مع التاريخ
        filename = f"dealzora_{strftime('%Y-%m-%d_%H-%M-%S')}.db"
        full_path = os.path.join(backup_path, filename)

        # نسخ قاعدة البيانات
        shutil.copy("db/dealzora.db", full_path)

        if return_message:
            return messagebox.showinfo("تم", f"تم حفظ النسخة في: {full_path}")

    except Exception:
        # إذا فشل الحفظ في المسار المحدد، استخدم المسار الافتراضي
        try:
            default_path = "backup"
            os.makedirs(default_path, exist_ok=True)
            filename = f"dealzora_{strftime('%Y-%m-%d_%H-%M-%S')}.db"
            full_path = os.path.join(default_path, filename)
            shutil.copy("db/dealzora.db", full_path)
            if return_message:
                return messagebox.showwarning(
                    "تم", f"تم حفظ النسخة في المسار الافتراضي: {full_path}"
                )

        except Exception as e2:
            if return_message:
                return messagebox.showerror(
                    "خطأ", f"فشل إنشاء النسخة الاحتياطية: {str(e2)}"
                )
