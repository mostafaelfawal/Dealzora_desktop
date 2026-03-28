# ========= Databases =========
from models.products import ProductsModel
from models.customers import CustomersModel
from models.expenses import ExpensesModel
from models.sale_items import SaleItmesModel
from models.sales import SalesModel
from models.stock_movements import StockMovementsModel
from models.supplier import SupplierModel
from models.users import UsersModel
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

# ─────────────────────────────────────────────
#  Color Palette & Theme
# ─────────────────────────────────────────────
COLORS = {
    "bg_dark": "#0D0F14",
    "bg_card": "#13161E",
    "bg_row": "#1A1D28",
    "bg_row_hover": "#1F2333",
    "accent": "#4F8EF7",
    "accent_glow": "#2D5FCC",
    "success": "#22D3A0",
    "success_dim": "#0F6B50",
    "warning": "#F7C948",
    "text_primary": "#E8ECF4",
    "text_secondary": "#7A82A0",
    "text_dim": "#5E6786",
    "border": "#242840",
    "progress_bg": "#1E2235",
}

TABLE_META = [
    {"key": "products", "label": "المنتجات", "icon": "📦"},
    {"key": "customers", "label": "العملاء", "icon": "👥"},
    {"key": "expenses", "label": "المصاريف", "icon": "💸"},
    {"key": "sale_items", "label": "منتجات الفواتير", "icon": "🧾"},
    {"key": "sales", "label": "الفواتير", "icon": "🗂️"},
    {"key": "stock_movements", "label": "حركات المخزون", "icon": "📊"},
    {"key": "suppliers", "label": "الموردين", "icon": "🏭"},
    {"key": "users", "label": "المستخدمين", "icon": "👤"},
    {"key": "categories", "label": "الفئات", "icon": "🏷️"},
    {"key": "units", "label": "الوحدات", "icon": "📐"},
]

FIELD_MAPS = {
    "products": [
        "id",
        "name",
        "barcode",
        "buy_price",
        "sell_price",
        "quantity",
        "category_id",
        "image_path",
        "low_stock",
        "supplier_id",
        "created_at",
        "unit_id",
    ],
    "categories": ["id", "name"],
    "units": ["id", "name", "small_unit_name", "conversion_factor"],
    "customers": ["id", "name", "phone", "debt"],
    "expenses": ["id", "amount", "description", "created_at"],
    "sale_items": ["id", "sale_id", "product_id", "quantity", "price", "total"],
    "sales": [
        "id",
        "number",
        "total",
        "discount",
        "tax",
        "paid",
        "change",
        "customer_id",
        "date",
    ],
    "stock_movements": [
        "id",
        "product_id",
        "quantity",
        "old_quantity",
        "new_quantity",
        "movement_type",
        "reference_id",
        "reference_number",
        "date",
    ],
    "suppliers": ["id", "name", "phone"],
    "users": [
        "id",
        "username",
        "password",
        "roles",
        "created_at",
        "is_admin",
        "is_cashier",
    ],
}


