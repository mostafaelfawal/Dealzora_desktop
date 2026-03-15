from customtkinter import set_appearance_mode, CTk
from sqlite3 import connect
from os import makedirs
from layout import Layout
from utils.backup_database import backup_database
from utils.trial import init_trial
from ui.Splash_screen import SplashScreen

# ============== Data bases ==============
from models.customers import CustomersModel
from models.products import ProductsModel
from models.users import UsersModel
from models.sale_items import SaleItmesModel
from models.sales import SalesModel
from models.stock_movements import StockMovementsModel
from models.supplier import SupplierModel
from models.settings import SettingsModel


class Dealzora:
    def __init__(self, root):
        self.root = root
        self.init_window()
        self.init_db()
        init_trial()
        
        SplashScreen(self.root, self.start_app)
        
        
            
    def start_app(self):
        from ui.Auth import Auth
        Auth(self.root, lambda uid: self.on_success(uid), self.users_db)

    def init_window(self):
        self.root.title("Dealzora | Basic")
        self.root.geometry("650x500")
        self.root.iconbitmap("icon.ico")
        set_appearance_mode("system")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        backup_database()
        self.root.destroy()

    def init_db(self):
        makedirs("db", exist_ok=True)
        self.con = connect("db/dealzora.db")
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA foreign_key = ON")

        self.customers_db = CustomersModel(self.cur, self.con)
        self.products_db = ProductsModel(self.cur, self.con)
        self.users_db = UsersModel(self.cur, self.con)
        self.sale_itmes_db = SaleItmesModel(self.cur, self.con)
        self.sales_db = SalesModel(self.cur, self.con)
        self.stock_movements_db = StockMovementsModel(self.cur, self.con)
        self.suppliers_db = SupplierModel(self.cur, self.con)
        self.settings = SettingsModel()

    def on_success(self, user_id):
        Layout(
            self.root,
            self.customers_db,
            self.products_db,
            user_id,
            self.users_db,
            self.sale_itmes_db,
            self.sales_db,
            self.stock_movements_db,
            self.suppliers_db,
            self.settings,
            self.con,
            self.cur,
        )


if __name__ == "__main__":
    pro = CTk()
    Dealzora(pro)
    pro.mainloop()
