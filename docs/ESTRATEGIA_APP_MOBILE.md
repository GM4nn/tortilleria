# Estrategia: App Mobile para Repartidores

## Objetivo
Que los repartidores vean y actualicen pedidos desde una app mobile (APK),
mientras la app de escritorio sigue usando SQLite local (rapido).

## Arquitectura decidida

```
[App Escritorio - SQLite local]
   Al crear pedido → guarda en SQLite + inserta en Neon (background)

[Neon PostgreSQL - solo pedidos]
   Almacena pedidos activos (pendiente/en_ruta/completado)

[App Mobile Repartidor - conexion directa a Neon]
   Lee pedidos pendientes asignados
   Marca como completado → escribe en Neon

[App Escritorio - polling cada 30seg]
   Consulta Neon: "hay pedidos con status actualizado?"
   Si hay cambios → actualiza SQLite local
```

## Flujo completo
1. En escritorio se crea pedido → SQLite + Neon
2. Repartidor abre APK → lee de Neon → ve sus pedidos
3. Repartidor completa entrega → actualiza status en Neon
4. App escritorio (polling 30seg) → detecta cambio → actualiza SQLite

## Seguridad de la URI en la APK
- Crear usuario de Neon con permisos limitados (solo SELECT/UPDATE en orders)
- Considerar ofuscar la URI en la APK
- Alternativa mas segura: mini API en servicio gratuito (Render/Railway)

## Conexion Neon (ya creada)
- Proyecto: Tortilleria
- Region: AWS South America East 1 (Sao Paulo)
- URI: postgresql://neondb_owner:***@ep-dark-thunder-ac9gb4ns-pooler.sa-east-1.aws.neon.tech/tortilleria
- Plan: Free (500MB, 100 compute-hrs/mes)

## Pendiente por definir
- [ ] Framework para la APK (Flutter? React Native? Kotlin?)
- [ ] Que datos exactos necesita ver el repartidor
- [ ] Si usar conexion directa a Neon desde APK o mini API intermedia
- [ ] Modelo de datos para sincronizacion (campo updated_at, sync_status, etc.)
