# Changelog

All notable project changes are documented here.

## [4.0.0] — 2026-07-29

### Added

- Manual 10-band EQ with 0.5 dB adjustment and per-band reset.
- NVIDIA AI EQ with user-provided API key.
- Windows DPAPI protection for saved API keys.
- Automatic track detection from metadata and filenames.
- Detect-only, detect-and-equalize, and automatic track-change modes.
- Native file and folder drag and drop.
- Playlist drag reordering, Up/Down controls, multi-selection, and persistence.
- Radio World for Miami, New York, Ibiza, Madrid, London, Paris, Berlin, Tokyo, Rio de Janeiro, and Mexico City.
- Stream testing and automated station URL repair.
- Separate Argentine and international radio state.
- Atomic configuration writes.
- Thread-safe UI result queue for network and background operations.

### Security

- Removed the API key that existed in the earlier source.
- Added BYOK behavior and secret deletion controls.

### Fixed

- Repaired station URLs now persist over same-name presets.
- Current playlist index survives reordering and multi-item removal correctly.
- Radio next/previous controls respect the active radio scope.
- Background workers no longer update Tkinter widgets directly.

## [3.2.0]

- Initial NVIDIA-assisted EQ form.
- User EQ memories.
- JBL-oriented factory presets.

## [3.0.0]

- 20-band spectrum analyzer.
- Animated cassette deck.
- Stereo VU meter and clipping indicator.
- Radio recording and sleep timer.
