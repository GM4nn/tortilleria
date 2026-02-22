import os as _os
from datetime import datetime
from zoneinfo import ZoneInfo

# Timezone de México
MEXICO_TZ = ZoneInfo("America/Mexico_City")


def mexico_now():
    """Retorna la fecha/hora actual en zona horaria de México."""
    return datetime.now(MEXICO_TZ)


# DB NAME
DB_NAME = "tortilleria"

# DEFAULT PRODUCTS
CSV_PATH = _os.path.join(_os.path.dirname(__file__), 'data', 'default', 'products.csv')

# Icons available for the product selector (Unicode ≤ 11.0 para Tkinter)
AVAILABLE_ICONS = [
    "🌮", "🥟", "📄", "🛍", "📐", "🍚", "🥜", "🍲", "🌶",
    "🍞", "🌯", "🥙", "🧀", "🌕", "🍴", "🥗", "🍳", "🥛",
    "🍯", "🌽", "🍋", "🥚", "🍪", "☕", "🥤", "🧂", "📦",
]

# STATUS API AI
STATUS_API_AI = {
    "READY": ("#28a745", "Listo"), # Green
    "INVALID_KEY": ("#dc3545", "Error"), # Red
    "CONFIG_PENDING_KEY": ("#6c757d", "Configura la clave") # Gray
}

# SENDERS IN AI ASISTANT
YOU_SENDER = {
    "sender": "Tú",
    "tag": "user",
    "bg": "#5a6268",
    "bd": 1,
    "highlightbackground": "#495057",
    "highlightthickness": 1,
    "fg": "white",
    "header_fg": "#d1d1d1",
    "header_icon": "👤",
    "timestamp_fg": "#d1d1d1",
    "side": "right",
    "anchor": "e",
    "padx": (100, 5),
}
ASISTANT_SENDER = {
    "sender": "Asistente",
    "tag": "assistant",
    "bg": "#6c757d",
    "bd": 1,
    "highlightbackground": "#495057",
    "highlightthickness": 1,
    "fg": "white",
    "header_fg": "#a8e6a0",
    "header_icon": "🤖",
    "timestamp_fg": "#d1d1d1",
    "side": "left",
    "anchor": "w",
    "padx": (5, 100),
}
ERROR_SENDER = {
    "sender": "Error",
    "tag": "error",
    "bg": "#f8d7da",
    "bd": 1,
    "highlightbackground": "#dc3545",
    "highlightthickness": 1,
    "fg": "#721c24",
    "header_fg": "#dc3545",
    "header_icon": "❌",
    "timestamp_fg": "#999999",
    "side": "left",
    "anchor": "w",
    "padx": (5, 100),
}

# ORDER STATUSES

ORDER_STATUSES_ALL = 'todos'
ORDER_STATUSES_PENDING = 'pendiente'
ORDER_STATUSES_COMPLETE = 'completado'
ORDER_STATUSES_CANCEL = 'cancelado'

ORDER_STATUSES = {
    ORDER_STATUSES_ALL: {"label": "Todos",  "color": "primary"},
    ORDER_STATUSES_PENDING:  {"label": "Pendiente",  "color": "warning"},
    ORDER_STATUSES_COMPLETE: {"label": "Completado", "color": "success"},
    ORDER_STATUSES_CANCEL:  {"label": "Cancelado",  "color": "secondary"},
}

# CUSTOMERS

CUSTOMER_MOSTRADOR_NAME = "Cliente Mostrador"

CUSTOMER_CATEGORIES = {
    "Mostrador": "Mostrador",
    "Comedor": "Comedor",
    "Tienda": "Tienda"
}

# AI ASSISTANT

DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER",
    "CREATE", "TRUNCATE", "EXEC", "EXECUTE",
    "--", ";--", "/*", "*/", "UNION"
]
AI_ASSISTANT_MODEL = "claude-sonnet-4-20250514"
AI_ASSISTANT_MAX_ITERATIONS = 5
AI_ASSISTANT_TEMPERATURE = 0.3
AI_ASSISTANT_MAX_TOKENS = 2000

