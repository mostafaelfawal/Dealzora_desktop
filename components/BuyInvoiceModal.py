from customtkinter import (
    CTkToplevel,
    CTkFrame,
    CTkLabel,
    CTkComboBox,
    CTkButton,
    CTkEntry,
    CTkInputDialog,
    CTkScrollableFrame,
)
from tkinter import messagebox
from tkcalendar import DateEntry
from utils.key_shortcut import key_shortcut
from utils.center_modal import center_modal
from utils.image import image
from components.ProductModal import ProductModal
from components.TreeView import TreeView
from models.settings import SettingsModel
from ui.RejectUI import RejectUI


class BuyInvoiceModal:
    def __init__(
        self, users_db, uid, parent, products_db, suppliers_db, on_success=None
    ):
        self.users_db = users_db
        self.uid = uid
        self.parent = parent
        self.products_db = products_db
        self.suppliers_db = suppliers_db
        self.on_success = on_success
        self.invoice_items = []  # قائمة المنتجات في الفاتورة
        self.c = SettingsModel().get_setting("currency")

        # إنشاء نافذة منبثقة
        self.window = CTkToplevel(parent)
        self.window.title("فاتورة شراء جديدة | Dealzora")
        self.window.grab_set()
        self.window.state("zoomed")
        if not self.users_db.check_permission(self.uid, "purchase_invoices" or "all"):
            RejectUI(self.window)
            return

        # إطار رئيسي
        self.main_frame = CTkFrame(self.window, fg_color=("#ebebeb", "#1a1a1a"))
        self.main_frame.pack(fill="both", expand=True)

        # عنوان النافذة
        title_label = CTkLabel(
            self.main_frame,
            text="فاتورة شراء جديدة",
            font=("Cairo", 24, "bold"),
            text_color="#2563eb",
            image=image("assets/invoices.png"),
            compound="left"
        )
        title_label.pack(pady=(10, 20))

        # ========== الإطار العلوي (المورد والتاريخ) ==========
        top_frame = CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        # اختيار المورد
        supplier_frame = CTkFrame(top_frame, fg_color="transparent")
        supplier_frame.pack(side="left", padx=20)

        CTkLabel(supplier_frame, text="اختر المورد:", font=("Cairo", 16, "bold")).pack(
            side="top", anchor="w"
        )

        # الحصول على قائمة الموردين
        suppliers_list = [s[1] for s in self.suppliers_db.get_suppliers()]

        self.supplier_combo = CTkComboBox(
            supplier_frame,
            values=suppliers_list if suppliers_list else ["لا يوجد موردين"],
            width=250,
            font=("Cairo", 14),
            dropdown_font=("Cairo", 14),
        )
        self.supplier_combo.pack(pady=(5, 0))

        # إضافة مورد جديد
        CTkButton(
            supplier_frame,
            text="➕ إضافة مورد جديد",
            font=("Cairo", 12),
            width=250,
            height=30,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.add_new_supplier,
        ).pack(pady=(5, 0))

        # اختيار التاريخ
        date_frame = CTkFrame(top_frame, fg_color="transparent")
        date_frame.pack(side="left", padx=20)

        CTkLabel(date_frame, text="تاريخ الفاتورة:", font=("Cairo", 16, "bold")).pack(
            side="top", anchor="w"
        )

        # DateEntry من tkcalendar
        self.date_entry = DateEntry(
            date_frame,
            width=20,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            font=("Cairo", 14),
            date_pattern="yyyy-mm-dd",
        )
        self.date_entry.pack(pady=(5, 0))

        # رقم الفاتورة (اختياري)
        invoice_num_frame = CTkFrame(top_frame, fg_color="transparent")
        invoice_num_frame.pack(side="left", padx=20)

        CTkLabel(
            invoice_num_frame, text="رقم الفاتورة:", font=("Cairo", 16, "bold")
        ).pack(side="top", anchor="w")

        self.invoice_number_entry = CTkEntry(
            invoice_num_frame, width=200, font=("Cairo", 14), placeholder_text="اختياري"
        )
        self.invoice_number_entry.pack(pady=(5, 0))

        # ========== إطار إضافة المنتجات ==========
        products_control_frame = CTkFrame(self.main_frame, fg_color="transparent")
        products_control_frame.pack(fill="x", padx=20, pady=20)

        CTkLabel(
            products_control_frame, text="منتجات الفاتورة:", font=("Cairo", 18, "bold")
        ).pack(side="left", padx=(0, 20))

        CTkButton(
            products_control_frame,
            text="➕ إضافة منتج موجود",
            font=("Cairo", 14),
            width=180,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.add_existing_product,
        ).pack(side="left", padx=5)

        CTkButton(
            products_control_frame,
            text="🆕 إضافة منتج جديد",
            font=("Cairo", 14),
            width=180,
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            command=self.add_new_product,
        ).pack(side="left", padx=5)

        # ========== جدول المنتجات باستخدام TreeView ==========
        table_container = CTkFrame(self.main_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=10)

        # إنشاء TreeView للعرض
        cols = ("المنتج", "الباركود", "الكمية", "سعر الشراء", "الإجمالي")
        widths = (300, 150, 100, 120, 120)

        self.tree_view = TreeView(table_container, cols, widths)

        # ربط حدث النقر المزدوج للحذف
        key_shortcut(self.tree_view.tree, "<Double-1>", self.on_item_double_click)
        # ========== إطار الإجماليات ==========
        totals_frame = CTkFrame(self.main_frame, fg_color=("#B9B9B9","#2d2d2d"))
        totals_frame.pack(fill="x", padx=20, pady=20)

        # إجمالي الفاتورة
        total_label = CTkLabel(
            totals_frame, text="الإجمالي:", font=("Cairo", 20, "bold")
        )
        total_label.pack(side="left", padx=20, pady=10)

        self.total_value_label = CTkLabel(
            totals_frame, text="0.00", font=("Cairo", 24, "bold"), text_color="#10b981"
        )
        self.total_value_label.pack(side="left", padx=5, pady=10)

        CTkLabel(totals_frame, text=f"{self.c}", font=("Cairo", 18)).pack(
            side="left", padx=5, pady=10
        )

        # عدد الأصناف
        CTkLabel(totals_frame, text="عدد الأصناف:", font=("Cairo", 16)).pack(
            side="left", padx=(50, 5), pady=10
        )

        self.items_count_label = CTkLabel(
            totals_frame, text="0", font=("Cairo", 18, "bold"), text_color=("#cf8709", "#f59e0b")
        )
        self.items_count_label.pack(side="left", padx=5, pady=10)

        # ========== أزرار الحفظ والإلغاء ==========
        CTkButton(
            totals_frame,
            text="💾 حفظ الفاتورة",
            font=("Cairo", 18, "bold"),
            width=200,
            height=50,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.save_invoice,
        ).pack(side="left", padx=10)

        CTkButton(
            totals_frame,
            text="❌ إلغاء",
            font=("Cairo", 18, "bold"),
            width=150,
            height=50,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.window.destroy,
        ).pack(side="left", padx=10)

        # اختصارات لوحة المفاتيح
        key_shortcut(self.window, "<Escape>", lambda: self.window.destroy())
        key_shortcut(self.window, "<Control-s>", self.save_invoice)
        key_shortcut(self.window, "<Delete>", self.remove_selected_item)

    def add_new_supplier(self):
        """إضافة مورد جديد"""
        dialog = CTkInputDialog(
            text="أدخل اسم المورد الجديد:",
            title="إضافة مورد جديد",
            font=("Cairo", 20, "bold"),
        )
        supplier_name = dialog.get_input()

        if supplier_name and supplier_name.strip():
            try:
                # تحديث قائمة الموردين
                suppliers_list = [s[1] for s in self.suppliers_db.get_suppliers()]
                self.supplier_combo.configure(values=suppliers_list)
                self.supplier_combo.set(supplier_name.strip())
                messagebox.showinfo("تم", f"تم إضافة المورد '{supplier_name}' بنجاح")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")

    def add_existing_product(self):
        """إضافة منتج موجود"""
        # نافذة بحث عن المنتج
        search_window = CTkToplevel(self.window)
        search_window.title("بحث عن منتج")
        search_window.geometry("600x500")
        center_modal(search_window)

        def search_products():
            # مسح الإطار
            for widget in results_frame.winfo_children():
                widget.destroy()

            keyword = search_entry.get().strip()

            # لو الحقل فاضي → هات كل المنتجات
            if not keyword:
                results = self.products_db.get_products()
            else:
                results = self.products_db.search_products(keyword)

            if not results:
                CTkLabel(results_frame, text="لا توجد نتائج", font=("Cairo", 14)).pack(
                    pady=20
                )
                return

            for product in results:
                product_frame = CTkFrame(results_frame, fg_color=("#B9B9B9","#2d2d2d"))
                product_frame.pack(fill="x", pady=2)

                CTkLabel(
                    product_frame, text=f"{product[1]}", font=("Cairo", 14), width=200
                ).pack(side="left", padx=10, pady=5)

                CTkLabel(
                    product_frame,
                    text=f"الباركود: {product[2] if product[2] else '---'}",
                    font=("Cairo", 12),
                    width=150,
                ).pack(side="left", padx=10)

                CTkLabel(
                    product_frame,
                    text=f"المخزون: {product[5]}",
                    font=("Cairo", 12),
                    width=80,
                ).pack(side="left", padx=10)

                CTkButton(
                    product_frame,
                    text="✅",
                    width=80,
                    command=lambda p=product: select_product(p, search_window),
                ).pack(side="left", padx=10)

        CTkLabel(search_window, text="بحث عن منتج", font=("Cairo", 20, "bold")).pack(
            pady=10
        )

        # حقل البحث
        search_frame = CTkFrame(search_window, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)

        search_entry = CTkEntry(
            search_frame,
            width=400,
            font=("Cairo", 14),
            placeholder_text="ابحث بالاسم أو الباركود...",
        )
        search_entry.pack(side="left", padx=5)

        search_btn = CTkButton(
            search_frame,
            text="🔍 بحث",
            width=80,
            font=("Cairo", 20),
            command=search_products,
        )
        search_btn.pack(side="left")

        # إطار النتائج
        results_frame = CTkScrollableFrame(search_window, height=300)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def select_product(product, window):
            window.destroy()
            self.add_quantity_dialog(product)

        # تنفيذ البحث عند الضغط على Enter
        search_products()
        key_shortcut(search_entry, "<Return>", search_products)

    def add_quantity_dialog(self, product):
        """نافذة إدخال الكمية وسعر الشراء للمنتج"""
        dialog = CTkToplevel(self.window)
        dialog.title("إضافة كمية")
        dialog.geometry("400x350")
        center_modal(dialog)

        CTkLabel(dialog, text=f"المنتج: {product[1]}", font=("Cairo", 18, "bold")).pack(
            pady=10
        )

        CTkLabel(
            dialog,
            text=f"الباركود: {product[2] if product[2] else '---'}",
            font=("Cairo", 14),
        ).pack(pady=5)

        CTkLabel(dialog, text=f"المخزون الحالي: {product[5]}", font=("Cairo", 14)).pack(
            pady=5
        )

        # الكمية
        CTkLabel(dialog, text="الكمية المشتراة:", font=("Cairo", 14)).pack(pady=(15, 5))

        quantity_entry = CTkEntry(
            dialog, width=200, font=("Cairo", 14), placeholder_text="أدخل الكمية"
        )
        quantity_entry.pack()
        quantity_entry.insert(0, "1")

        # سعر الشراء
        CTkLabel(dialog, text="سعر الشراء للوحدة:", font=("Cairo", 14)).pack(
            pady=(10, 5)
        )

        price_entry = CTkEntry(
            dialog, width=200, font=("Cairo", 14), placeholder_text="أدخل سعر الشراء"
        )
        price_entry.pack()
        price_entry.insert(0, str(product[3] if product[3] else "0"))

        def add_to_invoice():
            try:
                quantity = float(quantity_entry.get())
                price = float(price_entry.get())

                if quantity <= 0:
                    messagebox.showerror("خطأ", "الكمية يجب أن تكون أكبر من صفر")
                    return

                if price < 0:
                    messagebox.showerror("خطأ", "سعر الشراء غير صحيح")
                    return

                # التحقق من عدم تكرار المنتج
                for item in self.invoice_items:
                    if item["id"] == product[0]:
                        result = messagebox.askyesno(
                            "تأكيد",
                            f"المنتج '{product[1]}' موجود بالفعل في الفاتورة.\nهل تريد إضافة كمية أخرى؟",
                        )
                        if result:
                            item["quantity"] += quantity
                            item["total"] = item["quantity"] * item["buy_price"]
                        self.refresh_products_table()
                        dialog.destroy()
                        return

                # إضافة المنتج للفاتورة
                self.invoice_items.append(
                    {
                        "id": product[0],
                        "name": product[1],
                        "barcode": product[2] if product[2] else "---",
                        "quantity": quantity,
                        "buy_price": price,
                        "total": quantity * price,
                    }
                )

                self.refresh_products_table()
                dialog.destroy()

            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة")

        CTkButton(
            dialog,
            text="إضافة للفاتورة",
            font=("Cairo", 14),
            width=150,
            fg_color="#10b981",
            command=add_to_invoice,
        ).pack(pady=20)

    def add_new_product(self):
        """إضافة منتج جديد"""

        def on_product_added():
            # بعد إضافة المنتج، نضيفه للفاتورة
            products = self.products_db.get_products()
            if products:
                latest_product = products[0]  # أول منتج (الأحدث)
                self.add_quantity_dialog(latest_product)

        ProductModal(
            self.window,
            self.products_db,
            self.suppliers_db,
            mode="add",
            on_success=on_product_added,
        )

    def refresh_products_table(self):
        """تحديث جدول المنتجات باستخدام TreeView"""
        # مسح البيانات الحالية
        for item in self.tree_view.tree.get_children():
            self.tree_view.tree.delete(item)

        total = 0

        for i, item in enumerate(self.invoice_items):
            # إدراج صف في TreeView
            item_id = self.tree_view.tree.insert(
                "",
                "end",
                values=(
                    (
                        item["name"][:30] + "..."
                        if len(item["name"]) > 30
                        else item["name"]
                    ),
                    item["barcode"],
                    f"{item['quantity']:.0f}",
                    f"{item['buy_price']:.2f}",
                    f"{item['total']:.2f}",
                ),
                tags=("even" if i % 2 == 0 else "odd",),
            )

            # تخزين البيانات الكاملة للمنتج في عنصر TreeView
            self.tree_view.tree.item(
                item_id,
                values=(
                    (
                        item["name"][:30] + "..."
                        if len(item["name"]) > 30
                        else item["name"]
                    ),
                    item["barcode"],
                    f"{item['quantity']:.0f}",
                    f"{item['buy_price']:.2f}",
                    f"{item['total']:.2f}",
                ),
            )

            total += item["total"]

        # تحديث الإجماليات
        self.total_value_label.configure(text=f"{total:.2f}")
        self.items_count_label.configure(text=str(len(self.invoice_items)))

    def on_item_double_click(self, event):
        """معالج النقر المزدوج لحذف عنصر"""
        selected = self.tree_view.tree.selection()
        if selected:
            self.remove_selected_item()

    def remove_selected_item(self, event=None):
        """حذف المنتج المحدد من الفاتورة"""
        selected = self.tree_view.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد منتج للحذف")
            return

        # الحصول على مؤشر العنصر المحدد
        item_index = self.tree_view.tree.index(selected[0])

        if 0 <= item_index < len(self.invoice_items):
            product_name = self.invoice_items[item_index]["name"]
            result = messagebox.askyesno(
                "تأكيد الحذف",
                f"هل أنت متأكد من حذف المنتج '{product_name}' من الفاتورة؟",
            )
            if result:
                del self.invoice_items[item_index]
                self.refresh_products_table()

    def save_invoice(self, event=None):
        """حفظ الفاتورة وتحديث المخزون"""
        # التحقق من البيانات
        if not self.invoice_items:
            messagebox.showerror("خطأ", "الرجاء إضافة منتجات للفاتورة")
            return

        supplier = self.supplier_combo.get().strip()
        if not supplier or supplier == "لا يوجد موردين":
            messagebox.showerror("خطأ", "الرجاء اختيار المورد")
            return

        try:
            # الحصول على تاريخ الفاتورة
            invoice_date = self.date_entry.get_date()

            # الحصول على رقم الفاتورة (اختياري)
            invoice_number = self.invoice_number_entry.get().strip() or None

            # الحصول على ID المورد
            supplier_id = self.suppliers_db.get_or_create_supplier_id(supplier)

            # تحديث المخزون لكل منتج
            success_count = 0
            for item in self.invoice_items:
                try:
                    # الحصول على الكمية الحالية
                    current_product = self.products_db.get_product(item["id"])
                    old_qty = current_product[5] if current_product else 0

                    # تحديث سعر الشراء والكمية
                    self.products_db.cur.execute(
                        """UPDATE products SET 
                           quantity = quantity + ?,
                           buy_price = ?
                           WHERE id = ?""",
                        (item["quantity"], item["buy_price"], item["id"]),
                    )

                    # إضافة حركة مخزون
                    self.products_db.stock_movements_db.add_movement(
                        product_id=item["id"],
                        quantity=item["quantity"],
                        movement_type="شراء",
                        reference_id=supplier_id,
                        reference_number=invoice_number,
                        old_qty=old_qty,
                    )

                    success_count += 1

                except Exception as e:
                    continue

            # حفظ التغييرات
            self.products_db.con.commit()

            # رسالة النجاح
            messagebox.showinfo(
                "تم بنجاح",
                f"تم حفظ الفاتورة بنجاح\n"
                f"المورد: {supplier}\n"
                f"عدد المنتجات: {success_count}\n"
                f"التاريخ: {invoice_date}",
            )

            # تحديث الواجهة الرئيسية إذا وجدت
            if self.on_success:
                self.on_success()

            # إغلاق النافذة
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ الفاتورة:\n{str(e)}")
