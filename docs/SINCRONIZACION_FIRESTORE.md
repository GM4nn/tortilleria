# Sincronizacion Firestore (Desktop <-> Mobile)

## Flujo General

```
Python/Tkinter (Desktop)  ←→  Firebase Firestore  ←→  Flutter (Mobile)
```

- Desktop crea ordenes en SQLite y las sincroniza a Firestore
- Mobile consulta ordenes en tiempo real desde Firestore
- Mobile puede marcar ordenes como completadas
- Desktop detecta el cambio en tiempo real y actualiza SQLite + UI


## Arquitectura

```
DESKTOP/
├── app/services/
│   ├── firestore_service.py      → Conexion y escritura a Firestore
│   └── firestore_listener.py     → Escucha cambios en tiempo real
├── app/data/providers/
│   └── orders.py                 → Sync automatico al crear/actualizar ordenes
├── main.py                       → Inicia el listener al arrancar
└── serviceAccount.json           → Credenciales de servidor (NO subir a git)

MOBILE/tortilleria/
├── lib/core/
│   ├── constants/
│   │   └── firestore_collections.dart
│   └── theme/
│       └── app_theme.dart
└── lib/features/orders/
    ├── models/
    │   ├── order_model.dart
    │   └── order_item_model.dart
    ├── services/
    │   └── order_service.dart    → Lectura en tiempo real + update status
    ├── screens/
    │   └── orders_screen.dart
    └── widgets/
        ├── order_card.dart
        ├── order_filter_chips.dart
        └── order_status_badge.dart
```


## Estructura del documento en Firestore

Coleccion: `orders`

```
orders/{order_id}
├── order_id: int
├── customer_name: string
├── items: array
│   └── { product_id, name, price, quantity, subtotal }
├── total: float
├── amount_paid: float
├── status: string ("pendiente" | "completado" | "cancelado")
└── created_at: string (ISO 8601)
```


## Flujo: Crear orden (Desktop → Firestore)

1. `order_tab.py` llama a `order_provider.save()`
2. Se guarda en SQLite
3. `firestore_service.add_order()` sube el documento a Firestore
4. Flutter detecta el nuevo documento automaticamente via `snapshots()`


## Flujo: Completar orden (Mobile → Desktop)

1. Flutter llama a `order_service.completeOrder()` → actualiza `status` en Firestore
2. `firestore_listener.py` detecta el cambio via `on_snapshot`
3. Filtra solo documentos MODIFIED cuyo status cambio a `completado`
4. Ejecuta callback en el hilo principal de Tkinter via `root.after()`
5. `order_provider.update_status()` actualiza SQLite
6. Se notifica a `OrderContent` para refrescar la lista


## Listener: Como funciona on_snapshot

El listener de Firestore mantiene un cache de statuses conocidos:

```python
_known_statuses = {}  # doc_id -> status
```

En cada snapshot:
- Primer snapshot: solo llena el cache (no dispara callbacks)
- Snapshots siguientes: compara el status anterior vs nuevo
- Solo reacciona cuando `old_status != completado` y `new_status == completado`

Esto evita falsos positivos al iniciar la app.


## Seguridad: Diferencia de credenciales

| Lado | Archivo | Tipo | Acceso |
|------|---------|------|--------|
| Desktop (Python) | `serviceAccount.json` | Clave privada servidor | Total, sin restricciones |
| Mobile (Flutter) | `firebase_options.dart` | Credenciales publicas | Limitado por Firestore Rules |

**Importante:** `serviceAccount.json` nunca debe subirse a git ni incluirse en la APK.


## Dependencias

**Python (Desktop):**
```
pip install firebase-admin
```

**Flutter (Mobile):**
```yaml
firebase_core: ^3.12.1
cloud_firestore: ^5.6.9
intl: ^0.20.2
```


## Configuracion inicial

1. Crear proyecto en Firebase Console
2. Crear base de datos Firestore
3. Descargar `serviceAccount.json` → colocar en `DESKTOP/`
4. En Flutter: `flutterfire configure` → genera `firebase_options.dart`
5. `flutter pub get`