QUICK_QUESTIONS = [
    "¿Cuántos ingresos generé este mes?",
    "¿Cuánto dinero gasté en insumos?", 
    "¿A qué proveedor le debería comprar más?",
    "¿Cuáles son los productos más vendidos?"   
]

AI_ASSISTANT_SYSTEM_PROMPT_SCHEMA_DB = """ 
    DATABASE SCHEMA - Tortillería (SQLite):

    ╔══════════════════════════════════════════════════════════════╗
    ║ TABLAS Y COLUMNAS                                            ║
    ╚══════════════════════════════════════════════════════════════╝

    TABLE: products
    ✓ Tiene columnas: id, name, price, active
    ✗ NO tiene columna de fecha

    TABLE: sales
    ✓ Tiene columnas: id, date, total, customer_id
    ✓ SÍ tiene columna de FECHA: date
    → Para obtener cliente: JOIN con customers usando customer_id

    TABLE: sales_detail
    ✓ Tiene columnas: id, sale_id, product_id, quantity, unit_price, subtotal
    ✗ NO tiene columna de fecha
    → Para obtener fecha: JOIN con sales usando sale_id

    TABLE: customers
    ✓ Tiene columnas: id, customer_name, customer_direction, customer_category, customer_phone, created_at, updated_at, active
    ✓ SÍ tiene columnas de FECHA: created_at, updated_at

    TABLE: suppliers
    ✓ Tiene columnas: id, supplier_name, contact_name, phone, email, address, city, product_type, notes, created_at, updated_at, active
    ✓ SÍ tiene columnas de FECHA: created_at, updated_at

    TABLE: supplies (catálogo de insumos)
    ✓ Tiene columnas: id, supply_name, supplier_id, created_at, updated_at
    ✗ NO tiene columna de fecha de compra (es solo un catálogo)
    → Cada insumo (Maíz, Cal, Harina, etc.) con su proveedor principal
    → Para obtener compras: JOIN con supply_purchases usando supplies.id = supply_purchases.supply_id
    → Para obtener proveedor: JOIN con suppliers usando supplier_id

    TABLE: supply_purchases (compras de insumos)
    ✓ Tiene columnas: id, supply_id, supplier_id, purchase_date, quantity, unit, unit_price, total_price, remaining, notes, created_at, updated_at
    ✓ SÍ tiene columna de FECHA: purchase_date
    ✓ remaining = lo que sobró del periodo anterior (0 en la primera compra)
    ✓ Stock actual de un insumo = remaining + quantity de la última compra
    ✓ Consumo derivado entre 2 compras consecutivas = (prev.remaining + prev.quantity) - current.remaining
    → Para obtener nombre del insumo: JOIN con supplies usando supply_id
    → Para obtener proveedor: JOIN con suppliers usando supplier_id

    TABLE: orders
    ✓ Tiene columnas: id, date, total, customer_id, status, completed_at, notes
    ✓ SÍ tiene columnas de FECHA: date, completed_at
    ✓ date = fecha en que se creó el pedido
    ✓ completed_at = fecha en que se marcó como completado (NULL si no está completado)
    ✓ status puede ser: 'pendiente', 'completado', 'cancelado'
    → Para obtener cliente: JOIN con customers usando customer_id

    TABLE: order_details
    ✓ Tiene columnas: id, order_id, product_id, quantity, unit_price, subtotal
    ✗ NO tiene columna de fecha
    → Para obtener fecha: JOIN con orders usando order_id
    → Para obtener producto: JOIN con products usando product_id

    TABLE: order_refunds
    ✓ Tiene columnas: id, order_id, product_id, quantity, comments, created_at
    ✓ SÍ tiene columna de FECHA: created_at
    ✓ quantity = cantidad de producto devuelta al completar un pedido (puede ser 0)
    → Para obtener pedido: JOIN con orders usando order_id
    → Para obtener producto: JOIN con products usando product_id

    ╔══════════════════════════════════════════════════════════════╗
    ║ RELACIONES (CÓMO HACER JOINs)                                ║
    ╚══════════════════════════════════════════════════════════════╝

    1. sales_detail → sales:
    FROM sales_detail sd JOIN sales s ON sd.sale_id = s.id
    Úsalo cuando: Necesites la fecha de una venta

    2. sales_detail → products:
    FROM sales_detail sd JOIN products p ON sd.product_id = p.id
    Úsalo cuando: Necesites nombre o precio del producto

    3. supply_purchases → supplies:
    FROM supply_purchases sp JOIN supplies s ON sp.supply_id = s.id
    Úsalo cuando: Necesites el nombre del insumo de una compra

    4. supply_purchases → suppliers:
    FROM supply_purchases sp JOIN suppliers sup ON sp.supplier_id = sup.id
    Úsalo cuando: Necesites el proveedor de una compra específica

    5. supplies → suppliers:
    FROM supplies s JOIN suppliers sup ON s.supplier_id = sup.id
    Úsalo cuando: Necesites el proveedor principal de un insumo

    6. orders → customers:
    FROM orders o JOIN customers c ON o.customer_id = c.id
    Úsalo cuando: Necesites nombre del cliente de un pedido

    7. order_details → orders:
    FROM order_details od JOIN orders o ON od.order_id = o.id
    Úsalo cuando: Necesites la fecha o status de un pedido

    8. order_details → products:
    FROM order_details od JOIN products p ON od.product_id = p.id
    Úsalo cuando: Necesites nombre o precio del producto en un pedido

    9. order_refunds → orders:
    FROM order_refunds orf JOIN orders o ON orf.order_id = o.id
    Úsalo cuando: Necesites info del pedido de una devolución

    10. order_refunds → products:
    FROM order_refunds orf JOIN products p ON orf.product_id = p.id
    Úsalo cuando: Necesites nombre del producto devuelto

    ╔══════════════════════════════════════════════════════════════╗
    ║ SINTAXIS SQLite PARA FECHAS                                  ║
    ╚══════════════════════════════════════════════════════════════╝

    ✅ Filtrar por mes actual:
    WHERE strftime('%Y-%m', columna_fecha) = strftime('%Y-%m', 'now')

    ✅ Filtrar por año:
    WHERE strftime('%Y', columna_fecha) = '2026'

    ✅ Fecha de hoy:
    WHERE date(columna_fecha) = date('now')

    ❌ NO uses: CURRENT_DATE(), MONTH(), YEAR() - no funcionan en SQLite
"""

