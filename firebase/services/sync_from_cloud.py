# ========= Databases =========
from models.settings import SettingsModel

# ============ GUI ============
from customtkinter import (
    CTkButton,
    CTkScrollableFrame,
    CTkToplevel,
    CTkFrame,
    CTkLabel,
    CTkProgressBar,
    CTkFont,
)
from tkinter import messagebox
from utils.image import image
from firebase.firebase_config import db
import uuid
import threading
import sqlite3

# ─────────────────────────────────────────────
#  Color Palette & Theme
# ─────────────────────────────────────────────
COLORS = {
    "bg_dark":       "#0D0F14",
    "bg_card":       "#13161E",
    "bg_row":        "#1A1D28",
    "bg_row_hover":  "#1F2333",
    "accent":        "#4F8EF7",
    "accent_glow":   "#2D5FCC",
    "success":       "#22D3A0",
    "success_dim":   "#0F6B50",
    "warning":       "#F7C948",
    "error":         "#F75A4F",
    "text_primary":  "#E8ECF4",
    "text_secondary":"#7A82A0",
    "text_dim":      "#5E6786",
    "border":        "#242840",
    "progress_bg":   "#1E2235",
}

# ─────────────────────────────────────────────
#  Metadata for every collection
# ─────────────────────────────────────────────
TABLE_META = [
    {"key": "products",        "label": "المنتجات",        "icon": "📦"},
    {"key": "customers",       "label": "العملاء",          "icon": "👥"},
    {"key": "expenses",        "label": "المصاريف",         "icon": "💸"},
    {"key": "sale_items",      "label": "منتجات الفواتير",  "icon": "🧾"},
    {"key": "sales",           "label": "الفواتير",         "icon": "🗂️"},
    {"key": "stock_movements", "label": "حركات المخزون",    "icon": "📊"},
    {"key": "suppliers",       "label": "الموردين",         "icon": "🏭"},
    {"key": "users",           "label": "المستخدمين",       "icon": "👤"},
    {"key": "categories",      "label": "الفئات",           "icon": "🏷️"},
    {"key": "units",           "label": "الوحدات",          "icon": "📐"},
]

# ─────────────────────────────────────────────
#  INSERT helpers
# ─────────────────────────────────────────────
def _insert_record(table: str, record: dict, cur, con):
    try:
        if table == "products":
            cur.execute(
                """INSERT OR IGNORE INTO products
                   (id,name,barcode,buy_price,sell_price,quantity,
                    category_id,image_path,low_stock,supplier_id,created_at,unit_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    record.get("id"),           record.get("name"),
                    record.get("barcode"),       record.get("buy_price", 0),
                    record.get("sell_price", 0), record.get("quantity", 0),
                    record.get("category_id"),   record.get("image_path"),
                    record.get("low_stock", 5),  record.get("supplier_id"),
                    record.get("created_at"),    record.get("unit_id"),
                ),
            )
        elif table == "categories":
            cur.execute(
                "INSERT OR IGNORE INTO category (id, name) VALUES (?, ?)",
                (record.get("id"), record.get("name")),
            )
        elif table == "units":
            cur.execute(
                """INSERT OR IGNORE INTO units
                   (id, name, small_unit_name, conversion_factor)
                   VALUES (?, ?, ?, ?)""",
                (
                    record.get("id"),             record.get("name"),
                    record.get("small_unit_name"), record.get("conversion_factor"),
                ),
            )
        elif table == "customers":
            cur.execute(
                """INSERT OR IGNORE INTO customers (id, name, phone, debt)
                   VALUES (?, ?, ?, ?)""",
                (
                    record.get("id"),    record.get("name"),
                    record.get("phone"), record.get("debt", 0),
                ),
            )
        elif table == "expenses":
            cur.execute(
                """INSERT OR IGNORE INTO expenses
                   (id, date, type, beneficiary, amount, description, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.get("id"),        record.get("date"),
                    record.get("type"),      record.get("beneficiary"),
                    record.get("amount", 0), record.get("description", ""),
                    record.get("status", "مدفوع"),
                ),
            )
        elif table == "sale_items":
            cur.execute(
                """INSERT OR IGNORE INTO sale_items
                   (id, sale_id, product_id, quantity, price, total)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    record.get("id"),         record.get("sale_id"),
                    record.get("product_id"), record.get("quantity", 0),
                    record.get("price", 0),   record.get("total", 0),
                ),
            )
        elif table == "sales":
            cur.execute(
                """INSERT OR IGNORE INTO sales
                   (id, number, total, discount, tax, paid, change, customer_id, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.get("id"),        record.get("number"),
                    record.get("total", 0),  record.get("discount", 0),
                    record.get("tax", 0),    record.get("paid", 0),
                    record.get("change", 0), record.get("customer_id"),
                    record.get("date"),
                ),
            )
        elif table == "stock_movements":
            cur.execute(
                """INSERT OR IGNORE INTO stock_movements
                   (id, product_id, quantity, old_quantity, new_quantity,
                    movement_type, reference_id, reference_number, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.get("id"),             record.get("product_id"),
                    record.get("quantity", 0),    record.get("old_quantity", 0),
                    record.get("new_quantity", 0), record.get("movement_type"),
                    record.get("reference_id"),   record.get("reference_number"),
                    record.get("date"),
                ),
            )
        elif table == "suppliers":
            cur.execute(
                "INSERT OR IGNORE INTO suppliers (id, name, phone) VALUES (?, ?, ?)",
                (record.get("id"), record.get("name"), record.get("phone")),
            )
        elif table == "users":
            cur.execute(
                """INSERT OR IGNORE INTO users
                   (id, username, password, roles, created_at, is_admin, is_cashier)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.get("id"),         record.get("username"),
                    record.get("password"),   record.get("roles", ""),
                    record.get("created_at"), record.get("is_admin", 0),
                    record.get("is_cashier", 0),
                ),
            )

        con.commit()

    except Exception as e:
        print(f"[ERROR] {table} → {e}")


