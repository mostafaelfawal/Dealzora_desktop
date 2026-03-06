def center_modal(modal):
    modal.update_idletasks()
    modal.grab_set()
    modal.focus_force()
    modal.geometry(f"+200+100")
