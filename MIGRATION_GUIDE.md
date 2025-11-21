# Guía de Migración a SQLAlchemy + Alembic

## Migración Completada

La aplicación ha sido migrada exitosamente de sqlite3 puro a SQLAlchemy con Alembic para manejo de migraciones.

## Estructura del Proyecto

```
app/
├── models/                     # Modelos SQLAlchemy
│   ├── __init__.py            # Exporta todos los modelos
│   ├── products.py            # Modelo de Productos
│   ├── customers.py           # Modelo de Clientes
│   ├── sales.py               # Modelo de Ventas
│   └── sales_detail.py        # Modelo de Detalles de Venta
└── data/
    ├── database.py            # Configuración de SQLAlchemy
    ├── db_sqlalchemy.py       # Nueva implementación con SQLAlchemy
    └── db.py                  # Wrapper para compatibilidad

alembic/                        # Carpeta de migraciones
├── versions/                   # Archivos de migración
├── env.py                     # Configuración de entorno de Alembic
└── script.py.mako             # Plantilla para migraciones

alembic.ini                     # Configuración de Alembic
```

## Modelos Creados

1. **Product** - Productos de la tortillería
2. **Customer** - Clientes
3. **Sale** - Ventas
4. **SaleDetail** - Detalles de cada venta

## Comandos de Alembic

### Ver estado de la base de datos
```bash
source venv/Scripts/activate  # Activar entorno virtual
alembic current                # Ver versión actual
alembic history                # Ver historial de migraciones
```

### Crear una nueva migración

Después de modificar los modelos en `app/models/`:

```bash
# Generar migración automáticamente
alembic revision --autogenerate -m "Descripción del cambio"

# Revisar el archivo generado en alembic/versions/
# Aplicar la migración
alembic upgrade head
```

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar hasta una versión específica
alembic upgrade <revision_id>

# Avanzar una migración
alembic upgrade +1
```

### Revertir migraciones

```bash
# Revertir la última migración
alembic downgrade -1

# Revertir hasta una versión específica
alembic downgrade <revision_id>

# Revertir todas las migraciones
alembic downgrade base
```

### Crear migración manual (sin autogenerate)

```bash
alembic revision -m "Descripción del cambio"
```

## Ejemplo: Agregar un nuevo campo a un modelo

1. Modificar el modelo en `app/models/`:
```python
# app/models/products.py
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    stock = Column(Integer, default=0)  # NUEVO CAMPO
```

2. Generar migración:
```bash
source venv/Scripts/activate
alembic revision --autogenerate -m "Add stock field to products"
```

3. Revisar el archivo generado en `alembic/versions/`

4. Aplicar la migración:
```bash
alembic upgrade head
```

## Ejemplo: Crear una nueva tabla

1. Crear el modelo en `app/models/suppliers.py`:
```python
from sqlalchemy import Column, Integer, String, Boolean
from app.data.database import Base

class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    active = Column(Boolean, default=True)
```

2. Agregar al `app/models/__init__.py`:
```python
from .suppliers import Supplier

__all__ = ['Product', 'Customer', 'Sale', 'SaleDetail', 'Supplier']
```

3. Generar y aplicar migración:
```bash
source venv/Scripts/activate
alembic revision --autogenerate -m "Add suppliers table"
alembic upgrade head
```

## Ventajas de SQLAlchemy + Alembic

- **ORM**: Trabaja con objetos Python en lugar de SQL crudo
- **Type Safety**: Mejor validación de tipos
- **Migraciones versionadas**: Control de cambios en la base de datos
- **Rollback**: Posibilidad de revertir cambios
- **Portabilidad**: Fácil cambiar de SQLite a PostgreSQL, MySQL, etc.
- **Relationships**: Manejo automático de relaciones entre tablas

## Notas Importantes

- Siempre activar el entorno virtual antes de ejecutar comandos de Alembic
- Revisar las migraciones autogeneradas antes de aplicarlas
- Hacer backup de la base de datos antes de aplicar migraciones en producción
- No modificar archivos de migración que ya fueron aplicados

## Solución de Problemas

### Error: "can't locate revision identified by..."
```bash
# Recrear la base de datos
rm tortilleria.db
alembic upgrade head
```

### Ver SQL que se ejecutará sin aplicarlo
```bash
alembic upgrade head --sql
```

### Base de datos fuera de sync
```bash
# Marcar como aplicada sin ejecutar
alembic stamp head
```
