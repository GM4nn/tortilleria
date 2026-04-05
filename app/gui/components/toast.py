import tkinter as tk


class Toast(tk.Toplevel):

    def __init__(
        self,
        parent,
        message,
        on_action=None,
        action_text="Ver",
        duration=6000
    ):
        super().__init__(parent)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#323232")

        self._build_ui(message, on_action, action_text)
        self._position(parent)

        self._fade_after = self.after(duration, self._fade_out)

    def _build_ui(self, message, on_action, action_text):
        frame = tk.Frame(self, bg="#323232", padx=16, pady=12)
        frame.pack(fill=tk.BOTH)

        tk.Label(
            frame,
            text=message,
            bg="#323232",
            fg="white",
            font=("Segoe UI", 10),
            wraplength=300,
            justify=tk.LEFT,
        ).pack(side=tk.LEFT, padx=(0, 12))

        if on_action:
            btn = tk.Label(
                frame,
                text=action_text,
                bg="#323232",
                fg="#4FC3F7",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=(0, 8))
            btn.bind("<Button-1>", lambda e: self._do_action(on_action))

        close_btn = tk.Label(
            frame,
            text="✕",
            bg="#323232",
            fg="#999999",
            font=("Segoe UI", 10),
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.destroy())

    def _position(self, parent):
        self.update_idletasks()

        pw = parent.winfo_width()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        ph = parent.winfo_height()

        tw = self.winfo_reqwidth()
        th = self.winfo_reqheight()

        x = px + pw - tw - 20
        y = py + ph - th - 20

        self.geometry(f"+{x}+{y}")

    def _do_action(self, callback):
        self.after_cancel(self._fade_after)
        self.destroy()
        callback()

    def _fade_out(self):
        try:
            alpha = self.attributes("-alpha")
            if alpha > 0.1:
                self.attributes("-alpha", alpha - 0.1)
                self.after(50, self._fade_out)
            else:
                self.destroy()
        except tk.TclError:
            pass
