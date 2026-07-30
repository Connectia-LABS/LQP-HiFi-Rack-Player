# Roadmap

The roadmap describes direction, not guaranteed delivery dates.

## 4.x maintenance

- Expand automated validation on Windows.
- Improve station metadata display and ICY `StreamTitle` support.
- Add clearer offline and rate-limit states for AI EQ.
- Improve accessibility, focus order, and keyboard navigation.
- Add optional diagnostic export without secrets.

## 5.0 architecture

- Split the monolithic source into installable modules.
- Stream local decoding in blocks instead of loading complete files into RAM.
- Add unit tests for EQ coefficients, playlist mutations, persistence, track detection, and radio matching.
- Define provider interfaces for optional AI backends.
- Add structured logging and crash reports stored locally.
- Build a repeatable Windows executable and installer pipeline.

## Future research

- Read real ICY song metadata from online stations.
- Add replay-gain and loudness normalization options.
- Add measurement-based room correction import.
- Support gapless playback and crossfade.
- Add library indexing for large local collections.
