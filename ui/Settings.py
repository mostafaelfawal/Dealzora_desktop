from customtkinter import (
    CTkFrame,
    CTkScrollableFrame,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkOptionMenu,
    CTkCheckBox,
    StringVar,
    BooleanVar,
    CTkSwitch,
    set_appearance_mode,
)
from tkinter import messagebox, filedialog
import shutil
import os

import win32print
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
            image=image("assets/settings.png", (40, 40)),
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

        # ======= قسم الطباعة =======
        self.create_print_section()

        # ======= قسم النسخ الاحتياطي =======
        self.create_backup_section()

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

    def create_print_section(self):
        print_section = CTkFrame(
            self.content_frame, fg_color=("gray90", "gray20"), corner_radius=15
        )
        print_section.pack(fill="x", padx=10, pady=(0, 20))

        CTkLabel(
            print_section,
            text="طباعة الفواتير",
            font=("Cairo", 22, "bold"),
            text_color="#2b7de9",
        ).pack(pady=(15, 20))

        container = CTkFrame(print_section, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=(0, 20))

        # ===== اختيار الطابعة =====
        printers = self.get_printers()

        CTkLabel(
            container, text=":اختيار الطابعة", font=("Cairo", 18), anchor="e"
        ).pack(anchor="e", pady=(0, 5))

        saved_printer = self.settings.get("printer_name")

        # التحقق هل الطابعة مازالت موجودة
        if saved_printer in printers:
            printer_var = StringVar(value=saved_printer)
        else:
            printer_var = StringVar(value=printers[0])
            self.settings_db.update_settings(
                printer_name=printer_var.get()
            )  # تحديث اسم الطابعة في الإعدادات
            messagebox.showerror("خطأ", "الطابعة المحددة غير موجودة")

        self.vars["printer_name"] = printer_var

        printer_menu = CTkOptionMenu(
            container,
            values=printers,
            variable=printer_var,
            font=("Cairo", 16),
            height=45,
            corner_radius=8,
            dropdown_font=("Cairo", 14),
        )
        printer_menu.pack(fill="x", pady=(0, 15))

        # ===== عدد الفواتير =====
        CTkLabel(
            container,
            text=":عدد الفواتير لكل عملية بيع",
            font=("Cairo", 18),
            anchor="e",
        ).pack(anchor="e", pady=(0, 5))

        copies_var = StringVar(value=self.settings.get("invoices_per_print", "1"))
        self.vars["invoices_per_print"] = copies_var

        copies_entry = CTkEntry(
            container,
            textvariable=copies_var,
            justify="center",
            font=("Cairo", 16),
            height=45,
            corner_radius=8,
            border_width=2,
        )
        copies_entry.pack(fill="x")

        # ===== الطباعة التلقائية =====
        auto_print_var = BooleanVar(value=self.settings.get("auto_print", True))
        self.vars["auto_print"] = auto_print_var

        CTkCheckBox(
            container,
            text="طباعة الفاتورة تلقائيا بعد عملية البيع",
            font=("Cairo", 16),
            variable=auto_print_var,
        ).pack(anchor="e", pady=(15, 0))

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

    def create_backup_section(self):
        backup_section = CTkFrame(
            self.content_frame, fg_color=("gray90", "gray20"), corner_radius=15
        )
        backup_section.pack(fill="x", padx=10, pady=(0, 20))

        CTkLabel(
            backup_section,
            text="النسخ الاحتياطي",
            font=("Cairo", 22, "bold"),
            text_color="#2b7de9",
        ).pack(pady=(15, 20))

        container = CTkFrame(backup_section, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=(0, 20))

        # ===== Switch النسخ التلقائي =====
        auto_backup_var = BooleanVar(value=self.settings.get("auto_backup", False))
        self.vars["auto_backup"] = auto_backup_var

        CTkSwitch(
            container,
            text="تفعيل النسخ الاحتياطي التلقائي",
            variable=auto_backup_var,
            font=("Cairo", 16),
        ).pack(anchor="e", pady=(0, 15))

        # ===== مسار حفظ النسخ الاحتياطي =====
        CTkLabel(
            container,
            text=":مسار حفظ النسخ الاحتياطية",
            font=("Cairo", 18),
            anchor="e",
        ).pack(anchor="e", pady=(0, 5))

        path_container = CTkFrame(container, fg_color="transparent")
        path_container.pack(fill="x", pady=(0, 15))

        backup_path_var = StringVar(value=self.settings.get("backup_path", "backup"))
        self.vars["backup_path"] = backup_path_var

        backup_path_entry = CTkEntry(
            path_container,
            textvariable=backup_path_var,
            font=("Cairo", 14),
            height=40,
            corner_radius=8,
            border_width=2,
        )
        backup_path_entry.pack(side="right", fill="x", expand=True, padx=(5, 0))

        CTkButton(
            path_container,
            text="استعراض",
            font=("Cairo", 14),
            width=80,
            height=40,
            command=lambda: self.browse_backup_path(backup_path_var),
        ).pack(side="left")

        # ===== أزرار النسخ والاستعادة =====
        buttons_container = CTkFrame(container, fg_color="transparent")
        buttons_container.pack(fill="x", pady=10)

        # ===== زر استعادة البيانات =====
        CTkButton(
            buttons_container,
            text="استعادة البيانات",
            font=("Cairo", 16, "bold"),
            fg_color="#f39c12",
            hover_color="#d68910",
            command=self.restore_database,
            image=image("assets/data-recovery.png"),
            height=40,
            corner_radius=10,
        ).pack(side="right", padx=5, pady=10)

        # ===== زر النسخ الاحتياطي اليدوي =====
        BackupButton(buttons_container, self.settings.get("backup_path", "backup"))

    def browse_backup_path(self, path_var):
        """فتح نافذة اختيار المجلد"""
        folder_selected = filedialog.askdirectory(
            title="اختر مجلد لحفظ النسخ الاحتياطية"
        )
        if folder_selected:
            path_var.set(folder_selected)

    def restore_database(self):
        file_path = filedialog.askopenfilename(
            title="اختر ملف قاعدة البيانات",
            filetypes=[("Database Files", "*.db")],
        )

        if not file_path:
            return

        try:
            db_folder = "db"
            target_db = os.path.join(db_folder, "dealzora.db")

            if not os.path.exists(db_folder):
                os.makedirs(db_folder)

            shutil.copy(file_path, target_db)

            messagebox.showinfo(
                "تم", "تم استعادة البيانات بنجاح\nيرجى إعادة تشغيل البرنامج"
            )

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل استعادة البيانات\n{str(e)}")

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

    # ------- مساعدة ----------
    def get_printers(self):
        printers = []
        for p in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        ):
            printers.append(p[2])
        return printers if printers else ["لا يوجد طابعات"]

    # ---------- حفظ الإعدادات ----------
    def save_settings(self):
        try:
            tax = self.vars["tax"].get().strip()
            copies = self.vars["invoices_per_print"].get()

            try:
                if int(copies) < 1:
                    raise ValueError
            except ValueError:
                return messagebox.showerror("خطأ", "عدد الفواتير يجب أن يكون رقم")

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
                self.vars["printer_name"].get(),
                copies,
                self.vars["auto_print"].get(),
                self.vars["auto_backup"].get(),
                self.vars["backup_path"].get(),  # إضافة مسار النسخ الاحتياطي
            )

            # ======= تطبيق الـ Theme فوراً =======
            set_appearance_mode(theme)

            messagebox.showinfo("تم", "تم حفظ اعدادات النظام بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
