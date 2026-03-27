from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkScrollableFrame
from typing import Callable
from utils.image import image
from .data_structures import NavItem
from .Constants import (
    COLOR_ACCENT,
    COLOR_DANGER,   
    COLOR_DANGER_HV,
    COLOR_HOVER,
    COLOR_PRIMARY,
    FONT_NAV,
    FONT_TITLE,
    SIDEBAR_EXPANDED_WIDTH,
    SIDEBAR_COLLAPSED_WIDTH,
)

class Sidebar:
    """
    Manages the collapsible sidebar, the Dealzora brand label,
    and all navigation buttons.
    """

    def __init__(
        self,
        parent,
        nav_items: list[NavItem],
        on_navigate: Callable[[str], None],
        on_quit: Callable[[], None],
        users_db,
        user_id: int,
    ) -> None:
        self._parent = parent
        self._nav_items = nav_items
        self._on_navigate = on_navigate
        self._on_quit = on_quit
        self._users_db = users_db
        self._user_id = user_id
        self._collapsed = False

        self._frame = self._build_frame()
        self._scroll = self._build_scroll_area()
        self._brand_label = self._build_brand_label()
        self._nav_buttons = self._build_nav_buttons()
        self._exit_button = self._build_exit_button()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def toggle(self) -> None:
        if self._collapsed:
            self._expand()
        else:
            self._collapse()
        self._collapsed = not self._collapsed

    # ------------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------------

    def _build_frame(self) -> CTkFrame:
        frame = CTkFrame(self._parent, border_width=1, width=SIDEBAR_EXPANDED_WIDTH)
        frame.pack(side="right", fill="y")
        frame.pack_propagate(False)

        CTkButton(frame, text="☰", width=40, command=self.toggle).pack(fill="x", pady=5)
        return frame

    def _build_scroll_area(self) -> CTkScrollableFrame:
        scroll = CTkScrollableFrame(self._frame)
        scroll.pack(fill="both", expand=True)
        return scroll

    def _build_brand_label(self) -> CTkLabel:
        label = CTkLabel(
            self._scroll,
            image=image("assets/icon.png"),
            compound="right",
            text="Dealzora",
            font=FONT_TITLE,
            text_color=COLOR_ACCENT,
        )
        label.pack(padx=4)
        return label

    def _build_nav_buttons(self) -> list[CTkButton]:
        buttons: list[CTkButton] = []
        for item in self._nav_items:
            if not self._users_db.check_permission(self._user_id, item.permission):
                continue
            btn = CTkButton(
                self._scroll,
                text=item.text,
                image=image(item.icon_path),
                command=lambda key=item.screen_key: self._on_navigate(key),
                font=FONT_NAV,
                corner_radius=15,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_HOVER,
            )
            btn.original_text = item.text  # preserve label for expand
            btn.pack(padx=10, pady=5, fill="x")
            buttons.append(btn)
        return buttons

    def _build_exit_button(self) -> CTkButton:
        btn = CTkButton(
            self._scroll,
            text="خروج",
            image=image("assets/exit.png"),
            font=FONT_NAV,
            command=self._on_quit,
            corner_radius=15,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HV,
        )
        btn.pack(padx=10, pady=5, fill="x")
        return btn

    # ------------------------------------------------------------------
    # Collapse / Expand
    # ------------------------------------------------------------------

    def _collapse(self) -> None:
        self._frame.configure(width=SIDEBAR_COLLAPSED_WIDTH)
        self._brand_label.configure(text="")
        for btn in self._nav_buttons:
            btn.configure(text="")
        self._exit_button.configure(text="")

    def _expand(self) -> None:
        self._frame.configure(width=SIDEBAR_EXPANDED_WIDTH)
        self._refresh_brand_label()
        for btn in self._nav_buttons:
            btn.configure(text=btn.original_text)
        self._exit_button.configure(text="خروج")

    def _refresh_brand_label(self) -> None:
        self._brand_label.configure(text="Dealzora")