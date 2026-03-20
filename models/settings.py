import json
import os


class SettingsModel:
    def __init__(self, path="settings.json"):
        self.path = path

        # القيم الافتراضية
        self.defaults = {
            "shop_name": "DEALZORA",
            "currency": "ج.م",
            "tax": 0,
            "theme": "dark",
            "logo_path": "assets/icon.png",
            "printer_name": "",
            "invoices_per_print": 1,
            "auto_print": True,
            "auto_backup": False,
            "backup_path": "backup",
            "printer_type": "حرارية",
            "shop_phone": "",
            "shop_address": "",
            "currency_name": "جنيهاً"
        }

        # لو الملف مش موجود
        if not os.path.exists(self.path):
            self.save_settings(self.defaults)

    # قراءة كل الإعدادات
    def get_settings(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = self.defaults.copy()
            self.save_settings(data)

        # التأكد من وجود كل المفاتيح
        for key, value in self.defaults.items():
            if key not in data:
                data[key] = value

        return data

    # قراءة قيمة واحدة
    def get_setting(self, key):
        if key not in self.defaults:
            raise ValueError(
                f"{key} معامل خاطئ يجب ان يكون احد هذه: {list(self.defaults.keys())}"
            )

        return self.get_settings().get(key, self.defaults[key])

    # تحديث الإعدادات
    def update_settings(
        self,
        shop_name=None,
        currency=None,
        tax=None,
        theme=None,
        logo_path=None,
        printer_name=None,
        copies=None,
        auto_print=None,
        auto_backup=None,
        backup_path=None,
        printer_type=None,
        shop_phone=None,
        shop_address=None,
        currency_name=None

    ):
        data = self.get_settings()

        if shop_name is not None:
            data["shop_name"] = shop_name

        if currency is not None:
            data["currency"] = currency

        if tax is not None:
            try:
                data["tax"] = float(tax)
            except (ValueError, TypeError):
                data["tax"] = 0

        if theme is not None:
            if theme in ["dark", "light", "system"]:
                data["theme"] = theme
            else:
                data["theme"] = "system"

        if logo_path is not None:
            data["logo_path"] = logo_path

        if printer_name is not None:
            data["printer_name"] = printer_name

        if copies is not None:
            try:
                data["invoices_per_print"] = int(copies)
            except (ValueError, TypeError):
                data["invoices_per_print"] = 1

        if auto_print is not None:
            data["auto_print"] = bool(auto_print)

        if auto_backup is not None:
            data["auto_backup"] = bool(auto_backup)

        if backup_path is not None:
            data["backup_path"] = backup_path
            
        if printer_type is not None:
            if printer_type in ["A4", "حرارية"]:
                data["printer_type"] = printer_type
            else:
                data["printer_type"] = "A4"

        if shop_phone is not None:
            data["shop_phone"] = shop_phone
        
        if shop_address is not None:
            data["shop_address"] = shop_address
        
        if currency_name is not None:
            data["currency_name"] = currency_name
        
        self.save_settings(data)

    # حفظ الملف
    def save_settings(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
