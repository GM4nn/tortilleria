"""
CustomersTab - Orquestador de secciones de reportes de clientes
"""

from app.gui.reports.components.report_base import BaseReportTab
from .customers_kpi_panel import CustomersKPIPanel
from .top_customers_section import TopCustomersSection
from .customers_by_category_section import CustomersByCategorySection


class CustomersTab(BaseReportTab):
    def build_sections(self, db):
        CustomersKPIPanel.render(self, db)
        self.add_separator()
        TopCustomersSection.render(self, db)
        self.add_separator()
        CustomersByCategorySection.render(self, db)
