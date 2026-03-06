from customtkinter import (
    CTkToplevel,
    CTkFrame,
    CTkLabel,
    CTkButton,
    StringVar,
    CTkOptionMenu,
    CTkEntry,
)
from tkinter import messagebox
from components.TreeView import TreeView
from utils.key_shortcut import key_shortcut
from ui.RejectUI import RejectUI


class StockMovementsModal:
    def __init__(self, users_db, uid, parent, stock_movement_model, products_model):
        self.users_db = users_db
        self.uid = uid
        self.parent = parent
        self.stock_movement_model = stock_movement_model
        self.products_model = products_model

        # إنشاء نافذة منبثقة
        self.window = CTkToplevel(parent)
        self.window.title("حركات المخزون | Dealzora")

        self.window.grab_set()
        self.window.state("zoomed")

        if not self.users_db.check_permission(self.uid, "stock_movements_view" or "all"):
            RejectUI(self.window)
            return

        self.build_ui()
        self.load_movements()
        self.load_products()

        # ربط اختصارات لوحة المفاتيح
        self.bind_shortcuts()

    def build_ui(self):
        """بناء واجهة المستخدم"""

        # ========== الإطار الرئيسي ==========
        main_frame = CTkFrame(self.window, fg_color="#1f2937", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ========== الهيدر ==========
        header_frame = CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        CTkLabel(
            header_frame,
            text="📊 سجل حركات المخزون",
            font=("Cairo", 28, "bold"),
            text_color="#2b7de9",
        ).pack(side="right")

        CTkButton(
            header_frame,
            text="🔄 تحديث",
            width=100,
            font=("Cairo", 13),
            fg_color="#1f2937",
            hover_color="#2d3a4f",
            command=self.load_movements,
        ).pack(side="left", padx=5)

        # ========== أدوات التحكم والفلترة ==========
        controls_frame = CTkFrame(main_frame, fg_color="#111827", corner_radius=10)
        controls_frame.pack(fill="x", padx=20, pady=10)

        # الصف الأول: البحث والفلترة
        filter_row = CTkFrame(controls_frame, fg_color="transparent")
        filter_row.pack(fill="x", padx=15, pady=(15, 5))

        # تكوين الأعمدة
        filter_row.grid_columnconfigure(1, weight=1)
        filter_row.grid_columnconfigure(3, weight=1)
        filter_row.grid_columnconfigure(5, weight=1)

        # ===== فلترة حسب المنتج =====
        CTkLabel(
            filter_row, text="📦 المنتج:", font=("Cairo", 14), text_color="#9ca3af"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.product_var = StringVar(value="الكل")
        self.product_menu = CTkOptionMenu(
            filter_row,
            variable=self.product_var,
            values=["الكل"],
            font=("Cairo", 13),
            dropdown_font=("Cairo", 13),
            fg_color="#374151",
            button_color="#4b5563",
            button_hover_color="#6b7280",
            height=35,
            command=lambda x: self.filter_movements(),
        )
        self.product_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # ===== فلترة حسب نوع الحركة =====
        CTkLabel(
            filter_row, text="📋 نوع الحركة:", font=("Cairo", 14), text_color="#9ca3af"
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.type_var = StringVar(value="الكل")

        self.type_menu = CTkOptionMenu(
            filter_row,
            variable=self.type_var,
            values=["الكل", "شراء", "بيع", "ارجاع", "يدوي"],
            font=("Cairo", 13),
            dropdown_font=("Cairo", 13),
            fg_color="#374151",
            button_color="#4b5563",
            button_hover_color="#6b7280",
            height=35,
            command=lambda x: self.filter_movements(),
        )
        self.type_menu.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # ===== فلترة حسب التاريخ =====
        CTkLabel(
            filter_row, text="📅 التاريخ:", font=("Cairo", 14), text_color="#9ca3af"
        ).grid(row=0, column=4, padx=5, pady=5, sticky="w")

        date_frame = CTkFrame(filter_row, fg_color="transparent")
        date_frame.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        date_frame.grid_columnconfigure(0, weight=1)
        date_frame.grid_columnconfigure(1, weight=0)
        date_frame.grid_columnconfigure(2, weight=1)

        self.from_date = CTkEntry(
            date_frame,
            placeholder_text="من (YYYY-MM-DD)",
            height=35,
            font=("Cairo", 12),
            border_width=2,
            border_color="#374151",
        )
        self.from_date.grid(row=0, column=0, padx=2, sticky="ew")

        CTkLabel(date_frame, text="→", font=("Cairo", 14), text_color="#9ca3af").grid(
            row=0, column=1, padx=5
        )

        self.to_date = CTkEntry(
            date_frame,
            placeholder_text="إلى (YYYY-MM-DD)",
            height=35,
            font=("Cairo", 12),
            border_width=2,
            border_color="#374151",
        )
        self.to_date.grid(row=0, column=2, padx=2, sticky="ew")

        # ========== جدول حركات المخزون ==========
        table_frame = CTkFrame(main_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # أعمدة الجدول
        cols = (
            "ID",
            "المنتج",
            "الكمية",
            "الكمية القديمة",
            "الكمية الجديدة",
            "نوع الحركة",
            "رقم الفاتورة",
            "التاريخ",
        )

        widths = (30, 140, 100, 120, 120, 100, 140, 150)

        self.tree = TreeView(table_frame, cols, widths)

        # تخصيص ألوان الصفوف حسب نوع الحركة
        self.tree.tree.tag_configure("بيع", background="#489e7c")
        self.tree.tree.tag_configure("يدوي", background="#947373")
        self.tree.tree.tag_configure("ارجاع", background="#919140")
        self.tree.tree.tag_configure("شراء", background="#6785aa")

        # تفعيل النقر المزدوج لعرض التفاصيل
        key_shortcut(
            self.tree.tree, ["<Double-1>", "<Return>"], self.show_movement_details
        )
        key_shortcut(
            self.tree.tree,
            ["<Delete>", "<Control-D>", "<Control-d>"],
            self.handle_delete_movements,
        )

        # ========== شريط الحالة ==========
        self.status_bar = CTkFrame(
            main_frame, fg_color="#111827", height=30, corner_radius=5
        )
        self.status_bar.pack(fill="x", padx=20, pady=(0, 15))

        self.status_label = CTkLabel(
            self.status_bar,
            text="عدد الحركات: 0",
            font=("Cairo", 12),
            text_color="#9ca3af",
        )
        self.status_label.pack(side="left", padx=15, pady=5)

        self.total_label = CTkLabel(
            self.status_bar,
            text="إجمالي الكميات: 0",
            font=("Cairo", 12),
            text_color="#9ca3af",
        )
        self.total_label.pack(side="right", padx=15, pady=5)

    def load_products(self):
        """تحميل قائمة المنتجات للفلترة"""
        products = self.products_model.get_products()
        product_names = ["الكل"] + [f"{p[1]}" for p in products]
        self.product_menu.configure(values=product_names)

    def load_movements(self):
        """تحميل جميع حركات المخزون"""
        try:
            movements = self.stock_movement_model.get_movements()
            self.display_movements(movements)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل الحركات: {str(e)}")

    def display_movements(self, movements):
        """عرض الحركات في الجدول"""
        # مسح الجدول
        for item in self.tree.tree.get_children():
            self.tree.tree.delete(item)

        # ترجمة أنواع الحركات
        type_translation = {
            "purchase_add": "➕ إضافة (مشتريات)",
            "purchase_return": "↩️ مرتجع مشتريات",
            "sale_deduct": "➖ خصم (مبيعات)",
            "sale_return": "🔄 مرتجع مبيعات",
            "manual_adjust": "✏️ تعديل يدوي",
            "opening_balance": "⚖️ رصيد افتتاحي",
        }

        total_qty = 0

        for movement in movements:
            # movement: id, product_id, quantity, old_qty, new_qty, movement_type, reference_id, reference_number, date
            (
                movement_id,
                product_id,
                quantity,
                old_qty,
                new_qty,
                movement_type,
                _,
                ref_num,
                date,
            ) = movement

            # الحصول على اسم المنتج
            product = self.products_model.get_product(product_id)
            product_name = product[1]

            # تنسيق الكمية مع إشارة
            qty_display = f"+{quantity}" if quantity > 0 else str(quantity)

            # تحديد tag للتلوين
            tag = (
                movement_type
                if movement_type
                in [
                    "بيع",
                    "شراء",
                    "ارجاع",
                    "يدوي",
                ]
                else "normal"
            )

            self.tree.tree.insert(
                "",
                "end",
                values=(
                    movement_id,
                    product_name,
                    qty_display,
                    f"{old_qty:.2f}",
                    f"{new_qty:.2f}",
                    type_translation.get(movement_type, movement_type),
                    ref_num or "—",
                    date if date else "—",
                ),
                tags=(tag,),
            )

            total_qty += abs(quantity)

        # تحديث شريط الحالة
        self.status_label.configure(text=f"عدد الحركات: {len(movements)}")
        self.total_label.configure(text=f"إجمالي الكميات: {total_qty:.2f}")

    def filter_movements(self):
        """تطبيق الفلترة على الحركات"""
        try:
            selected_product = self.product_var.get()
            movement_type = self.type_var.get()
            from_date = self.from_date.get().strip()
            to_date = self.to_date.get().strip()

            # الحصول على جميع الحركات
            movements = self.stock_movement_model.get_movements()

            # تطبيق الفلاتر
            filtered_movements = []
            for movement in movements:
                (_, product_id, _, _, _, m_type, _, _, date) = movement

                # فلترة حسب المنتج
                if selected_product != "الكل":
                    product_name = self.products_model.get_product(product_id)[1]
                    if product_name != selected_product:
                        continue

                # فلترة حسب نوع الحركة
                if movement_type != "الكل" and m_type != movement_type:
                    continue

                # فلترة حسب التاريخ
                if from_date and date:
                    if date[:10] < from_date:
                        continue
                if to_date and date:
                    if date[:10] > to_date:
                        continue

                filtered_movements.append(movement)

            self.display_movements(filtered_movements)

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الفلترة: {str(e)}")

    def show_movement_details(self):
        """عرض تفاصيل الحركة المحددة"""
        selected = self.tree.tree.selection()
        if not selected:
            return

        values = self.tree.tree.item(selected[0])["values"]
        if not values:
            return

        # إنشاء نافذة تفاصيل
        details_window = CTkToplevel(self.window)
        details_window.title("تفاصيل الحركة | Dealzora")
        details_window.geometry("500x520")
        details_window.configure(bg="#1a1a1a")
        details_window.transient(self.window)
        details_window.grab_set()

        # محتوى التفاصيل
        frame = CTkFrame(details_window, fg_color="#1f2937", corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        CTkLabel(
            frame,
            text="📋 تفاصيل حركة المخزون",
            font=("Cairo", 20, "bold"),
            text_color="#2b7de9",
        ).pack(pady=(20, 30))

        details = [
            (":رقم الحركة", values[0]),
            (":المنتج", values[1]),
            (":الكمية", values[2]),
            (":الكمية القديمة", values[3]),
            (":الكمية الجديدة", values[4]),
            (":نوع الحركة", values[5]),
            (":رقم الفاتورة", values[6]),
            (":التاريخ", values[7]),
        ]

        for label, value in details:
            detail_frame = CTkFrame(frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=30, pady=5)

            CTkLabel(
                detail_frame,
                text=label,
                font=("Cairo", 14, "bold"),
                text_color="#9ca3af",
                width=120,
                anchor="e",
            ).pack(side="right")

            CTkLabel(
                detail_frame,
                text=str(value),
                font=("Cairo", 14),
                text_color="white",
                anchor="e",
            ).pack(side="right", padx=(10, 0))

        CTkButton(
            frame,
            text="إغلاق",
            font=("Cairo", 14),
            fg_color="#4b5563",
            hover_color="#6b7280",
            width=200,
            height=40,
            command=details_window.destroy,
        ).pack(pady=30)

    def bind_shortcuts(self):
        """ربط اختصارات لوحة المفاتيح"""
        key_shortcut(self.window, "<Escape>", lambda: self.window.destroy())
        key_shortcut(self.window, "<F5>", self.load_movements)
        key_shortcut(self.window, "<Control-f>", lambda: self.from_date.focus())
        key_shortcut(self.window, "<Control-t>", lambda: self.to_date.focus())

    def handle_delete_movements(self):
        selected = self.tree.tree.selection()
        if not selected:
            return messagebox.showwarning("تنبيه", "اختر حركة")

        ids = [self.tree.tree.item(i)["values"][0] for i in selected]
        if messagebox.askokcancel("تأكد", "هل انت متأكد؟"):
            self.stock_movement_model.delete_movement(ids)
            self.load_movements()
