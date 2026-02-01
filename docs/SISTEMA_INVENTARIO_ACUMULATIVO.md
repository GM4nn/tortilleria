# Sistema de Inventario Acumulativo

## ¿Qué cambió?

Anteriormente, el sistema trataba cada compra de manera aislada. Ahora implementa un **sistema de inventario acumulativo** que considera el stock restante de períodos anteriores.

## Ejemplo Práctico

### Antes (Sistema Antiguo)
- **Semana 1**: Compras 15 costales, consumes 10, sobran 5
- **Semana 2**: Compras 10 costales nuevos
  - ❌ El sistema solo consideraba los 10 nuevos
  - ❌ Los 5 sobrantes no se tenían en cuenta

### Ahora (Sistema Acumulativo)
- **Semana 1**: Compras 15 costales, consumes 10, sobran 5
- **Semana 2**: Compras 10 costales nuevos
  - ✅ Stock inicial: 5 costales (sobrantes)
  - ✅ Nueva compra: 10 costales
  - ✅ **Stock total disponible: 15 costales** (5 + 10)
  - ✅ Cuando registres el consumo, debe ser sobre los 15 totales

## Cambios Implementados

### 1. Modelo de Base de Datos
- Se agregó el campo `initial_stock` a la tabla `supply_purchases`
- Este campo almacena automáticamente el stock acumulado ANTES de cada compra

### 2. Cálculo Automático de Stock
El sistema ahora calcula automáticamente:
- **Stock actual**: Restante de la última compra/consumo registrado
- **Stock inicial de nueva compra**: Se calcula automáticamente cuando registras una compra
- **Validaciones**: Consumido + Restante debe ser igual al stock total (stock anterior + compra actual)

### 3. Formulario de Compras
Cuando registras una nueva compra, el formulario muestra:
- **Última Compra**: Fecha y cantidad de la compra anterior
- **Stock Anterior a esa Compra**: Cuánto había antes de esa compra
- **Validación de Consumo**: Ahora valida contra el stock total disponible

Ejemplo de validación:
```
Stock anterior: 5.00 costales
Última compra: 15.00 costales
Total disponible: 20.00 costales

Consumido: 12.00 costales
Restante: 8.00 costales
✅ 12 + 8 = 20 (Correcto)
```

### 4. Vista de Detalle de Insumos
Los indicadores ahora muestran:
- **Stock Actual**: Inventario total disponible en este momento (acumulativo)
- **Restante (Período)**: Lo que sobró del período específico
- **Stock Total Disponible**: Incluye el stock anterior + la compra

### 5. Panel de Consumo
Cuando seleccionas una compra en el historial:
- Muestra el **Stock Anterior** si había inventario previo
- Muestra la **Compra del período**
- Muestra el **Stock Total Disponible** (suma de ambos)
- Calcula el porcentaje de consumo sobre el stock total

## Flujo de Trabajo Recomendado

### Primera Compra
1. Registras la compra (ej: 15 costales)
2. Stock inicial = 0
3. Stock total = 15

### Segunda Compra en Adelante
1. El sistema te pide el consumo de la compra anterior
2. Debes ingresar:
   - **Consumido**: Cuánto usaste
   - **Restante**: Cuánto sobró
   - ✅ Consumido + Restante = Stock anterior + Compra anterior
3. El sistema guarda automáticamente el restante como `initial_stock` de la nueva compra
4. Registras la nueva compra
5. Stock total = Restante anterior + Nueva compra

## Beneficios

1. **Trazabilidad Real**: Sabes exactamente cuánto inventario tienes en todo momento
2. **Control Acumulativo**: No se pierden los sobrantes de períodos anteriores
3. **Reportes Precisos**: Los indicadores reflejan el inventario real
4. **Validaciones Mejoradas**: El sistema valida que los números cuadren con el stock total
5. **Transparencia**: Puedes ver el flujo completo del inventario en cada compra

## Migración de Datos

- Las compras existentes tienen `initial_stock = 0.0` por defecto
- Las nuevas compras calcularán automáticamente el `initial_stock` basándose en el último consumo registrado
- El sistema es retrocompatible: funciona tanto con datos antiguos como nuevos

## Notas Técnicas

### Cálculo de Stock Actual
```python
# Si hay consumos registrados:
stock_actual = último_consumo.quantity_remaining

# Si no hay consumos pero hay compras:
stock_actual = suma_de_todas_las_compras

# Si no hay nada:
stock_actual = 0
```

### Validación de Consumo
```python
stock_total_disponible = initial_stock + última_compra
consumido + restante = stock_total_disponible ± tolerancia(0.01)
```

## Soporte

Si encuentras algún problema o tienes preguntas sobre el sistema de inventario acumulativo, por favor reporta el issue en el repositorio.
