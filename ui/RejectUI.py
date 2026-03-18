from customtkinter import CTkLabel
from utils.image import image


class RejectUI:
    def __init__(self, root):
        self.root = root
        CTkLabel(
            self.root, text="", image=image("assets/unauthorized.png", (100, 100))
        ).pack(pady=5, padx=5)

        CTkLabel(
            self.root,
            text="غير مسموح لك بالدخول لهذه الواجهه",
            font=("Cairo", 40, "bold"),
            text_color="#0084ff",
        ).pack()
