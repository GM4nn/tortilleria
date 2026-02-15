"""
SalesTab - Orquestador de secciones de reportes de ventas
"""

from app.gui.reports.components.report_base import BaseReportTab
from .sales_kpi_panel import SalesKPIPanel
from .orders_by_status_section import OrdersByStatusSection


class SalesTab(BaseReportTab):
    def build_sections(self, db):
        SalesKPIPanel.render(self, db)
        self.add_separator()
        OrdersByStatusSection.render(self, db)
