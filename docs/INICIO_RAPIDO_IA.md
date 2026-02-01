# 🚀 Inicio Rápido - Asistente IA con Claude

## ⚡ Instalación Express (3 pasos)

### 1. Obtener API Key de Anthropic
```
Ir a: https://console.anthropic.com/settings/keys
Crear cuenta → Create Key → Copiar tu API key
```

### 2. Configurar la API Key

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="tu-api-key-aqui"
```

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY="tu-api-key-aqui"
```

### 3. Instalar dependencias e iniciar
```bash
pip install anthropic sqlalchemy alembic
python main.py
```

**¡Listo!** Haz clic en **🤖 Asistente IA** en el menú.

---

## 💡 Ejemplos de Preguntas

### 📈 VENTAS E INGRESOS

```
¿Cuántos ingresos generé este mes?
```
**Respuesta esperada**: Total de ventas del mes actual con desglose

```
¿Cuánto vendí hoy?
```
**Respuesta esperada**: Ventas del día actual

```
¿Cuáles son mis productos más vendidos?
```
**Respuesta esperada**: Top 10 productos con cantidades y revenue

```
¿Cuántas ventas hice esta semana?
```
**Respuesta esperada**: Desglose diario de ventas de los últimos 7 días

---

### 💰 GASTOS E INSUMOS

```
¿Cuánto gasté en insumos este mes?
```
**Respuesta esperada**: Total gastado con desglose por tipo de insumo

```
¿En qué insumo gasté más dinero?
```
**Respuesta esperada**: Lista ordenada de gastos por insumo

```
¿Cuánto me costó el maíz este mes?
```
**Respuesta esperada**: Total gastado específicamente en maíz

---

### 🚚 PROVEEDORES

```
¿A qué proveedor le debería comprar más?
```
**Respuesta esperada**: Lista de proveedores ordenados por cantidad comprada

```
¿Cuál es mi proveedor principal?
```
**Respuesta esperada**: Proveedor con más compras totales

```
¿Cuánto le he comprado a cada proveedor?
```
**Respuesta esperada**: Desglose de gastos por proveedor

---

### 📦 PRODUCTOS

```
¿Qué producto genera más ingresos?
```
**Respuesta esperada**: Producto con mayor revenue total

```
¿Cuántas tortillas de maíz vendí este mes?
```
**Respuesta esperada**: Cantidad específica de ese producto

```
Muéstrame las ventas de tostadas
```
**Respuesta esperada**: Estadísticas de ventas de tostadas

---

## 🎯 Consejos para hacer mejores preguntas

### ✅ Buenas preguntas:
- "¿Cuántos ingresos generé este mes?"
- "¿Qué proveedor tiene mejores precios?"
- "Muéstrame los productos más vendidos"

### ❌ Evitar:
- Preguntas muy vagas: "¿Cómo va todo?"
- Múltiples preguntas a la vez: "¿Cuánto vendí y cuánto gasté y quién es el mejor cliente?"
- Datos que no están en la base de datos: "¿Qué clima hará mañana?"

---

## 🟢 Indicadores de Estado

| Color | Estado | Significado |
|-------|--------|-------------|
| 🟢 Verde | Listo | Claude está funcionando |
| 🟡 Amarillo | Falta API Key | Configura ANTHROPIC_API_KEY |
| 🔴 Rojo | API Key Inválida | Verifica tu API key |

---

## ⚠️ Solución Rápida de Problemas

### "Falta configurar ANTHROPIC_API_KEY"
```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="tu-api-key-aqui"

# macOS/Linux
export ANTHROPIC_API_KEY="tu-api-key-aqui"
```

### "API key inválida"
1. Ve a: https://console.anthropic.com/settings/keys
2. Crea una nueva API key
3. Copia la key completa (empieza con `sk-ant-`)
4. Actualiza la variable de entorno

### "El asistente tarda en responder"
- Espera 5-10 segundos (normal para consultas complejas)
- Verifica tu conexión a internet
- Claude procesa las consultas en la nube

---

## 📱 Interfaz del Asistente

```
┌─────────────────────────────────────────┐
│ 🤖 Asistente Inteligente      🟢 Listo │
│ Pregunta sobre ventas, gastos...       │
├─────────────────────────────────────────┤
│                                         │
│  [Chat Area]                            │
│                                         │
│  TÚ: ¿Cuánto vendí este mes?           │
│                                         │
│  ASISTENTE: Este mes generaste         │
│  $15,432.50 MXN en 87 ventas...        │
│                                         │
├─────────────────────────────────────────┤
│ [Preguntas Rápidas]                     │
│ [¿Ingresos?] [¿Gastos?] [...]          │
├─────────────────────────────────────────┤
│ [Escribe tu pregunta aquí...          ]│
│                        [Preguntar] [X]  │
└─────────────────────────────────────────┘
```

---

## 🔧 Configuración Permanente de API Key

### Windows (Permanente):
1. Busca "Variables de entorno" en el menú inicio
2. Clic en "Editar las variables de entorno del sistema"
3. Clic en "Variables de entorno..."
4. En "Variables del sistema" → "Nueva..."
5. Nombre: `ANTHROPIC_API_KEY`
6. Valor: tu-api-key
7. Aceptar en todas las ventanas
8. Reiniciar la aplicación

### macOS/Linux (Permanente):
```bash
# Agregar al archivo de configuración de tu shell
echo 'export ANTHROPIC_API_KEY="tu-api-key"' >> ~/.bashrc
source ~/.bashrc
```

---

## 💰 Costos de Uso

### Precios de Claude API:
- **~$0.001 USD por pregunta simple** (menos de 1 centavo)
- **~$0.01 USD por pregunta compleja** (1 centavo)

### Estimaciones mensuales:
- **100 preguntas/mes**: ~$1 USD
- **500 preguntas/mes**: ~$5 USD
- **1000 preguntas/mes**: ~$10 USD

**Más económico que:**
- Contratar un analista de datos
- Licencias de software empresarial
- Hardware para correr modelos locales

---

## 📊 Comparación: Claude vs Ollama

| Característica | Claude Sonnet 4.5 | Ollama Local |
|----------------|-------------------|---------------|
| Instalación | 5 minutos | 30-60 minutos |
| Tamaño descarga | 0 MB | 2-4 GB |
| Velocidad | 1-3 seg | 5-30 seg |
| Precisión | Excelente | Buena |
| Hardware necesario | Cualquier PC | 8+ GB RAM |
| Internet | Requerido | Opcional |
| Costo mensual | $5-10 USD | Gratis |

**Recomendación:** Claude es mejor para la mayoría de usuarios por su facilidad de uso y precisión.

---

## ✨ Próximos Pasos

Después de probar el asistente básico:

1. Lee el [ASISTENTE_IA_README.md](ASISTENTE_IA_README.md) completo
2. Experimenta con diferentes tipos de preguntas
3. Revisa las consultas SQL ejecutadas (botón "Ver SQL")
4. Configura la API key de forma permanente

---

## 🔐 Seguridad y Privacidad

**¿Es seguro usar Claude?**
- Sí. Anthropic no usa tus datos para entrenar modelos
- Las conversaciones no se almacenan permanentemente
- Cumple con GDPR y regulaciones de privacidad
- Solo se envían datos agregados (totales, conteos)
- NO se envía la base de datos completa

Más info: https://www.anthropic.com/privacy

---

¡Disfruta tu asistente inteligente! 🎉
