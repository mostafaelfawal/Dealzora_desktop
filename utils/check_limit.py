from utils.license import is_license_valid

def check_limit(key, current_count):
    if is_license_valid():
        return True  # الترخيص صالح، لا يوجد حدود

    LIMITS = {
        "انشاء الفواتير": 10,
        "اضافة العملاء": 10,
        "اضافة الموردين": 10,
        "اضافة المنتجات": 10,
        "استعادة البيانات": 0,
    }
    limit = LIMITS[key]

    if limit is None:
        return True  # غير محدود

    if current_count >= limit:
        from tkinter.messagebox import showwarning

        message = f"""
لقد وصلت للحد الأقصى من {key}
قم بالترقية لأستخدم البرنامج بشكل غير محدود
----------------
للحصول على النسخه الكامله
تواصل معنا عبر الواتساب:
+201151083509
        """

        showwarning("تم الوصول للحد", message)
        return False

    return True
