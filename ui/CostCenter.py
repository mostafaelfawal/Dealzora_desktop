from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkLabel,
    CTkFrame,
    CTkToplevel,
    CTkTextbox,
)

from utils.image import image


class CostCenterDialog(CTkToplevel):
    def __init__(self):
        super().__init__()
        self.add_sponsor_exist = False

        self.config_dialgo()

        CTkLabel(
            self,
            text="اسم المركز",
            font=("Cairo", 20),
        ).pack(padx=10, pady=10)

        CTkEntry(
            self,
            placeholder_text="أدخل اسم المركز",
            font=("Cairo", 20),
        ).pack(padx=10, pady=10)

        CTkLabel(
            self,
            text="الوصف",
            font=("Cairo", 20),
        ).pack(padx=10, pady=10)

        CTkTextbox(
            self,
            font=("Cairo", 20),
            height=100,
        ).pack(padx=10, pady=10)

        sponsors_frame = CTkFrame(self, fg_color="transparent")
        sponsors_frame.pack(padx=10, pady=10, fill="x")

        CTkLabel(
            sponsors_frame,
            text="الممولين",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=10)

        CTkButton(
            sponsors_frame,
            text="",
            image=image("assets/add.png"),
            font=("Cairo", 20),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            command=self.create_sponsor,
        ).pack(side="left", padx=10, pady=10)

    def create_sponsor(self):
        if self.add_sponsor_exist:
            return

        self.sponsor_frame = CTkFrame(self, border_width=1, border_color="#ccc")
        self.sponsor_frame.pack(padx=10, pady=10, fill="x")

        row_1 = CTkFrame(self.sponsor_frame, fg_color="transparent")
        row_1.pack(padx=10, pady=10, fill="x")
        CTkLabel(
            row_1,
            text="اسم الممول",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=5)

        CTkEntry(
            row_1,
            placeholder_text="أدخل اسم الممول",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=5)

        row_2 = CTkFrame(self.sponsor_frame, fg_color="transparent")
        row_2.pack(padx=10, pady=10, fill="x")
        CTkLabel(
            row_2,
            text="المساهمه",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=5)

        CTkEntry(
            row_2,
            placeholder_text="أدخل مبلغ المساهمة",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=5)

        row_3 = CTkFrame(self.sponsor_frame, fg_color="transparent")
        row_3.pack(padx=10, pady=10, fill="x")
        CTkLabel(
            row_3,
            text="النسبه",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=5)

        CTkEntry(
            row_3,
            placeholder_text="أدخل نسبة اللي ياخدها المساهم",
            font=("Cairo", 20),
        ).pack(side="right", padx=10, pady=5)

        CTkButton(
            self.sponsor_frame,
            text="",
            image=image("assets/checked.png"),
            corner_radius=50,
            width=25,
            height=25,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            command=self.save_sponsor,
        ).pack(padx=10, pady=10)

        self.add_sponsor_exist = True
        
    def save_sponsor(self):
        self.sponsor_frame.destroy()
        CTkFrame(self, border_width=1, border_color="#ccc").pack(padx=10, pady=10, fill="x")
        self.add_sponsor_exist = False

    def config_dialgo(self):
        self.title("اضافة مركز تكلفة | Dealzora")
        self.geometry("400x300")
        self.grab_set()
        self.focus_force()


class CostCenter:
    def __init__(self, root):
        self.root = root

        self._build_title()
        self._build_actions_frame()

    def _build_title(self):
        CTkLabel(
            self.root,
            text="مراكز التكلفة",
            image=image("assets/cost_center.png"),
            font=("Cairo", 40, "bold"),
            compound="left",
        ).pack(padx=10, pady=10)

    def _build_actions_frame(self):
        actions_frame = CTkFrame(self.root)
        actions_frame.pack(padx=10, pady=10, fill="x")

        CTkButton(
            actions_frame,
            text="اضافة مركز تكلفة",
            image=image("assets/add.png"),
            font=("Cairo", 20),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            corner_radius=30,
            command=self.open_add_dialog,
        ).grid(row=0, column=0, padx=10, pady=10)

    def open_add_dialog(self):
        CostCenterDialog()
