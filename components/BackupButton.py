from customtkinter import CTkButton
from tkinter.messagebox import showinfo
from utils.image import image
from utils.backup_database import backup_database

class BackupButton:
    def __init__(self, parent):
        CTkButton(
            parent,
            text="نسخ احتياطي للبيانات",
            width=120,
            fg_color="#25b3eb",
            hover_color="#1b92c2",
            font=("Cairo", 20, "bold"),
            image=image("assets/backup_db.png"),
            command=lambda: (
                backup_database(),
                showinfo("تم", "تم عمل نسخة احتياطية\nفي ملف backup/dealzora.db"),
            ),
        ).pack(side="left", padx=5)
