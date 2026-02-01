# Ejemplo de Uso: Stock Acumulativo

## Caso Real de Uso

Este documento explica cómo el sistema maneja el caso donde consumes tanto de la compra actual como del stock sobrante anterior.

## 📊 Escenario Ejemplo

### Semana 1 (15/12/2024)
**Compra:**
- 15 costales de maíz
- Precio: $150/costal
- Total: $2,250

**Consumo (hasta 22/12/2024):**
- Gastaste: 13 costales
- Sobraron: **2 costales**

---

### Semana 2 (22/12/2024)
**Nueva Compra:**
- 10 costales nuevos
- Precio: $150/costal
- Total: $1,500

**Stock Total Disponible:**
- 2 costales (sobrantes de la semana 1)
- + 10 costales (compra nueva)
- **= 12 costales totales**

**Consumo (hasta 29/12/2024):**
- Gastaste: 11 costales (¡incluyen 2 del stock anterior!)
- Sobraron: **1 costal**

**Desglose del consumo:**
```
11 costales gastados pueden ser:
- 2 costales del stock anterior
- 9 costales de la compra nueva
```

---

### Semana 3 (29/12/2024)
**Nueva Compra:**
- 20 costales nuevos
- Precio: $150/costal
- Total: $3,000

**Stock Total Disponible:**
- 1 costal (sobrante de la semana 2)
- + 20 costales (compra nueva)
- **= 21 costales totales**

## 🎯 Cómo lo Maneja el Sistema

### 1. Formulario de Nueva Compra

Cuando registras una nueva compra, el sistema te muestra:

```
╔═══════════════════════════════════════════════════════╗
║  Registrar Consumo del Período                       ║
║  ¿Cuánto gastaste desde la última compra?            ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Última Compra: 22/12/2025 (12.00 costales)         ║
║  Lo que Sobraba Antes: 2.00 costales                 ║
║                                                       ║
║  ┌─────────────────────────────────────────────┐     ║
║  │  Total Disponible en el Período             │     ║
║  │  12.00 costales                              │     ║
║  │  (2.00 sobrantes + 10.00 comprados)         │     ║
║  └─────────────────────────────────────────────┘     ║
║                                                       ║
║  ¿Cuánto Gastaste?*                                  ║
║  [11] (puede incluir lo sobrante)                    ║
║                                                       ║
║  ¿Cuánto Sobró?*                                     ║
║  [1] (lo que no usaste)                              ║
║                                                       ║
║  ✓ Perfecto: 11.00 + 1.00 = 12.00                   ║
╚═══════════════════════════════════════════════════════╝
```

### 2. Validación en Tiempo Real

Mientras escribes los números, el sistema valida:

**Caso 1: Números correctos**
```
Gastaste: 11
Sobró: 1
✓ Perfecto: 11.00 + 1.00 = 12.00
```

**Caso 2: Te falta asignar**
```
Gastaste: 10
Sobró: 1
⚠ Faltan 1.00 por asignar (Total: 12.00)
```

**Caso 3: Te pasaste**
```
Gastaste: 12
Sobró: 2
✗ Te pasaste por 2.00 (Total: 12.00)
```

### 3. Registro en Base de Datos

El sistema registra:

**Consumo:**
```sql
supply_consumptions:
- start_date: 2024-12-22
- end_date: 2024-12-29
- quantity_consumed: 11.00
- quantity_remaining: 1.00
```

**Nueva Compra:**
```sql
supply_purchases:
- purchase_date: 2024-12-29
- quantity: 20.00
- initial_stock: 1.00  ← ¡Automático!
```

## ✅ Ventajas del Sistema

1. **No pierdes control**: Sabes exactamente cuánto tienes en todo momento
2. **Validación automática**: El sistema verifica que los números cuadren
3. **Trazabilidad completa**: Puedes rastrear todo el flujo de inventario
4. **Flexibilidad**: Puedes consumir tanto del stock anterior como de la compra nueva
5. **Visual**: Ves en tiempo real si los números están correctos

## 🔍 Vista de Detalle

En la vista de detalle del insumo, verás:

```
╔════════════════════════════════════════════════════════╗
║  Período Actual de Consumo                            ║
║  Del 22/Dic/2024 al 29/Dic/2024                      ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  Compra (22/Dic/2024)    Consumido    Inventario      ║
║  10.00 costales          11.00        Disponible      ║
║                          costales     21.00 costales  ║
║  Restante (Período)      Compra       (Lo que tienes  ║
║  1.00 costales           Actual       ahora)          ║
║                          20.00                         ║
║                          costales                      ║
╚════════════════════════════════════════════════════════╝
```

## 💡 Consejos

- **Siempre registra el consumo** cuando hagas una nueva compra
- **Los números deben cuadrar**: Gastado + Sobrante = Total Disponible
- **Usa las notas** para aclarar detalles importantes
- **Revisa el resumen visual** antes de guardar

## 🎓 Resumen

El sistema acumulativo te permite:
- Gestionar inventario de manera realista
- Consumir del stock anterior y de la compra nueva
- Validar que todo cuadre automáticamente
- Tener visibilidad completa del flujo

**¡No más inventario perdido!** 🎉
