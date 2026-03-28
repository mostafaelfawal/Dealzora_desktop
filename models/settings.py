import json
import os


class SettingsModel:
    def __init__(self, path="settings.json"):
        self.path = path

        self.defaults = {
            "shop_name": "DEALZORA",
            "currency": "ج.م",
            "tax": 0.0,
            "theme": "dark",
            "logo_path": "assets/icon.png",
            "printer_name": "",
            "invoices_per_print": 1,
            "auto_print": True,
            "auto_backup": False,
            "backup_path": "backup",
            "printer_type": "حرارية",
            "paper_size": "58",
            "shop_phone": "",
            "shop_address": "",
            "currency_name": "جنيهاً",
            "sub_currency_name": "قرشاً",
            "decimal_places": 2,
            "user_id": "",
        }

        # validators لكل مفتاح
        self.validators = {
            "tax": lambda v: float(v) if self._is_number(v) else 0.0,
            "invoices_per_print": lambda v: int(v) if self._is_number(v) else 1,
            "auto_print": bool,
            "auto_backup": bool,
            "theme": lambda v: v if v in ["dark", "light", "system"] else "system",
            "printer_type": lambda v: v if v in ["A4", "حرارية"] else "A4",
        }

        self._ensure_file()

    # ================== Utils ==================
    def _ensure_file(self):
        if not os.path.exists(self.path):
            self.save_settings(self.defaults)

    def _is_number(self, value):
        try:
            float(value)
            return True
        except:
            return False

    # ================== Core ==================
    def get_settings(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}

        # merge مع defaults
        merged = {**self.defaults, **data}
        return merged

    def get_setting(self, key):
        if key not in self.defaults:
            raise ValueError(f"{key} غير موجود في الإعدادات")

        return self.get_settings()[key]

    # ================== Update ==================
    def update_settings(self, **kwargs):
        data = self.get_settings()

        for key, value in kwargs.items():

            if key not in self.defaults:
                continue  # تجاهل أي مفتاح غلط

            # apply validator لو موجود
            if key in self.validators:
                try:
                    value = self.validators[key](value)
                except:
                    value = self.defaults[key]

            data[key] = value

        self.save_settings(data)

    # ================== Save ==================
    def save_settings(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)