import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.supplies.detail.periods.current_period_summary import CurrentPeriodSummary
from app.gui.supplies.detail.periods.period_table import PeriodTable


class PeriodsContent(ttk.Frame):
    """Coordinador del tab periodos: resumen actual + grid de cards"""

    def __init__(self, parent, supply_data):
        super().__init__(parent)
        self.supply_data = supply_data

        self.setup_ui()

    def setup_ui(self):
        self.summary = CurrentPeriodSummary(self, self.supply_data)
        self.summary.pack(fill=X, pady=(0, 5))

        self.cards = PeriodTable(self, self.supply_data['id'])
        self.cards.pack(fill=BOTH, expand=YES)