# ─────────────────────────────────────────────
#  TableRow Widget
# ─────────────────────────────────────────────
class TableRow(CTkFrame):
    def __init__(self, master, icon, label, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_row"], corner_radius=10, **kwargs)

        self.configure(border_width=1, border_color=COLORS["border"])

        # Icon + Label
        left = CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=(14, 6), pady=10)

        CTkLabel(
            left, text=icon, font=CTkFont(size=18), text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 8))
        CTkLabel(
            left,
            text=label,
            font=CTkFont(family="Cairo", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # Status badge
        self.status_label = CTkLabel(
            self,
            text="انتظار…",
            font=CTkFont(family="Cairo", size=11, weight="bold"),
            text_color=COLORS["text_dim"],
            width=90,
            anchor="e",
        )
        self.status_label.pack(side="right", padx=12)

        # Counter label
        self.counter_label = CTkLabel(
            self,
            text="0 / 0",
            font=CTkFont(family="Cairo", size=11),
            text_color=COLORS["text_secondary"],
            width=70,
            anchor="e",
        )
        self.counter_label.pack(side="right", padx=4)

        # Progress bar
        self.bar = CTkProgressBar(
            self,
            height=8,
            corner_radius=4,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent"],
        )
        self.bar.set(0)
        self.bar.pack(side="right", padx=8, fill="x", expand=True)

    def update_progress(self, done, total):
        ratio = done / total if total else 0
        self.bar.set(ratio)
        self.counter_label.configure(
            text=f"تم رفع {done} / {total}", text_color=COLORS["text_secondary"]
        )
        if done == total and total > 0:
            self.bar.configure(progress_color=COLORS["success"])
            self.status_label.configure(text="✔ اكتمل", text_color=COLORS["success"])
        else:
            self.status_label.configure(
                text=f"{int(ratio*100)}%", text_color=COLORS["accent"]
            )

    def set_uploading(self):
        self.status_label.configure(text="⬆ جاري الرفع", text_color=COLORS["warning"])

    def set_skipped(self, done, total):
        self.bar.configure(progress_color=COLORS["success"])
        self.bar.set(1)
        self.counter_label.configure(
            text=f"تم رفع {done} / {total}", text_color=COLORS["text_secondary"]
        )
        self.status_label.configure(text="✔ اكتمل", text_color=COLORS["success"])


# ─────────────────────────────────────────────
#  Main Upload Dialog
# ─────────────────────────────────────────────
class UploadToCloud(CTkToplevel):
    def __init__(self, cur, con):
        super().__init__()
        self.cur = cur
        self.con = con
        self.settings = SettingsModel()
        self.uid = self._get_user_id()

        self._total_items = 0
        self._uploaded_items = 0
        self._lock = threading.Lock()

        self._setup_window()
        self._setup_databases()
        self._load_all_data()
        self._build_ui()

    # ── Window ──────────────────────────────
    def _setup_window(self):
        self.title("رفع البيانات إلى السحابة")
        h = self.winfo_screenheight()
        self.geometry(f"800x{h-100}+200+0")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])

    # ── DB Setup ────────────────────────────
    def _setup_databases(self):
        self.dbs = {
            "products": ProductsModel(self.cur, self.con),
            "customers": CustomersModel(self.cur, self.con),
            "expenses": ExpensesModel(self.cur, self.con),
            "sale_items": SaleItmesModel(self.cur, self.con),
            "sales": SalesModel(self.cur, self.con),
            "stock_movements": StockMovementsModel(self.cur, self.con),
            "suppliers": SupplierModel(self.cur, self.con),
            "users": UsersModel(self.cur, self.con),
        }

    def _load_all_data(self):
        self.data = {
            "products": self.dbs["products"].get_products(),
            "categories": self.dbs["products"].get_categorys(),
            "units": self.dbs["products"].get_units(),
            "customers": self.dbs["customers"].get_customers(),
            "expenses": self.dbs["expenses"].get_expenses(),
            "sale_items": self.dbs["sale_items"].get_sale_items_all(),
            "sales": self.dbs["sales"].get_sales(),
            "stock_movements": self.dbs["stock_movements"].get_movements(),
            "suppliers": self.dbs["suppliers"].get_suppliers(),
            "users": self.dbs["users"].get_all_users(),
        }

    def _get_user_id(self):
        uid = self.settings.get_setting("user_id")
        if not uid:
            generated_uid = str(uuid.uuid4())
            self.settings.update_settings(user_id=generated_uid)
            return generated_uid
        return uid

    # ── UI Build ────────────────────────────
    def _build_ui(self):
        # ── Header ──
        header = CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        CTkLabel(
            header,
            text="رفع البيانات إلى السحابة",
            image=image("assets/cloud.png"),
            compound="left",
            font=CTkFont(family="Cairo", size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=24, pady=18)

        self.uid_label = CTkLabel(
            header,
            text=f"معرّف: {self.uid[:18]}…",
            font=CTkFont(family="Cairo", size=10, weight="bold"),
            text_color=COLORS["text_dim"],
        )
        self.uid_label.pack(side="right", padx=20)

        # ── Divider ──
        CTkFrame(self, fg_color=COLORS["border"], height=1).pack(fill="x")

        # ── Rows container ──
        container = CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(16, 8))

        self.rows: dict[str, TableRow] = {}
        for meta in TABLE_META:
            row = TableRow(container, icon=meta["icon"], label=meta["label"])
            row.pack(fill="x", pady=4)
            self.rows[meta["key"]] = row

        # ── Overall progress ──
        bottom = CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0)
        bottom.pack(fill="x", side="bottom")

        CTkFrame(bottom, fg_color=COLORS["border"], height=1).pack(fill="x")

        inner = CTkFrame(bottom, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=14)

        # Overall bar label
        top_row = CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        CTkLabel(
            top_row,
            text="التقدم الكلي",
            font=CTkFont(family="Cairo", size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        self.overall_pct_label = CTkLabel(
            top_row,
            text="(0%)",
            font=CTkFont(family="Cairo", size=12, weight="bold"),
            text_color=COLORS["accent"],
        )
        self.overall_pct_label.pack(side="left", padx=6)

        self.overall_counter = CTkLabel(
            top_row,
            text="",
            font=CTkFont(family="Cairo", size=11, weight="bold"),
            text_color=COLORS["text_dim"],
        )
        self.overall_counter.pack(side="right")

        self.overall_bar = CTkProgressBar(
            inner,
            height=12,
            corner_radius=6,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent_glow"],
        )
        self.overall_bar.set(0)
        self.overall_bar.pack(fill="x", pady=(6, 0))

        # Internet hint
        CTkLabel(
            bottom,
            text="⚠  تأكد من اتصالك بالإنترنت قبل الرفع",
            font=CTkFont(family="Cairo", size=11, weight="bold"),
            text_color=COLORS["text_dim"],
        ).pack(pady=(0, 12))

        self.upload_btn = CTkButton(
            bottom,
            text="بدء الرفع",
            image=image("assets/upload.png"),
            compound="left",
            font=CTkFont(family="Cairo", size=12, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_glow"],
            command=self._start_upload_thread,
        )
        self.upload_btn.pack(pady=(0, 12))

    # ── Upload Logic ────────────────────────
    def _start_upload_thread(self):
        self.upload_btn.configure(state="disabled", text="جاري الرفع…")
        self._total_items = sum(len(v) for v in self.data.values())
        t = threading.Thread(target=self._upload_all, daemon=True)
        t.start()

    def _upload_all(self):
        for meta in TABLE_META:
            key = meta["key"]
            rows = self.data.get(key, [])
            fields = FIELD_MAPS.get(key, [])

            self.after(0, lambda k=key: self.rows[k].set_uploading())
            self._upload_table(key, rows, fields)

        # Final UI update
        self.after(0, self._on_complete)

    def _upload_table(self, table: str, rows: list, fields: list):
        """رفع جدول واحد مع التحقق من وجود الـ ID مسبقاً (batch للسرعة)"""
        total = len(rows)
        if total == 0:
            self.after(0, lambda: self.rows[table].update_progress(0, 0))
            self.after(
                0,
                lambda: self.rows[table].status_label.configure(
                    text="لا توجد بيانات", text_color=COLORS["text_dim"]
                ),
            )
            return

        col_ref = db.collection("users").document(self.uid).collection(table)

        # ── جلب الـ IDs الموجودة مسبقاً (بالـ batch) ──
        existing_ids: set = set()
        docs = col_ref.stream()
        for doc in docs:
            existing_ids.add(doc.id)

        done = 0
        BATCH_SIZE = 400  # Firestore batch limit is 500

        records = []
        for row in rows:
            record = dict(zip(fields, row))
            doc_id = str(record.get("id", uuid.uuid4()))
            if doc_id not in existing_ids:
                records.append((doc_id, record))

        # Upload in batches
        for chunk_start in range(0, len(records), BATCH_SIZE):
            chunk = records[chunk_start : chunk_start + BATCH_SIZE]
            batch = db.batch()
            for doc_id, record in chunk:
                ref = col_ref.document(doc_id)
                batch.set(ref, record)
            batch.commit()
            done += len(chunk)

            # Update UI
            _done = done
            _total = total
            self.after(
                0, lambda k=table, d=_done, t=_total: self.rows[k].update_progress(d, t)
            )
            self._update_overall(len(chunk))

        # Mark skipped as done too
        skipped = total - len(records)
        if skipped > 0:
            _total = total
            self.after(
                0, lambda k=table, d=_total, t=_total: self.rows[k].set_skipped(d, t)
            )
            self._update_overall(skipped)

    def _update_overall(self, increment: int):
        with self._lock:
            self._uploaded_items += increment
            done = self._uploaded_items
            total = self._total_items

        ratio = done / total if total else 0
        pct = int(ratio * 100)

        self.after(0, lambda: self.overall_bar.set(ratio))
        self.after(
            0,
            lambda: self.overall_pct_label.configure(
                text=f"({pct}%)",
                text_color=COLORS["success"] if pct == 100 else COLORS["accent"],
            ),
        )
        self.after(
            0,
            lambda: self.overall_counter.configure(
                text=f"تم رفع {done} عنصر من {total}"
            ),
        )

    def _on_complete(self):
        self.overall_bar.configure(progress_color=COLORS["success"])
        self.overall_pct_label.configure(text="(100%) ✔", text_color=COLORS["success"])
        messagebox.showinfo("تم الرفع", "تم رفع جميع البيانات إلى السحابة بنجاح ✅")
        self.destroy()
