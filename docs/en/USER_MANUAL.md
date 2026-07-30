# User manual

## LQP HiFi Rack Player 4.0 — World Edition

This manual covers installation, local playback, manual equalization, NVIDIA-assisted equalization, EQ memories, Argentine and international radio, recording, spectrum analysis, and audio output configuration.

> The interface is inspired by late-1980s and early-1990s Hi-Fi racks, while the actual audio processing is digital and runs in real time.

![Full LQP HiFi Rack Player interface](../../screenshots/full-application.png)

## 1. Requirements

### Recommended system

- 64-bit Windows 10 or Windows 11.
- Python 3.11 or newer installed from Python.org.
- Tcl/Tk included with Python.
- A Windows-compatible audio output device.
- Internet access for online radio, station search, initial FFmpeg download, and AI EQ.

### Main dependencies

The application uses NumPy, SciPy, SoundDevice, Requests, Pillow, Mutagen, and TkinterDnD2. FFmpeg handles audio decoding, online radio streams, and radio recording.

## 2. Installation

### Recommended method

1. Download or clone the repository.
2. Open PowerShell in the repository folder.
3. Install dependencies:

```powershell
py -3 -m pip install -r requirements.txt
```

4. Run:

```powershell
py -3 src\lqp_hifi_rack_player.py
```

You can also double-click `run_windows.bat`.

### First launch

The application attempts to install missing Python packages. When FFmpeg is not available on the system, it attempts to download a portable Windows build into the current user's local application data folder. The first launch may take longer than later launches.

## 3. Interface overview

The window is divided into three main areas:

- **SOURCE BAY** on the left: playlist, Argentine radio, and international radio.
- **Deck and processing** in the center: cassette, display, transport, volume, preamp, Power Stage DSP, spectrum, and VU meters.
- **Graphic Equalizer** on the right: manual EQ, presets, memories, AI EQ, and sleep timer.

![Player header](../../screenshots/header-panel.png)

The top panel identifies the product edition and shows the main system capabilities.

## 4. Playlist and local files

![Playlist panel](../../screenshots/playlist-panel.png)

### Adding music

There are three ways to add content:

1. **+ Files** selects one or more audio files.
2. **+ Folder** scans a folder and its subfolders for supported audio.
3. **Drag and drop** accepts files or folders from Windows File Explorer.

The player prevents duplicate paths. Supported formats include FLAC, MP3, WAV, OGG, M4A, AAC, AIFF, WMA, OPUS, APE, and other formats that FFmpeg can decode.

### Playing a track

- Double-click a track.
- Select a track and press Play.
- The `▶` marker identifies the active track.

### Reordering

- Drag a track inside the list and drop it at the desired position.
- Use **Up** and **Down** for precise movement.
- The new order is saved between sessions.

### Removing content

Select one or multiple tracks and press **Remove**. **Clear** empties the playlist after confirmation.

### Import and export

Playlists can be imported or exported as M3U, M3U8, or JSON.

### Shuffle and Repeat

- **Shuffle** chooses a different random track when possible.
- **Repeat** returns to the beginning after the last track.

## 5. Deck, transport, and timeline

![Cassette deck and display](../../screenshots/cassette-deck.png)

The cassette reels animate during playback. For local files, the reel balance represents approximate track progress.

### Controls

- `⏮`: previous track or station.
- `▶`: play or resume.
- `⏸`: pause.
- `■`: stop.
- `⏭`: next track or station.
- `● REC`: start or stop radio recording.

### Timeline

For local files, use the timeline to seek within the current track. Online radio is live and does not support backward seeking.

### Volume and preamp

- **MAIN VOLUME** controls the final listening level.
- **PREAMP dB** raises or lowers the signal before the final processing stages.

When the clipping indicator lights up, reduce the preamp, Power Stage, or heavily boosted EQ bands.

## 6. Audio output selection

![Audio output selector](../../screenshots/audio-output-selector.png)

The **AUDIO OUT** menu lists output devices reported by SoundDevice and the Windows audio host APIs.

**Default output** follows the Windows default device. Select a specific headphone output, USB interface, HDMI device, or speaker output when needed.

Changing the output device during playback reopens the audio stream and may cause a brief interruption.

## 7. Manual 10-band equalizer

![Manual equalizer](../../screenshots/manual-equalizer.png)

