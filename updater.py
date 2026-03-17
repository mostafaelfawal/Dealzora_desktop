import os
import time
import sys

time.sleep(3)

app_dir = os.path.dirname(os.path.abspath(sys.executable))

old_exe = os.path.join(app_dir, "Dealzora.exe")
new_exe = os.path.join(app_dir, "Dealzora_update.exe")

# محاولة حذف النسخة القديمة عدة مرات
for _ in range(10):
    try:
        if os.path.exists(old_exe):
            os.remove(old_exe)
        
        break
    except:
        time.sleep(1)

# إعادة تسمية النسخة الجديدة
os.rename(new_exe, old_exe)

# تشغيل البرنامج بعد التحديث
os.startfile(old_exe)