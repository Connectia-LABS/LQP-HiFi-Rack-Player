# Architecture

## Overview

LQP HiFi Rack Player 4.0 is intentionally distributed as a single Python application file for simple Windows deployment. Internally, the source still separates responsibilities through classes and focused helper functions.

```text
User interface (Tkinter / TkinterDnD2)
        |
        +-- Playlist and metadata ---------------- Mutagen / pathlib
        |
        +-- Local file decode -------------------- FFmpeg -> float32 PCM
        |
        +-- Online radio ------------------------- Radio-Browser -> FFmpeg stream
        |
        +-- Audio engine ------------------------- SoundDevice callback
        |       |
        |       +-- 10-band biquad EQ ------------ SciPy signal filters
        |       +-- Preamp / volume
        |       +-- Power Stage DSP
        |       +-- Metering and monitor signal
        |
        +-- AI EQ -------------------------------- NVIDIA NIM API
        |
        +-- Persistence --------------------------- Atomic JSON + Windows DPAPI
        |
        +-- Visual components -------------------- Canvas cassette, spectrum, VU
```

## Audio pipeline

### Local files

1. The selected file is inspected with Mutagen.
2. FFmpeg decodes it to stereo `float32` PCM.
3. The audio engine provides blocks to the SoundDevice callback.
4. Each block passes through the ten peaking filters.
5. Preamp and main volume are applied.
6. Power Stage optionally adds gain, compression, limiting, and soft clipping.
7. The output is clipped to a safe digital range and sent to the selected device.
8. RMS, peak, and mono monitor data update the visual meters.

### Online radio

1. A station URL is selected from a preset, Radio-Browser result, imported list, or manual entry.
2. FFmpeg connects with reconnect options enabled.
3. Decoded PCM blocks enter a bounded queue.
4. The SoundDevice callback consumes queued blocks in order.
5. The same EQ, gain, Power Stage, and metering path is applied.

## Equalizer

The EQ uses ten peaking biquad filters centered at 31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, and 16000 Hz. Filter coefficients are recalculated only for changed bands. Existing filter state is preserved where possible to reduce audible clicks during live adjustment.

## AI EQ

AI EQ does not process or upload the audio waveform. It sends structured text containing available genre, artist, title, speaker, and signal-chain information. The NVIDIA model returns a JSON object with ten gains, a short name, and an explanation. Returned gains are validated, quantized to 0.5 dB, and clamped to the supported range before application.

## Concurrency model

Potentially blocking work runs outside Tkinter's main thread:

- File decoding
- Radio discovery
- Stream tests and repair
- Station artwork download
- NVIDIA API calls

Worker results are placed into a thread-safe queue. The main UI loop consumes the queue and performs all widget updates. Audio output uses SoundDevice's callback thread with locks around shared DSP and playback state.

## Persistence

Configuration is written to the current user's local application data directory. The write path uses a temporary file and atomic replacement to reduce the chance of a truncated configuration after an unexpected shutdown.

On Windows, a saved NVIDIA API key is protected with DPAPI for the current user. The key is never embedded in the source code.

## Radio resilience

Radio streams are volatile. The application combines:

- Curated presets
- Radio-Browser discovery
- `hidebroken` filtering
- FFmpeg stream testing
- Name-similarity matching for repair
- Persistence of replacement URLs

No application can guarantee that third-party stations remain online.

## Current trade-offs

- Local files are decoded fully into memory before playback.
- The source is monolithic to keep distribution simple.
- The UI is optimized for desktop Windows rather than responsive or cross-platform layouts.
- AI EQ is metadata-based and is not acoustic room correction.

## Planned modularization

A future major version should split the project into:

```text
lqp_player/
  audio/
    engine.py
    equalizer.py
    power_stage.py
  ai/
    nvidia_provider.py
    track_detection.py
  radio/
    browser.py
    recorder.py
  ui/
    app.py
    widgets.py
  storage/
    config.py
    secrets.py
```

This would make unit testing, alternative providers, streaming decode, and packaging easier while preserving the existing interface.
