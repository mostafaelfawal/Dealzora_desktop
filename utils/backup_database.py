import shutil
import os

def backup_database():
    os.makedirs("backup", exist_ok=True)  # تأكد وجود الملف
    path = "backup/dealzora.db"
    shutil.copy("db/dealzora.db", path)  # نسخ احتياطي
