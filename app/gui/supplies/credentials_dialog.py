import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CredentialsDialog(ttk.Toplevel):
    """Ventana emergente para pedir usuario y clave de un servicio default."""

    # Actions
    ACTION_SYNC = "sync"
    ACTION_SKIP = "skip"
    ACTION_CANCEL = "cancel"

    def __init__(self, parent, supply_name: str, has_synced_data: bool = False):
        super().__init__(parent)
        self.title(f"Credenciales - {supply_name}")
        height = 400 if has_synced_data else 340
        self.geometry(f"400x{height}")
        self.resizable(False, False)
        self.grab_set()

        self.result = None
        self.action = self.ACTION_CANCEL
        self.has_synced_data = has_synced_data

        self.setup_ui(supply_name)
        self.center_on_parent(parent)
        self.user_entry.focus()

        self.bind("<Return>", lambda e: self.on_sync())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def setup_ui(self, supply_name):
        container = ttk.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)

        ttk.Label(
            container,
            text=f"Sincronizar datos - {supply_name}",
            font=("Arial", 11, "bold"),
        ).pack(anchor=W, pady=(0, 15))

        # Usuario
        ttk.Label(container, text="Usuario:").pack(anchor=W, pady=(0, 2))
        self.user_var = ttk.StringVar()
        self.user_entry = ttk.Entry(container, textvariable=self.user_var)
        self.user_entry.pack(fill=X, pady=(0, 8))

        # Clave
        ttk.Label(container, text="Clave:").pack(anchor=W, pady=(0, 2))
        self.password_var = ttk.StringVar()
        self.password_entry = ttk.Entry(container, textvariable=self.password_var, show="*")
        self.password_entry.pack(fill=X, pady=(0, 8))

        # Nro Servicio (opcional)
        ttk.Label(container, text="Nro Servicio (opcional):").pack(anchor=W, pady=(0, 2))
        self.service_number_var = ttk.StringVar()
        self.service_number_entry = ttk.Entry(container, textvariable=self.service_number_var)
        self.service_number_entry.pack(fill=X, pady=(0, 15))

        # Botones
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(5, 0))

        ttk.Button(
            btn_frame,
            text="Sincronizar",
            command=self.on_sync,
            bootstyle="primary",
        ).pack(fill=X, pady=(0, 5))

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.on_cancel,
            bootstyle="secondary-outline",
        ).pack(fill=X)

        # Boton "Continuar sin credenciales" solo si ya hay datos sincronizados
        if self.has_synced_data:
            skip_frame = ttk.Frame(container)
            skip_frame.pack(fill=X, pady=(10, 0))

            ttk.Label(
                skip_frame,
                text="Si desea sincronizar nuevamente, ingrese los campos necesarios.",
                font=("Arial", 8),
                bootstyle="secondary",
                wraplength=350,
            ).pack(anchor=W, pady=(0, 5))

            ttk.Button(
                skip_frame,
                text="Continuar sin credenciales",
                command=self.on_skip,
                bootstyle="info-outline",
            ).pack(fill=X)

    def on_sync(self):
        user = self.user_var.get().strip()
        password = self.password_var.get().strip()

        if not user or not password:
            return

        self.result = {
            "user": user,
            "password": password,
            "service_number": self.service_number_var.get().strip() or None,
        }
        self.action = self.ACTION_SYNC
        self.destroy()

    def on_skip(self):
        self.result = None
        self.action = self.ACTION_SKIP
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.action = self.ACTION_CANCEL
        self.destroy()

    def center_on_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