# ─────────────────────────────────────────────
#  TableRow Widget
# ─────────────────────────────────────────────
class TableRow(CTkFrame):
    def __init__(self, master, icon, label, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_row"], corner_radius=10, **kwargs)
        self.configure(border_width=1, border_color=COLORS["border"])

        left = CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=(14, 6), pady=10)

        CTkLabel(
            left, text=icon, font=CTkFont(size=18),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 8))
        CTkLabel(
            left, text=label,
            font=CTkFont(family="Cairo", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        self.status_label = CTkLabel(
            self, text="انتظار…",
            font=CTkFont(family="Cairo", size=11, weight="bold"),
            text_color=COLORS["text_dim"],
            width=110, anchor="e",
        )
        self.status_label.pack(side="right", padx=12)

        self.counter_label = CTkLabel(
            self, text="0 / 0",
            font=CTkFont(family="Cairo", size=11),
            text_color=COLORS["text_secondary"],
            width=80, anchor="e",
        )
        self.counter_label.pack(side="right", padx=4)

        self.bar = CTkProgressBar(
            self, height=8, corner_radius=4,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent"],
        )
        self.bar.set(0)
        self.bar.pack(side="right", padx=8, fill="x", expand=True)

    def set_syncing(self):
        self.bar.configure(progress_color=COLORS["accent"])
        self.bar.set(0)
        self.status_label.configure(text="⬇ جاري المزامنة", text_color=COLORS["warning"])
        self.counter_label.configure(text="0 / 0")

    def update_progress(self, done: int, total: int):
        ratio = done / total if total else 0
        self.bar.set(ratio)
        self.counter_label.configure(
            text=f"تم {done} / {total}",
            text_color=COLORS["text_secondary"],
        )
        if done == total and total > 0:
            self.bar.configure(progress_color=COLORS["success"])
            self.status_label.configure(text="✔ اكتمل", text_color=COLORS["success"])
        else:
            self.status_label.configure(
                text=f"{int(ratio * 100)}%", text_color=COLORS["accent"]
            )

    def set_empty(self):
        self.bar.set(1)
        self.bar.configure(progress_color=COLORS["text_dim"])
        self.counter_label.configure(text="0 / 0")
        self.status_label.configure(text="لا توجد بيانات", text_color=COLORS["text_dim"])

    def set_error(self, msg: str = "خطأ"):
        self.bar.configure(progress_color=COLORS["error"])
        self.status_label.configure(text=f"✘ {msg}", text_color=COLORS["error"])


# ─────────────────────────────────────────────
#  Main Sync Dialog
# ─────────────────────────────────────────────
class SyncFromCloud(CTkToplevel):
    """
    نافذة مزامنة البيانات من Firebase إلى قاعدة البيانات المحلية.
    الاستخدام: SyncFromCloud(db_path)
    """

    CHUNK = 30  # عدد السجلات بين كل تحديث للـ UI

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.settings = SettingsModel()
        self.uid = self._get_user_id()

        self._total_items  = 0
        self._synced_items = 0
        self._lock         = threading.Lock()

        # ✅ Event لمزامنة الـ sync thread مع الـ main thread
        self._ui_ready = threading.Event()

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.title("مزامنة البيانات من السحابة")
        h = self.winfo_screenheight()
        self.geometry(f"800x{h-100}+200+0")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])

    def _get_user_id(self):
        uid = self.settings.get_setting("user_id")
        if not uid:
            uid = str(uuid.uuid4())
            self.settings.update_settings(user_id=uid)
        return uid

    # ── UI Build ────────────────────────────────
    def _build_ui(self):
        header = CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        CTkLabel(
            header,
            text="مزامنة البيانات من السحابة",
            image=image("assets/syncronization.png"),
            compound="left",
            font=CTkFont(family="Cairo", size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=24, pady=18)

        CTkLabel(
            header,
            text=f"معرّف: {self.uid[:18]}…",
            font=CTkFont(family="Cairo", size=10, weight="bold"),
            text_color=COLORS["text_dim"],
        ).pack(side="right", padx=20)

        CTkFrame(self, fg_color=COLORS["border"], height=1).pack(fill="x")

        container = CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(16, 8))

        self.rows: dict[str, TableRow] = {}
        for meta in TABLE_META:
            row = TableRow(container, icon=meta["icon"], label=meta["label"])
            row.pack(fill="x", pady=4)
            self.rows[meta["key"]] = row

        bottom = CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0)
        bottom.pack(fill="x", side="bottom")

        CTkFrame(bottom, fg_color=COLORS["border"], height=1).pack(fill="x")

        inner = CTkFrame(bottom, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=14)

        top_row = CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        CTkLabel(
            top_row, text="التقدم الكلي",
            font=CTkFont(family="Cairo", size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        self.overall_pct_label = CTkLabel(
            top_row, text="(0%)",
            font=CTkFont(family="Cairo", size=12, weight="bold"),
            text_color=COLORS["accent"],
        )
        self.overall_pct_label.pack(side="left", padx=6)

        self.overall_counter = CTkLabel(
            top_row, text="",
            font=CTkFont(family="Cairo", size=11, weight="bold"),
            text_color=COLORS["text_dim"],
        )
        self.overall_counter.pack(side="right")

        self.overall_bar = CTkProgressBar(
            inner, height=12, corner_radius=6,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent_glow"],
        )
        self.overall_bar.set(0)
        self.overall_bar.pack(fill="x", pady=(6, 0))

        CTkLabel(
            bottom,
            text="⚠  تأكد من اتصالك بالإنترنت قبل المزامنة",
            font=CTkFont(family="Cairo", size=11, weight="bold"),
            text_color=COLORS["text_dim"],
        ).pack(pady=(0, 12))

        self.sync_btn = CTkButton(
            bottom,
            text="بدء المزامنة",
            image=image("assets/upload.png"),
            compound="left",
            font=CTkFont(family="Cairo", size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_glow"],
            command=self._start_sync_thread,
        )
        self.sync_btn.pack(pady=(0, 12))

    # ────────────────────────────────────────────
    #  Sync Logic
    # ────────────────────────────────────────────
    def _start_sync_thread(self):
        self.sync_btn.configure(state="disabled", text="جاري المزامنة…")
        threading.Thread(target=self._sync_all, daemon=True).start()

    def _sync_all(self):
        """
        يعمل في sync thread.
        يستخدم threading.Event لضمان أن الـ UI يتحدث فعلاً
        قبل أن يكمل الـ thread — هذا يمنع مشكلة "يملأ كل الـ bars دفعة واحدة".
        """
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        try:
            # ── 1. جلب كل البيانات من Firebase أولاً ──
            cloud_data: dict[str, list[dict]] = {}
            for meta in TABLE_META:
                key = meta["key"]
                try:
                    docs = list(
                        db.collection("users")
                        .document(self.uid)
                        .collection(key)
                        .stream()
                    )
                    cloud_data[key] = [d.to_dict() for d in docs]
                except Exception as e:
                    print(f"[Firebase ERROR] {key} → {e}")
                    cloud_data[key] = []

            self._total_items = sum(len(v) for v in cloud_data.values())

            # ── 2. مزامنة جدول بجدول مع انتظار الـ UI ──
            for meta in TABLE_META:
                key     = meta["key"]
                records = cloud_data.get(key, [])

                # ✅ انتظر الـ UI يرسم "جاري المزامنة" قبل ما نبدأ الإدخال
                self._ui_ready.clear()
                self.after(0, lambda k=key: self._ui_set_syncing(k))
                self._ui_ready.wait(timeout=1.0)

                self._sync_table(key, records, cur, con)

        finally:
            con.close()

        self.after(0, self._on_complete)

    def _sync_table(self, table: str, records: list[dict], cur, con):
        total = len(records)

        if total == 0:
            self.after(0, lambda: self.rows[table].set_empty())
            return

        done = 0

        for record in records:
            _insert_record(table, record, cur, con)
            done += 1

            # ✅ كل CHUNK سجل: توقف وانتظر الـ UI يتحدث فعلاً
            if done % self.CHUNK == 0 or done == total:
                _done, _total = done, total
                self._ui_ready.clear()
                self.after(
                    0,
                    lambda k=table, d=_done, t=_total:
                        self._ui_update_progress(k, d, t),
                )
                self._ui_ready.wait(timeout=1.0)

        # تحديث الشريط الكلي بعد انتهاء الجدول بالكامل
        with self._lock:
            self._synced_items += total
            done_now  = self._synced_items
            total_now = self._total_items

        self._ui_ready.clear()
        self.after(
            0,
            lambda d=done_now, t=total_now: self._ui_refresh_overall(d, t),
        )
        self._ui_ready.wait(timeout=1.0)

    # ────────────────────────────────────────────
    #  UI callbacks — تعمل في الـ main thread فقط
    # ────────────────────────────────────────────
    def _ui_set_syncing(self, key: str):
        """يحدّث الـ row ثم يُطلق الـ sync thread ليكمل."""
        self.rows[key].set_syncing()
        self._ui_ready.set()

    def _ui_update_progress(self, key: str, done: int, total: int):
        """يحدّث progress bar الجدول ثم يُطلق الـ sync thread."""
        self.rows[key].update_progress(done, total)
        self._ui_ready.set() 

    def _ui_refresh_overall(self, done: int, total: int):
        """يحدّث الشريط الكلي ثم يُطلق الـ sync thread."""
        ratio = done / total if total else 0
        pct   = int(ratio * 100)
        self.overall_bar.set(ratio)
        self.overall_pct_label.configure(
            text=f"({pct}%)",
            text_color=COLORS["success"] if pct == 100 else COLORS["accent"],
        )
        self.overall_counter.configure(
            text=f"تمت مزامنة {done} عنصر من {total}"
        )
        self._ui_ready.set()  

    # ── Completion ─────────────────────────────
    def _on_complete(self):
        self.overall_bar.configure(progress_color=COLORS["success"])
        self.overall_pct_label.configure(
            text="(100%) ✔", text_color=COLORS["success"]
        )
        messagebox.showinfo(
            "تمت المزامنة",
            "تمت مزامنة جميع البيانات من السحابة إلى جهازك بنجاح ✅",
        )
        self.destroy()