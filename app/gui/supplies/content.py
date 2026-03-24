import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from app.gui.supplies.grid.supply_content import SupplyContent
from app.gui.supplies.detail.supply_detail import SupplyDetailView
from app.gui.supplies.credentials_dialog import CredentialsDialog
from app.data.providers.supplies import supply_provider


class SuppliesContent(ttk.Frame):
    """Contenedor principal del módulo de insumos: grid - detail"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_view = None

        self.setup_ui()
        self.show_grid_view()

    def setup_ui(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def clear_view(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_grid_view(self):
        self.clear_view()

        self.supply_content = SupplyContent(
            self.main_container,
            self.app,
            on_card_click=self.show_detail_view
        )
        self.supply_content.pack(fill=BOTH, expand=YES)

        self.current_view = "grid"

    def show_detail_view(self, supply_id):
        supply = supply_provider.get_supply_by_id(supply_id)
        if not supply:
            return

        if supply.get('is_default', False):
            has_data = supply_provider.has_purchases(supply_id)

            dialog = CredentialsDialog(self, supply['supply_name'], has_synced_data=has_data)
            self.wait_window(dialog)

            if dialog.action == CredentialsDialog.ACTION_CANCEL:
                return

            if dialog.action == CredentialsDialog.ACTION_SYNC:
                self.run_sync(supply_id, supply['supply_name'], dialog.result)
                return

            # ACTION_SKIP: continue to detail without syncing

        self.navigate_to_detail(supply_id)

    def run_sync(self, supply_id, supply_name, credentials):
        """Run the CFE scraper in a background thread and sync results."""
        # Show loading indicator
        self.clear_view()
        loading_frame = ttk.Frame(self.main_container)
        loading_frame.pack(expand=YES)

        ttk.Label(
            loading_frame,
            text=f"Sincronizando datos de {supply_name}...",
            font=("Arial", 14),
        ).pack(pady=(0, 10))

        progress = ttk.Progressbar(loading_frame, mode="indeterminate", length=300)
        progress.pack()
        progress.start(15)

        def sync_task():
            from app.scrapers.cfe.scraper import scrape_cfe

            invoices = scrape_cfe(credentials["user"], credentials["password"])
            added = 0
            if invoices:
                added = supply_provider.sync_cfe_invoices(supply_id, invoices)

            self.after(0, lambda: self.on_sync_complete(supply_id, supply_name, len(invoices), added))

        thread = threading.Thread(target=sync_task, daemon=True)
        thread.start()

    def on_sync_complete(self, supply_id, supply_name, total_invoices, added):
        """Called on main thread when sync finishes."""
        if total_invoices == 0:
            Messagebox.show_warning(
                "No se pudieron obtener facturas. Verifique sus credenciales.",
                "Sincronizacion"
            )
            self.show_grid_view()
            return

        Messagebox.show_info(
            f"Se encontraron {total_invoices} facturas.\n{added} nuevas sincronizadas.",
            f"Sincronizacion - {supply_name}"
        )

        self.navigate_to_detail(supply_id)

    def navigate_to_detail(self, supply_id):
        """Navigate to supply detail view."""
        self.clear_view()

        self.detail_view = SupplyDetailView(
            self.main_container,
            self.app,
            supply_id,
            on_back_callback=self.show_grid_view
        )
        self.detail_view.pack(fill=BOTH, expand=YES)

        self.current_view = "detail"
