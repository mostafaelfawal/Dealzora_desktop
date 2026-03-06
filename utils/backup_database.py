import shutil
import os
from tkinter.messagebox import showinfo


def backup_database():
    os.makedirs("backup", exist_ok=True)  # تأكد وجود الملف
    path = "backup/dealzora.db"
    shutil.copy("db/dealzora.db", path)  # نسخ احتياطي
