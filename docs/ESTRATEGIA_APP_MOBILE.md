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

## Flujo completo (5 pasos)
1. **Crear pedido**: El usuario crea un pedido en la app de escritorio → se guarda en SQLite + se inserta en Neon (en background)
2. **Asignar repartidor**: Se asigna el pedido a un repartidor (ej: "José")
3. **Repartidor ve pedido**: José abre la APK → la APK consulta Neon via API → ve sus pedidos pendientes
4. **Repartidor completa**: José entrega y marca como completado → se actualiza status en Neon
5. **Escritorio detecta cambio**: La app de escritorio (polling cada 30seg) detecta que el pedido paso de "pendiente" a "completado" en Neon → actualiza SQLite local → muestra toast/notificacion

## Implementacion tecnica del polling (Paso 5)

### Tkinter `after()` para polling en background
```python
# En la clase principal de la app (TortilleriaApp)
def iniciar_polling_pedidos(self):
    self._verificar_pedidos_neon()

def _verificar_pedidos_neon(self):
    # Ejecutar consulta a Neon en thread separado para no bloquear GUI
    import threading
    thread = threading.Thread(target=self._consultar_neon, daemon=True)
    thread.start()
    # Re-programar cada 30 segundos
    self.root.after(30000, self._verificar_pedidos_neon)

def _consultar_neon(self):
    # Conectar a Neon, buscar pedidos con status cambiado
    # Si hay cambios → actualizar SQLite local
    # Mostrar toast en el hilo principal:
    #   self.root.after(0, lambda: self._mostrar_toast("Pedido #123 completado"))
    pass
```

### Toast / Notificacion
- Usar `ttkbootstrap.toast.ToastNotification` o crear un widget custom
- Aparece en esquina inferior derecha, se auto-cierra en 5 segundos
- Muestra: "Pedido #XX completado por [repartidor]"

## Seguridad

### URI en la APK
- **NO** exponer la URI de Neon directamente en la APK
- Usar una **mini API** (FastAPI en Render/Railway, plan gratuito) como intermediario
- La API valida al repartidor y solo expone endpoints necesarios:
  - `GET /pedidos?repartidor=jose` → pedidos pendientes
  - `PATCH /pedidos/{id}` → marcar como completado

### Permisos en Neon
- Crear usuario con permisos limitados (solo SELECT/UPDATE en tabla orders)
- La API usa este usuario restringido

## Conexion Neon (ya creada)
- Proyecto: Tortilleria
- Region: AWS South America East 1 (Sao Paulo)
- URI: postgresql://neondb_owner:***@ep-dark-thunder-ac9gb4ns-pooler.sa-east-1.aws.neon.tech/tortilleria
- Plan: Free (500MB, 100 compute-hrs/mes)

## Pendiente por definir
- [ ] Framework para la APK (Flutter? React Native? Kotlin?)
- [ ] Que datos exactos necesita ver el repartidor
- [ ] Diseñar la mini API (FastAPI + hosting gratuito)
- [ ] Modelo de datos para sincronizacion (campo updated_at, sync_status, etc.)
- [ ] Autenticacion del repartidor en la APK
- [ ] Tabla de repartidores (nombre, telefono, activo)
