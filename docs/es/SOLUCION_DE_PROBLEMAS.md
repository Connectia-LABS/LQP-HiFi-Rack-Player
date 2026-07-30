# Solución de problemas

## La aplicación no abre

1. Verificá que Python sea de 64 bits:

```powershell
py -3 --version
py -3 -c "import struct; print(struct.calcsize('P') * 8)"
```

2. Reinstalá dependencias:

```powershell
py -3 -m pip install --upgrade -r requirements.txt
```

3. Ejecutá desde PowerShell para ver el error completo:

```powershell
py -3 src\lqp_hifi_rack_player.py
```

## Error relacionado con Tkinter

Instalá Python desde Python.org y asegurate de incluir Tcl/Tk. Algunas distribuciones mínimas de Python no traen la interfaz gráfica.

## No aparece el arrastre de archivos

Reinstalá TkinterDnD2:

```powershell
py -3 -m pip install --upgrade tkinterdnd2
```

Después cerrá y abrí el reproductor.

## No se escucha audio

- Revisá **AUDIO OUT** y elegí el dispositivo correcto.
- Confirmá que Windows no tenga el dispositivo silenciado.
- Probá **Salida predeterminada**.
- Cerrá otras aplicaciones que puedan estar usando una interfaz en modo exclusivo.
- Bajá y volvé a subir el volumen dentro de la aplicación.

Para listar dispositivos desde Python:

```powershell
py -3 -c "import sounddevice as sd; print(sd.query_devices())"
```

## FFmpeg no está disponible

Instalá FFmpeg manualmente y agregalo a `PATH`, o eliminá la carpeta local incompleta para que la aplicación vuelva a intentar la descarga.

Comprobación:

```powershell
ffmpeg -version
```

## Un archivo no reproduce

- Probá abrirlo directamente con FFmpeg.
- Verificá que no esté dañado.
- Movelo a una ruta más corta y sin caracteres extraños.
- Confirmá que no tenga protección DRM.

## La radio no conecta

1. Presioná **Probar stream**.
2. Usá **Reparar** para buscar una URL nueva.
3. Volvé a cargar la ciudad o buscá la emisora por nombre.
4. Probá otra estación para descartar un problema general de red.

Algunas radios bloquean determinadas regiones o cambian sus enlaces sin aviso.

## AI EQ devuelve 401

La clave fue rechazada. Generá una nueva en NVIDIA, copiala completa y pegala sin espacios adicionales. Si la clave estuvo publicada, revocala antes de crear otra.

## AI EQ devuelve 429

El endpoint está limitado o saturado. Esperá un momento y volvé a intentar. El modo automático puede generar varias consultas al cambiar rápidamente de pista.

## El modelo de NVIDIA no responde

El catálogo y los modelos disponibles pueden cambiar. Revisá la página de NVIDIA Build y confirmá que el modelo configurado en `NVIDIA_MODEL` siga ofreciendo endpoint.

## La clave no queda guardada

El guardado cifrado está diseñado para Windows y usa DPAPI. Ejecutá la aplicación con el mismo usuario de Windows que guardó la clave. Si movés el archivo de configuración a otra cuenta o PC, el blob no se podrá descifrar.

## Hay clipping o distorsión

- Bajá PREAMP.
- Reducí Power Stage.
- Bajá las bandas con aumentos grandes.
- Observá el indicador rojo de clip.
- Probá el preset Flat para aislar la causa.

## La aplicación consume mucha memoria

Los archivos locales se decodifican completos antes de reproducirse. Un archivo de varias horas o de alta resolución puede usar bastante RAM. Dividí el archivo o convertí una copia a un formato más liviano.

## La playlist no conserva un archivo

Al iniciar, la aplicación elimina de la lista las rutas que ya no existen. Confirmá que el archivo no haya sido movido, renombrado o desconectado en una unidad externa.

## Restablecer la configuración

Cerrá la aplicación y renombrá la carpeta:

```text
%LOCALAPPDATA%\LQP_HiFi_Rack_Player
```

Al volver a abrir, se crea una configuración nueva. Guardá una copia antes si necesitás conservar presets, radios o playlist.
