from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkEntry,
    StringVar,
    CTkOptionMenu,
    CTkButton,
)
from utils.image import image
from utils.key_shortcut import key_shortcut
from tkinter import messagebox


class Auth:
    def __init__(self, root, on_success, users_db):
        self.root = root
        self.on_success = on_success
        self.users_db = users_db
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        """تجهيز إعدادات النافذة"""
        self.root.title("Dealzora | تسجيل الدخول")

        # إطار الخلفية الرئيسي مع تأثير تدرج
        self.main_frame = CTkFrame(self.root, fg_color="#1a1a1a", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

    def create_widgets(self):
        """إنشاء جميع عناصر الواجهة"""
        # حاوية مركزية مع تأثير زجاجي
        self.glass_frame = CTkFrame(
            self.main_frame,
            fg_color="#2d2d2d",
            bg_color="transparent",
            corner_radius=30,
            width=380,
            height=550,
            border_width=2,
            border_color="#3d3d3d",
        )
        self.glass_frame.place(relx=0.5, rely=0.5, anchor="center")

        # أيقونة التطبيق مع تأثير الظل
        self.icon_frame = CTkFrame(
            self.glass_frame, fg_color="transparent", width=120, height=120
        )
        self.icon_frame.pack(pady=(40, 20))

        self.icon_label = CTkLabel(
            self.icon_frame, image=image("assets/icon.png", (100, 100)), text=""
        )
        self.icon_label.pack()

        # اسم التطبيق مع تأثير متدرج
        self.title_label = CTkLabel(
            self.glass_frame,
            text="Dealzora",
            font=("Cairo", 40, "bold"),
            text_color="#ffffff",
        )
        self.title_label.pack()

        self.subtitle_label = CTkLabel(
            self.glass_frame,
            text="النسخه الأساسية",
            font=("Cairo", 16),
            text_color="#808080",
        )
        self.subtitle_label.pack(pady=(0, 15))

        # خط فاصل أنيق
        separator = CTkFrame(self.glass_frame, height=2, width=200, fg_color="#3d3d3d")
        separator.pack(pady=(0, 15))

        # حقل كلمة السر
        self.password_frame = CTkFrame(self.glass_frame, fg_color="transparent")
        self.password_frame.pack(pady=10, padx=40, fill="x")

        # أيقونة القفل
        lock_icon = CTkLabel(
            self.password_frame, text="🔒", font=("Segoe UI", 20), text_color="#808080"
        )
        lock_icon.pack(side="left", padx=(0, 10))

        self.password_entry = CTkEntry(
            self.password_frame,
            placeholder_text="كلمة المرور",
            show="•",
            width=250,
            height=45,
            font=("Cairo", 14),
            border_width=2,
            border_color="#3d3d3d",
            fg_color="#262626",
            placeholder_text_color="#808080",
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        # حقل الدور مع تصميم أنيق
        self.role_frame = CTkFrame(self.glass_frame, fg_color="transparent")
        self.role_frame.pack(pady=20, padx=40, fill="x")

        # أيقونة المستخدم
        user_icon = CTkLabel(
            self.role_frame, text="👤", font=("Segoe UI", 20), text_color="#808080"
        )
        user_icon.pack(side="left", padx=(0, 10))

        # قائمة الخيارات المنسدلة للدور
        self.role_var = StringVar(value="اختر الدور")
        self.role_menu = CTkOptionMenu(
            self.role_frame,
            variable=self.role_var,
            width=250,
            height=45,
            font=("Cairo", 14),
            dropdown_font=("Cairo", 14),
        )
        self.role_menu.pack(side="left", fill="x", expand=True)
        self.fill_users()  # وضع المستخدمين داخل Role_menu

        # زر تسجيل الدخول مع تأثيرات متقدمة
        self.login_btn = CTkButton(
            self.glass_frame,
            text="تسجيل الدخول",
            font=("Cairo", 16, "bold"),
            height=50,
            width=200,
            corner_radius=25,
            fg_color="#4a90e2",
            hover_color="#357abd",
            text_color="#ffffff",
            command=self.login,
        )
        self.login_btn.pack(pady=30)
        self.help = CTkLabel(
            self.glass_frame,
            text="مساعدة",
            font=("Cairo", 12),
            text_color="#808080",
            cursor="hand2",
        )
        self.help.pack(pady=10)
        key_shortcut(self.help, "<Button-1>", self.help_click)

        # ربط مفتاح Enter بتسجيل الدخول
        key_shortcut(self.root, "<Return>", self.login)

        # تعيين التركيز على حقل كلمة المرور
        self.password_entry.focus()

    def login(self):
        """وظيفة تسجيل الدخول"""
        password = self.password_entry.get()
        role = self.role_var.get()

        if not password:
            self.show_error("❌ خطأ", "الرجاء إدخال كلمة المرور")
            return

        if role == "اختر الدور":
            self.show_error("❌ خطأ", "الرجاء اختيار المستخدم")
            return

        user_name = role.split(" ~ ")[0]
        user = self.users_db.verify_login(user_name, password)
        if user:
            uid = user[0]
            self.show_success(f"✅ مرحباً بك - {user_name}")
            self.on_success(uid)
        else:
            self.show_error("❌ خطأ", "كلمة المرور غير صحيحة")

    def fill_users(self):
        users = []
        for u in self.users_db.get_all_users():
            roles = u[3]
            roles_list = roles.split(",")
            roles_count = len(roles_list)
            if roles_count > 2:
                roles = f"{', '.join(roles_list[:2])} +اضافية{roles_count-2}"
            users.append(f"{u[1]} ~ {roles}")
        self.role_menu.configure(values=users)

    def show_error(self, title, message):
        """عرض رسالة خطأ"""
        messagebox.showerror(title, message)

    def show_success(self, message):
        """عرض رسالة نجاح"""
        messagebox.showinfo("نجاح", message)

    def help_click(self):
        """معالج المساعدة"""
        help_text = """مرحباً بك في نظام Dealzora 1.0.0v

للاستفسار:
armostafa982@gmail.com 
او على الواتساب 1151083509+20"""
        messagebox.showinfo("مساعدة", help_text)
