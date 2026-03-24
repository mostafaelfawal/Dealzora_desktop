from customtkinter import CTkToplevel, CTkLabel, CTkEntry, CTkFrame, CTkButton
from tkinter import messagebox
from utils.center_modal import center_modal
from utils.image import image
from utils.key_shortcut import key_shortcut
from utils.is_number import is_number


class CustomerModal:
    def __init__(
        self, add_customer, tree=None, edit_customer=None, mode="add", refresh_results=None, customers_dialog=None
    ):
        self.tree = tree
        self.add_customer = add_customer
        self.edit_customer = edit_customer
        self.refresh_results = refresh_results
        self.customers_dialog = customers_dialog
        selected_data = None

        if mode == "edit" and self.tree:
            selected = self.tree.tree.selection()
            if not selected:
                return messagebox.showwarning("تنبيه", "اختر عميل")
            selected_data = self.tree.tree.item(selected[0])["values"]
            self.customer_selected_phone = selected_data[2]

        modal = CTkToplevel()
        modal.title(
            "اضافة عميل | Dealzora" if mode == "add" else "تعديل العميل | Dealzora"
        )
        center_modal(modal)

        fields = ["*الأسم", "الهاتف", "حجم الدين"]
        self.entries = {}
        for i, f in enumerate(fields):
            CTkLabel(modal, text=f, font=("Cairo", 18, "bold")).grid(
                row=i, column=1, sticky="e", padx=10, pady=8
            )
            entry = CTkEntry(
                modal, border_width=1, width=250, font=("Cairo", 16, "bold")
            )
            entry.grid(row=i, column=0, sticky="w", padx=10, pady=8)
            if selected_data:
                if f == "حجم الدين":
                    entry.insert(0, selected_data[1])
                elif f == "الهاتف":
                    entry.insert(0, "" if selected_data[2] == "—" else selected_data[2])
                elif f == "*الأسم":
                    entry.insert(0, selected_data[3])
            self.entries[f] = entry

        def clear_fields():
            for e in self.entries.values():
                e.delete(0, "end")

        def save(event=None):
            name = self.entries["*الأسم"].get().strip()
            phone = self.entries["الهاتف"].get().strip() or None
            debt = self.entries["حجم الدين"].get().strip() or 0
            if not self.validate_customer_fields(name, debt):
                return
            if mode == "add":
                self.add_customer(name, phone, debt, modal)
            else:
                self.edit_customer(name, phone, debt, selected_data[0], modal)

            if self.refresh_results:
                self.refresh_results()
            if self.customers_dialog:
                center_modal(self.customers_dialog)

        key_shortcut(modal, "<Return>", save)

        btn_frame = CTkFrame(modal, fg_color="transparent")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        CTkButton(
            btn_frame,
            text="اضافة العميل" if mode == "add" else "تعديل العميل",
            font=("Cairo", 18, "bold"),
            width=150,
            fg_color="#2563eb",
            hover_color="#1749b6",
            image=image("assets/add.png" if mode == "add" else "assets/edit.png"),
            command=save,
        ).pack(side="right", padx=10)

        CTkButton(
            btn_frame,
            text="تنظيف الحقول",
            font=("Cairo", 18, "bold"),
            width=150,
            fg_color="#dc2626",
            hover_color="#a11616",
            image=image("assets/clear.png"),
            command=clear_fields,
        ).pack(side="right", padx=10)

    def validate_customer_fields(self, name, debt):
        if not name:
            messagebox.showerror("خطأ", "اكتب اسم العميل اولاً!")
            return False
        if not is_number(debt):
            messagebox.showerror("خطأ", "يجب ادخال حجم الدين بشكل صحيح")
            return False
        return True
