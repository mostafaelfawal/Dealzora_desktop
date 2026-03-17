from customtkinter import CTkButton
from utils.image import image
from utils.backup_database import backup_database


class BackupButton:
    def __init__(self, parent, get_save_path_callback):
        self.get_save_path_callback = get_save_path_callback
        CTkButton(
            parent,
            text="نسخ احتياطي للبيانات",
            width=120,
            fg_color="#25b3eb",
            hover_color="#1b92c2",
            font=("Cairo", 20, "bold"),
            image=image("assets/backup_db.png"),
            command=self.handle_backup,
        ).pack(side="left", padx=5)

    def handle_backup(self):
        path = self.get_save_path_callback()
        backup_database(path, True)