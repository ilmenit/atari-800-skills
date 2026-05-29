# Pcm Pdm

## AUDC Forced-DC Output — PCM Entry Point

When AUDC bit 4 = 1:

- The polynomial counter output is disconnected.
- AUDF is ignored.
- The 4-bit volume value from bits 0–3 drives the DAC directly.
- No waveform period — the output is a static level, held until the next AUDC write.

This readwrite path is how 4-bit PCM samples stream continuously on POKEY: `ORA #$10; STA AUDC1` fires a new sample value every instruction pair, at rates up to 15 kHz on NTSC systems with ANTIC DMA disabled.

Refer to `digital-audio.md` for full PCM timing methods and sample rate calculations.

---
