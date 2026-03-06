import sqlite3
from typing import List, Tuple, Optional
import hashlib


class UsersModel:
    def __init__(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
        self.cur = cursor
        self.con = connection
        self.create_table()
        self.create_default_admin()
        self.create_default_cashier()

    def create_table(self):
        """إنشاء جدول المستخدمين إذا لم يكن موجوداً"""
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                roles TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT 0,
                is_cashier BOOLEAN DEFAULT 0
            )
        """
        )
        self.con.commit()

    def create_default_admin(self):
        """إنشاء مستخدم مدير افتراضي إذا لم يكن موجوداً"""
        self.cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        if self.cur.fetchone()[0] == 0:
            # تشفير كلمة المرور الافتراضية
            hashed_password = self.hash_password("123456")

            # جميع الصلاحيات للمدير
            all_roles = "all"

            self.cur.execute(
                """
                INSERT INTO users (username, password, roles, is_admin, is_cashier)
                VALUES (?, ?, ?, ?, ?)
            """,
                ("admin", hashed_password, all_roles, 1, 0),
            )
            self.con.commit()

    def create_default_cashier(self):
        """إنشاء مستخدم كاشير افتراضي إذا لم يكن موجوداً"""
        self.cur.execute("SELECT id FROM users WHERE username = 'cashier'")
        if not self.cur.fetchone():

            hashed_password = self.hash_password("123456")
            cashier_roles = "cashier_interface,invoices_management"

            self.cur.execute(
                """
                INSERT INTO users (username, password, roles, is_admin, is_cashier)
                VALUES (?, ?, ?, ?, ?)
            """,
                ("cashier", hashed_password, cashier_roles, 0, 1),
            )

            self.con.commit()

    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username: str, password: str, roles: List[str]) -> int:
        """إضافة مستخدم جديد"""
        try:
            # التحقق من الصلاحيات
            if "admin" in roles:
                roles_list = ["all"]
                is_admin = 1
                is_cashier = 1 if "cashier" in roles else 0
            else:
                roles_list = roles
                is_admin = 0
                is_cashier = 1 if "cashier" in roles else 0

            roles_str = ",".join(roles_list)
            hashed_password = self.hash_password(password)

            self.cur.execute(
                """
                INSERT INTO users (username, password, roles, is_admin, is_cashier)
                VALUES (?, ?, ?, ?, ?)
            """,
                (username, hashed_password, roles_str, is_admin, is_cashier),
            )
            self.con.commit()
            return self.cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("اسم المستخدم موجود بالفعل")

    def get_all_users(self) -> List[Tuple]:
        """الحصول على جميع المستخدمين"""
        self.cur.execute("SELECT * FROM users ORDER BY id")
        return self.cur.fetchall()

    def get_user_by_id(self, user_id: int) -> Optional[Tuple]:
        """الحصول على مستخدم بواسطة المعرف"""
        self.cur.execute(
            """
            SELECT id, username, roles, created_at, is_admin, is_cashier 
            FROM users WHERE id = ?
        """,
            (user_id,),
        )
        return self.cur.fetchone()

    def update_user(
        self,
        user_id: int,
        username: str,
        roles: List[str],
        password: Optional[str] = None,
    ):
        """تحديث بيانات المستخدم"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("المستخدم غير موجود")

        # منع تعديل المدير الرئيسي
        # لو المستخدم admin نخلي صلاحياته ثابتة
        if user[4] == 1:
            roles_list = ["all"]
        else:
            if "admin" in roles:
                roles_list = ["all"]
            else:
                roles_list = roles

        # منع تعديل اسم المستخدم للمدير والكاشير الافتراضيين
        if user[1] in ["admin", "cashier"] and username != user[1]:
            raise ValueError(f"لا يمكن تغيير اسم المستخدم لـ {user[1]} الافتراضي")

        try:
            # التحقق من الصلاحيات
            if "admin" in roles:
                roles_list = ["all"]
            else:
                roles_list = roles

            roles_str = ",".join(roles_list)

            # الحفاظ على القيم الأصلية لو كان المستخدم admin أو cashier
            is_admin = user[4]
            is_cashier = user[5]

            # لو المستخدم ليس admin ولا cashier يمكن تعديلهم
            if not user[4]:
                is_admin = 1 if "admin" in roles else 0

            if not user[5]:
                is_cashier = 1 if "cashier" in roles else 0

            roles_str = ",".join(roles_list)

            if password:
                hashed_password = self.hash_password(password)
                self.cur.execute(
                    """
                    UPDATE users 
                    SET username = ?, password = ?, roles = ?, is_admin = ?, is_cashier = ?
                    WHERE id = ?
                """,
                    (
                        username,
                        hashed_password,
                        roles_str,
                        is_admin,
                        is_cashier,
                        user_id,
                    ),
                )
            else:
                self.cur.execute(
                    """
                    UPDATE users 
                    SET username = ?, roles = ?, is_admin = ?, is_cashier = ?
                    WHERE id = ?
                """,
                    (username, roles_str, is_admin, is_cashier, user_id),
                )

            self.con.commit()
        except sqlite3.IntegrityError:
            raise ValueError("اسم المستخدم موجود بالفعل")

    def delete_user(self, user_id: int):
        """حذف مستخدم"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("المستخدم غير موجود")

        # منع حذف المدير الرئيسي والكاشير الافتراضي
        if user[4] == 1:
            raise ValueError("لا يمكن حذف مستخدم المدير الرئيسي")

        if user[1] == "cashier" and user[5] == 1:
            raise ValueError("لا يمكن حذف مستخدم الكاشير الافتراضي")

        self.cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.con.commit()

    def verify_login(self, username: str, password: str) -> Optional[Tuple]:
        """التحقق من صحة تسجيل الدخول"""
        hashed_password = self.hash_password(password)
        self.cur.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, hashed_password),
        )
        return self.cur.fetchone()

    def verify_password(self, user_id: int, password: str) -> bool:
        """التحقق من كلمة المرور القديمة"""
        hashed_password = self.hash_password(password)

        self.cur.execute(
            "SELECT id FROM users WHERE id = ? AND password = ?",
            (user_id, hashed_password),
        )

        return self.cur.fetchone() is not None

    def get_user_roles(self, user_id: int) -> List[str]:
        """الحصول على صلاحيات المستخدم"""
        user = self.get_user_by_id(user_id)
        if user:
            roles_str = user[2]
            if roles_str == "all":
                return ["all"]
            return roles_str.split(",") if roles_str else []
        return []

    def check_permission(self, user_id: int, permission: str) -> bool:
        """التحقق من صلاحية محددة للمستخدم"""
        roles = self.get_user_roles(user_id)
        return "all" in roles or permission in roles
