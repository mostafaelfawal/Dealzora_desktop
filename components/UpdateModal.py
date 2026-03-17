import requests
import os
import sys
import threading
from utils.image import image
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkProgressBar


class UpdateModal:
    def __init__(self, root, version, url, on_close=None):
        self.root = root
        self.version = version
        self.url = url
        self.on_close_callback = on_close  # callback للـ splash

        self.overlay = None
        self.frame = None
        self.disabled_widgets = []
        self.progress_bar = None
        self.percent_label = None
        self.size_label = None
        self.update_button = None

        self.init_overlay()

    def init_overlay(self):
        # Overlay لتعتيم الخلفية
        self.overlay = CTkFrame(self.root, fg_color="#000000")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()

        # تعطيل كل عناصر self.root ماعدا overlay نفسه
        for widget in self.root.winfo_children():
            if widget != self.overlay:
                try:
                    widget.configure(state="disabled")
                    self.disabled_widgets.append(widget)
                except:
                    pass

        # Frame التحديث في المنتصف
        self.frame = CTkFrame(
            self.overlay,
            width=450,
            height=360,
            corner_radius=15,
            border_width=2,
            border_color="#00a0df",
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_frame = CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(pady=20, padx=5)

        icon_label = CTkLabel(
            header_frame, text="", image=image("assets/icon.png", (100, 100))
        )
        icon_label.pack(side="left", padx=10)

        text_frame = CTkFrame(header_frame, fg_color="transparent")
        text_frame.pack(side="left", padx=10)

        CTkLabel(
            text_frame,
            text="تحديث متوفر!",
            font=("Cairo", 20, "bold"),
            text_color="#0284C7",
        ).pack(anchor="w")
        CTkLabel(
            text_frame,
            text=f"Dealzora {self.version}v | متوفر الآن للتحميل.",
            font=("Cairo", 16, "bold"),
            text_color="#0369A1",
        ).pack(anchor="w")

        # Progress bar (مخفي أولاً)
        progress_frame = CTkFrame(self.frame, fg_color="transparent")
        progress_frame.pack(pady=10)

        self.progress_bar = CTkProgressBar(progress_frame, width=300)
        self.progress_bar.set(0)
        self.progress_bar.pack()
        self.progress_bar.pack_forget()

        self.percent_label = CTkLabel(
            progress_frame, text="0%", font=("Cairo", 16, "bold")
        )
        self.percent_label.pack(pady=5)
        self.percent_label.pack_forget()

        self.size_label = CTkLabel(
            progress_frame, text="...جاري معاينة الرابط", font=("Cairo", 14, "bold")
        )
        self.size_label.pack()
        self.size_label.pack_forget()

        # Buttons
        button_frame = CTkFrame(self.frame, fg_color="transparent")
        button_frame.pack(pady=20)

        self.update_button = CTkButton(
            button_frame,
            text="تحديث الآن",
            width=140,
            corner_radius=20,
            fg_color="#0EA5E9",
            hover_color="#0284C7",
            text_color="white",
            font=("Arial", 20, "bold"),
            command=self.start_update,
        )
        self.update_button.pack(side="right", padx=10)

        CTkButton(
            button_frame,
            text="لاحقاً",
            width=140,
            corner_radius=20,
            fg_color="#E0F2FE",
            hover_color="#BAE6FD",
            text_color="#0284C7",
            font=("Arial", 20, "bold"),
            border_width=2,
            border_color="#0EA5E9",
            command=self.destroy,
        ).pack(side="right", padx=10)

    def start_update(self):
        self.update_button.configure(state="disabled")
        self.progress_bar.pack()
        self.percent_label.pack()
        self.size_label.pack()
        threading.Thread(target=self.download_update, daemon=True).start()

    def download_update(self):
        try:
            r = requests.get(self.url, stream=True)
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            temp_update = os.path.join(project_root, "Dealzora_new.exe")
            print("Temp update path:", temp_update)
            with open(temp_update, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = downloaded / total_size
                            self.root.after(
                                0, self.update_progress, percent, downloaded, total_size
                            )
            self.root.after(0, self.finish_update)
        except Exception as e:
            print("Update error:", e)

    def update_progress(self, percent, downloaded, total_size):
        if self.progress_bar.winfo_exists():
            self.progress_bar.set(percent)
            self.percent_label.configure(text=f"{int(percent*100)}%")
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            self.size_label.configure(text=f"{downloaded_mb:.2f} / {total_mb:.2f} MB")

    def finish_update(self):
        self.percent_label.configure(text="تم التحميل ✓")
        self.size_label.configure(text="")

        import subprocess
        import os
        # المسار الكامل للملف
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        updater_path = os.path.join(project_root, "Dealzora_update.exe")
        if not os.path.exists(updater_path):
            from tkinter import messagebox
            messagebox.showerror("تحديث فشل", "ملف التحديث Dealzora_update.exe غير موجود!")
            return

        subprocess.Popen(updater_path)
        self.root.after(500, self.root.quit())

    def destroy(self):
        # إعادة تفعيل العناصر
        for widget in self.disabled_widgets:
            try:
                widget.configure(state="normal")
            except:
                pass
        self.disabled_widgets.clear()

        if self.frame.winfo_exists():
            self.frame.destroy()
        if self.overlay.winfo_exists():
            self.overlay.destroy()

        # استدعاء callback لو موجود
        if self.on_close_callback:
            self.on_close_callback()
