# Inicio rápido

## 1. Preparar Windows

Instalá Python de 64 bits desde Python.org. Durante la instalación, marcá **Add Python to PATH** y asegurate de incluir **Tcl/Tk and IDLE**.

## 2. Instalar dependencias

Abrí PowerShell en la carpeta del proyecto y ejecutá:

```powershell
py -3 -m pip install -r requirements.txt
```

## 3. Iniciar el reproductor

Usá una de estas opciones:

```powershell
py -3 src\lqp_hifi_rack_player.py
```

O hacé doble clic en `run_windows.bat`.

## 4. Cargar música

Entrá en **PLAYLIST** y usá **+ Archivos**, **+ Carpeta**, o arrastrá archivos y carpetas desde el Explorador de Windows. Hacé doble clic sobre una pista para reproducirla.

## 5. Ecualizar

Mové cualquiera de las diez palancas para ajustar manualmente. También podés elegir un preset, guardar una memoria propia o abrir **AI EQ · AUTO / NVIDIA**.

## 6. Configurar AI EQ

En el panel AI EQ pegá tu clave personal de NVIDIA. Podés usar **Detectar tema actual** para revisar artista, título y género, o **Detectar + Ecualizar** para aplicar una curva automáticamente.

## 7. Escuchar radio

Usá **RADIO FM** para emisoras argentinas o **RADIO WORLD** para radios internacionales. Seleccioná una estación y presioná **Play Radio**. Si falla, probá **Probar stream** y luego **Reparar**.

Para una explicación completa, consultá el [Manual de usuario](MANUAL_USUARIO.md).
