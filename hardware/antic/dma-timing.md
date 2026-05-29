# Dma Timing

## 3.1  ANTIC Architecture, DMA & Timing

### Clock tree

| item | NTSC | PAL |
|---|---|---|
| Master crystal | 14.318 18 MHz | 14.187 57 MHz |
| Machine clock (CPU) | 14.318 18 ÷ 8 = **1.789 773 MHz** | 14.187 57 ÷ 8 = **1.773 447 MHz** |
| Color clock | 3.579 545 MHz (NTSC subcarrier) | 4.433 618 MHz ÷ 2 |
| Cycles / scan line | **114** | **114** |
| Scan lines / frame | 262 (NTSC) | 312 (PAL) |
| Frame rate | 59.922 71 Hz | 49.860 74 Hz |

### Playfield widths (DMACTL bits 0–1)

| Width | Color clocks | Bytes/line (normal) | Use |
|---|---|---|---|
| Narrow | 128 ($40–$7F) | 32 | Saves DMA, more CPU cycles |
| Normal | 160 ($30–$CF) | 40 | Default GR.0 width |
| Wide | 192 ($20–$DF) | 48 | Covers overscan |

Wide playfield left-clipped to 178 actual visible (ANTIC cuts 12 color clocks; right 2 cut by HBLANK).

### Cycle-stealing budget

ANTIC DMA steals CPU cycles per scan line. **These are hard limits for DLI code.**

| Scenario | Available 6502 cycles / line |
|---|---|
| Baseline (playfield DMA + refresh) | ~97 |
| Mode E bitmap (160×192 4-color) | ~57 |
| Mode 2 first scan line | ~30 (font fetch dominates) |
| Mode 2 subsequent | ~60 |
| Mode 4 + scroll + PMG | <10 first line, ~50 subsequent |

Wide playfield (+16 bytes/line) + horizontal scroll (+8 bytes/line) = **more DMA steal → fewer DLI cycles**.

### Memory refresh

ANTIC performs up to 9 refresh cycles per scan line (all 9 during VBLANK). Refresh rows are 128-entry (older ANTIC) or 256-entry (later). Any CPU or ANTIC non-refresh access to a DRAM row also refreshes that row — a DRAM access counts as a refresh in addition to doing useful work.

### Bus and video timing landmarks

For cycle-exact kernels, remember these stable hardware landmarks:

| Event | Position |
|---|---|
| Scan line length | 114 CPU cycles = 228 color clocks |
| Color clocks per CPU cycle | 2 |
| HBLANK end / wide playfield start | color clock 32 |
| Visible normal playfield start | color clock 48 |
| Narrow playfield starts | color clock 64 |
| Center of scan line | color clock 128 |
| Normal playfield end / `WSYNC` release | color clock 208 |
| HBLANK start / VCOUNT increment | color clock 222 |

Display-list bytes are fetched by ANTIC on the CPU bus; each byte costs one CPU cycle. A display-list instruction with LMS or JVB consumes the opcode plus two address bytes. Player DMA costs cycles every scan line when enabled; missile DMA is automatically enabled with player DMA.

---