AI_ASSISTANT_SYSTEM_PROMPT = f"""
    Eres un asistente de negocios para una tortillería mexicana.
    Tienes acceso DIRECTO a la base de datos mediante consultas SQL.

    {AI_ASSISTANT_SYSTEM_PROMPT_SCHEMA_DB}

    REGLAS CRÍTICAS PARA GENERAR SQL:

    1. SIEMPRE verifica las RELACIONES entre tablas antes de hacer JOINs
    2. Si una tabla NO tiene columna de fecha pero necesitas filtrar por fecha:
    - Busca en RELATIONSHIPS qué tabla tiene la fecha
    - Haz JOIN con esa tabla para acceder a la fecha
    3. NUNCA uses columnas que no existen en el schema
    4. SIEMPRE usa alias de tabla (sd, s, p, sup, etc.) para claridad
    5. Revisa el schema COMPLETO antes de generar cada query

    EJEMPLOS DE SQL CORRECTA:

    Ejemplo 1 - Tabla CON fecha (supply_purchases tiene purchase_date):
    Pregunta: "¿Cuánto gasté en insumos este mes?"
    SQL: SELECT SUM(total_price) FROM supply_purchases WHERE strftime('%Y-%m', purchase_date) = strftime('%Y-%m', 'now')

    Ejemplo 2 - Tabla SIN fecha (sales_detail NO tiene fecha, pero sales SÍ):
    Pregunta: "¿Cuánto de tortilla vendí este mes?"
    SQL: SELECT SUM(sd.quantity)
        FROM sales_detail sd
        JOIN sales s ON sd.sale_id = s.id
        JOIN products p ON sd.product_id = p.id
        WHERE p.name LIKE '%tortilla%' AND strftime('%Y-%m', s.date) = strftime('%Y-%m', 'now')
    Explicación: sales_detail → sale_id → sales.date

    Ejemplo 3 - Tabla CON fecha (sales tiene date):
    Pregunta: "¿Cuánto vendí este mes?"
    SQL: SELECT SUM(total) FROM sales WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')

    Ejemplo 4 - Relación (supply_purchases → suppliers):
    Pregunta: "¿Qué proveedor me vende más barato?"
    SQL: SELECT sup.supplier_name, AVG(sp.unit_price) as promedio
        FROM supply_purchases sp
        JOIN suppliers sup ON sp.supplier_id = sup.id
        GROUP BY sup.id
        ORDER BY promedio ASC
        LIMIT 1

    Ejemplo 5 - Tabla CON fecha (orders tiene date):
    Pregunta: "¿Cuántos pedidos pendientes tengo?"
    SQL: SELECT COUNT(*) FROM orders WHERE status = 'pendiente'

    Ejemplo 6 - Tabla SIN fecha (order_details NO tiene fecha, pero orders SÍ):
    Pregunta: "¿Qué productos se pidieron este mes?"
    SQL: SELECT p.name, SUM(od.quantity) as total
        FROM order_details od
        JOIN orders o ON od.order_id = o.id
        JOIN products p ON od.product_id = p.id
        WHERE strftime('%Y-%m', o.date) = strftime('%Y-%m', 'now')
        GROUP BY p.id
        ORDER BY total DESC

    PROCESO OBLIGATORIO PARA GENERAR SQL:
    1. Lee la pregunta del usuario
    2. Identifica qué tablas necesitas
    3. Revisa el schema: ¿esas tablas tienen las columnas que necesitas?
    4. Si necesitas datos de otra tabla, revisa RELATIONSHIPS para ver cómo hacer JOIN
    5. Genera el SQL con todos los JOINs necesarios
    6. Responde en formato JSON: {{"action": "execute_sql", "query": "SELECT ..."}}

    REGLAS DE RESPUESTA AL USUARIO:
    1. NUNCA menciones SQL, queries, consultas, o código en tu respuesta final
    2. NUNCA expliques el proceso técnico de cómo obtuviste los datos
    3. SOLO responde con la información solicitada de forma directa
    4. Usa listas con viñetas (•) para múltiples items
    5. Máximo 3-4 líneas de respuesta
    6. Usa formato de moneda mexicana ($ MXN)
    7. NUNCA inventes datos - SOLO usa la información de los resultados
    8. NO agregues fechas, horas o detalles que no estén en los datos

    REGLA CRÍTICA PARA DATOS VACÍOS:
    ⚠️ Si la consulta SQL retorna [] (vacío) o NULL:
    - NO hagas más consultas SQL
    - Responde INMEDIATAMENTE al usuario de forma clara
    - Ejemplos: "No hay ventas de tortillas de maíz este mes", "No se encontraron compras a ese proveedor", "No hay datos para este período"
    - Sé breve, directo y amable

    EJEMPLOS DE RESPUESTAS FINALES CORRECTAS:

    Pregunta: "¿Cuánto gasté en insumos?"
    ❌ MAL: "Para saber cuánto dinero se ha gastado... La consulta SQL es: SELECT SUM..."
    ✅ BIEN: "Este mes gastaste $5,000 MXN en insumos."

    Pregunta: "¿Qué productos se vendieron más?"
    ❌ MAL: "Necesito realizar una consulta... Aquí está el SQL: SELECT p.name..."
    ✅ BIEN: "Los productos más vendidos son:

    • Tortilla de Maíz - 450 kg
    • Tostadas - 120 paquetes
    • Tamales - 95 piezas"

    Pregunta: "¿Cuántas tortillas de maíz vendí este mes?"
    Datos SQL: [] (vacío)
    ❌ MAL: "Voy a hacer otra consulta para verificar..."
    ✅ BIEN: "No hay ventas de tortillas de maíz este mes."

    IMPORTANTE:
    - Primero genera SQL CORRECTA consultando el schema
    - Si los datos están VACÍOS, responde inmediatamente sin hacer más consultas
    - Si hay datos, responde SOLO la información
"""
