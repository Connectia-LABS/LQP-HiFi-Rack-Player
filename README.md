# LQP HiFi Rack Player

A vintage-inspired Hi-Fi music player for Windows, built with Python. It combines local audio playback, a real-time 10-band equalizer, NVIDIA-assisted tuning, international radio streaming, playlist management, recording, spectrum analysis, VU metering, and DSP controls in a single rack-style interface.

![LQP HiFi Rack Player](screenshots/full-application.png)

## Documentation

- [Manual de usuario — Español rioplatense](docs/es/MANUAL_USUARIO.md)
- [User manual — US English](docs/en/USER_MANUAL.md)
- [Inicio rápido en español](docs/es/INICIO_RAPIDO.md)
- [Quick start in English](docs/en/QUICK_START.md)
- [Architecture and technical design](docs/ARCHITECTURE.md)
- [Security and API key handling](SECURITY.md)
- [License guide](docs/LICENSE_GUIDE.md)
- [Troubleshooting — Español](docs/es/SOLUCION_DE_PROBLEMAS.md)
- [Troubleshooting — English](docs/en/TROUBLESHOOTING.md)

## Main features

- Local playback for FLAC, MP3, WAV, OGG, M4A, AAC, AIFF, WMA, OPUS, APE, WV, and other FFmpeg-supported formats.
- Real-time 10-band graphic equalizer with manual control, factory presets, user memories, and fine 0.5 dB adjustment.
- AI EQ through NVIDIA NIM with user-provided API keys.
- Automatic track detection using embedded metadata and filename fallback.
- Drag-and-drop playlist loading, folder scanning, duplicate prevention, reordering, and M3U/M3U8/JSON import/export.
- Argentine and international online radio with search, stream testing, URL repair, and recording to MP3.
- International presets for Miami, New York, Ibiza, Madrid, London, Paris, Berlin, Tokyo, Rio de Janeiro, and Mexico City.
- Animated cassette deck, 20-band spectrum analyzer, stereo VU meter, clipping indicator, sleep timer, and configurable audio output.
- Windows DPAPI protection for a saved NVIDIA API key.

## Technology

- Python and Tkinter
- NumPy and SciPy for DSP
- SoundDevice for audio output
- FFmpeg for decoding, radio streaming, and recording
- Mutagen for music metadata
- Pillow for station artwork
- TkinterDnD2 for native drag and drop
- NVIDIA NIM API for AI-assisted equalization
- Radio-Browser for station discovery and stream recovery

## Quick start

### Requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.11 or newer from Python.org with Tcl/Tk enabled
- Internet access for online radio, dependency setup, FFmpeg download, and AI EQ

### Run

Double-click:

```text
run_windows.bat
```

Or use PowerShell from the repository root:

```powershell
py -3 -m pip install -r requirements.txt
py -3 src\lqp_hifi_rack_player.py
```

On first launch, the application can install missing Python dependencies and download a portable FFmpeg build when needed.

## AI EQ and privacy

AI EQ is optional. The application does not ship with a shared NVIDIA credential. Each user supplies their own API key through the AI EQ panel or the `NVIDIA_API_KEY` environment variable.

When the user chooses to remember the key on Windows, the application protects it with Windows DPAPI for the current Windows account. The repository contains no production API key. Never commit personal credentials, configuration files, or exported secrets.

See [Security](SECURITY.md) and the manual for complete setup instructions.

## Project status

Version **4.0 World Edition** is a portfolio-ready desktop release. The application remains intentionally distributed as a single executable Python source file to simplify use on Windows. The roadmap includes modularizing the audio engine, UI, persistence, radio, and AI provider layers.

## License

This project is **source-available for noncommercial use** under the [PolyForm Noncommercial License 1.0.0](LICENSE).

Personal study, experimentation, education, research, hobby projects, and other permitted noncommercial uses are allowed under the license. Commercial use, paid redistribution, sale, inclusion in a commercial product, or use intended for commercial advantage requires separate written permission from Connectia-LABS.

This is not an OSI-approved open-source license. See [License guide](docs/LICENSE_GUIDE.md) for a practical summary. The full `LICENSE` file controls in case of any difference.

## Trademarks and external services

NVIDIA, FFmpeg, Radio-Browser, JBL, station names, and other product names belong to their respective owners. This project is independent and is not endorsed by those organizations.
