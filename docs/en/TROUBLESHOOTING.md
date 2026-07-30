# Troubleshooting

## The application does not start

1. Verify that Python is 64-bit:

```powershell
py -3 --version
py -3 -c "import struct; print(struct.calcsize('P') * 8)"
```

2. Reinstall dependencies:

```powershell
py -3 -m pip install --upgrade -r requirements.txt
```

3. Run from PowerShell to see the complete error:

```powershell
py -3 src\lqp_hifi_rack_player.py
```

## Tkinter error

Install Python from Python.org and include Tcl/Tk. Some minimal Python distributions do not include the desktop GUI toolkit.

## Drag and drop does not work

Reinstall TkinterDnD2:

```powershell
py -3 -m pip install --upgrade tkinterdnd2
```

Restart the player afterward.

## No audio output

- Check **AUDIO OUT** and select the correct device.
- Confirm that the device is not muted in Windows.
- Try **Default output**.
- Close applications that may be using the device in exclusive mode.
- Move the in-app volume control down and back up.

List devices from Python with:

```powershell
py -3 -c "import sounddevice as sd; print(sd.query_devices())"
```

## FFmpeg is unavailable

Install FFmpeg manually and add it to `PATH`, or remove an incomplete local FFmpeg folder so the application can retry its portable download.

Check with:

```powershell
ffmpeg -version
```

## A local file will not play

- Test it directly with FFmpeg.
- Check whether the file is damaged.
- Move it to a shorter path with simple characters.
- Confirm that it is not DRM-protected.

## A radio station will not connect

1. Press **Test stream**.
2. Use **Repair** to search for a current URL.
3. Reload the city or search for the station by name.
4. Try a different station to rule out a general network problem.

Some stations restrict regions or change stream addresses without notice.

## AI EQ returns 401

The API key was rejected. Generate a new key through NVIDIA, copy it completely, and paste it without extra spaces. Revoke any key that has been publicly exposed.

## AI EQ returns 429

The endpoint is rate-limited or busy. Wait and try again. Automatic mode can generate several requests when tracks are changed rapidly.

## The NVIDIA model does not respond

Model availability can change. Check NVIDIA Build and confirm that the model configured in `NVIDIA_MODEL` still provides a hosted API endpoint.

## The key is not remembered

Encrypted storage is intended for Windows and uses DPAPI. Run the application under the same Windows account that saved the key. A protected blob copied to another account or computer cannot normally be decrypted.

## Clipping or distortion

- Lower PREAMP.
- Reduce Power Stage.
- Reduce heavily boosted EQ bands.
- Watch the red clipping indicator.
- Apply Flat to isolate the source of the problem.

## High memory usage

Local files are fully decoded before playback. Very long or high-resolution files can use substantial RAM. Split the file or convert a copy to a lighter format.

## A playlist entry disappears

At startup, the player removes paths that no longer exist. Check whether the file was moved, renamed, or stored on a disconnected drive.

## Reset configuration

Close the application and rename:

```text
%LOCALAPPDATA%\LQP_HiFi_Rack_Player
```

The next launch creates a clean configuration. Make a backup first if you need saved EQ memories, stations, or playlist data.
