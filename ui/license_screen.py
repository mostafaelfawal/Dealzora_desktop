from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
from utils.license import get_machine_guid, generate_expected_license, save_license
from tkinter.messagebox import showinfo


class LicenseScreen(CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.pack(expand=True, fill="both", padx=30, pady=30)

        CTkLabel(self, text="🔐 تفعيل البرنامج", font=("Cairo", 26, "bold")).pack(
            pady=15
        )

        CTkLabel(
            self,
            text=(
                "للتفعيل:\n"
                "انسخ كود الجهاز ●\n"
                "ابعت الكود على الرقم واتساب: 01151083509 ●\n"
                "سيتم التواصل معك في أقرب وقت بكود التفعيل ●\n"
                "الصق كود التفعيل في الحقل بالأسفل ثم شغّل البرنامج ●"
            ),
            font=("Cairo", 14),
            justify="right",
            text_color="#9ca3af",
            wraplength=500,
        ).pack(pady=(5, 15))

        CTkLabel(self, text="كود جهازك", font=("Cairo", 16)).pack(pady=(20, 5))

        self.guid_label = CTkLabel(
            self, text=get_machine_guid(), font=("Cairo", 14), text_color="#93c5fd"
        )
        self.guid_label.pack()

        self.entry = CTkEntry(
            self, width=350, placeholder_text="ادخل كود التفعيل", font=("Cairo", 16)
        )
        self.entry.pack(pady=20)

        self.msg = CTkLabel(self, text="", text_color="red", font=("Cairo", 14))
        self.msg.pack()

        CTkButton(
            self,
            text="✔ تفعيل الترخيص",
            height=45,
            font=("Cairo", 18),
            command=lambda: self.activate(on_success),
        ).pack(pady=10)

        CTkButton(
            self,
            text="📋 نسخ كود الجهاز",
            command=self.copy_guid,
            font=("Cairo", 18),
        ).pack()

        CTkButton(
            self,
            text="▶ الدخول بالفترة التجريبية",
            height=40,
            fg_color="#22c55e",
            text_color="black",
            hover_color="#16a34a",
            font=("Cairo", 16),
            command=lambda: self.enter_trial(on_success),
        ).pack(pady=10)

    def enter_trial(self, on_success):
        self.destroy()
        on_success()

    def copy_guid(self):
        self.clipboard_clear()
        self.clipboard_append(get_machine_guid())
        self.msg.configure(text="تم نسخ كود الجهاز")

    def activate(self, on_success):
        if self.entry.get().strip() == generate_expected_license():
            save_license(self.entry.get().strip())
            showinfo("تم", "تم تفعيل البرنامج بنجاح")
            self.destroy()
            on_success()
        else:
            self.msg.configure(text="كود التفعيل غير صحيح")