The equalizer uses ten center frequencies:

| Band | Approximate range | Common effect |
|---|---|---|
| 31 Hz | Sub-bass | Deep vibration; small speakers may reproduce very little |
| 62 Hz | Low bass | Kick impact and bass weight |
| 125 Hz | Bass | Body and warmth |
| 250 Hz | Low mids | Fullness; too much can sound muddy |
| 500 Hz | Lower mids | Density and box character |
| 1 kHz | Midrange | General vocal and instrument presence |
| 2 kHz | Upper mids | Definition, attack, and intelligibility |
| 4 kHz | Presence | Clarity and detail; excess can be fatiguing |
| 8 kHz | Treble | Brightness, cymbals, and near-air detail |
| 16 kHz | Air | Openness, depending on the recording and hardware |

### Per-band controls

- Drag a slider to change gain.
- Use the mouse wheel for 0.5 dB steps.
- Double-click a slider to reset only that band to 0 dB.

Changes are processed in real time. Sliders remain editable after applying a factory preset, a saved memory, or an AI-generated curve.

### Practical guidelines

- Start with adjustments between 0.5 and 2 dB.
- Try cutting unwanted frequencies before boosting several others.
- Lower the preamp when boosting multiple bands to preserve headroom.
- On small monitors, extreme 31 Hz boosts usually consume headroom without producing true sub-bass.

## 8. Presets and MEMORY EQ

![Equalizer presets](../../screenshots/equalizer-presets.png)

The preset menu contains factory curves and user-created memories.

### Apply a preset

1. Select the preset name.
2. Press **Apply**.
3. Fine-tune any band manually.

### Save a memory

1. Build a curve manually or with AI EQ.
2. Press **Save**.
3. Enter a descriptive name.
4. The memory appears with a star marker.

### Delete, import, and export

- **Delete** removes a user memory; factory presets remain protected.
- **Import** loads curves from JSON.
- **Export** saves user memories to JSON for backup or transfer.

## 9. AI EQ with NVIDIA

![Automatic AI EQ panel](../../screenshots/ai-eq-auto.png)

AI EQ asks an NVIDIA NIM model to propose ten EQ gains based on the track information and the user's audio equipment. The result is a starting point and always remains manually editable.

### 9.1 Getting an API key

1. Open the NVIDIA model catalog at `https://build.nvidia.com/`.
2. Sign in or create an NVIDIA account.
3. Open a model page that provides a hosted API endpoint. The application uses the model configured in its source code, which may change in later releases.
4. Click **Generate API Key** or **Get API Key**.
5. Copy the key and store it securely.
6. Paste it into **YOUR NVIDIA API KEY** in the LQP AI EQ panel.

Do not post the key in GitHub, screenshots, chat messages, or shared files. NVIDIA describes the key as account-specific and recommends keeping it secret.

### 9.2 Secure storage

- **Session only** keeps the key in memory until the application closes.
- **Remember encrypted for this user** protects it with Windows DPAPI and ties it to the current Windows account.
- **Delete key** removes the application-stored value.

The `NVIDIA_API_KEY` environment variable is also supported. Never commit a real key to the repository.

### 9.3 Form fields

- **Music genre**: rock, jazz, electronic, tango, pop, and so on.
- **Band / artist**: primary performer.
- **Specific track**: song title.
- **Speakers**: speaker model or description.
- **Equipment chain**: DAC, amplifier, mixer, Bluetooth path, or other relevant hardware.

### 9.4 Detect current track

Detection fills the form without calling NVIDIA yet.

The application looks for data in this order:

1. Embedded audio metadata.
2. Artist and title already loaded in the audio engine.
3. Filename parsing, such as `Artist - Track.mp3`.
4. The selected playlist track, even when it is not currently playing.

Review and correct the fields before requesting the curve.

### 9.5 Detect + Equalize

This mode detects available metadata, sends the request to NVIDIA in a background thread, and applies all ten returned gains.

Response time depends on the endpoint and network availability. The interface remains usable while the request is running.

### 9.6 AUTO on track change

When enabled, each new local track triggers detection and a fresh AI EQ request.

- It is not automatically applied to radio because many stations do not expose the actual song title.
- It requires a valid API key.
- It may consume service quota or credits.
- All sliders remain manually editable afterward.

### 9.7 Understanding the result

