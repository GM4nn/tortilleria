# Paginacion Server-Side con Tableview

## Problema

`ttkbootstrap.Tableview` con `paginated=True` carga **todos** los registros en memoria
y solo muestra de a N filas. Si hay miles de registros, la memoria crece y la carga
inicial es lenta.

## Solucion

Subclasear `Tableview` y sobreescribir los 5 metodos de paginacion para que, en lugar
de leer de la lista interna `self._tablerows`, hagan un `SELECT ... LIMIT ? OFFSET ?`
a la base de datos.

---

## Como funciona Tableview internamente

Los 5 metodos de paginacion (`goto_first_page`, `goto_next_page`, `goto_prev_page`,
`goto_last_page`, `goto_page`) todos hacen lo mismo:

1. Calculan `self._rowindex` (offset del primer registro a mostrar)
2. Llaman `self.load_table_data()`
3. `load_table_data()` hace un slice de `self._tablerows[page_start:page_end]`

```
# Fuente: venv/Lib/site-packages/ttkbootstrap/widgets/tableview.py L1206-L1218
if self._paginated:
    page_start = self._rowindex.get()
    page_end = self._rowindex.get() + self._pagesize.get()

rowdata = self._tablerows[page_start:page_end]  # <-- todo en memoria
```

La idea es interceptar ese flujo y reemplazarlo con una query a la DB.

---

## Implementacion: ServerPaginatedTableview

### Archivo: `app/gui/components/server_paginated_table.py`

```python
from math import ceil
from ttkbootstrap.tableview import Tableview, TableRow


class ServerPaginatedTableview(Tableview):
    """
    Tableview con paginacion server-side.

    En vez de cargar todos los datos en memoria, consulta la base de datos
    en cada cambio de pagina usando OFFSET y LIMIT.

    Parametros extra en el constructor:
        fetch_page: callable(offset: int, limit: int) -> list[list]
            Funcion que retorna las filas de la pagina actual.
        count_rows: callable() -> int
            Funcion que retorna el total de registros.
    """

    def __init__(self, master, coldata, fetch_page, count_rows,
                 pagesize=10, **kwargs):
        self._fetch_page = fetch_page
        self._count_rows = count_rows

        # Iniciar con rowdata vacio, paginated=True
        super().__init__(
            master=master,
            coldata=coldata,
            rowdata=[],
            paginated=True,
            pagesize=pagesize,
            **kwargs
        )

        # Cargar primera pagina
        self._load_server_page()

    def _load_server_page(self):
        """Consulta la DB para la pagina actual y muestra los datos."""
        offset = self._rowindex.get()
        limit = self._pagesize.get()
        total = self._count_rows()

        # Calcular total de paginas
        total_pages = ceil(total / limit) if total > 0 else 1
        self._pagelimit.set(total_pages)

        # Consultar DB
        rows = self._fetch_page(offset, limit)

        # Limpiar vista actual
        self.unload_table_data()
        self._tablerows.clear()
        self._viewdata.clear()

        # Insertar filas nuevas
        for i, values in enumerate(rows):
            record = TableRow(self, values)
            self._tablerows.append(record)
            stripe = self._stripecolor is not None and i % 2 == 0
            record.show(stripe)
            self._viewdata.append(record)

        # Actualizar indicador de pagina
        page_end = offset + limit
        pageindex = ceil(page_end / limit) if total > 0 else 1
        self._pageindex.set(min(total_pages, pageindex))

    # ─── Override de los 5 metodos de paginacion ──────────────

    def goto_first_page(self):
        self._rowindex.set(0)
        self._load_server_page()

    def goto_last_page(self):
        pagelimit = self._pagelimit.get() - 1
        if pagelimit < 0:
            pagelimit = 0
        self._rowindex.set(self.pagesize * pagelimit)
        self._load_server_page()

    def goto_next_page(self):
        if self._pageindex.get() >= self._pagelimit.get():
            return
        self._rowindex.set(self._rowindex.get() + self.pagesize)
        self._load_server_page()

    def goto_prev_page(self):
        if self._pageindex.get() <= 1:
            return
        self._rowindex.set(self._rowindex.get() - self.pagesize)
        self._load_server_page()

    def goto_page(self, *_):
        pagelimit = self._pagelimit.get()
        pageindex = self._pageindex.get()
        if pageindex > pagelimit:
            pageindex = pagelimit
            self._pageindex.set(pageindex)
        elif pageindex <= 0:
            pageindex = 1
            self._pageindex.set(pageindex)
        self._rowindex.set((pageindex * self.pagesize) - self.pagesize)
        self._load_server_page()

    def refresh(self):
        """Recargar la pagina actual (util despues de insertar/editar)."""
        self._load_server_page()
```

