from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkScrollableFrame,
    set_appearance_mode,
)
from tkinter.messagebox import askokcancel
from ui.Sales.SaleState import SaleState
from ui.Sales.services.DataService import DataService
from utils.image import image
from utils.clear import clear
from utils.trial import get_remaining_days
from utils.license import is_license_valid

# import UIs
from ui.Sales.sale_screen import Sale
from ui.Products import Products
from ui.Users import UsersManagement
from ui.Stock import Stock
from ui.Reports import Reports
from ui.Customers import Customers
from ui.Invoices import Invoices
from ui.Settings import Settings
from ui.RejectUI import RejectUI
from ui.Suppliers import Suppliers


class Layout:
    def __init__(
        self,
        root,
        customers_db,
        products_db,
        user_id,
        users_db,
        sale_itmes_db,
        sales_db,
        stock_movements_db,
        suppliers_db,
        settings,
        con,
        cur,
    ):
        self.root = root
        self.customers_db = customers_db
        self.products_db = products_db
        self.uid = user_id
        self.users_db = users_db
        self.sale_itmes_db = sale_itmes_db
        self.sales_db = sales_db
        self.stock_movements_db = stock_movements_db
        self.suppliers_db = suppliers_db
        self.settings = settings
        self.con = con
        self.cur = cur

        tax_rate = self.settings.get_setting("tax")
        
        self.data_service = DataService(
            self.products_db,
            self.customers_db,
            self.stock_movements_db,
            self.sales_db,
            self.sale_itmes_db,
            self.settings,
            self.get_edit_price_permission()
        )
        
        self.sale_state = SaleState(tax_rate, self.data_service)

        self.sidebar_collapsed = False

        theme = self.settings.get_setting("theme")
        set_appearance_mode(theme)
        self.root.title("Dealzora | Basic")

        clear(self.root)
        self.init_side_bar()

        self.main_frame = CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both")

        self.init_ui()

    def init_ui(self):
        CTkLabel(
            self.main_frame,
            text="",
            image=image("assets/icon.png", size=(100, 100)),
            font=("Cairo", 50, "bold"),
        ).pack(pady=(10, 0))

        CTkLabel(
            self.main_frame, text="Dealzora اهلا بك في", font=("Cairo", 50, "bold")
        ).pack(pady=(10, 0))

        CTkLabel(
            self.main_frame, text="لإدارة المتاجر بأحترافيه", font=("Cairo", 40)
        ).pack()

        CTkLabel(
            self.main_frame, text="Powered by Softvanta", font=("Cairo", 15)
        ).pack(side="bottom")

        CTkLabel(self.main_frame, text="v1.4.6", font=("Cairo", 15)).pack(
            pady=(50, 0), side="bottom"
        )

    def init_side_bar(self):
        self.side_buttons = [
            {"text": "بيع", "icon": "assets/pos.png", "screen": "sale"},
            {"text": "منتجات", "icon": "assets/products.png", "screen": "products"},
            {"text": "مستخدم", "icon": "assets/users.png", "screen": "users"},
            {"text": "مخزون", "icon": "assets/stock.png", "screen": "stock"},
            {"text": "تقارير", "icon": "assets/reports.png", "screen": "reports"},
            {"text": "عملاء", "icon": "assets/customers.png", "screen": "customers"},
            {"text": "فواتير", "icon": "assets/invoices.png", "screen": "invoices"},
            {
                "text": "الموردين",
                "icon": "assets/suppliers.png",
                "screen": "suppliers",
            },
            {"text": "الأعدادات", "icon": "assets/settings.png", "screen": "settings"},
        ]

        self.side_bar = CTkFrame(self.root, border_width=1, width=250)
        self.side_bar.pack(side="right", fill="y")
        self.side_bar.pack_propagate(False)

        # زر Collapse
        CTkButton(
            self.side_bar,
            text="☰",
            width=40,
            command=self.toggle_sidebar,
        ).pack(fill="x", pady=5)

        # Scrollable Frame
        self.scroll_frame = CTkScrollableFrame(self.side_bar)
        self.scroll_frame.pack(fill="both", expand=True)

        if not is_license_valid():
            days = get_remaining_days()
            self.dealzora_title = CTkLabel(
                self.scroll_frame,
                text=f"Dealzora | الفترة التجريبيه\nباقي {days} يوم🕐",
                font=("Cairo", 14),
                text_color=("#997a00", "#facc15"),
            )
            self.dealzora_title.pack()
        else:
            self.dealzora_title = CTkLabel(
                self.scroll_frame,
                image=image("assets/icon.png"),
                compound="right",
                text="Dealzora",
                font=("Cairo", 30, "bold"),
                text_color="#00b7ff",
            )
            self.dealzora_title.pack(padx=4)

        self.buttons_refs = []

        for btn in self.side_buttons:
            b = CTkButton(
                self.scroll_frame,
                text=btn["text"],
                image=image(btn["icon"]),
                command=lambda s=btn["screen"]: self.change_screen(s),
                font=("Cairo", 20, "bold"),
                corner_radius=15,
                fg_color="#0078da",
                hover_color="#0060af",
            )
            b.original_text = btn["text"]
            b.pack(padx=10, pady=5, fill="x")
            self.buttons_refs.append(b)

        # زر خروج
        self.exit_btn = CTkButton(
            self.scroll_frame,
            text="خروج",
            image=image("assets/exit.png"),
            font=("Cairo", 20, "bold"),
            command=self.quit_window,
            corner_radius=15,
            fg_color="#c62828",
            hover_color="#b71c1c",
        )
        self.exit_btn.pack(padx=10, pady=5, fill="x")

    def toggle_sidebar(self):
        """Collapse / Expand"""
        if self.sidebar_collapsed:
            self.side_bar.configure(width=250)
            if is_license_valid():
                self.dealzora_title.configure(text="Dealzora")
            else:
                self.dealzora_title.configure(
                    text=f"Dealzora | الفترة التجريبيه\nباقي {get_remaining_days()} يوم🕐"
                )

            for b in self.buttons_refs:
                b.configure(text=b.original_text)

            self.exit_btn.configure(text="خروج")

        else:
            self.side_bar.configure(width=120)
            self.dealzora_title.configure(text="")
            for b in self.buttons_refs:
                b.configure(text="")

            self.exit_btn.configure(text="")

        self.sidebar_collapsed = not self.sidebar_collapsed

    def quit_window(self):
        if askokcancel("تأكد", "ستخرج من البرنامج الأن"):
            self.root.quit()
            
    def get_edit_price_permission(self):
        return self.users_db.check_permission(self.uid, "edit_price_in_invoice")

    def change_screen(self, screen_type: str):
        clear(self.main_frame)

        roles = {
            "sale": "cashier_interface",
            "products": "products_management",
            "stock": "inventory_management",
            "reports": "reports_view",
            "customers": "customers_management",
            "invoices": "invoices_management",
            "settings": "settings_edit",
            "users": "users_management",
            "suppliers": "suppliers_management",
        }

        if not self.users_db.check_permission(self.uid, roles.get(screen_type, "all")):
            RejectUI(self.main_frame)
            return

        if screen_type == "sale":
            Sale(self.main_frame, self.settings, self.sale_state, self.data_service)

        elif screen_type == "products":
            Products(self.main_frame, self.products_db, self.suppliers_db)

        elif screen_type == "users":
            UsersManagement(self.main_frame, self.users_db)

        elif screen_type == "stock":
            Stock(
                self.main_frame,
                self.users_db,
                self.uid,
                self.products_db,
                self.suppliers_db,
                self.stock_movements_db,
                self.settings,
            )

        elif screen_type == "reports":
            Reports(self.main_frame, self.cur)

        elif screen_type == "customers":
            Customers(self.main_frame, self.customers_db)

        elif screen_type == "invoices":
            Invoices(
                self.main_frame,
                self.con,
                self.sales_db,
                self.sale_itmes_db,
                self.customers_db,
                self.products_db,
                self.stock_movements_db,
                self.settings,
            )

        elif screen_type == "suppliers":
            Suppliers(self.main_frame, self.suppliers_db, self.uid, self.users_db)

        else:
            Settings(self.main_frame, self.settings)
