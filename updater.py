# Dealzora_update.py
import os
import sys
import time
import hashlib
import psutil
from tkinter import messagebox, Tk


# ==========================
# دوال مساعدة
# ==========================
def check_sha256(file_path, expected_hash):
    """تحقق من سلامة الملف باستخدام SHA256"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash


def wait_for_close(exe_path, timeout=15):
    """انتظر حتى يغلق البرنامج القديم قبل الاستبدال"""
    for _ in range(timeout * 2):
        try:
            running = any(p.exe() == exe_path for p in psutil.process_iter(["exe"]))
        except:
            running = False
        if not running:
            return True
        time.sleep(0.5)
    return False


# ==========================
# بداية التحديث
# ==========================
time.sleep(1)  # انتظر البرنامج يغلق نفسه

# لإنشاء نافذة مؤقتة لـ MessageBox
root = Tk()
root.withdraw()  # اخفي نافذة الـ Tkinter الرئيسية

app_dir = os.path.dirname(sys.executable)
old_exe = os.path.join(app_dir, "Dealzora.exe")
new_exe = os.path.join(app_dir, "Dealzora_new.exe")  # الملف الذي تم تحميله

# تحقق من وجود الملف الجديد
if not os.path.exists(new_exe):
    messagebox.showerror("تحديث فشل", "ملف التحديث غير موجود! التحديث فشل.")
    sys.exit(1)

# توليد hash تلقائي من الملف الجديد
with open(new_exe, "rb") as f:
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: f.read(8192), b""):
        sha256.update(chunk)
    EXPECTED_HASH = sha256.hexdigest()

# تحقق من اكتمال وسلامة الملف الجديد
if not check_sha256(new_exe, EXPECTED_HASH):
    messagebox.showerror("تحديث فشل", "ملف التحديث تالف أو غير مكتمل! التحديث أُوقف.")
    sys.exit(1)

# انتظر البرنامج القديم يغلق
if not wait_for_close(old_exe):
    messagebox.showwarning(
        "تحديث فشل", "البرنامج القديم لا يزال يعمل، يرجى غلقه قبل التحديث."
    )
    sys.exit(1)

# حذف النسخة القديمة واستبدالها بالجديدة
try:
    os.remove(old_exe)
    os.rename(new_exe, old_exe)
    messagebox.showinfo("تم التحديث", "تم التحديث بنجاح! جاري تشغيل البرنامج...")
    os.startfile(old_exe)
except Exception as e:
    messagebox.showerror("تحديث فشل", f"حدث خطأ أثناء استبدال النسخة القديمة: {e}")
    sys.exit(1)
