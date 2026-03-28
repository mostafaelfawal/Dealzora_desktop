import threading
from customtkinter import CTkLabel, CTkFrame, CTkProgressBar
from components.UpdateModal import UpdateModal
from utils.image import image
from utils.license import is_activated
from utils.update_checker import check_for_update

APP_VERSION = "1.7.7"

class SplashScreen:
    def __init__(self, root, on_finish):
        self.root = root
        self.on_finish = on_finish  # callback لتشغيل البرنامج الرئيسي بعد الـ splash
        self.frame = None
        self.progress_bar = None
        self.status_label = None
        self.version_label = None
        self.check_thread = None

        self.init_splash()

    def init_splash(self):
        # Overlay أساسي لتعتيم الخلفية
        self.frame = CTkFrame(self.root, width=500, height=350, corner_radius=15, border_width=2, border_color="#00b8ae")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        self.frame.lift()

        # شعار Dealzora
        logo = CTkLabel(self.frame, text="", image=image("assets/icon.png", (120, 120)))
        logo.pack(pady=20)
        
        CTkLabel(self.frame, text="Dealzora", font=("Cairo", 30, "bold"), text_color="#0084ff").pack(pady=5)

        # Progress bar
        self.progress_bar = CTkProgressBar(self.frame, width=300)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, padx=20)

        # Status label
        self.status_label = CTkLabel(self.frame, text="...جارٍ التحقق من التحديثات", font=("Cairo", 16, "bold"))
        self.status_label.pack(pady=5)

        # Version label
        self.version_label = CTkLabel(self.frame, text=f"vالإصدار الحالي: {APP_VERSION}", font=("Cairo", 14, "bold"))
        self.version_label.pack(pady=5)
        
        CTkLabel(self.frame, text="Powered By Softvanta", font=("Cairo", 12, "bold")).pack(pady=(0, 10))

        # بدء فحص التحديث في Thread منفصل
        self.check_thread = threading.Thread(target=self.check_update, daemon=True)
        self.check_thread.start()

    def check_update(self):
        try:
            for i in range(50):
                # وهميًا نتحرك بالـ ProgressBar حتى نصل لفحص التحديث
                self.progress_bar.set(i/100)
                threading.Event().wait(0.01)

            version, url = check_for_update()  # دالة التحقق من التحديث

            # ملء ProgressBar بعد الانتهاء
            self.root.after(0, lambda: self.progress_bar.set(1.0))

            if version:
                # فتح نافذة التحديث، مع عدم إغلاق الـ Splash تلقائيًا
                self.root.after(500, lambda: UpdateModal(self.root, version, url, on_close=self.finish_splash))
            else:
                self.root.after(1000, self.finish_splash)

        except Exception as e:
            self.root.after(0, self.finish_splash)

    def finish_splash(self):
        if self.frame and self.frame.winfo_exists():
            self.frame.destroy()
        self.root.state("zoomed")
        if is_activated():
            self.on_finish()
        else:
            from ui.license_screen import LicenseScreen
            LicenseScreen(self.root, self.on_finish)
