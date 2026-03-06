from tkinter import messagebox
from customtkinter import CTkFrame, CTkButton, CTkEntry, CTkLabel

from utils.key_shortcut import key_shortcut
from utils.image import image
from components.TreeView import TreeView
from components.UserDialog import UserDialog


class UsersManagement:
    def __init__(self, parent, users_db):
        self.parent = parent
        self.users_db = users_db
        CTkLabel(
            self.parent,
            text="ادارة المستخدمين",
            image=image("assets/مستخدمين.png", (40, 40)),
            font=("Cairo", 36, "bold"),
            compound="right",
            text_color="#2b7de9",
        ).pack()

        # إطارات رئيسية
        self.setup_ui()
        self.load_users()
        self.setup_keyboard_shortcuts()

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # الإطار الرئيسي
        self.main_frame = CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # إطار شريط الأدوات
        self.toolbar = CTkFrame(self.main_frame, height=50)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        self.toolbar.pack_propagate(False)

        # أزرار الإجراءات
        self.add_btn = CTkButton(
            self.toolbar,
            text="إضافة مستخدم",
            command=self.open_add_user_dialog,
            image=image("assets/اضافة.png", (20, 20)),
            width=150,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Cairo", 14),
        )
        self.add_btn.pack(side="right", padx=5)

        self.edit_btn = CTkButton(
            self.toolbar,
            text="تعديل",
            command=self.open_edit_user_dialog,
            image=image("assets/تعديل.png", (20, 20)),
            width=100,
            height=35,
            fg_color="#1565c0",
            hover_color="#0d47a1",
            font=("Cairo", 14),
        )
        self.edit_btn.pack(side="right", padx=5)

        self.delete_btn = CTkButton(
            self.toolbar,
            text="حذف",
            command=self.delete_user,
            image=image("assets/حذف.png", (20, 20)),
            width=100,
            height=35,
            fg_color="#c62828",
            hover_color="#8e0000",
            font=("Cairo", 14),
        )
        self.delete_btn.pack(side="right", padx=5)

        self.refresh_btn = CTkButton(
            self.toolbar,
            text="🔄 تحديث",
            command=self.load_users,
            width=100,
            height=35,
            fg_color="#546e7a",
            hover_color="#29434e",
            font=("Cairo", 14),
        )
        self.refresh_btn.pack(side="right", padx=5)

        # إطار البحث
        self.search_frame = CTkFrame(self.toolbar)
        self.search_frame.pack(side="left", padx=5)

        self.search_entry = CTkEntry(
            self.search_frame,
            placeholder_text="🔍 بحث عن مستخدم...",
            width=200,
            height=35,
            font=("Cairo", 13),
        )
        self.search_entry.pack(side="right", padx=5)
        key_shortcut(self.search_entry, "<KeyRelease>", self.search_users)

        # TreeView للمستخدمين
        self.setup_treeview()

    def setup_treeview(self):
        """إعداد Treeview لعرض المستخدمين"""
        # إطار Treeview
        self.tree_frame = CTkFrame(self.main_frame)
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # أعمدة Treeview
        cols = ("ID", "اسم المستخدم", "الصلاحيات", "تاريخ الإنشاء", "نوع المستخدم")
        widths = (30, 150, 250, 150, 120)

        # إنشاء Treeview مخصص
        self.tree_view = TreeView(self.tree_frame, cols, widths, [])

        # ربط الأحداث
        key_shortcut(
            self.tree_view.tree, ["<Double-1>", "<Return>"], self.open_edit_user_dialog
        )
        key_shortcut(self.tree_view.tree, "<Delete>", self.delete_user)

    def setup_keyboard_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح"""
        key_shortcut(self.tree_view.tree, "<F2>", self.open_edit_user_dialog)
        key_shortcut(self.tree_view.tree, "<Insert>", self.open_add_user_dialog)

    def load_users(self):
        """تحميل وعرض المستخدمين"""
        # مسح البيانات الحالية
        for item in self.tree_view.tree.get_children():
            self.tree_view.tree.delete(item)

        # الحصول على المستخدمين
        users = self.users_db.get_all_users()

        # عرض المستخدمين
        for user in users:
            user_id, username, _, roles_str, created_at, is_admin, is_cashier = user

            # تنسيق الصلاحيات
            if roles_str == "all":
                roles_display = "مدير النظام (جميع الصلاحيات)"
            else:
                roles_list = roles_str.split(",") if roles_str else []
                roles_display = self.format_roles_display(roles_list)

            # نوع المستخدم
            user_type = "مدير" if is_admin else "كاشير" if is_cashier else "مستخدم"

            # تحديد لون الصف
            tags = ()
            if is_admin:
                tags = ("success",)  # أخضر للمدير
            elif is_cashier:
                tags = ("warning",)  # برتقالي للكاشير

            # إدراج الصف
            self.tree_view.tree.insert(
                "",
                "end",
                values=(user_id, username, roles_display, created_at, user_type),
                tags=tags,
            )

    def format_roles_display(self, roles) -> str:
        """تنسيق عرض الصلاحيات"""
        roles_dict = {
            "cashier_interface": "واجهة الكاشير",
            "products_management": "إدارة المنتجات",
            "inventory_management": "إدارة المخزون",
            "reports_view": "رؤية التقارير",
            "customers_management": "إدارة العملاء",
            "invoices_management": "إدارة الفواتير",
            "settings_edit": "تعديل الإعدادات",
            "suppliers_management": "إدارة الموردين",
            "purchase_invoices": "إنشاء فواتير الشراء",
            "stock_movements_view": "رؤية حركة المخزون",
        }

        display_names = [roles_dict.get(r, r) for r in roles if r in roles_dict]
        return "، ".join(display_names) if display_names else "لا توجد صلاحيات"

    def search_users(self, event=None):
        """البحث في المستخدمين"""
        search_term = self.search_entry.get().lower()

        for item in self.tree_view.tree.get_children():
            values = self.tree_view.tree.item(item)["values"]
            if len(values) >= 2:
                username = str(values[1]).lower()
                if search_term in username:
                    self.tree_view.tree.selection_set(item)
                    self.tree_view.tree.see(item)
                    break

    def get_selected_user_id(self):
        """الحصول على معرف المستخدم المحدد"""
        selection = self.tree_view.tree.selection()
        if not selection:
            messagebox.showwarning("تحذير", "الرجاء تحديد مستخدم أولاً")
            return None

        item = self.tree_view.tree.item(selection[0])
        return int(item["values"][0])

    def open_add_user_dialog(self):
        """فتح نافذة إضافة مستخدم"""
        UserDialog(self.parent, self.users_db, self.on_user_added)

    def open_edit_user_dialog(self):
        """فتح نافذة تعديل مستخدم"""
        user_id = self.get_selected_user_id()
        if user_id:
            user = self.users_db.get_user_by_id(user_id)
            if user:
                UserDialog(self.parent, self.users_db, self.on_user_updated, user)

    def delete_user(self):
        """حذف المستخدم المحدد"""
        user_id = self.get_selected_user_id()
        if not user_id:
            return

        user = self.users_db.get_user_by_id(user_id)
        if not user:
            return

        # التحقق من عدم حذف المدير
        if user[4] == 1:
            messagebox.showerror("خطأ", "لا يمكن حذف مستخدم المدير الرئيسي")
            return

        # تأكيد الحذف
        if messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف المستخدم {user[1]}؟"):
            try:
                self.users_db.delete_user(user_id)
                self.load_users()
                messagebox.showinfo("نجاح", "تم حذف المستخدم بنجاح")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حذف المستخدم: {str(e)}")

    def on_user_added(self):
        """عند إضافة مستخدم جديد"""
        self.load_users()

    def on_user_updated(self):
        """عند تحديث مستخدم"""
        self.load_users()
