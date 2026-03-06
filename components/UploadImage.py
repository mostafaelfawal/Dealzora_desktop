from tkinter import filedialog, messagebox
from customtkinter import CTkButton, CTkLabel
from PIL import Image
from utils.image import image


class UploadImage:
    def __init__(self, parent):
        self.parent = parent
        self.default_image = "assets/icon.png"
        self.selected_image = self.default_image

        self.img_preview = image(self.selected_image, (60, 60))
        self.label_image = CTkLabel(self.parent, text="", image=self.img_preview)

        self.label_image.pack(pady=5, padx=5)

        CTkButton(
            self.parent,
            text="اختر صورة",
            font=("Cairo", 24, "bold"),
            fg_color="#00be8f",
            hover_color="#008d6a",
            command=self.import_image,
        ).pack(pady=(20, 0))

    def import_image(self):
        image_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")]
        )

        if image_path:
            try:
                img = Image.open(image_path)
                img.verify()
                self.selected_image = image_path
                self.img_preview = image(image_path, (60, 60))
                self.label_image.configure(image=self.img_preview)
            except:
                messagebox.showerror("غير صالحه", "صورة غير صالحه!")

    def set_image(self, path):
        self.selected_image = path
        self.img_preview = image(path, (60, 60))
        self.label_image.configure(image=self.img_preview)

    def get_image(self):
        return self.selected_image
