# Event Loop en Tkinter

## Que es

El event loop es un ciclo infinito que corre en el hilo principal de la aplicacion.
En Tkinter se inicia con `root.mainloop()`.

Su trabajo es escuchar y procesar eventos:
- Clicks del mouse
- Teclas presionadas
- Redibujar la interfaz
- Funciones programadas con `after()`

## Por que importa

Tkinter NO es thread-safe. Solo se puede modificar la UI desde el hilo principal (donde corre el event loop).

Si intentas modificar la UI desde otro hilo (ej: un callback de Firebase), Tkinter falla.

## Como ejecutar algo en el hilo principal desde otro hilo

```python
# Desde un hilo secundario (ej: callback de Firebase)
root.after(0, mi_funcion, argumento1, argumento2)
```

- `after(ms, func, *args)` programa `func` para ejecutarse en el event loop
- El `0` son milisegundos de espera (0 = lo antes posible)
- La funcion se ejecuta en el hilo principal porque el event loop corre ahi

## Ejemplo en el proyecto

```python
# firestore_listener.py
# _on_snapshot se ejecuta en hilo de Firebase
def _on_snapshot(self, _snapshot, changes, _read_time):
    ...
    # No podemos tocar la UI aqui (hilo de Firebase)
    # Programamos la funcion en el event loop de Tkinter
    self._app.root.after(0, self._handle_order_completed, order_id)

# _handle_order_completed se ejecuta en el hilo principal
def _handle_order_completed(self, order_id):
    # Aqui si podemos modificar la UI (toast, refrescar lista, etc)
    ...
```

## Para investigar

- "Tkinter event loop"
- "Tkinter mainloop explained"
- "Tkinter threading after method"
- "GUI event loop pattern"
