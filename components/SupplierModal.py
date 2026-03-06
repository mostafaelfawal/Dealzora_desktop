from customtkinter import (
    CTkToplevel,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkFrame,
)
from tkinter import messagebox
from utils.center_modal import center_modal
from utils.key_shortcut import key_shortcut
from components.TreeView import TreeView
from ui.RejectUI import RejectUI

class SupplierModal:
    def __init__(
        self,
        root,
        supplier_model,
        uid,
        users_db
    ):
        self.root = root
        self.supplier_model = supplier_model
        self.selected_supplier_id = None
        self.uid = uid
        self.users_db = users_db
        self.build_modal()

    # ================= BUILD =================
    def build_modal(self):
        self.modal = CTkToplevel(self.root)
        self.modal.title("إدارة الموردين | Dealzora")
        self.modal.geometry("800x600")
        self.modal.state("zoomed")
        center_modal(self.modal)

        if not self.users_db.check_permission(self.uid, "suppliers_management" or "all"):
            RejectUI(self.modal)
            return

        # عنوان النافذة
        CTkLabel(
            self.modal,
            text="🏭 إدارة الموردين",
            font=("Cairo", 24, "bold"),
            text_color="#2b7de9",
        ).pack(pady=(20, 10))

        # إطار رئيسي
        main_frame = CTkFrame(self.modal, fg_color="transparent")
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # ========== قسم البحث ==========
        search_frame = CTkFrame(main_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)

        CTkLabel(
            search_frame,
            text="🔍 بحث:",
            font=("Cairo", 14),
        ).pack(side="left", padx=(0, 10))

        self.search_entry = CTkEntry(
            search_frame,
            width=300,
            height=35,
            font=("Cairo", 14),
            placeholder_text="ابحث باسم المورد...",
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        key_shortcut(self.search_entry, "<KeyRelease>", self.filter_suppliers)
        key_shortcut(self.modal, "<Escape>", lambda: self.modal.destroy())
        
        # ========== أزرار التحكم في القائمة ==========
        btn_frame = CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        CTkButton(
            btn_frame,
            text="✏️ تعديل",
            font=("Cairo", 14, "bold"),
            width=120,
            height=35,
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=self.edit_selected,
        ).pack(side="left", padx=5)

        CTkButton(
            btn_frame,
            text="🗑️ حذف",
            font=("Cairo", 14, "bold"),
            width=120,
            height=35,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.delete_selected,
        ).pack(side="left", padx=5)

        CTkButton(
            btn_frame,
            text="➕ إضافة مورد جديد",
            font=("Cairo", 16, "bold"),
            width=180,
            height=40,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.open_add_modal,
        ).pack(side="left", padx=5)

        CTkButton(
            btn_frame,
            text="🔄 تحديث",
            font=("Cairo", 14, "bold"),
            width=120,
            height=35,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.load_suppliers,
        ).pack(side="left", padx=5)

        # ========== جدول عرض الموردين ==========
        tree_frame = CTkFrame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=10)

        # إنشاء TreeView
        cols = ("المعرف", "اسم المورد", "رقم الهاتف")
        widths = (100, 300, 300)

        self.tree_view = TreeView(tree_frame, cols, widths, [])
        key_shortcut(
            self.tree_view.tree, ["<Double-1>", "<Return>"], self.edit_selected
        )

        # تحميل البيانات
        self.load_suppliers()

    # ========== مودال إضافة مورد جديد ==========
    def open_add_modal(self):
        """فتح نافذة منبثقة لإضافة مورد جديد"""
        add_modal = CTkToplevel(self.modal)
        add_modal.title("إضافة مورد جديد | Dealzora")
        add_modal.geometry("500x400")
        add_modal.transient(self.modal)  # تجعلها تابعة للنافذة الرئيسية
        add_modal.grab_set()  # تمنع التفاعل مع النافذة الرئيسية
        center_modal(add_modal)

        # عنوان النافذة
        CTkLabel(
            add_modal,
            text="➕ إضافة مورد جديد",
            font=("Cairo", 20, "bold"),
            text_color="#2563eb",
        ).pack(pady=(20, 10))

        # إطار المدخلات
        form_frame = CTkFrame(add_modal, fg_color="transparent")
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)

        # ================= حقل الاسم =================
        CTkLabel(
            form_frame,
            text="📋 اسم المورد *",
            font=("Cairo", 16, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        name_entry = CTkEntry(
            form_frame,
            width=350,
            height=40,
            font=("Cairo", 16),
            placeholder_text="أدخل اسم المورد",
            border_width=2,
            border_color="#374151",
        )
        name_entry.pack(pady=(0, 15))
        name_entry.focus()  # التركيز على حقل الاسم

        # ================= حقل الهاتف =================
        CTkLabel(
            form_frame,
            text="📞 رقم الهاتف",
            font=("Cairo", 16, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(5, 5))

        phone_entry = CTkEntry(
            form_frame,
            width=350,
            height=40,
            font=("Cairo", 16),
            placeholder_text="أدخل رقم الهاتف (اختياري)",
            border_width=2,
            border_color="#374151",
        )
        phone_entry.pack(pady=(0, 15))

        # ================= أزرار التحكم =================
        btn_frame = CTkFrame(add_modal, fg_color="transparent")
        btn_frame.pack(pady=20)

        # زر الحفظ
        CTkButton(
            btn_frame,
            text="💾 حفظ",
            font=("Cairo", 16, "bold"),
            width=150,
            height=40,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=lambda: self.save_new_supplier(name_entry, phone_entry, add_modal),
        ).pack(side="left", padx=10)

        # زر إلغاء
        CTkButton(
            btn_frame,
            text="❌ إلغاء",
            font=("Cairo", 16, "bold"),
            width=150,
            height=40,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=add_modal.destroy,
        ).pack(side="left", padx=10)

        # اختصار Enter للحفظ
        key_shortcut(
            add_modal,
            "<Return>",
            lambda: self.save_new_supplier(name_entry, phone_entry, add_modal),
        )
        # اختصار Esc للإلغاء
        key_shortcut(add_modal, "<Escape>", add_modal.destroy)

    def save_new_supplier(self, name_entry, phone_entry, modal):
        """حفظ المورد الجديد من المودال"""
        name = name_entry.get().strip()
        phone = phone_entry.get().strip() or None

        # التحقق من صحة المدخلات
        if not name:
            messagebox.showerror("خطأ", "❌ اسم المورد مطلوب")
            name_entry.focus()
            return

        try:
            # إضافة مورد جديد
            self.supplier_model.cur.execute(
                "INSERT INTO suppliers (name, phone) VALUES (?, ?)", (name, phone)
            )
            self.supplier_model.con.commit()
            messagebox.showinfo("تم", f"✅ تم إضافة المورد '{name}' بنجاح")

            # إعادة تحميل قائمة الموردين
            self.load_suppliers()

            # إغلاق المودال
            modal.destroy()

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror(
                    "خطأ", "❌ رقم الهاتف موجود مسبقاً\nالرجاء استخدام رقم هاتف آخر"
                )
            else:
                messagebox.showerror("خطأ", f"❌ حدث خطأ: {str(e)}")

    # ========== مودال تعديل مورد ==========
    def open_edit_modal(self, supplier_id):
        """فتح نافذة منبثقة لتعديل مورد"""
        try:
            supplier = self.supplier_model.get_supplier_by_id(supplier_id)
            if not supplier:
                return

            edit_modal = CTkToplevel(self.modal)
            edit_modal.title("تعديل مورد | Dealzora")
            edit_modal.geometry("500x400")
            edit_modal.transient(self.modal)
            edit_modal.grab_set()
            center_modal(edit_modal)

            # عنوان النافذة
            CTkLabel(
                edit_modal,
                text="✏️ تعديل مورد",
                font=("Cairo", 20, "bold"),
                text_color="#f59e0b",
            ).pack(pady=(20, 10))

            # إطار المدخلات
            form_frame = CTkFrame(edit_modal, fg_color="transparent")
            form_frame.pack(padx=40, pady=20, fill="both", expand=True)

            # ================= حقل الاسم =================
            CTkLabel(
                form_frame,
                text="📋 اسم المورد *",
                font=("Cairo", 16, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(10, 5))

            name_entry = CTkEntry(
                form_frame,
                width=350,
                height=40,
                font=("Cairo", 16),
                placeholder_text="أدخل اسم المورد",
                border_width=2,
                border_color="#374151",
            )
            name_entry.pack(pady=(0, 15))
            name_entry.insert(0, supplier[1] or "")

            # ================= حقل الهاتف =================
            CTkLabel(
                form_frame,
                text="📞 رقم الهاتف",
                font=("Cairo", 16, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(5, 5))

            phone_entry = CTkEntry(
                form_frame,
                width=350,
                height=40,
                font=("Cairo", 16),
                placeholder_text="أدخل رقم الهاتف (اختياري)",
                border_width=2,
                border_color="#374151",
            )
            phone_entry.pack(pady=(0, 15))
            if len(supplier) > 2 and supplier[2]:
                phone_entry.insert(0, supplier[2])

            # ================= أزرار التحكم =================
            btn_frame = CTkFrame(edit_modal, fg_color="transparent")
            btn_frame.pack(pady=20)

            # زر التحديث
            CTkButton(
                btn_frame,
                text="💾 تحديث",
                font=("Cairo", 16, "bold"),
                width=150,
                height=40,
                fg_color="#f59e0b",
                hover_color="#d97706",
                command=lambda: self.update_supplier(
                    supplier_id, name_entry, phone_entry, edit_modal
                ),
            ).pack(side="left", padx=10)

            # زر إلغاء
            CTkButton(
                btn_frame,
                text="❌ إلغاء",
                font=("Cairo", 16, "bold"),
                width=150,
                height=40,
                fg_color="#6b7280",
                hover_color="#4b5563",
                command=edit_modal.destroy,
            ).pack(side="left", padx=10)

            # اختصارات لوحة المفاتيح
            key_shortcut(
                edit_modal,
                "<Return>",
                lambda: self.update_supplier(
                    supplier_id, name_entry, phone_entry, edit_modal
                ),
            )
            key_shortcut(edit_modal, "<Escape>", edit_modal.destroy)

        except Exception as e:
            messagebox.showerror("خطأ", f"❌ حدث خطأ: {str(e)}")

    def update_supplier(self, supplier_id, name_entry, phone_entry, modal):
        """تحديث بيانات المورد"""
        name = name_entry.get().strip()
        phone = phone_entry.get().strip() or None

        # التحقق من صحة المدخلات
        if not name:
            messagebox.showerror("خطأ", "❌ اسم المورد مطلوب")
            name_entry.focus()
            return

        try:
            # تحديث بيانات المورد
            self.supplier_model.update_supplier(supplier_id, name, phone)
            messagebox.showinfo("تم", f"✅ تم تحديث بيانات المورد '{name}' بنجاح")

            # إعادة تحميل قائمة الموردين
            self.load_suppliers()

            # إغلاق المودال
            modal.destroy()

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror(
                    "خطأ", "❌ رقم الهاتف موجود مسبقاً\nالرجاء استخدام رقم هاتف آخر"
                )
            else:
                messagebox.showerror("خطأ", f"❌ حدث خطأ: {str(e)}")

    # ================= تحميل وعرض الموردين =================
    def load_suppliers(self):
        """تحميل قائمة الموردين"""
        try:
            suppliers = self.supplier_model.get_suppliers()
            self.all_suppliers = suppliers
            self.display_suppliers(suppliers)
        except Exception as e:
            messagebox.showerror("خطأ", f"❌ حدث خطأ في تحميل البيانات: {str(e)}")

    def display_suppliers(self, suppliers):
        """عرض الموردين في الجدول"""
        # مسح البيانات القديمة
        for item in self.tree_view.tree.get_children():
            self.tree_view.tree.delete(item)

        # إضافة البيانات الجديدة
        for supplier in suppliers:
            values = (supplier[0], supplier[1], supplier[2] if supplier[2] else "-")
            self.tree_view.tree.insert("", "end", values=values)

    def filter_suppliers(self, event=None):
        """تصفية الموردين حسب البحث"""
        search_term = self.search_entry.get().strip().lower()

        if not search_term:
            self.display_suppliers(self.all_suppliers)
            return

        filtered = [s for s in self.all_suppliers if search_term in s[1].lower()]
        self.display_suppliers(filtered)

    # ================= عمليات التعديل والحذف =================
    def get_selected_supplier(self):
        """الحصول على المورد المحدد"""
        selected = self.tree_view.tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "⚠️ الرجاء تحديد مورد أولاً")
            return None

        item = self.tree_view.tree.item(selected[0])
        supplier_id = item["values"][0]
        return supplier_id

    def edit_selected(self):
        """تعديل المورد المحدد"""
        supplier_id = self.get_selected_supplier()
        if supplier_id:
            self.open_edit_modal(supplier_id)

    def delete_selected(self):
        """حذف المورد المحدد"""
        supplier_id = self.get_selected_supplier()
        if not supplier_id:
            return

        # الحصول على اسم المورد للتأكيد
        item = self.tree_view.tree.item(self.tree_view.tree.selection()[0])
        supplier_name = item["values"][1]

        # تأكيد الحذف
        result = messagebox.askyesno(
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف المورد '{supplier_name}'؟",
            icon="warning",
        )

        if result:
            try:
                self.supplier_model.delete_supplier(supplier_id)
                messagebox.showinfo("تم", f"✅ تم حذف المورد '{supplier_name}' بنجاح")

                # إعادة تحميل البيانات
                self.load_suppliers()

            except Exception as e:
                if "FOREIGN KEY constraint failed" in str(e):
                    messagebox.showerror(
                        "خطأ",
                        "❌ لا يمكن حذف هذا المورد لأنه مرتبط بمنتجات\nقم بحذف المنتجات المرتبطة أولاً",
                    )
                else:
                    messagebox.showerror("خطأ", f"❌ حدث خطأ: {str(e)}")
