def key_shortcut(widget, keys, func):
    if not isinstance(keys, (tuple, list)):
        keys = [keys]

    def on_press(event):
        func()
        return "break"

    for key in keys:
        widget.bind(key, on_press)
