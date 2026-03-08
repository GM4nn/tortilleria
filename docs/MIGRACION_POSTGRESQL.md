# Migracion a PostgreSQL

## Diagnostico actual (SQLite)

- **Archivo:** tortilleria.db
- **Peso total:** 308 KB (315,392 bytes)
- **Total de registros:** 6,013

| Tabla                   | Registros | Peso estimado |   % del total |
|-------------------------|----------:|:-------------:|--------------:|
| sales                   |     1,728 |    56.7 KB    |        32.7%  |
| sales_detail            |     2,811 |    45.5 KB    |        26.2%  |
| orders                  |       284 |    17.9 KB    |        10.3%  |
| cash_cuts               |       179 |    17.7 KB    |        10.2%  |
| customers               |       171 |    13.6 KB    |         7.9%  |
| order_details           |       703 |    11.4 KB    |         6.6%  |
| supply_purchases        |       105 |     9.1 KB    |         5.2%  |
| suppliers               |         3 |     496 B     |         0.3%  |
| products                |        14 |     270 B     |         0.2%  |
| supplies                |         4 |     264 B     |         0.1%  |
| order_refunds           |         6 |     254 B     |         0.1%  |
| customer_product_prices |         3 |     179 B     |         0.1%  |
| ia_config               |         1 |     109 B     |         0.1%  |
| alembic_version         |         1 |      12 B     |         0.0%  |

Las tablas mas pesadas son **sales** y **sales_detail** (59% del total), seguidas de **orders** y **cash_cuts**.

## Estimacion de crecimiento (1 año de uso real)

- ~50 ventas mostrador/dia x 365 = **~18,250 ventas** + **~30,000 detalles** (~1.6 productos por venta)
- ~30 pedidos/dia x 365 = **~10,950 pedidos** + **~27,000 detalles** (~2.5 productos por pedido)
- ~365 cortes de caja
- Compras de insumos, clientes nuevos: ~500 registros

**Total estimado al año: ~87,000 registros = 5-8 MB**

En 5 años: ~435,000 registros = 25-40 MB. Sigue siendo poco para cualquier base de datos.

## Servicios gratuitos de PostgreSQL

| Servicio   | Plan gratis | Almacenamiento | Nota                                          |
|------------|-------------|----------------|-----------------------------------------------|
| **Neon**   | Free tier   | 512 MB         | El mas popular, sin expiracion                |
| **Supabase** | Free tier | 500 MB         | Incluye dashboard, API REST                   |
| **Railway** | Trial      | 1 GB           | $5 de credito gratis/mes                      |
| **Render** | Free tier   | 256 MB         | Se borra despues de 90 dias de inactividad    |
| **Aiven**  | Free tier   | 1 GB           | Buena opcion, sin limite de tiempo            |

**Recomendacion: Neon o Supabase.** Con el volumen de datos (1-2 MB al ano), el plan gratis sobra por anos.

## Pasos para migrar

### 1. Crear la base en el servicio elegido

Obtener el connection string, ejemplo de Neon:
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/tortilleria?sslmode=require
```

### 2. Instalar el driver de PostgreSQL

```bash
pip install psycopg2-binary
```

### 3. Cambiar la URL de conexion en `database.py`

Cambiar de:
```python
DATABASE_URL = "sqlite:///tortilleria.db"
```

A:
```python
DATABASE_URL = "postgresql://user:password@host/tortilleria?sslmode=require"
```

### 4. Crear las tablas con Alembic

```bash
alembic upgrade head
```

Esto aplica todas las migraciones existentes y crea las tablas en PostgreSQL con el mismo esquema.

### 5. Migrar datos existentes (opcional)

Si se necesita conservar los datos de SQLite, usar un script de migracion o herramienta como `pgloader`.

## Compatibilidad del codigo

El codigo ya esta preparado para PostgreSQL. Se reemplazaron todas las funciones especificas de SQLite (`func.date()`) por comparaciones de rango de datetime que son portables:

```python
# Antes (solo SQLite):
func.date(Sale.date) == today_str

# Ahora (SQLite + PostgreSQL + MySQL):
Sale.date >= day_start
Sale.date < day_end
```

Archivos actualizados:
- `app/data/providers/cash_cut.py`
- `app/data/providers/sales.py`
- `app/data/providers/orders.py`
- `app/gui/reports/sales/sales_kpi_panel.py`
- `seed_data.py`
