"""
SuppliesTab - Orquestador de secciones de reportes de insumos
"""

from app.gui.reports.components.report_base import BaseReportTab
from .supplies_kpi_panel import SuppliesKPIPanel
from .stock_status_section import StockStatusSection
from .top_supplies_section import TopSuppliesSection


class SuppliesTab(BaseReportTab):
    def build_sections(self, db):
        SuppliesKPIPanel.render(self, db)
        self.add_separator()
        StockStatusSection.render(self, db)
        self.add_separator()
        TopSuppliesSection.render(self, db)
