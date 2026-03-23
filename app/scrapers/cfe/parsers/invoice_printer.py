"""Formatted representation of CFE invoices."""

from app.scrapers.cfe.schemas import Invoice


class InvoicePrinter:
    """Formats a list of CFE invoices into a readable string."""

    def format(self, invoices: list[Invoice]) -> str:
        lines = []
        lines.append(f"\n{'=' * 70}")
        lines.append(f"  CFE INVOICES TYPE OCR - Total: {len(invoices)}")
        lines.append(f"{'=' * 70}")

        for i, inv in enumerate(invoices, 1):
            lines.extend(self.format_invoice(i, inv))

        lines.extend(self.format_summary(invoices))
        return "\n".join(lines)

    def format_invoice(self, number: int, inv: Invoice) -> list[str]:
        lines = []
        lines.append(f"\n{'─' * 70}")
        lines.append(f"  INVOICE #{number}")
        lines.append(f"{'─' * 70}")

        lines.append(f"  Series/Folio:      {inv.series}-{inv.folio}")
        lines.append(f"  Issue date:        {inv.date}")
        lines.append(f"  RPU:               {inv.rpu}")
        lines.append(f"  Account holder:    {inv.account_holder.name}")
        lines.append(f"  Address:           {inv.account_holder.address} {inv.account_holder.city}, {inv.account_holder.state}")
        lines.append(f"  Usage:             {inv.account_holder.usage}")
        lines.append(f"  Rate:              {inv.rate}")
        lines.append(f"  Service type:      {inv.service_type}")

        lines.append(f"\n  -- PERIOD --")
        lines.append(f"  From:              {inv.period.date_from}")
        lines.append(f"  To:                {inv.period.date_to}")
        lines.append(f"  Days:              {inv.period.days}")
        lines.append(f"  Payment due date:  {inv.period.payment_due_date}")
        lines.append(f"  Cutoff date:       {inv.period.cutoff_date}")

        lines.append(f"\n  -- CONSUMPTION --")
        lines.append(f"  Total consumption: {inv.consumption.total_kwh} kWh")
        lines.append(f"  Daily consumption: {inv.consumption.daily_kwh} kWh/day")
        lines.append(f"  Consumption type:  {inv.consumption.type}")

        lines.append(f"\n  -- CHARGES --")
        lines.append(f"  Energy subtotal:   ${inv.charge.subtotal}")
        lines.append(f"  Tax:               ${inv.charge.tax}")
        lines.append(f"  DAP (lighting):    ${inv.charge.dap}")
        lines.append(f"  TOTAL:             ${inv.charge.total} {inv.charge.currency}")
        lines.append(f"  Daily price:       ${inv.charge.daily_price} /day")

        return lines

    def format_summary(self, invoices: list[Invoice]) -> list[str]:
        lines = []
        lines.append(f"\n{'=' * 70}")
        try:
            grand_total = sum(float(inv.charge.total) for inv in invoices)
            total_kwh = sum(int(inv.consumption.total_kwh) for inv in invoices)
            lines.append(f"  SUMMARY: {len(invoices)} invoices | {total_kwh} kWh | ${grand_total:,.2f} MXN")
        except (ValueError, TypeError):
            pass
        lines.append(f"{'=' * 70}")
        return lines
