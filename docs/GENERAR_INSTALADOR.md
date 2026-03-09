# Generar instalador (.exe) - Tortilleria

## Requisitos previos
- Python con el venv activado
- PyInstaller instalado: `pip install pyinstaller`
- Inno Setup instalado: https://jrsoftware.org/isinfo.php

## Paso 0: Generar el .spec (solo la primera vez)

```bash
pyinstaller --onedir --windowed --name "Tortilleria Tierra del campo" --icon=icono.ico --add-data "app/data/default;app/data/default" --add-data "tortilleria_logo.png;." --add-data "icono.ico;." main.py
```

Esto genera `Tortilleria Tierra del campo.spec`. Editarlo si necesitas agregar mas archivos en `datas=[]`.

## Paso 1: Generar el .exe con PyInstaller

```bash
pyinstaller "Tortilleria Tierra del campo.spec"
```

El resultado queda en: `dist/Tortilleria Tierra del campo/`

## Paso 2: Verificar que funcione

1. Ir a `dist/Tortilleria Tierra del campo/`
2. Ejecutar `Tortilleria Tierra del campo.exe`
3. Verificar que:
   - Se crea `tortilleria.db` junto al .exe
   - Se cargan los productos por defecto
   - La app abre sin errores

## Paso 3: Generar instalador con Inno Setup

1. Abrir Inno Setup
2. File > New > "Create a new script using the Script Wizard"
3. Configurar:
   - **Application name**: Tortilleria Tierra del Campo
   - **Application version**: 1.0
   - **Application publisher**: (tu nombre)
   - **Application destination folder**: `{autopf}\Tortilleria Tierra del Campo`
4. Application files:
   - **Main exe**: `dist\Tortilleria Tierra del campo\Tortilleria Tierra del campo.exe`
   - **Add folder**: toda la carpeta `dist\Tortilleria Tierra del campo\`
   - Marcar "Include subfolders"
5. Application icons:
   - Marcar "Create a desktop shortcut"
6. Compilar > genera `TortilleriaSetup.exe`

## Estructura del .exe generado

```
Tortilleria Tierra del campo/
  Tortilleria Tierra del campo.exe    <- ejecutable principal
  tortilleria.db                      <- se crea en primer inicio
  _internal/
    app/data/default/                 <- CSVs de productos
    tortilleria_logo.png              <- logo
    icono.ico                         <- icono
    (dependencias de Python...)
```

## Notas

- La DB (`tortilleria.db`) se crea automaticamente en el primer inicio gracias a `bootstrap.py`
- Los archivos de datos (CSVs, logo) se empaquetan dentro de `_internal/` via el `.spec`
- Si agregas nuevos archivos de datos, actualiza el `.spec` en la seccion `datas=[]`
- Para regenerar despues de cambios en el codigo: repetir Paso 1 y 3
