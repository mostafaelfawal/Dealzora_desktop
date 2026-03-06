def export_products(products, get_category):
    """Export products to Excel/CSV"""
    from tkinter import filedialog, messagebox
    import csv

    filename = filedialog.asksaveasfilename(
        title="حفظ ملف التصدير",
        defaultextension=".xlsx",
        initialfile="products",
        filetypes=[
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*"),
        ],
    )

    if filename:
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(
                    [
                        "ID",
                        "الاسم",
                        "الباركود",
                        "سعر الشراء",
                        "سعر البيع",
                        "الكمية",
                        "حد التنبيه",
                        "الفئة",
                    ]
                )

                # Write data
                for product in products:
                    category_name = get_category(product[6])
                    writer.writerow(
                        [
                            product[0],
                            product[1],
                            product[2] or "",
                            product[3],
                            product[4],
                            product[5],
                            product[8],
                            category_name,
                        ]
                    )

            messagebox.showinfo("نجاح", f"✅ تم تصدير {len(products)} منتج بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"❌ فشل التصدير: {str(e)}")
