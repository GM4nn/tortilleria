# Sistema de Inventario Acumulativo v2

## Concepto

El sistema rastrea compras de insumos y deriva el consumo a partir de datos consecutivos. Solo se almacena **remaining** (lo que sobro del periodo anterior) en cada compra. El consumo se calcula automaticamente.

## Formula Principal

```
consumido = (prev.remaining + prev.quantity) - current.remaining
```

Donde:
- `prev.remaining` = lo que sobro del periodo antes del anterior
- `prev.quantity` = lo que se compro en la compra anterior
- `current.remaining` = lo que el usuario reporta que le sobro al momento de la nueva compra

## Stock Actual

```
stock = ultima_compra.remaining + ultima_compra.quantity
```

## Modelo de Datos

Solo existe una tabla para compras: `supply_purchases`

| Columna | Tipo | Descripcion |
|---|---|---|
| id | Integer | PK |
| supply_id | Integer | FK a supplies |
| supplier_id | Integer | FK a suppliers |
| purchase_date | Date | Fecha de compra |
| quantity | Float | Cantidad comprada |
| unit | String | Unidad (kilos, costales, etc.) |
| unit_price | Float | Precio unitario |
| total_price | Float | Precio total |
| remaining | Float | Lo que sobro del periodo anterior (0 en la primera compra) |
| notes | String | Notas opcionales |

> **Nota:** La tabla `supply_consumptions` fue eliminada en v2. El consumo se deriva de compras consecutivas.

## Flujo del Usuario

1. El usuario registra una nueva compra
2. Si no es la primera compra, el sistema le muestra cuanto tenia disponible en el periodo anterior (`prev.remaining + prev.quantity`)
3. El usuario ingresa **cuanto le sobro** en el campo "Cuanto Sobro"
4. El sistema calcula y muestra automaticamente cuanto se consumio (informativo, no editable)
5. Se valida que `remaining >= 0` y `remaining <= total_disponible`
6. Se guarda la compra con el `remaining` reportado

## Ejemplo

| Compra | Cantidad | Remaining | Stock | Consumido (derivado) |
|---|---|---|---|---|
| 1ra | 50 kg | 0 (primera) | 50 kg | - |
| 2da | 40 kg | 5 kg | 45 kg | 45 kg (0 + 50 - 5) |
| 3ra | 35 kg | 8 kg | 43 kg | 37 kg (5 + 40 - 8) |

## Archivos Clave

| Archivo | Responsabilidad |
|---|---|
| `app/models/supplies.py` | Modelo `SupplyPurchase` con columna `remaining` |
| `app/data/providers/supplies.py` | CRUD de compras, calculo de stock |
| `app/gui/supplies/detail/history/purchase_form/consumption_inputs.py` | Input de "Cuanto Sobro" + consumido auto-calculado |
| `app/gui/supplies/detail/history/purchase_form/content.py` | Logica de guardado, pasa `remaining` al provider |
| `app/gui/supplies/detail/periods/period_table.py` | Tabla de periodos, deriva consumo entre compras consecutivas |
| `app/gui/supplies/detail/periods/current_period_summary.py` | Resumen del periodo actual (2 compras mas recientes) |
| `app/gui/reports/supplies/stock_status_section.py` | Reporte de stock actual por insumo |
| `app/gui/supplies/detail/history/historic_table.py` | Tabla de historial con columna "Sobro" |

## Migracion desde v1

- `initial_stock` renombrado a `remaining`
- Tabla `supply_consumptions` eliminada
- Migracion Alembic: `be7520d40658_rename_initial_stock_to_remaining_and_.py`
