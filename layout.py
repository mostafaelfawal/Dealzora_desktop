from customtkinter import CTkFrame, CTkLabel, CTkButton, StringVar, set_appearance_mode
from tkinter.messagebox import askokcancel
from utils.image import image
from utils.clear import clear
from utils.trial import get_remaining_days
from utils.license import is_license_valid

# import UIs
from ui.Sale import Sale
from ui.Products import Products
from ui.Users import UsersManagement
from ui.Stock import Stock
from ui.Reports import Reports
from ui.Customers import Customers
from ui.Invoices import Invoices
from ui.Settings import Settings
from ui.RejectUI import RejectUI


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
        theme = self.settings.get_setting("theme")
        set_appearance_mode(theme)
        self.root.title("Dealzora | Basic")

        clear(self.root)
        self.init_sale_vars()
        self.init_side_bar()
        self.main_frame = CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(expand=True)
        self.init_ui()

    def init_sale_vars(self):
        self.selected_products = []
        self.customer_var = StringVar(value="نقدي")
        self.customer_id = None
        self.discount_type = "amount"
        self.discount_value = 0.0

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
            self.main_frame, text="Powered by Mostafa hamdi", font=("Cairo", 15)
        ).pack(side="bottom")
        CTkLabel(self.main_frame, text="v1.1.2", font=("Cairo", 15)).pack(
            pady=(50, 0), side="bottom"
        )

    def init_side_bar(self):
        self.side_buttons = [
            {
                "text": "بيع",
                "icon": "assets/pos.png",
                "com": lambda: self.change_screen("sale"),
            },
            {
                "text": "منتجات",
                "icon": "assets/products.png",
                "com": lambda: self.change_screen("products"),
            },
            {
                "text": "مستخدم",
                "icon": "assets/users.png",
                "com": lambda: self.change_screen("users"),
            },
            {
                "text": "مخزون",
                "icon": "assets/stock.png",
                "com": lambda: self.change_screen("stock"),
            },
            {
                "text": "تقارير",
                "icon": "assets/reports.png",
                "com": lambda: self.change_screen("reports"),
            },
            {
                "text": "عملاء",
                "icon": "assets/customers.png",
                "com": lambda: self.change_screen("customers"),
            },
            {
                "text": "فواتير",
                "icon": "assets/invoices.png",
                "com": lambda: self.change_screen("invoices"),
            },
            {
                "text": "الأعدادات",
                "icon": "assets/settings.png",
                "com": lambda: self.change_screen("settings"),
            },
        ]

        self.side_bar = CTkFrame(self.root, border_width=1)
        self.side_bar.pack(side="right", fill="y")

        if not is_license_valid():
            days = get_remaining_days()
            CTkLabel(
                self.side_bar,
                text=f"Dealzora | الفترة التجريبيه\nباقي {days} يوم🕐",
                font=("Cairo", 14),
                text_color=("#997a00","#facc15"),
            ).pack()
        else:
            CTkLabel(
                self.side_bar,
                image=image("assets/icon.png"),
                compound="right",
                text="Dealzora",
                font=("Cairo", 35, "bold"),
                text_color="#00b7ff",
            ).pack(padx=4)

        button_style = {
            "font": ("Cairo", 30, "bold"),
            "corner_radius": 20,
            "fg_color": "#0078da",
            "hover_color": "#0060af",
        }

        for button in self.side_buttons:
            CTkButton(
                self.side_bar,
                text=button["text"],
                image=image(button["icon"]),
                command=button["com"],
                **button_style,
            ).pack(padx=30, pady=5, fill="x")

        CTkButton(
            self.side_bar,
            text="خروج",
            image=image("assets/exit.png"),
            command=self.quit_window,
            **button_style,
        ).pack(padx=30, pady=5, fill="x")

    def quit_window(self):
        if askokcancel("تأكد", "ستخرج من البرنامج الأن"):
            self.root.quit()

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
        }

        if not self.users_db.check_permission(self.uid, roles[screen_type] or "all"):
            RejectUI(self.main_frame)
            return

        if screen_type == "sale":
            Sale(
                self.main_frame,
                self.products_db,
                self.customers_db,
                self.sales_db,
                self.sale_itmes_db,
                self.stock_movements_db,
                self.settings,
                self.selected_products,
                self.customer_var,
                self.customer_id,
                self.discount_type,
                self.discount_value,
                self.con,
            )

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
            )

        else:  # settings
            Settings(self.main_frame, self.settings)
