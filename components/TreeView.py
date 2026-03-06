from tkinter import ttk
from utils.key_shortcut import key_shortcut


class TreeView:
    def __init__(self, parent, cols: tuple, width: tuple, data):
        self.parent = parent
        self.data = data

        vsb = ttk.Scrollbar(self.parent, orient="vertical")
        vsb.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.parent, columns=cols, show="headings", yscrollcommand=vsb.set
        )
        vsb.config(command=self.tree.yview)

        for c, w in zip(cols, width):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")

        self.tree.tag_configure("success", background="#e7ffe7")
        self.tree.tag_configure("warning", background="#fff9e7")
        self.tree.tag_configure("danger", background="#ffe7e7")

        self.tree.pack(fill="both", expand=True)

        self.init_key_shortcuts()

    def init_key_shortcuts(self):
        def on_select_all():
            self.tree.selection_set(self.tree.get_children())

        def on_unselect_all():
            self.tree.selection_remove(self.tree.get_children())

        def on_select_last_first(mode="first"):
            children = self.tree.get_children()
            if children:
                self.tree.selection_set(
                    children[0] if mode == "first" else children[-1]
                )

        key_shortcut(self.tree, ["<Control-a>", "<Control-A>"], on_select_all)
        key_shortcut(
            self.tree, ["<Control-Shift-a>", "<Control-Shift-A>"], on_unselect_all
        )
        key_shortcut(self.tree, "<Home>", on_select_last_first)
        key_shortcut(self.tree, "<End>", lambda: on_select_last_first("last"))
