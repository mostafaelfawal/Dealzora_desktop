import pandas as pd
from tkinter import filedialog, messagebox
import threading
from sqlite3 import connect
from models.products import ProductsModel


def import_products(self):
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        return

    def worker():
        try:
            conn = connect("db/dealzora.db")
            cur = conn.cursor()
            products_db = ProductsModel(cur, conn)

            # قراءة الملف
            if file_path.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)

            # تحويل أسماء الأعمدة لعربية/انجليزية موحدة
            df_columns = {col.lower(): col for col in df.columns}
            column_map = {}
            # احتمالات لأسماء الأعمدة
            name_cols = ["name", "الاسم", "الأسم", "الاسم المنتج", "product_name", "product name"]
            barcode_cols = ["barcode", "code", "كود", "الباركود"]
            buy_price_cols = ["buy_price", "سعر الشراء", "cost", "الشراء", "شراء"]
            sell_price_cols = ["sell_price", "سعر البيع", "price", "السعر", "سعر"]
            quantity_cols = [
                "quantity",
                "كمية",
                "qty",
                "الكمية",
                "in_stock",
                "in",
                "في المخزون",
            ]
            low_stock_cols = ["low_stock", "حد التنبيه", "min_qty"]
            category_cols = ["الفئة", "category", "فئة"]

            def find_col(possible_names):
                for n in possible_names:
                    if n.lower() in df_columns:
                        return df_columns[n.lower()]
                return None

            column_map["name"] = find_col(name_cols)
            column_map["barcode"] = find_col(barcode_cols)
            column_map["buy_price"] = find_col(buy_price_cols)
            column_map["sell_price"] = find_col(sell_price_cols)
            column_map["quantity"] = find_col(quantity_cols)
            column_map["low_stock"] = find_col(low_stock_cols)
            column_map["category"] = find_col(category_cols)

            # تأكد أن العمود الأساسي موجود (الاسم)
            if not column_map["name"]:
                messagebox.showerror("خطأ", "لا يوجد عمود للاسم في الملف")
                return

            products_to_add = []
            for _, row in df.iterrows():
                name = str(row[column_map["name"]]).strip()
                if not name:
                    continue
                barcode = (
                    str(row[column_map["barcode"]]).strip()
                    if column_map["barcode"]
                    else None
                )
                buy_price = (
                    float(row[column_map["buy_price"]])
                    if column_map["buy_price"]
                    and pd.notna(row[column_map["buy_price"]])
                    else 0
                )
                sell_price = (
                    float(row[column_map["sell_price"]])
                    if column_map["sell_price"]
                    and pd.notna(row[column_map["sell_price"]])
                    else 0
                )
                quantity = (
                    int(row[column_map["quantity"]])
                    if column_map["quantity"] and pd.notna(row[column_map["quantity"]])
                    else 0
                )
                low_stock = (
                    int(row[column_map["low_stock"]])
                    if column_map["low_stock"]
                    and pd.notna(row[column_map["low_stock"]])
                    else 5
                )
                category = (
                    str(row[column_map["category"]]).strip()
                    if column_map["category"]
                    else ""
                )

                products_to_add.append(
                    (
                        name,
                        barcode,
                        buy_price,
                        sell_price,
                        quantity,
                        low_stock,
                        category,
                    )
                )

            # إضافة المنتجات في DB
            for prod in products_to_add:
                products_db.add_product(
                    name=prod[0],
                    barcode=prod[1],
                    buy_price=prod[2],
                    sell_price=prod[3],
                    quantity=prod[4],
                    image_path=None,
                    low_stock=prod[5],
                    category_name=prod[6],
                )

            conn.commit()
            conn.close()

            def update_ui():
                conn_ui = connect("db/dealzora.db")
                cur_ui = conn_ui.cursor()
                products_ui = ProductsModel(cur_ui, conn_ui)

                self.products = products_ui.get_products()
                self.refresh_table()

                conn_ui.close()

                messagebox.showinfo(
                    "تم", f"تم اضافة {len(products_to_add)} منتجات بنجاح"
                )

            self.root.after(0, update_ui)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("خطأ", str(e)))

    # تشغيل في الخلفية
    threading.Thread(target=worker, daemon=True).start()
