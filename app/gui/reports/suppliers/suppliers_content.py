"""
SuppliersTab - Orquestador de secciones de reportes de proveedores
"""

from app.gui.reports.components.report_base import BaseReportTab
from .suppliers_kpi_panel import SuppliersKPIPanel
from .best_suppliers_section import BestSuppliersSection
from .suppliers_by_demand_section import SuppliersByDemandSection


class SuppliersTab(BaseReportTab):
    def build_sections(self, db):
        SuppliersKPIPanel.render(self, db)
        self.add_separator()
        BestSuppliersSection.render(self, db)
        self.add_separator()
        SuppliersByDemandSection.render(self, db)
