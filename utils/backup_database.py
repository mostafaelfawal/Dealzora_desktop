import shutil
import os
from time import strftime


def backup_database():
    os.makedirs("backup", exist_ok=True)  # تأكد وجود الملف
    path = f"backup/dealzora_{strftime('%Y-%m-%d_%H-%M-%S')}.db"
    shutil.copy("db/dealzora.db", path)  # نسخ احتياطي
