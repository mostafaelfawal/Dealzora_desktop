# ui/Reports.py
import tkinter as tk
from components.TreeView import TreeView
from tkinter import ttk
from customtkinter import (
    CTkFrame,
    CTkScrollableFrame,
    CTkLabel,
    CTkButton,
    CTkTabview,
    CTkEntry,
)
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from utils.format_currency import format_currency
from utils.ar_support import ar
from tkinter.messagebox import showinfo


class Reports:
    def __init__(self, root, cur):
        self.root = root
        self.cur = cur

        # إطارات رئيسية
        self.main_container = CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # عنوان الصفحة
        header_frame = CTkFrame(self.main_container, fg_color="transparent", height=50)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        CTkLabel(
            header_frame, text="التقارير والإحصائيات", font=("Cairo", 24, "bold")
        ).pack(side="right", padx=10)

        # إطار التحكم بالفترة
        self.controls_frame = CTkFrame(self.main_container, fg_color="transparent")
        self.controls_frame.pack(fill="x", pady=(0, 10))

        self.init_controls()

        # إطار التبويبات الرئيسي
        self.tab_view = CTkTabview(self.main_container)
        self.tab_view.pack(fill="both", expand=True)

        # إضافة التبويبات
        self.tab_view.add("المبيعات")
        self.tab_view.add("المخزون")
        self.tab_view.add("العملاء")
        self.tab_view.add("الموردين")
        self.tab_view.add("الأرباح")
        self.tab_view._segmented_button.configure(font=("Cairo", 16, "bold"))

        # تهيئة كل تبويب
        self.init_sales_tab()
        self.init_stock_tab()
        self.init_customers_tab()
        self.init_suppliers_tab()
        self.init_profits_tab()

        # تحميل البيانات الافتراضية
        self.load_all_reports()

    def init_controls(self):
        """تهيئة عناصر التحكم بالفترة"""
        # إطار الفلاتر
        filter_frame = CTkFrame(self.controls_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)

        # تاريخ البداية
        CTkLabel(filter_frame, text="من:", font=("Cairo", 14)).pack(
            side="right", padx=(0, 5)
        )
        self.start_date = CTkEntry(filter_frame, width=120, font=("Cairo", 14))
        self.start_date.pack(side="right", padx=5)
        self.start_date.insert(
            0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        )

        # تاريخ النهاية
        CTkLabel(filter_frame, text="إلى:", font=("Cairo", 14)).pack(
            side="right", padx=(0, 5)
        )
        self.end_date = CTkEntry(filter_frame, width=120, font=("Cairo", 14))
        self.end_date.pack(side="right", padx=5)
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # فترات سريعة
        CTkButton(
            filter_frame,
            text="آخر 7 أيام",
            font=("Cairo", 14),
            command=lambda: self.set_quick_date(7),
            width=100,
        ).pack(side="right", padx=2)

        CTkButton(
            filter_frame,
            text="آخر 30 يوم",
            font=("Cairo", 14),
            command=lambda: self.set_quick_date(30),
            width=100,
        ).pack(side="right", padx=2)

        CTkButton(
            filter_frame,
            text="آخر 90 يوم",
            font=("Cairo", 14),
            command=lambda: self.set_quick_date(90),
            width=100,
        ).pack(side="right", padx=2)

        # زر تحديث
        CTkButton(
            filter_frame,
            text="تحديث",
            font=("Cairo", 14, "bold"),
            command=self.load_all_reports,
            width=100,
            fg_color="#28a745",
            hover_color="#218838",
        ).pack(side="right", padx=20)

    def set_quick_date(self, days):
        """تعيين تاريخ سريع"""
        self.start_date.delete(0, tk.END)
        self.start_date.insert(
            0, (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        )
        self.end_date.delete(0, tk.END)
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.load_all_reports()

    def init_sales_tab(self):
        """تهيئة تبويب المبيعات"""
        tab = self.tab_view.tab("المبيعات")

        # إطار علوي للملخصات
        summary_frame = CTkFrame(tab)
        summary_frame.pack(fill="x", padx=10, pady=10)

        # ملخصات المبيعات
        self.sales_summary_widgets = {}
        summaries = [
            ("total_sales", "إجمالي المبيعات", "0"),
            ("total_invoices", "عدد الفواتير", "0"),
            ("avg_invoice", "متوسط الفاتورة", "0"),
            ("total_discounts", "إجمالي الخصومات", "0"),
        ]

        for i, (key, label, value) in enumerate(summaries):
            frame = CTkFrame(summary_frame, width=200, height=100)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            frame.grid_propagate(False)

            CTkLabel(frame, text=label, font=("Cairo", 14)).pack(pady=(10, 5))
            self.sales_summary_widgets[key] = CTkLabel(
                frame, text=value, font=("Cairo", 20, "bold")
            )
            self.sales_summary_widgets[key].pack(pady=(0, 10))

        # تكبير الأعمدة
        for i in range(4):
            summary_frame.grid_columnconfigure(i, weight=1)

        # إطار للرسوم البيانية
        charts_frame = CTkFrame(tab)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # تقسيم إلى عمودين
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)

        # رسم بياني للمبيعات اليومية
        daily_frame = CTkFrame(charts_frame)
        daily_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        CTkLabel(daily_frame, text="المبيعات اليومية", font=("Cairo", 16, "bold")).pack(
            pady=5
        )
        self.daily_sales_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.daily_sales_plot = self.daily_sales_figure.add_subplot(111)
        self.daily_sales_plot.set_facecolor("#333333")
        self.daily_sales_plot.tick_params(colors="white")
        self.daily_sales_plot.spines["bottom"].set_color("white")
        self.daily_sales_plot.spines["top"].set_color("white")
        self.daily_sales_plot.spines["left"].set_color("white")
        self.daily_sales_plot.spines["right"].set_color("white")
        self.daily_sales_plot.xaxis.label.set_color("white")
        self.daily_sales_plot.yaxis.label.set_color("white")

        self.daily_sales_canvas = FigureCanvasTkAgg(
            self.daily_sales_figure, daily_frame
        )
        self.daily_sales_canvas.get_tk_widget().pack(fill="both", expand=True)

        # رسم بياني لأكثر المنتجات مبيعاً
        top_products_frame = CTkFrame(charts_frame)
        top_products_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            top_products_frame, text="أكثر المنتجات مبيعاً", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.top_products_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.top_products_plot = self.top_products_figure.add_subplot(111)
        self.top_products_plot.set_facecolor("#333333")
        self.top_products_plot.tick_params(colors="white")
        self.top_products_plot.spines["bottom"].set_color("white")
        self.top_products_plot.spines["top"].set_color("white")
        self.top_products_plot.spines["left"].set_color("white")
        self.top_products_plot.spines["right"].set_color("white")

        self.top_products_canvas = FigureCanvasTkAgg(
            self.top_products_figure, top_products_frame
        )
        self.top_products_canvas.get_tk_widget().pack(fill="both", expand=True)

    def init_stock_tab(self):
        """تهيئة تبويب المخزون"""
        tab = self.tab_view.tab("المخزون")
        
        # إطار علوي للملخصات
        summary_frame = CTkFrame(tab)
        summary_frame.pack(fill="x", pady=10)

        self.stock_summary_widgets = {}
        summaries = [
            ("total_products", "إجمالي المنتجات", "0"),
            ("total_value", "قيمة المخزون", "0"),
            ("low_stock", "منتجات منخفضة", "0"),
            ("out_stock", "نفذ من المخزون", "0"),
        ]

        for i, (key, label, value) in enumerate(summaries):
            frame = CTkFrame(summary_frame, width=200, height=100)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            frame.grid_propagate(False)

            CTkLabel(frame, text=label, font=("Cairo", 14)).pack(pady=(10, 5))
            self.stock_summary_widgets[key] = CTkLabel(
                frame, text=value, font=("Cairo", 20, "bold")
            )
            self.stock_summary_widgets[key].pack(pady=(0, 10))

        for i in range(4):
            summary_frame.grid_columnconfigure(i, weight=1)
            
        # Scrollable Frame للتبويب كله
        scrollable_tab = CTkScrollableFrame(tab, height=400)
        scrollable_tab.pack(fill="both", expand=True, padx=10, pady=10)

        # إطار للرسوم البيانية
        charts_frame = CTkFrame(scrollable_tab)
        charts_frame.pack(fill="both", expand=True, pady=10)

        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)

        # رسم بياني لتوزيع المخزون حسب الفئة
        category_frame = CTkFrame(charts_frame)
        category_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            category_frame, text="توزيع المنتجات حسب الفئة", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.category_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.category_plot = self.category_figure.add_subplot(111)
        self.category_plot.set_facecolor("#333333")
        self.category_plot.tick_params(colors="white")

        self.category_canvas = FigureCanvasTkAgg(self.category_figure, category_frame)
        self.category_canvas.get_tk_widget().pack(fill="both", expand=True)

        # رسم بياني لحالة المخزون
        stock_status_frame = CTkFrame(charts_frame)
        stock_status_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            stock_status_frame, text="حالة المخزون", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.stock_status_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.stock_status_plot = self.stock_status_figure.add_subplot(111)
        self.stock_status_plot.set_facecolor("#333333")
        self.stock_status_plot.tick_params(colors="white")

        self.stock_status_canvas = FigureCanvasTkAgg(
            self.stock_status_figure, stock_status_frame
        )
        self.stock_status_canvas.get_tk_widget().pack(fill="both", expand=True)

        # جدول المنتجات المنخفضة
        low_stock_frame = CTkFrame(scrollable_tab)
        low_stock_frame.pack(fill="both", expand=True, pady=10)

        CTkLabel(
            low_stock_frame,
            text="المنتجات المنخفضة (أقل من الحد الأدنى)",
            font=("Cairo", 16, "bold"),
        ).pack(pady=5)

        # إنشاء جدول
        columns = ("المنتج", "الكمية", "الحد الأدنى", "الحالة")
        self.low_stock_tree = TreeView(low_stock_frame, columns, (100, 100, 200, 30))

        for col in columns:
            self.low_stock_tree.tree.heading(col, text=col)
            self.low_stock_tree.tree.column(col, width=150, anchor="center")
        
    def init_customers_tab(self):
        """تهيئة تبويب العملاء"""
        tab = self.tab_view.tab("العملاء")

        # إطار علوي للملخصات
        summary_frame = CTkFrame(tab)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.customers_summary_widgets = {}
        summaries = [
            ("total_customers", "إجمالي العملاء", "0"),
            ("total_debts", "إجمالي الديون", "0"),
            ("top_customer", "أكثر عميل", "لا يوجد"),
            ("avg_debt", "متوسط الدين", "0"),
        ]

        for i, (key, label, value) in enumerate(summaries):
            frame = CTkFrame(summary_frame, width=200, height=100)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            frame.grid_propagate(False)

            CTkLabel(frame, text=label, font=("Cairo", 14)).pack(pady=(10, 5))
            self.customers_summary_widgets[key] = CTkLabel(
                frame, text=value, font=("Cairo", 20, "bold")
            )
            self.customers_summary_widgets[key].pack(pady=(0, 10))

        for i in range(4):
            summary_frame.grid_columnconfigure(i, weight=1)

        # إطار للرسوم البيانية
        charts_frame = CTkFrame(tab)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)

        # رسم بياني لأكثر العملاء مبيعات
        top_customers_frame = CTkFrame(charts_frame)
        top_customers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            top_customers_frame, text="أكثر العملاء مبيعات", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.top_customers_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.top_customers_plot = self.top_customers_figure.add_subplot(111)
        self.top_customers_plot.set_facecolor("#333333")
        self.top_customers_plot.tick_params(colors="white")

        self.top_customers_canvas = FigureCanvasTkAgg(
            self.top_customers_figure, top_customers_frame
        )
        self.top_customers_canvas.get_tk_widget().pack(fill="both", expand=True)

        # رسم بياني لتوزيع الديون
        debts_frame = CTkFrame(charts_frame)
        debts_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        CTkLabel(debts_frame, text="توزيع الديون", font=("Cairo", 16, "bold")).pack(
            pady=5
        )
        self.debts_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.debts_plot = self.debts_figure.add_subplot(111)
        self.debts_plot.set_facecolor("#333333")
        self.debts_plot.tick_params(colors="white")

        self.debts_canvas = FigureCanvasTkAgg(self.debts_figure, debts_frame)
        self.debts_canvas.get_tk_widget().pack(fill="both", expand=True)

    def init_suppliers_tab(self):
        """تهيئة تبويب الموردين"""
        tab = self.tab_view.tab("الموردين")

        # إطار علوي للملخصات
        summary_frame = CTkFrame(tab)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.suppliers_summary_widgets = {}
        summaries = [
            ("total_suppliers", "إجمالي الموردين", "0"),
            ("total_products", "منتجات الموردين", "0"),
            ("top_supplier", "أكثر مورد", "لا يوجد"),
            ("avg_products", "متوسط المنتجات", "0"),
        ]

        for i, (key, label, value) in enumerate(summaries):
            frame = CTkFrame(summary_frame, width=200, height=100)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            frame.grid_propagate(False)

            CTkLabel(frame, text=label, font=("Cairo", 14)).pack(pady=(10, 5))
            self.suppliers_summary_widgets[key] = CTkLabel(
                frame, text=value, font=("Cairo", 20, "bold")
            )
            self.suppliers_summary_widgets[key].pack(pady=(0, 10))

        for i in range(4):
            summary_frame.grid_columnconfigure(i, weight=1)

        # رسم بياني لتوزيع المنتجات حسب المورد
        chart_frame = CTkFrame(tab)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        CTkLabel(
            chart_frame, text="توزيع المنتجات حسب المورد", font=("Cairo", 16, "bold")
        ).pack(pady=5)

        self.suppliers_figure = Figure(figsize=(10, 5), dpi=100, facecolor="#2b2b2b")
        self.suppliers_plot = self.suppliers_figure.add_subplot(111)
        self.suppliers_plot.set_facecolor("#333333")
        self.suppliers_plot.tick_params(colors="white")

        self.suppliers_canvas = FigureCanvasTkAgg(self.suppliers_figure, chart_frame)
        self.suppliers_canvas.get_tk_widget().pack(fill="both", expand=True)

    def init_profits_tab(self):
        """تهيئة تبويب الأرباح"""
        tab = self.tab_view.tab("الأرباح")

        # إطار علوي للملخصات
        summary_frame = CTkFrame(tab)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.profits_summary_widgets = {}
        summaries = [
            ("total_profit", "صافي الربح", "0"),
            ("total_revenue", "الإيرادات", "0"),
            ("total_cost", "التكلفة", "0"),
            ("profit_margin", "هامش الربح", "0%"),
        ]

        for i, (key, label, value) in enumerate(summaries):
            frame = CTkFrame(summary_frame, width=200, height=100)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            frame.grid_propagate(False)

            CTkLabel(frame, text=label, font=("Cairo", 14)).pack(pady=(10, 5))
            self.profits_summary_widgets[key] = CTkLabel(
                frame, text=value, font=("Cairo", 20, "bold")
            )
            self.profits_summary_widgets[key].pack(pady=(0, 10))

        for i in range(4):
            summary_frame.grid_columnconfigure(i, weight=1)

        # إطار للرسوم البيانية
        charts_frame = CTkFrame(tab)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_rowconfigure(1, weight=1)

        # رسم بياني للأرباح اليومية
        daily_profit_frame = CTkFrame(charts_frame)
        daily_profit_frame.grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew"
        )

        CTkLabel(
            daily_profit_frame, text="الأرباح اليومية", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.daily_profit_figure = Figure(figsize=(12, 4), dpi=100, facecolor="#2b2b2b")
        self.daily_profit_plot = self.daily_profit_figure.add_subplot(111)
        self.daily_profit_plot.set_facecolor("#333333")
        self.daily_profit_plot.tick_params(colors="white")

        self.daily_profit_canvas = FigureCanvasTkAgg(
            self.daily_profit_figure, daily_profit_frame
        )
        self.daily_profit_canvas.get_tk_widget().pack(fill="both", expand=True)

        # رسم بياني لأكثر المنتجات ربحاً
        top_profit_frame = CTkFrame(charts_frame)
        top_profit_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            top_profit_frame, text="أكثر المنتجات ربحاً", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.top_profit_figure = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        self.top_profit_plot = self.top_profit_figure.add_subplot(111)
        self.top_profit_plot.set_facecolor("#333333")
        self.top_profit_plot.tick_params(colors="white")

        self.top_profit_canvas = FigureCanvasTkAgg(
            self.top_profit_figure, top_profit_frame
        )
        self.top_profit_canvas.get_tk_widget().pack(fill="both", expand=True)

        # رسم بياني لنسبة الربح لكل فئة
        category_profit_frame = CTkFrame(charts_frame)
        category_profit_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            category_profit_frame, text="الأرباح حسب الفئة", font=("Cairo", 16, "bold")
        ).pack(pady=5)
        self.category_profit_figure = Figure(
            figsize=(6, 4), dpi=100, facecolor="#2b2b2b"
        )
        self.category_profit_plot = self.category_profit_figure.add_subplot(111)
        self.category_profit_plot.set_facecolor("#333333")
        self.category_profit_plot.tick_params(colors="white")

        self.category_profit_canvas = FigureCanvasTkAgg(
            self.category_profit_figure, category_profit_frame
        )
        self.category_profit_canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_all_reports(self):
        """تحميل جميع التقارير"""
        try:
            self.load_sales_report()
            self.load_stock_report()
            self.load_customers_report()
            self.load_suppliers_report()
            self.load_profits_report()
        except Exception as e:
            showinfo("خطأ", f"حدث خطأ في تحميل التقارير: {str(e)}")

    def load_sales_report(self):
        """تحميل تقرير المبيعات"""
        start = self.start_date.get()
        end = self.end_date.get()

        # إجمالي المبيعات
        self.cur.execute(
            """
            SELECT COALESCE(SUM(total), 0) as total,
                   COUNT(*) as count,
                   COALESCE(SUM(discount), 0) as discounts
            FROM sales 
            WHERE date BETWEEN ? AND ?
        """,
            (start, end),
        )

        row = self.cur.fetchone()
        total_sales = row[0] if row else 0
        count = row[1] if row else 0
        total_discounts = row[2] if row else 0

        self.sales_summary_widgets["total_sales"].configure(
            text=format_currency(total_sales)
        )
        self.sales_summary_widgets["total_invoices"].configure(text=str(count))
        self.sales_summary_widgets["total_discounts"].configure(
            text=format_currency(total_discounts)
        )

        avg_invoice = total_sales / count if count > 0 else 0
        self.sales_summary_widgets["avg_invoice"].configure(
            text=format_currency(avg_invoice)
        )

        # المبيعات اليومية
        self.cur.execute(
            """
            SELECT date, COALESCE(SUM(total), 0) as daily_total
            FROM sales 
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        """,
            (start, end),
        )

        daily_sales = self.cur.fetchall()

        self.daily_sales_plot.clear()
        if daily_sales:
            dates = [row[0] for row in daily_sales]
            totals = [row[1] for row in daily_sales]

            self.daily_sales_plot.plot(
                dates,
                totals,
                marker="o",
                linewidth=2,
                color="#28a745"
            )

            self.daily_sales_plot.fill_between(
                dates,
                totals,
                alpha=0.2,
                color="#28a745"
            )
            self.daily_sales_plot.set_xlabel(ar("التاريخ"), color="white")
            self.daily_sales_plot.set_ylabel(ar("المبيعات"), color="white")
            self.daily_sales_plot.tick_params(axis="x", rotation=45, colors="white")
        else:
            self.daily_sales_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.daily_sales_plot.set_facecolor("#333333")
        self.daily_sales_figure.tight_layout()
        self.daily_sales_canvas.draw()

        # أكثر المنتجات مبيعاً
        self.cur.execute(
            """
            SELECT p.name, COALESCE(SUM(si.quantity), 0) as total_qty
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE s.date BETWEEN ? AND ?
            GROUP BY si.product_id
            ORDER BY total_qty DESC
            LIMIT 7
        """,
            (start, end),
        )

        top_products = self.cur.fetchall()

        self.top_products_plot.clear()
        if top_products:
            names = [
                ar(row[0][:15] + "..." if len(row[0]) > 15 else row[0])
                for row in top_products
            ]
            qtys = [row[1] for row in top_products]

            self.top_products_plot.barh(names, qtys, color="#0078da")
            self.top_products_plot.set_xlabel(ar("الكمية"), color="white")
            self.top_products_plot.tick_params(colors="white")
        else:
            self.top_products_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.top_products_plot.set_facecolor("#333333")
        self.top_products_figure.tight_layout()
        self.top_products_canvas.draw()

    def load_stock_report(self):
        """تحميل تقرير المخزون"""
        # إجمالي المنتجات
        self.cur.execute("SELECT COUNT(*) FROM products")
        total_products = self.cur.fetchone()[0]

        # قيمة المخزون
        self.cur.execute("SELECT COALESCE(SUM(quantity * buy_price), 0) FROM products")
        total_value = self.cur.fetchone()[0]

        # المنتجات المنخفضة
        self.cur.execute(
            "SELECT COUNT(*) FROM products WHERE quantity <= low_stock AND quantity > 0"
        )
        low_stock_count = self.cur.fetchone()[0]

        # المنتجات النافدة
        self.cur.execute("SELECT COUNT(*) FROM products WHERE quantity = 0")
        out_stock_count = self.cur.fetchone()[0]

        self.stock_summary_widgets["total_products"].configure(text=str(total_products))
        self.stock_summary_widgets["total_value"].configure(
            text=format_currency(total_value)
        )
        self.stock_summary_widgets["low_stock"].configure(text=str(low_stock_count))
        self.stock_summary_widgets["out_stock"].configure(text=str(out_stock_count))

        # توزيع المنتجات حسب الفئة
        self.cur.execute(
            """
            SELECT c.name, COUNT(p.id) as count
            FROM category c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id
        """
        )

        categories = self.cur.fetchall()

        self.category_plot.clear()
        if categories:
            names = [ar(row[0]) for row in categories if row[1] > 0]
            counts = [row[1] for row in categories if row[1] > 0]

            if names and counts:
                colors = plt.cm.Set3(np.linspace(0, 1, len(names)))
                self.category_plot.pie(
                    counts,
                    labels=names,
                    autopct="%1.1f%%",
                    textprops={"color": "white"},
                    colors=colors,
                )
            else:
                self.category_plot.text(
                    0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
                )
        else:
            self.category_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.category_plot.set_facecolor("#333333")
        self.category_figure.tight_layout()
        self.category_canvas.draw()

        # حالة المخزون
        self.stock_status_plot.clear()
        if total_products > 0:
            labels = [ar("متوفر"), ar("منخفض"), ar("نافد")]
            values = [
                total_products - low_stock_count - out_stock_count,
                low_stock_count,
                out_stock_count,
            ]
            colors = ["#28a745", "#ffc107", "#dc3545"]

            if any(values):
                self.stock_status_plot.pie(
                    values,
                    labels=labels,
                    autopct="%1.1f%%",
                    colors=colors,
                    textprops={"color": "white"},
                )
            else:
                self.stock_status_plot.text(
                    0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
                )
        else:
            self.stock_status_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.stock_status_plot.set_facecolor("#333333")
        self.stock_status_figure.tight_layout()
        self.stock_status_canvas.draw()

        # جدول المنتجات المنخفضة
        self.cur.execute(
            """
            SELECT name, quantity, low_stock,
                   CASE 
                       WHEN quantity = 0 THEN 'نافد'
                       WHEN quantity <= low_stock THEN 'منخفض'
                   END as status
            FROM products 
            WHERE quantity <= low_stock
            ORDER BY quantity ASC
        """
        )

        low_stock_items = self.cur.fetchall()

        # مسح الجدول
        for item in self.low_stock_tree.tree.get_children():
            self.low_stock_tree.tree.delete(item)

        # إضافة البيانات
        for item in low_stock_items:
            self.low_stock_tree.tree.insert("", tk.END, values=item)

    def load_customers_report(self):
        """تحميل تقرير العملاء"""
        start = self.start_date.get()
        end = self.end_date.get()

        # إجمالي العملاء
        self.cur.execute("SELECT COUNT(*) FROM customers")
        total_customers = self.cur.fetchone()[0]

        # إجمالي الديون
        self.cur.execute("SELECT COALESCE(SUM(debt), 0) FROM customers")
        total_debts = self.cur.fetchone()[0]

        # متوسط الدين
        avg_debt = total_debts / total_customers if total_customers > 0 else 0

        # أكثر عميل مبيعات
        self.cur.execute(
            """
            SELECT c.name, COALESCE(SUM(s.total), 0) as total_sales
            FROM customers c
            LEFT JOIN sales s ON c.id = s.customer_id AND s.date BETWEEN ? AND ?
            GROUP BY c.id
            ORDER BY total_sales DESC
            LIMIT 1
        """,
            (start, end),
        )

        top_customer = self.cur.fetchone()

        self.customers_summary_widgets["total_customers"].configure(
            text=str(total_customers)
        )
        self.customers_summary_widgets["total_debts"].configure(
            text=format_currency(total_debts)
        )
        self.customers_summary_widgets["avg_debt"].configure(
            text=format_currency(avg_debt)
        )

        if top_customer and top_customer[1] > 0:
            self.customers_summary_widgets["top_customer"].configure(
                text=f"{top_customer[0]} ({format_currency(top_customer[1])})"
            )
        else:
            self.customers_summary_widgets["top_customer"].configure(text="لا يوجد")

        # أكثر العملاء مبيعات
        self.cur.execute(
            """
            SELECT c.name, COALESCE(SUM(s.total), 0) as total_sales
            FROM customers c
            LEFT JOIN sales s ON c.id = s.customer_id AND s.date BETWEEN ? AND ?
            GROUP BY c.id
            HAVING total_sales > 0
            ORDER BY total_sales DESC
            LIMIT 10
        """,
            (start, end),
        )

        top_customers = self.cur.fetchall()

        self.top_customers_plot.clear()
        if top_customers:
            names = [
                ar(row[0][:15] + "..." if len(row[0]) > 15 else row[0])
                for row in top_customers
            ]
            totals = [row[1] for row in top_customers]

            self.top_customers_plot.barh(names, totals, color="#0078da")
            self.top_customers_plot.set_xlabel(ar("المبيعات"), color="white")
            self.top_customers_plot.tick_params(colors="white")
        else:
            self.top_customers_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.top_customers_plot.set_facecolor("#333333")
        self.top_customers_figure.tight_layout()
        self.top_customers_canvas.draw()

        # توزيع الديون
        self.debts_plot.clear()

        self.cur.execute(
            """
            SELECT 
                CASE 
                    WHEN debt = 0 THEN 'بدون ديون'
                    WHEN debt <= 100 THEN 'ديون صغيرة'
                    WHEN debt <= 500 THEN 'ديون متوسطة'
                    ELSE 'ديون كبيرة'
                END as debt_range,
                COUNT(*) as count
            FROM customers
            GROUP BY debt_range
        """
        )

        debt_ranges = self.cur.fetchall()

        if debt_ranges:
            labels = [ar(row[0]) for row in debt_ranges]
            counts = [row[1] for row in debt_ranges]
            colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))

            self.debts_plot.pie(
                counts,
                labels=labels,
                autopct="%1.1f%%",
                textprops={"color": "white"},
                colors=colors,
            )
        else:
            self.debts_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.debts_plot.set_facecolor("#333333")
        self.debts_figure.tight_layout()
        self.debts_canvas.draw()

    def load_suppliers_report(self):
        """تحميل تقرير الموردين"""
        # إجمالي الموردين
        self.cur.execute("SELECT COUNT(*) FROM suppliers")
        total_suppliers = self.cur.fetchone()[0]

        # إجمالي منتجات الموردين
        self.cur.execute("SELECT COUNT(*) FROM products WHERE supplier_id IS NOT NULL")
        total_products = self.cur.fetchone()[0]

        # متوسط المنتجات لكل مورد
        avg_products = total_products / total_suppliers if total_suppliers > 0 else 0

        # أكثر مورد منتجات
        self.cur.execute(
            """
            SELECT s.name, COUNT(p.id) as product_count
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            GROUP BY s.id
            ORDER BY product_count DESC
            LIMIT 1
        """
        )

        top_supplier = self.cur.fetchone()

        self.suppliers_summary_widgets["total_suppliers"].configure(
            text=str(total_suppliers)
        )
        self.suppliers_summary_widgets["total_products"].configure(
            text=str(total_products)
        )
        self.suppliers_summary_widgets["avg_products"].configure(
            text=f"{avg_products:.1f}"
        )

        if top_supplier and top_supplier[1] > 0:
            self.suppliers_summary_widgets["top_supplier"].configure(
                text=f"{top_supplier[0]} ({top_supplier[1]})"
            )
        else:
            self.suppliers_summary_widgets["top_supplier"].configure(text="لا يوجد")

        # توزيع المنتجات حسب المورد
        self.cur.execute(
            """
            SELECT s.name, COUNT(p.id) as product_count
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            GROUP BY s.id
            HAVING product_count > 0
            ORDER BY product_count DESC
        """
        )

        supplier_products = self.cur.fetchall()

        self.suppliers_plot.clear()
        if supplier_products:
            names = [
                ar(row[0][:15] + "..." if len(row[0]) > 15 else row[0])
                for row in supplier_products
            ]
            counts = [row[1] for row in supplier_products]

            colors = plt.cm.Paired(np.linspace(0, 1, len(names)))
            self.suppliers_plot.pie(
                counts,
                labels=names,
                autopct="%1.1f%%",
                textprops={"color": "white"},
                colors=colors,
            )
        else:
            self.suppliers_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.suppliers_plot.set_facecolor("#333333")
        self.suppliers_figure.tight_layout()
        self.suppliers_canvas.draw()

    def load_profits_report(self):
        """تحميل تقرير الأرباح"""
        start = self.start_date.get()
        end = self.end_date.get()

        # حساب الإيرادات والتكلفة والأرباح
        self.cur.execute(
            """
            SELECT 
                COALESCE(SUM(s.total), 0) as revenue,
                COALESCE(SUM(si.quantity * p.buy_price), 0) as cost
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE s.date BETWEEN ? AND ?
        """,
            (start, end),
        )

        row = self.cur.fetchone()
        revenue = row[0] if row else 0
        cost = row[1] if row else 0
        profit = revenue - cost
        margin = (profit / revenue * 100) if revenue > 0 else 0

        self.profits_summary_widgets["total_profit"].configure(
            text=format_currency(profit)
        )
        self.profits_summary_widgets["total_revenue"].configure(
            text=format_currency(revenue)
        )
        self.profits_summary_widgets["total_cost"].configure(text=format_currency(cost))
        self.profits_summary_widgets["profit_margin"].configure(text=f"{margin:.1f}%")

        # الأرباح اليومية
        self.cur.execute(
            """
            SELECT 
                s.date,
                COALESCE(SUM(s.total), 0) as revenue,
                COALESCE(SUM(si.quantity * p.buy_price), 0) as cost
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE s.date BETWEEN ? AND ?
            GROUP BY s.date
            ORDER BY s.date
        """,
            (start, end),
        )

        daily_data = self.cur.fetchall()

        self.daily_profit_plot.clear()
        if daily_data:
            dates = [ar(row[0]) for row in daily_data]
            revenues = [row[1] for row in daily_data]
            costs = [row[2] for row in daily_data]
            profits = [r - c for r, c in zip(revenues, costs)]

            x = range(len(dates))
            width = 0.25

            self.daily_profit_plot.bar(
                [i - width for i in x],
                revenues,
                width,
                label=ar("الإيرادات"),
                color="#28a745",
                alpha=0.7,
            )
            self.daily_profit_plot.bar(
                [i for i in x],
                costs,
                width,
                label=ar("التكلفة"),
                color="#dc3545",
                alpha=0.7,
            )
            self.daily_profit_plot.bar(
                [i + width for i in x],
                profits,
                width,
                label=ar("الربح"),
                color="#0078da",
                alpha=0.7,
            )

            self.daily_profit_plot.set_xlabel(ar("التاريخ"), color="white")
            self.daily_profit_plot.set_ylabel(ar("القيمة"), color="white")
            self.daily_profit_plot.set_xticks(x)
            self.daily_profit_plot.set_xticklabels(dates, rotation=45)
            self.daily_profit_plot.legend(facecolor="#333333", labelcolor="white")
            self.daily_profit_plot.tick_params(colors="white")
        else:
            self.daily_profit_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.daily_profit_plot.set_facecolor("#333333")
        self.daily_profit_figure.tight_layout()
        self.daily_profit_canvas.draw()

        # أكثر المنتجات ربحاً
        self.cur.execute(
            """
            SELECT 
                p.name,
                COALESCE(SUM((si.price - p.buy_price) * si.quantity), 0) as profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE s.date BETWEEN ? AND ?
            GROUP BY si.product_id
            ORDER BY profit DESC
            LIMIT 10
        """,
            (start, end),
        )

        top_profit_products = self.cur.fetchall()

        self.top_profit_plot.clear()
        if top_profit_products:
            names = [
                ar(row[0][:15] + "..." if len(row[0]) > 15 else row[0])
                for row in top_profit_products
            ]
            profits = [row[1] for row in top_profit_products]

            self.top_profit_plot.barh(names, profits, color="#28a745")
            self.top_profit_plot.set_xlabel(ar("الربح"), color="white")
            self.top_profit_plot.tick_params(colors="white")
        else:
            self.top_profit_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.top_profit_plot.set_facecolor("#333333")
        self.top_profit_figure.tight_layout()
        self.top_profit_canvas.draw()

        # الأرباح حسب الفئة
        self.cur.execute(
            """
            SELECT 
                c.name,
                COALESCE(SUM((si.price - p.buy_price) * si.quantity), 0) as profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            LEFT JOIN category c ON p.category_id = c.id
            WHERE s.date BETWEEN ? AND ?
            GROUP BY p.category_id
            HAVING profit > 0
        """,
            (start, end),
        )

        category_profits = self.cur.fetchall()

        self.category_profit_plot.clear()
        if category_profits:
            names = [ar(row[0]) if row[0] else ar("بدون فئة") for row in category_profits]
            profits = [row[1] for row in category_profits]

            colors = plt.cm.Set1(np.linspace(0, 1, len(names)))
            self.category_profit_plot.pie(
                profits,
                labels=names,
                autopct="%1.1f%%",
                textprops={"color": "white"},
                colors=colors,
            )
        else:
            self.category_profit_plot.text(
                0.5, 0.5, ar("لا توجد بيانات"), ha="center", va="center", color="white"
            )

        self.category_profit_plot.set_facecolor("#333333")
        self.category_profit_figure.tight_layout()
        self.category_profit_canvas.draw()
