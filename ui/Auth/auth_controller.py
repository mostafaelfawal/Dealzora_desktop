class AuthController:
    def __init__(self, users_db, on_success, view):
        self.users_db = users_db
        self.on_success = on_success
        self.view = view

    def login(self):
        password = self.view.get_password()
        role = self.view.get_role()

        if not password:
            self.view.show_error("❌ خطأ", "الرجاء إدخال كلمة المرور")
            return

        user_name = role.split(" ~ ")[0]
        user = self.users_db.verify_login(user_name, password)

        if user:
            uid = user[0]
            self.view.show_success(f"✅ مرحباً بك - {user_name}")
            self.on_success(uid)
        else:
            self.view.show_error("❌ خطأ", "كلمة المرور غير صحيحة")

    def get_users_display(self):
        users = []
        for u in self.users_db.get_all_users():
            roles = u[3].split(",")
            if len(roles) > 2:
                roles = f"{', '.join(roles[:2])} +اضافية{len(roles)-2}"
            else:
                roles = ", ".join(roles)

            users.append(f"{u[1]} ~ {roles}")

        return users