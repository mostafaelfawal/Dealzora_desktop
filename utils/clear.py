def clear(frame):
    for widget in frame.winfo_children():
        widget.destroy()