---

## Uso en el provider

Agregar metodos con OFFSET/LIMIT en el provider de supplies:

```python
# app/data/providers/supplies.py

def get_periods_page(self, supply_id, offset, limit):
    """Retorna una pagina de periodos con OFFSET y LIMIT."""
    query = """
        SELECT
            p1.purchase_date AS start_date,
            p2.purchase_date AS end_date,
            p1.quantity, p1.unit, p1.initial_stock,
            c.quantity_consumed, c.quantity_remaining, c.unit AS cons_unit, c.notes
        FROM purchases p1
        JOIN purchases p2 ON p2.supply_id = p1.supply_id
            AND p2.purchase_date > p1.purchase_date
        LEFT JOIN consumptions c ON c.supply_id = p1.supply_id
            AND c.start_date >= p1.purchase_date
            AND c.end_date <= p2.purchase_date
        WHERE p1.supply_id = ?
        ORDER BY p1.purchase_date DESC
        LIMIT ? OFFSET ?
    """
    cursor = self.db.execute(query, (supply_id, limit, offset))
    return cursor.fetchall()

def get_periods_count(self, supply_id):
    """Retorna el total de periodos para un insumo."""
    query = """
        SELECT COUNT(*)
        FROM purchases p1
        JOIN purchases p2 ON p2.supply_id = p1.supply_id
            AND p2.purchase_date > p1.purchase_date
        WHERE p1.supply_id = ?
    """
    cursor = self.db.execute(query, (supply_id,))
    return cursor.fetchone()[0]
```

> **Nota:** La query de arriba es un ejemplo. Hay que ajustarla segun la estructura
> real de las tablas y la logica de matching de periodos (tolerancia de 2 dias, etc).

---

## Uso en el componente GUI

```python
# app/gui/supplies/detail/periods/period_cards.py

from app.gui.components.server_paginated_table import ServerPaginatedTableview
from app.data.providers.supplies import supply_provider

class PeriodCards(ttk.Frame):
    def __init__(self, parent, supply_id):
        super().__init__(parent)
        self.supply_id = supply_id
        self.setup_ui()

    def setup_ui(self):
        columns = [
            {"text": "Desde", "stretch": False, "width": 100},
            {"text": "Hasta", "stretch": False, "width": 100},
            {"text": "Compra", "stretch": False, "width": 100},
            # ... demas columnas
        ]

        self.table = ServerPaginatedTableview(
            master=self,
            coldata=columns,
            fetch_page=self._fetch_page,
            count_rows=self._count_rows,
            pagesize=10,
            searchable=False,
            bootstyle="primary",
            height=10
        )
        self.table.pack(fill="both", expand=True)

    def _fetch_page(self, offset, limit):
        """Callback que consulta la DB y formatea las filas."""
        raw = supply_provider.get_periods_page(self.supply_id, offset, limit)
        rows = []
        for r in raw:
            # Formatear cada fila segun las columnas
            rows.append([
                r['start_date'].strftime("%d/%b/%Y"),
                r['end_date'].strftime("%d/%b/%Y"),
                f"{r['quantity']:.2f} {r['unit']}",
                # ... demas campos
            ])
        return rows

    def _count_rows(self):
        """Callback que retorna el total de periodos."""
        return supply_provider.get_periods_count(self.supply_id)
```

---

## Resumen de cambios necesarios

| Paso | Archivo | Que hacer |
|------|---------|-----------|
| 1 | `app/gui/components/server_paginated_table.py` | Crear la subclase `ServerPaginatedTableview` |
| 2 | Provider (`supplies.py`) | Agregar `get_periods_page(id, offset, limit)` y `get_periods_count(id)` |
| 3 | `period_cards.py` | Reemplazar `Tableview` por `ServerPaginatedTableview` con los callbacks |
| 4 | (Opcional) `historic_table.py` | Aplicar lo mismo para la tabla de historial de compras |

## Notas

- El sorting por columna no funciona server-side con este approach. Si se necesita,
  habria que tambien override `sort_column_data()` y pasar ORDER BY a la query.
- El search/filter tampoco funciona server-side. Si se habilita `searchable=True`,
  habria que interceptar el filtro y pasarlo como WHERE a la query.
- Para refrescar despues de insertar/editar, llamar `self.table.refresh()`.
