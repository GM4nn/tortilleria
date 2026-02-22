# Módulo de Corte de Caja

## Descripción

El módulo de Corte de Caja permite cerrar el día, declarando cuánto dinero hay en caja por cada forma de pago y comparándolo con lo que el sistema esperaba según las ventas y pedidos del día.

El corte siempre es **diario** (un corte por día). Toma todas las ventas y pedidos completados del día actual.

## Estructura de Archivos

```
app/
├── models/
│   └── cash_cut.py              # Modelo SQLAlchemy CashCut
├── data/
│   └── providers/
│       └── cash_cut.py          # Provider (acceso a datos)
└── gui/
    └── cash/
        ├── content.py           # Vista principal
        ├── summary_panel.py     # KPIs del dia actual
        ├── register_form.py     # Formulario para declarar montos
        └── history_panel.py     # Historial de cortes (paginado)
```

## Modelo: `cash_cuts`

| Columna           | Tipo     | Descripción                                      |
|-------------------|----------|--------------------------------------------------|
| id                | Integer  | PK autoincremental                               |
| opened_at         | DateTime | Inicio del dia (00:00:00)                        |
| closed_at         | DateTime | Fecha/hora en que se registró el corte           |
| sales_count       | Integer  | Cantidad de ventas directas del dia              |
| orders_count      | Integer  | Cantidad de pedidos completados del dia          |
| sales_total       | Float    | Total $ de ventas directas                       |
| orders_total      | Float    | Total $ de pedidos completados                   |
| expected_total    | Float    | sales_total + orders_total                       |
| declared_cash     | Float    | Efectivo declarado por el usuario                |
| declared_card     | Float    | Tarjeta declarado por el usuario                 |
| declared_transfer | Float    | Transferencia declarada por el usuario           |
| declared_total    | Float    | Suma de los tres declarados                      |
| difference        | Float    | declared_total - expected_total                  |
| notes             | String   | Notas opcionales                                 |

## Cómo Funciona

### 1. Panel Resumen del Dia (arriba izquierda)

Muestra 3 KPIs de las ventas/pedidos de HOY:

- **Ventas Directas**: cantidad y total $ de ventas POS del dia
- **Pedidos Completados**: cantidad y total $ de pedidos completados hoy
- **Total Esperado**: suma de ambos

### 2. Formulario Registrar Corte (arriba derecha)

El usuario declara cuánto dinero tiene por forma de pago:

- **Efectivo**: dinero en caja física
- **Tarjeta**: cobros por tarjeta de débito/crédito
- **Transferencia**: cobros por transferencia electrónica

El sistema calcula automáticamente:

- **Total Declarado** = Efectivo + Tarjeta + Transferencia
- **Diferencia** = Total Declarado - Total Esperado
  - `$0.00 Exacto` → cuadra perfecto
  - `+$X Sobrante` → hay más dinero del esperado
  - `-$X Faltante` → hay menos dinero del esperado

### 3. Historial de Cortes (abajo)

Tabla paginada con todos los cortes anteriores mostrando:
ID, Fecha Cierre, Ventas, Pedidos, Esperado, Declarado, Diferencia.

## Flujo de un Corte

```
1. Usuario navega a "Caja" en el menú lateral
2. Ve el resumen del dia (ventas/pedidos de hoy)
3. Cuenta el dinero físico y llena el formulario
4. Click "Registrar Corte de Caja"
5. Confirma en el diálogo
6. El corte se guarda
7. Solo se permite un corte por dia
```

## Reglas

- El corte es **diario**: filtra ventas por `date(sales.date) == hoy` y pedidos por `date(orders.completed_at) == hoy`
- Solo se permite **un corte por dia**. Si ya existe un corte de hoy, el sistema no permite registrar otro
- `opened_at` se guarda como el inicio del dia (00:00:00)
- `closed_at` es el momento exacto en que se registra el corte

## Migración

La tabla se creó con Alembic:

```
alembic revision --autogenerate -m "add_cash_cuts_table"
alembic upgrade head
```
