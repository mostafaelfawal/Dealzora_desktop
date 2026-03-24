from utils.key_shortcut import key_shortcut

class KeyShortcutsManager:
    def __init__(self, widget):
        self.widget = widget
        self.bindings = []

    def _get_root(self):
        window = self.widget
        while window.master:
            window = window.master
        return window

    def bind(self, key, callback):
        root = self._get_root()
        bind_id = key_shortcut(root, key, callback)
        self.bindings.append((key, bind_id))

    def unbind_all(self):
        root = self._get_root()
        for key, bind_id in self.bindings:
            root.unbind(key, bind_id)
        self.bindings.clear()