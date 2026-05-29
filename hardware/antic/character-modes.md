# Character Modes

## 3.4  Character Modes (ANTIC 2–7)

| Mode | Scan lines | Characters/line | Character memory | Colors |
|---|---|---|---|---|
| 2 | 8 | 40 | 1 KB @ 1K boundary | 2 |
| 3 | 10 | 40 | 1 KB | 2 (descenders) |
| 4 | 8 | 40 | 1 KB | 4+1 |
| 5 | 16 | 40 | 1 KB | 4+1 |
| 6 | 8 | 20 | 512 B @ 512B boundary | 5 |
| 7 | 16 | 20 | 512 B | 5 |
### 3.2.1  Complete ANTIC Mode Table (Modes 2–F)

| Mode | Lines/cell | Chars/line | Memory | Align | Colors | Pixel size |
|---|---|---|---|---|---|---|
| 2 | 8 | 40 | 1 KB | 1 KB | 2 | 8×8 bit |
| 3 | 10 | 40 | 1 KB | 1 KB | 2 | 8×8 (descenders) |
| 4 | 8 | 40 | 1 KB | 1 KB | 4+1 | 4×8 |
| 5 | 16 | 40 | 1 KB | 1 KB | 4+1 | 4×8 (double height) |
| 6 | 8 | 20 | 512 B | 512 B | 5 | 8×8 (1-color-clock) |
| 7 | 16 | 20 | 512 B | 512 B | 5 | 8×8 (double height) |
| 8 | 4 | 40 | 2 KB | 2 KB | 4 | 4×4 |
| 9 | 4 | 80 | 2 KB | 2 KB | 2 | 2×4 |
| A | 4 | 80 | 2 KB | 2 KB | 4 | 2×4 |
| B | 2 | 160 | 4 KB | 4 KB | 2 | 1×2 |
| C | 1 | 160 | 4 KB | 4 KB | 2 | 1×1 |
| D | 2 | 160 | 4 KB | 4 KB | 4 | 1×2 |
| E | 1 | 160 | 4 KB | 4 KB | 4 | 1×1 |
| F | 1 | 320 | 8 KB | — | 2 hires | 1×1 (PF2 luminance) |

Key: **Lines/cell** = scan lines per character row. **Aligned** = address must be 512B/1K-aligned for char modes; bitmap modes require every-row LMS (`$40`+LMS on every scan-line instruction) for playfield widths >4K. `+1` color in modes 4/5 = background color. Mode F background = PF2 colour. Hardware P/M graphics are available over standard playfield modes when `DMACTL` missile/player DMA and `GRACTL` display bits are enabled; PMG DMA steals cycles but does not change the playfield mode.

**Dynamic CHBASE switching:** write to `CHBASE = $D409`; takes effect two cycles after write. For Mode 6/7, use CHBASE bits 0 used as mode-selection: CHBASE bit 1 must match the mode's alignment boundary for correct color-clock pipeline.

**Blink/inversion:** CHACTL bits 0–1. Bit 1 = invert cells where char-name bit 7=1; bit 0 = blank cells where char-name bit 7=1; both = inverted space.

```asm
        lda #$00            ; no blink, no invert
        sta CHACTL
        lda #$02            ; invert bit 7 characters
        sta CHACTL
```

**Vertical reflection:** CHACTL bit 2 = flip character upside-down (row 7 displayed first). Affects all modes.

---
