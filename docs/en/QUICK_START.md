# Quick start

## 1. Prepare Windows

Install 64-bit Python from Python.org. During setup, enable **Add Python to PATH** and make sure **Tcl/Tk and IDLE** are included.

## 2. Install dependencies

Open PowerShell in the project folder and run:

```powershell
py -3 -m pip install -r requirements.txt
```

## 3. Start the player

Use either option:

```powershell
py -3 src\lqp_hifi_rack_player.py
```

Or double-click `run_windows.bat`.

## 4. Load music

Open **PLAYLIST** and use **+ Files**, **+ Folder**, or drag files and folders from Windows File Explorer. Double-click a track to play it.

## 5. Equalize

Move any of the ten sliders for manual control. You can also select a factory preset, save a custom memory, or open **AI EQ · AUTO / NVIDIA**.

## 6. Configure AI EQ

Paste your personal NVIDIA API key into the AI EQ panel. Use **Detect current track** to review the detected metadata, or **Detect + Equalize** to apply a curve automatically.

## 7. Listen to radio

Use **RADIO FM** for Argentine stations or **RADIO WORLD** for international stations. Select a station and press **Play Radio**. When a stream fails, use **Test stream** and then **Repair**.

For full details, read the [User manual](USER_MANUAL.md).
