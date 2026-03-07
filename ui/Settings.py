from customtkinter import (
    CTkFrame,
    CTkScrollableFrame,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkOptionMenu,
    StringVar,
    set_appearance_mode,
)
from tkinter import messagebox
from components.UploadImage import UploadImage
from components.BackupButton import BackupButton
from utils.image import image
from utils.is_number import is_number


class Settings:
    def __init__(self, root, settings_db):
        self.root = root
        self.vars = {}

        # ======= الهيدر =======
        header_frame = CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        CTkLabel(
            header_frame,
            text="اعدادات النظام",
            image=image("assets/الأعدادات.png", (40, 40)),
            font=("Cairo", 36, "bold"),
            compound="right",
            text_color="#2b7de9",
        ).pack(side="right")

        CTkFrame(self.root, height=2, fg_color="#2b7de9", corner_radius=0).pack(
            fill="x", pady=(0, 20)
        )

        # ======= إعداد قاعدة البيانات =======
        self.settings_db = settings_db
        self.settings = self.settings_db.get_settings()

        # ======= Scrollable Frame للمحتوى =======
        self.content_frame = CTkScrollableFrame(
            self.root, fg_color="transparent", height=600, width=550
        )
        self.content_frame.pack(fill="x")

        # ======= قسم الشعار =======
        self.create_logo_section()

        # ======= قسم البيانات =======
        self.create_data_section()

        # ======= زر حفظ نهائي =======
        CTkButton(
            self.content_frame,
            text="حفظ الإعدادات",
            font=("Cairo", 16, "bold"),
            fg_color="#00be8f",
            hover_color="#008d6a",
            command=self.save_settings,
            height=40,
            corner_radius=10,
        ).pack(pady=(20, 30))
        backup_frame = CTkFrame(self.content_frame, fg_color="transparent")
        backup_frame.pack(pady=10)
        CTkLabel(
            backup_frame,
            text="! يتم عمل نسخ احتياطي تلقائي للبيانات",
            text_color=("#9B9B9B", "#616161"),
            font=("Cairo", 16, "bold")
        ).pack(side="right")
        BackupButton(backup_frame)

    # ---------- أقسام منفصلة ----------
    def create_logo_section(self):
        logo_section = CTkFrame(
            self.content_frame, fg_color="transparent", corner_radius=15
        )
        logo_section.pack(fill="x", pady=(0, 20), padx=10)

        CTkLabel(
            logo_section,
            text="شعار المحل",
            font=("Cairo", 22, "bold"),
            text_color="#2b7de9",
        ).pack(pady=(15, 10))

        self.upload_logo = UploadImage(logo_section)
        self.upload_logo.set_image(self.settings["logo_path"])

    def create_data_section(self):
        data_section = CTkFrame(
            self.content_frame, fg_color=("gray90", "gray20"), corner_radius=15
        )
        data_section.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        CTkLabel(
            data_section,
            text="بيانات المحل",
            font=("Cairo", 22, "bold"),
            text_color="#2b7de9",
        ).pack(anchor="center", pady=(15, 20))

        fields_container = CTkFrame(data_section, fg_color="transparent")
        fields_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # ======= الحقول =======
        self.add_field(
            fields_container, ":اسم المحل", self.settings["shop_name"], "shop_name"
        )
        self.add_field(
            fields_container, ":العملة", self.settings["currency"], "currency"
        )
        self.add_field(
            fields_container,
            ":الضريبة %",
            self.settings["tax"],
            "tax",
        )
        self.add_combo(
            fields_container,
            ":الوضع",
            ["dark", "light", "system"],
            self.settings["theme"],
            "theme",
        )

    # ---------- إضافة الحقول ----------
    def add_field(self, parent, label_text, value, var_name):
        frame = CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))

        CTkLabel(frame, text=label_text, font=("Cairo", 18), anchor="e").pack(
            anchor="e", pady=(0, 5)
        )

        var = StringVar(value=value)
        self.vars[var_name] = var

        entry = CTkEntry(
            frame,
            textvariable=var,
            font=("Cairo", 16),
            height=45,
            corner_radius=8,
            border_width=2,
        )
        entry.pack(fill="x")

    def add_combo(self, parent, label_text, options, value, var_name):
        frame = CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))

        CTkLabel(frame, text=label_text, font=("Cairo", 18), anchor="e").pack(
            anchor="e", pady=(0, 5)
        )

        var = StringVar(value=value)
        self.vars[var_name] = var

        combo = CTkOptionMenu(
            frame,
            values=options,
            variable=var,
            font=("Cairo", 16),
            height=45,
            corner_radius=8,
            dropdown_font=("Cairo", 14),
        )
        combo.pack(fill="x")

    # ---------- حفظ الإعدادات ----------
    def save_settings(self):
        try:
            tax = self.vars["tax"].get().strip()
            if is_number(tax):
                tax = float(tax)
            else:
                return messagebox.showerror("خطأ", "ادخل رقم صحيح في الضريبه")

            theme = self.vars["theme"].get()
            currency = self.vars["currency"].get().strip()

            if len(currency) > 3:
                return messagebox.showerror("خطأ", "ادخل عملة ثلاثية مثلا (ج.م)")

            self.settings_db.update_settings(
                self.vars["shop_name"].get(),
                currency,
                tax,
                theme,
                self.upload_logo.get_image(),
            )

            # ======= تطبيق الـ Theme فوراً =======
            set_appearance_mode(theme)

            messagebox.showinfo("تم", "تم حفظ اعدادات النظام بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
