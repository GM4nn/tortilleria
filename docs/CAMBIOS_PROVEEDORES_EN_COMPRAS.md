# Refactorización: Proveedores en Compras de Insumos

## Resumen de Cambios

Se ha refactorizado el sistema de compras de insumos para que cada compra esté asociada a un proveedor específico, en lugar de estar ligada únicamente al insumo.

### Motivación

Anteriormente, cada insumo tenía un proveedor fijo, y las compras se asociaban solo al insumo. Esto no reflejaba la realidad del negocio donde:
- Un mismo insumo puede comprarse a diferentes proveedores
- Los precios varían entre proveedores
- Es importante trackear qué proveedor suministró cada compra

### Cambios Implementados

#### 1. Modelo de Datos (`app/models/supplies.py`)

**Antes:**
```python
class SupplyPurchase(Base):
    supply_id = Column(Integer, ForeignKey('supplies.id'), nullable=False)
    # Sin relación directa con Supplier
```

**Después:**
```python
class SupplyPurchase(Base):
    supply_id = Column(Integer, ForeignKey('supplies.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)  # NUEVO

    # Relationships
    supply = relationship("Supply", back_populates="purchases")
    supplier = relationship("Supplier", backref="supply_purchases")  # NUEVO
```

#### 2. Base de Datos

**Migración de Alembic:** `2b1312ba3c20_add_supplier_to_supply_purchases.py`

- Agregó columna `supplier_id` a la tabla `supply_purchases`
- Migró datos existentes: copió el `supplier_id` del insumo a las compras existentes
- Agregó constraint de foreign key a la tabla `suppliers`

#### 3. Provider (`app/data/providers/supplies.py`)

**Cambios:**
- `get_supply_by_id()`: Ahora incluye joinedload del supplier de cada compra, y retorna `supplier_id` y `supplier_name` en cada compra
- `get_purchases_by_supply()`: Incluye información del proveedor en cada compra
- `add_purchase()`: Ahora requiere `supplier_id` como parámetro obligatorio
- `update_purchase()`: Ahora permite actualizar el `supplier_id`

#### 4. Formulario de Compra (`app/gui/supplies/purchase_form.py`)

**Nuevas características:**
- Campo de selección de proveedor (Combobox)
- Carga la lista de proveedores activos
- Pre-selecciona el proveedor sugerido del insumo (si existe)
- Valida que se seleccione un proveedor antes de guardar
- Pasa el `supplier_id` al método `add_purchase()`

#### 5. Vista de Detalle (`app/gui/supplies/supply_detail.py`)

**Mejoras:**
- La tabla de compras ahora muestra una columna "Proveedor"
- El panel de información de compra muestra el proveedor de cada compra
- Se ajustaron los anchos de columna para acomodar el nuevo campo

#### 6. Controlador de Contenido (`app/gui/supplies/content.py`)

**Modificación:**
- El método `show_purchase_form()` ahora obtiene el `supplier_id` sugerido del insumo
- Lo pasa al formulario a través del método `set_supply()`

### Flujo de Usuario

1. Usuario hace clic en "Nueva Compra" para un insumo
2. El formulario se abre con el proveedor sugerido pre-seleccionado
3. Usuario puede cambiar el proveedor si lo desea
4. Usuario completa los demás campos (cantidad, precio, etc.)
5. Al guardar, la compra queda asociada al proveedor seleccionado
6. En el historial de compras se muestra qué proveedor suministró cada compra

### Beneficios

- ✅ Mayor flexibilidad: permite comprar el mismo insumo a diferentes proveedores
- ✅ Mejor tracking: se sabe exactamente qué proveedor suministró cada compra
- ✅ Análisis de precios: se pueden comparar precios entre proveedores
- ✅ Histórico completo: se mantiene el registro de todos los proveedores utilizados
- ✅ Proveedor sugerido: el insumo mantiene un proveedor por defecto que se sugiere en nuevas compras

### Compatibilidad con Datos Existentes

La migración automática copia el proveedor del insumo a todas las compras existentes, asegurando que no se pierda información y que el sistema siga funcionando correctamente con datos históricos.

### Archivos Modificados

```
app/models/supplies.py                           - Modelo SupplyPurchase actualizado
app/data/providers/supplies.py                   - Provider con soporte de supplier_id
app/gui/supplies/purchase_form.py                - Formulario con selector de proveedor
app/gui/supplies/supply_detail.py                - Vista con columna de proveedor
app/gui/supplies/content.py                      - Controlador actualizado
alembic/versions/2b1312ba3c20_*.py              - Migración de base de datos
alembic/env.py                                   - Configuración batch mode para SQLite
```

### Próximos Pasos Sugeridos

- [ ] Agregar reportes de compras por proveedor
- [ ] Comparador de precios entre proveedores
- [ ] Historial de proveedores por insumo
- [ ] Evaluación de proveedores (calidad, puntualidad, etc.)
