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


def force_close_process(process_name):
    """إغلاق العملية بالقوة إذا كانت تعمل"""
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            if proc.info["name"] == process_name or (
                proc.info["exe"] and process_name in proc.info["exe"]
            ):
                proc.kill()
                time.sleep(0.5)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def wait_for_close(exe_path, timeout=15):
    """انتظر حتى يغلق البرنامج القديم قبل الاستبدال"""
    for _ in range(timeout * 2):
        try:
            running = False
            for proc in psutil.process_iter(["exe", "name"]):
                try:
                    if proc.info["exe"] and proc.info["exe"] == exe_path:
                        running = True
                        break
                    elif proc.info["name"] == "Dealzora.exe":
                        running = True
                        break
                except:
                    continue
        except:
            running = False

        if not running:
            return True
        time.sleep(0.5)

    # إذا لم يغلق، حاول إغلاقه بالقوة
    force_close_process("Dealzora.exe")
    time.sleep(1)
    return False


# ==========================
# بداية التحديث
# ==========================
time.sleep(2)  # انتظر البرنامج يغلق نفسه

# لإنشاء نافذة مؤقتة لـ MessageBox
root = Tk()
root.withdraw()  # اخفي نافذة الـ Tkinter الرئيسية

# تحديد المسار الصحيح
if getattr(sys, "frozen", False):
    app_dir = os.path.dirname(sys.executable)
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

old_exe = os.path.join(app_dir, "Dealzora.exe")
new_exe = os.path.join(app_dir, "Dealzora_new.exe")  # الملف الذي تم تحميله

print(f"App directory: {app_dir}")
print(f"Old exe: {old_exe}")
print(f"New exe: {new_exe}")

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
    # إذا لم يغلق، اسأل المستخدم
    result = messagebox.askyesno(
        "تحديث", "البرنامج القديم لا يزال يعمل. هل تريد إغلاقه بالقوة واستكمال التحديث؟"
    )
    if result:
        force_close_process("Dealzora.exe")
        time.sleep(1)
    else:
        sys.exit(1)

# حذف النسخة القديمة واستبدالها بالجديدة
try:
    # تأكد من أن الملف القديم غير موجود أو محذوف
    if os.path.exists(old_exe):
        os.remove(old_exe)

    os.rename(new_exe, old_exe)
    messagebox.showinfo("تم التحديث", "تم التحديث بنجاح! جاري تشغيل البرنامج...")

    # تشغيل البرنامج الجديد
    os.startfile(old_exe)

    # إغلاق أداة التحديث
    root.destroy()
    sys.exit(0)

except Exception as e:
    messagebox.showerror("تحديث فشل", f"حدث خطأ أثناء استبدال النسخة القديمة: {e}")
    sys.exit(1)
