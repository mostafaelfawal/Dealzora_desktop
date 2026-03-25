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


class AuthView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.show_password = False

        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.root.title("Dealzora | تسجيل الدخول")

        self.main_frame = CTkFrame(self.root, fg_color="#1a1a1a", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

    def create_widgets(self):
        # ====== Glass Frame ======
        self.glass_frame = CTkFrame(
            self.main_frame,
            fg_color="#2d2d2d",
            corner_radius=30,
            height=550,
            border_width=2,
            border_color="#3d3d3d",
        )
        self.glass_frame.place(relx=0.5, rely=0.5, relwidth=0.4, anchor="center")

        # ====== Icon ======
        icon_frame = CTkFrame(self.glass_frame, fg_color="transparent")
        icon_frame.pack(pady=(40, 20))

        CTkLabel(
            icon_frame,
            image=image("assets/icon.png", (100, 100)),
            text="",
        ).pack()

        # ====== Title ======
        CTkLabel(
            self.glass_frame,
            text="Dealzora",
            font=("Cairo", 40, "bold"),
            text_color="#ffffff",
        ).pack()

        CTkLabel(
            self.glass_frame,
            text="النسخه الأساسية",
            font=("Cairo", 16),
            text_color="#808080",
        ).pack(pady=(0, 15))

        # ====== Separator ======
        CTkFrame(
            self.glass_frame, height=2, width=200, fg_color="#3d3d3d"
        ).pack(pady=(0, 15))

        # ====== Password ======
        password_frame = CTkFrame(self.glass_frame, fg_color="transparent")
        password_frame.pack(pady=10, padx=40, fill="x")

        CTkLabel(
            password_frame,
            text="🔒",
            font=("Segoe UI", 20),
            text_color="#808080",
        ).pack(side="left", padx=(0, 10))

        self.password_entry = CTkEntry(
            password_frame,
            placeholder_text="كلمة المرور",
            show="•",
            height=45,
            font=("Cairo", 14),
            border_width=2,
            text_color="#ffffff",
            border_color="#3d3d3d",
            fg_color="#262626",
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.show_btn = CTkButton(
            password_frame,
            text="إظهار",
            font=("Cairo", 12),
            width=60,
            command=self.toggle_password,
        )
        self.show_btn.pack(side="right", padx=(10, 0))

        # ====== Role ======
        role_frame = CTkFrame(self.glass_frame, fg_color="transparent")
        role_frame.pack(pady=20, padx=40, fill="x")

        CTkLabel(
            role_frame,
            text="👤",
            font=("Segoe UI", 20),
            text_color="#808080",
        ).pack(side="left", padx=(0, 10))

        self.role_var = StringVar()
        self.role_menu = CTkOptionMenu(
            role_frame,
            variable=self.role_var,
            height=45,
            font=("Cairo", 14, "bold"),
            dropdown_font=("Cairo", 14),
        )
        self.role_menu.pack(side="left", fill="x", expand=True)

        # ====== Login Button ======
        CTkButton(
            self.glass_frame,
            text="تسجيل الدخول",
            font=("Cairo", 16, "bold"),
            height=50,
            corner_radius=25,
            fg_color="#4a90e2",
            hover_color="#357abd",
            command=self.controller.login,
        ).pack(pady=30)

        # ====== Shortcuts ======
        key_shortcut(self.root, "<Return>", self.controller.login)

        self.load_users()
        self.password_entry.focus()

    # ====== Logic ======
    def toggle_password(self):
        self.show_password = not self.show_password
        self.password_entry.configure(show="" if self.show_password else "•")
        self.show_btn.configure(text="إخفاء" if self.show_password else "إظهار")

    def load_users(self):
        users = self.controller.get_users_display()
        self.role_menu.configure(values=users)
        self.role_var.set(users[0])

    def get_password(self):
        return self.password_entry.get()

    def get_role(self):
        return self.role_var.get()

    def highlight_password(self, success):
        self.password_entry.configure(border_color="#33ff00" if success else "#e74c3c")
        self.password_entry.focus()

    def show_error(self, title, msg):
        from tkinter import messagebox
        self.highlight_password(success=False)
        messagebox.showerror(title, msg)
    
    def show_success(self, msg):
        from tkinter import messagebox
        self.highlight_password(success=True)
        messagebox.showinfo("نجاح", msg)