The **WHY THIS CURVE** area summarizes the model's reasoning. Treat it as a recommendation, not a room measurement. The API does not listen to the audio or measure the speakers; it works from metadata and the equipment description.

Accurate acoustic correction requires a measurement microphone and dedicated calibration software.

## 10. Power Stage DSP

![Power Stage DSP](../../screenshots/power-stage-dsp.png)

Power Stage adds perceived loudness and controls peaks with compression, limiting, and soft clipping.

- Enable **controlled amplification**.
- Increase the percentage gradually.
- Moderate values can add presence without crushing dynamics.
- Reduce Power, Preamp, or Volume if clipping or listening fatigue appears.

This control does not increase the physical power of an amplifier or speaker. It only processes the digital signal.

## 11. Spectrum Analyzer and VU Meter

![Spectrum analyzer and VU meter](../../screenshots/spectrum-vu-meter.png)

### Spectrum Analyzer

The analyzer divides the signal into twenty display bands and shows approximate energy in real time. Peak markers fall more slowly than the main bars.

### VU Meter

The L and R bars represent the left and right channels. The clip indicator activates when the signal approaches the digital ceiling.

- Green: normal range.
- Amber: high level.
- Red: limiting or clipping risk.

## 12. Argentine radio

![Argentine radio panel](../../screenshots/radio-argentina.png)

The **RADIO FM** tab includes Argentine presets and Radio-Browser results.

### Controls

- **Play Radio** opens the selected station.
- **Test stream** asks FFmpeg to verify that the URL provides audio.
- **Repair** searches for a replacement URL when a stream stops working.
- **Top AR** loads popular Argentine stations from Radio-Browser.
- **Search** finds stations by name.
- **+ Manual** adds a station with a name, genre, and stream URL.
- **Import / Export** works with JSON and M3U lists.
- **Logos** refreshes station artwork.

Radio streams belong to third parties and may change, become region-restricted, or go offline without notice.

## 13. Radio World

![International radio panel](../../screenshots/radio-world.png)

Radio World organizes discovery around major cities:

- Miami
- New York
- Ibiza
- Madrid
- London
- Paris
- Berlin
- Tokyo
- Rio de Janeiro
- Mexico City

Select a city and press **Load city**. The application queries Radio-Browser, prioritizes featured stations, and fills the list with regional results.

You can also search by station name, genre, or keyword. International streams support the same test, repair, import, and export controls as Argentine radio.

## 14. Radio recording

While a station is playing, press `● REC` to start recording. FFmpeg performs the recording in a separate process.

Recordings are stored by default in:

```text
%USERPROFILE%\Music\LQP Grabaciones
```

Press the button again to stop and finalize the MP3 file.

Check local law and the station's terms before recording or redistributing a broadcast. The feature is intended for permitted personal use.

## 15. Sleep timer

The sleep timer pauses playback after the selected duration. During the final seconds, it gradually lowers the volume for a fade-out.

Typical options include 15, 30, 45, 60, and 90 minutes.

## 16. Keyboard shortcuts

| Shortcut | Action |
|---|---|
| Space | Play / Pause |
| Right arrow | Seek forward 10 seconds in a local file |
| Left arrow | Seek backward 10 seconds in a local file |
| Up arrow | Increase volume |
| Down arrow | Decrease volume |
| Ctrl + O | Add files |
| Double-click | Play the selected track or station |

## 17. Local configuration and data

Configuration is stored in the current user's profile, normally under:

```text
%LOCALAPPDATA%\LQP_HiFi_Rack_Player
```

It may contain:

- Playlist and ordering.
- Volume, preamp, and Power Stage values.
- EQ gains and user memories.
- Added or repaired radio stations.
- Selected Radio World city.
- Audio output device.
- Window size and position.
- The DPAPI-protected NVIDIA key blob when the user chooses to remember it.

Configuration and recordings are intentionally excluded from Git.

## 18. Safe listening practices

- Start at a low volume before enabling Power Stage or applying a new curve.
- Avoid large boosts in EQ, preamp, and Power at the same time.
- Watch the VU and clipping indicators.
- Avoid prolonged high-volume headphone listening.
- A useful EQ curve depends on the recording, speakers, room, and personal preference.

## 19. Help

See [Troubleshooting](TROUBLESHOOTING.md) for audio, dependency, FFmpeg, radio, or API key issues.
