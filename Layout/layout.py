"""
layout.py
---------
Main application layout for Dealzora POS system.
Handles sidebar navigation and screen switching.
"""

from __future__ import annotations

from tkinter.messagebox import askokcancel
from customtkinter import CTkFrame, set_appearance_mode

from .Sidebar import Sidebar
from .ScreenFactory import ScreenFactory
from .data_structures import AppDependencies, NAV_ITEMS
from utils.clear import clear
from .build_data_service import _build_data_service

from ui.Sales.SaleState import SaleState
# Screens
from ui.WelcomeScreen import WelcomeScreen

# ---------------------------------------------------------------------------
# Helper: service factory
# ---------------------------------------------------------------------------

class Layout:
    """
    Top-level controller that wires the sidebar, welcome screen,
    and screen factory together.
    """

    def __init__(
        self,
        root,
        customers_db,
        products_db,
        user_id: int,
        users_db,
        sale_itmes_db,
        sales_db,
        stock_movements_db,
        suppliers_db,
        settings,
        expenses_db,
        con,
        cur,
    ) -> None:
        deps = AppDependencies(
            root=root,
            customers_db=customers_db,
            products_db=products_db,
            user_id=user_id,
            users_db=users_db,
            sale_items_db=sale_itmes_db,
            sales_db=sales_db,
            stock_movements_db=stock_movements_db,
            suppliers_db=suppliers_db,
            settings=settings,
            expenses_db=expenses_db,
            con=con,
            cur=cur,
        )
        self._deps = deps

        set_appearance_mode(settings.get_setting("theme"))
        root.title("Dealzora | Basic")
        clear(root)

        can_edit_price = users_db.check_permission(user_id, "edit_price_in_invoice")
        data_service = _build_data_service(deps, can_edit_price)
        sale_state = SaleState(settings.get_setting("tax"), data_service)

        self._screen_factory = ScreenFactory(deps, sale_state, data_service)
        self._main_frame = CTkFrame(root, fg_color="transparent")

        self._sidebar = Sidebar(
            parent=root,
            nav_items=NAV_ITEMS,
            on_navigate=self._navigate,
            on_quit=self._quit,
            users_db=users_db,
            user_id=user_id,
        )

        self._main_frame.pack(expand=True, fill="both")
        WelcomeScreen(self._main_frame)

    # ------------------------------------------------------------------
    # Private callbacks
    # ------------------------------------------------------------------

    def _navigate(self, screen_key: str) -> None:
        clear(self._main_frame)
        self._screen_factory.build(self._main_frame, screen_key)

    def _quit(self) -> None:
        if askokcancel("تأكد", "ستخرج من البرنامج الأن"):
            self._deps.root.quit()
