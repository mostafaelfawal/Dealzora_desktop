from customtkinter import (
    CTkToplevel,
    CTkFrame,
    CTkLabel,
    CTkEntry,
    BooleanVar,
    CTkCheckBox,
    CTkButton,
)
from tkinter import messagebox
from utils.key_shortcut import key_shortcut

class UserDialog(CTkToplevel):
    def __init__(self, parent, users_db, callback, user=None):
        super().__init__(parent)

        self.users_db = users_db
        self.callback = callback
        self.user = user  # None للإضافة، موجود للتعديل

        self.title("إضافة مستخدم جديد" if not user else "تعديل المستخدم")
        self.geometry("600x650")
        self.resizable(False, False)

        # جعل النافذة في المقدمة
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        key_shortcut(self, "<Return>", self.save_user)

        if user:
            self.load_user_data()

    def setup_ui(self):
        """إعداد واجهة النافذة"""
        # الإطار الرئيسي
        main_frame = CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # عنوان
        title_label = CTkLabel(
            main_frame,
            text="👤 "
            + ("إضافة مستخدم جديد" if not self.user else "تعديل بيانات المستخدم"),
            font=("Cairo", 25, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # إطار بيانات المستخدم
        data_frame = CTkFrame(main_frame)
        data_frame.pack(fill="x", padx=10, pady=10)

        # اسم المستخدم
        username_label = CTkLabel(
            data_frame, text="اسم المستخدم:", anchor="e", font=("Cairo", 14)
        )
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = CTkEntry(
            data_frame, width=300, height=35, font=("Cairo", 13)
        )
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # كلمة المرور
        if not self.user:
            # مستخدم جديد
            password_label = CTkLabel(
                data_frame, text="كلمة المرور:", anchor="e", font=("Cairo", 14)
            )
            password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

            self.password_entry = CTkEntry(
                data_frame, width=300, height=35, show="*", font=("Cairo", 13)
            )
            self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

            confirm_password_label = CTkLabel(
                data_frame, text="تأكيد كلمة المرور:", anchor="e", font=("Cairo", 14)
            )
            confirm_password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

            self.confirm_password_entry = CTkEntry(
                data_frame, width=300, height=35, show="*", font=("Cairo", 13)
            )
            self.confirm_password_entry.grid(
                row=2, column=1, padx=10, pady=10, sticky="ew"
            )

        else:
            # تعديل المستخدم
            old_pass_label = CTkLabel(
                data_frame, text="كلمة المرور القديمة:", anchor="e", font=("Cairo", 14)
            )
            old_pass_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

            self.old_password_entry = CTkEntry(
                data_frame, width=300, height=35, show="*", font=("Cairo", 13)
            )
            self.old_password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

            new_pass_label = CTkLabel(
                data_frame, text="كلمة المرور الجديدة:", anchor="e", font=("Cairo", 14)
            )
            new_pass_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

            self.new_password_entry = CTkEntry(
                data_frame, width=300, height=35, show="*", font=("Cairo", 13)
            )
            self.new_password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # إطار الصلاحيات
        self.setup_role_section(main_frame)
        # أزرار التحكم
        buttons_frame = CTkFrame(main_frame)
        buttons_frame.pack(fill="x", padx=10, pady=20)

        save_btn = CTkButton(
            buttons_frame,
            text="💾 حفظ",
            command=self.save_user,
            width=150,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Cairo", 14, "bold"),
        )
        save_btn.pack(side="right", padx=5, pady=10)

        cancel_btn = CTkButton(
            buttons_frame,
            text="❌ إلغاء",
            command=self.destroy,
            width=150,
            height=40,
            fg_color="#c62828",
            hover_color="#8e0000",
            font=("Cairo", 14, "bold"),
        )
        cancel_btn.pack(side="right", padx=5, pady=10)

        # تكوين تمدد الأعمدة
        data_frame.columnconfigure(1, weight=1)

    def setup_role_section(self, parent):
        self.roles_vars = {}  # قائمة الصلاحيات مع Checkboxes
        # لو المستخدم موجود ومحدد كمدير مثلا، لا نعرض قسم الصلاحيات
        if self.user:
            roles_str = self.user[2]
            if roles_str == "all":  # المدير
                return  # نخلي الدالة ترجع بدون إنشاء الواجهة

        # إنشاء الإطار كما كان
        roles_frame = CTkFrame(parent)
        roles_frame.pack(fill="both", expand=True, padx=10, pady=10)

        roles_label = CTkLabel(
            roles_frame,
            text="🔑 الصلاحيات (اختر واحداً على الأقل):",
            font=("Cairo", 16, "bold"),
        )
        roles_label.pack(pady=10)

        # إنشاء إطار للـ Grid
        grid_frame = CTkFrame(roles_frame)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        roles_list = [
            ("cashier_interface", "واجهة الكاشير"),
            ("products_management", "إدارة المنتجات"),
            ("inventory_management", "إدارة المخزون"),
            ("users_management", "إدارة المستخدمين"),
            ("reports_view", "رؤية التقارير"),
            ("customers_management", "إدارة العملاء"),
            ("invoices_management", "إدارة الفواتير"),
            ("settings_edit", "تعديل الإعدادات"),
            ("suppliers_management", "إدارة الموردين"),
            ("purchase_invoices", "إنشاء فواتير الشراء"),
            ("stock_movements_view", "رؤية حركة المخزون"),
            ("edit_price_in_invoice", "تعديل السعر في الفاتورة"),
        ]

        for i, (role_key, role_name) in enumerate(roles_list):
            row = i // 3
            col = i % 3

            var = BooleanVar()
            self.roles_vars[role_key] = var

            checkbox = CTkCheckBox(
                grid_frame,
                text=role_name,
                variable=var,
                onvalue=True,
                offvalue=False,
                font=("Cairo", 13),
                checkbox_height=20,
                checkbox_width=20,
            )
            checkbox.grid(row=row, column=col, padx=15, pady=8, sticky="e")

    def load_user_data(self):
        """تحميل بيانات المستخدم للتعديل"""
        if not self.user:
            return

        _, username, roles_str, _, _, _ = self.user

        # تعيين اسم المستخدم
        self.username_entry.insert(0, username)

        if self.roles_vars:
            roles_list = roles_str.split(",") if roles_str else []
            for role in roles_list:
                if role in self.roles_vars:
                    self.roles_vars[role].set(True)

    def save_user(self):
        """حفظ المستخدم"""
        # التحقق من اسم المستخدم
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("خطأ", "اسم المستخدم مطلوب")
            return

        # الحصول على الصلاحيات المحددة
        if self.user and self.user[4] == 1:  # إذا كان المستخدم admin
            selected_roles = ["all"]
        else:
            selected_roles = [
                role for role, var in self.roles_vars.items() if var.get()
            ]

        # التحقق من اختيار صلاحية واحدة على الأقل
        if not selected_roles:
            messagebox.showerror("خطأ", "يجب اختيار صلاحية واحدة على الأقل")
            return

        # إذا كان مستخدم جديد
        if not self.user:
            # التحقق من كلمة المرور
            password = self.password_entry.get()
            confirm_password = self.confirm_password_entry.get()

            if not password:
                messagebox.showerror("خطأ", "كلمة المرور مطلوبة")
                return

            if password != confirm_password:
                messagebox.showerror("خطأ", "كلمة المرور غير متطابقة")
                return

            try:
                self.users_db.add_user(username, password, selected_roles)
                messagebox.showinfo("نجاح", "تم إضافة المستخدم بنجاح")
                self.callback()
                self.destroy()
            except ValueError as e:
                messagebox.showerror("خطأ", str(e))
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")

        # تعديل مستخدم
        else:
            try:
                old_password = self.old_password_entry.get().strip()
                new_password = self.new_password_entry.get().strip()

                password_to_update = None

                # لو المستخدم يريد تغيير كلمة المرور
                if old_password or new_password:

                    if not old_password or not new_password:
                        messagebox.showerror(
                            "خطأ", "يجب إدخال كلمة المرور القديمة والجديدة"
                        )
                        return

                    # التحقق من كلمة المرور القديمة
                    if not self.users_db.verify_password(self.user[0], old_password):
                        messagebox.showerror("خطأ", "كلمة المرور القديمة غير صحيحة")
                        return

                    password_to_update = new_password

                self.users_db.update_user(
                    self.user[0], username, selected_roles, password=password_to_update
                )

                messagebox.showinfo("نجاح", "تم تحديث المستخدم بنجاح")
                self.callback()
                self.destroy()

            except ValueError as e:
                messagebox.showerror("خطأ", str(e))
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
