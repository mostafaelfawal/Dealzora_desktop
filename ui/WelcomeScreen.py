from customtkinter import CTkLabel
from utils.image import image
from Layout.Constants import FONT_LARGE, FONT_SMALL, FONT_MEDIUM 

class WelcomeScreen:
    """Renders the initial welcome/home view inside main_frame."""

    def __init__(self, parent) -> None:
        self._render(parent)

    def _render(self, parent) -> None:
        CTkLabel(
            parent,
            text="",
            image=image("assets/icon.png", size=(100, 100)),
            font=FONT_LARGE,
        ).pack(pady=(10, 0))

        CTkLabel(
            parent,
            text="Dealzora اهلا بك في",
            font=FONT_LARGE,
        ).pack(pady=(10, 0))

        CTkLabel(parent, text="لإدارة المتاجر بأحترافيه", font=FONT_MEDIUM).pack()
        CTkLabel(parent, text="v1.5.6", font=FONT_SMALL).pack(side="bottom")
        CTkLabel(parent, text="Powered by Softvanta", font=FONT_SMALL).pack(
            side="bottom"
        )
