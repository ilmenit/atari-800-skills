---
name: atari8bit-gtia
description: >-
  Atari 8-bit GTIA graphics — register map, 9-bit palette, P/M graphics, collision, advanced modes (HIP/RIP/TIP/GTIA 9++/ORA overlap).
---

# 04 — GTIA — Graphics Chip

> **Key items:** COLPF0-3 $D016–$D019, PRIOR/GraColorPriority $D01B/$D01C, SIZEPn/SIZEM $D008/$D009, HPOSn $D000+
> **Scope:** GTIA ($D000–$D01F) register map, 9-bit palette, P/M graphics, collision, advanced modes HIP/RIP/TIP/GTIA 9++/ORA

---

## Quick-lookup

| Need | See § |
|---|---|
| Full register map $D000–$D01F (3 mirrored copies) | §4.1 |
| HPOSn/SIZEPn/SIZEM + priority/collision crosswalk | §4.1 |
| GRAFPn/GRAFM/PRIOR/GraColorPriority priority rules | §4.1 |
| 9-bit palette + NTSC artifact mixing | §4.2 |
| Multi-color / composite color mode | §4.3 |
| GRAPHICS 0 / 8 — Hires PF2 luminance | §4.4 |
| GTIA modes 9/10/11 | §4.5 |
| **HIP / RIP interlaced 30-shade** | §4.5.1 |
| **TIP (Taquart Interlace Picture)** | §4.5.2 |
| **GTIA 9++ DCTR-VSCROL kernel** | §4.5.3 |
| **ORA overlapping for multi-colour sprites** | §4.7 |
| P/M memory layout (double-width, double-bank) | §4.6 |
| GRACTL bits + 5th-player trick | §4.6 |
| Collision register table (PFP/MFP/CLPM) | §4.8 |

---

## §4.1  Register Map (3 mirrored copies $D000–$D00F / $D010–$D01F / $D080–$D08F)

| Adr | R (←) | W (→) | Reset | Notes |
|---|---|---|---|---|
| `$D000` | M0PF | HPOSP0 | $00 | Missile-0/Playfield collision flags; only W on HPOSP0 |
| `$D001` | M1PF | HPOSP1 | $00 | |
| `$D002` | M2PF | HPOSP2 | $00 | |
| `$D003` | M3PF | HPOSP3 | $00 | |
| `$D004` | P0PF | HPOSM0 | $00 | Player-0/Playfield collision; W on missile-0 HPOS |
| `$D005` | P1PF | HPOSM1 | $00 | |
| `$D006` | P2PF | HPOSM2 | $00 | |
| `$D007` | P3PF | HPOSM3 | $00 | |
| `$D008` | M0PL | SIZEP0 | $0F | Missile-0/Player collision; W on player-size-0 (0–3) |
| `$D009` | M1PL | SIZEP1 | $0F | |
| `$D00A` | M2PL | SIZEP2 | $0F | |
| `$D00B` | M3PL | SIZEP3 | $0F | |
| `$D00C` | P0PL | SIZEM  | $0E | Player-0/Player-Missile collision; W on missile size (0–3) |
| `$D00D` | P1PL | GRAFP0 | $0D | Player-1/Player collision; W on player-0 mask pattern |
| `$D00E` | P2PL | GRAFP1 | $0B | Player-2/Player-1 collision; W on player-1 mask pattern |
| `$D00F` | P3PL | GRAFP2 | $07 | Player-3/Player-2 collision; W on player-2 mask pattern |
| `$D010` | TRIG0 | GRAFP3 | $01 | Trigger-0; W on player-3 mask pattern |
| `$D011` | TRIG1 | GRAFM  | $01 | Trigger-1; W on combined missile mask |
| `$D012` | TRIG2 | COLPM0 | $01 | Trigger-2 (TRIG3 is cartridge sense on XL/XE); W on player-0 colour |
| `$D013` | TRIG3 | COLPM1 | $01 | Trigger-3; W on player-1 colour |
| `$D014` | PAL  | COLPM2 | $0F/$01 | NTSC=$0F PAL=$01; W only on player-2 colour |
| `$D015` | —    | COLPM3 | $0F | W: player-3 colour |
| `$D016` | —    | COLPF0 | $0F | W: playfield colour 0 (BAK when B=0,P=0) |
| `$D017` | —    | COLPF1 | $0F | W: playfield colour 1 |
| `$D018` | —    | COLPF2 | $0F | W: playfield colour 2 |
| `$D019` | —    | COLPF3 | $0F | W: playfield colour 3 (=PF3 if priority allocs PF3 to P/M) |
| `$D01A` | —    | COLBK  | $0F | W: background/border colour |
| `$D01B` | —    | PRIOR  | $0F | W: P/M priority + GTIA mode =9/10/11 |
| `$D01C` | —    | VDELAY | $0F | W: P/M vertical delay (player/missile sub-scanline offset) |
| `$D01D` | —    | GRACTL | $0F | W: P/M enable: bits 0=missile, 1=player, 2=dma |
| `$D01E` | —    | HITCLR | $0F | W: write any clears all P/M collision flags |
| `$D01F` | —    | CONSOL | $00 | R/W: bit 0=Start, bit1=Select, bit2=Option |

**HPOSPn horizontal range:** `$22` — just visible left edge; `$80` = screen centre; `$DE` — just visible right edge; wider playfields map `$20–$DF`.

### SIZEPn / SIZEM values

```
SIZEPn / SIZEM = $00–$03  (0–3):
  $00 = 1 pixel  (8 dots)
  $01 = 2 pixels (16 dots = double width)
  $02 = 4 pixels (32 dots = quad)
  $03 = 8 pixels (64 dots = double-height in hires)
```

---

## §4.2  9-bit Palette & NTSC Artifact Colours

GTIA produces 9-bit colour: 4 bits luminance (bits 0–3) + 4 bits chrominance (bits 4–7) + 1 artefact bit (bit 8). Each of the 16 registers (`COLPM0–3`, `COLPF0–3`, `COLBK`) hold a 4-bit NTSC colour.

**NTSC Artfact notes:** P/M sprites can produce false colours at pixel-clock boundary (mode 8–F GTIA with ORA overlapping. High-resolution pixels are **half-colour-clock** wide (effectively 320 colour-clock pixels in 160 colour-clock field).

---

## §4.3  Multi-Colour & Composite Colour Modes

| Mode | Colour bits per pixel | Notes |
|---|---|---|
| ANTIC 2/3 | 1-bit (PF2) | BAK or PF2 = hi-res text mode |
| ANTIC 4 | 2 bit pairs | BAK, PF0–2; optional PF3 at bit 7 |
| ANTIC 5 | 2-bit double-height | BAK, PF0–2 |
| ANTIC 6/7 | 1-bit + FG-colour bits | 5-colour single line width |
| ANTIC 8/E | 2-bit (4 colour) | 40×192 or 160×192 4-colour |
| ANTIC 9/A | 1-bit (2 colour) | 80×192 |
| ANTIC B/D | 1-bit (2 colour) | 160×96 (double vertical res) |
| ANTIC C | 1-bit (2 colour) | 160×192 |
| ANTIC F | 1-bit hi-res | BAK/PF2 luminance at dot-clock |
| GTIA 9 | 4-bit brightness | BAK background, 16 shades of one hue |
| GTIA 10 | 3-bit intensity | 9 colours (3 lum × 3 chroma) using COLPFn as hue |
| GTIA 11 | 4-bit hue | 16 hues (one lum) using PF2 register as luminance |

**GTIA 9+10+11 priority:** Only bits 6–7 of `PRIOR` select GTIA mode; all other `PRIOR` bits still affect P/M priority.

---

## §4.4  Hires GRAPHICS 0 / GRAPHICS 8

**GRAPHICS 0 (ANTIC mode 2):** 1-bit pixels; all pixels = PF2 colour; bit=1 = PF1 luminance, bit=0 = BAK colour. P/M sprites alter *chrominance* not luminance of pixels they overlap — this is the key trick used by the *Ironman Atari* compositing mode.

**GRAPHICS 8 (ANTIC mode F):** 320-pixel hi-res at normal playfield width; each bit of each byte maps directly to luminance at half-colour-clock rate. Full visible width = 320 colour-clocks → dots at 7.16 MHz dot clock. One byte = 2 pixels. Each byte stored MSB-left, LSB-right.

```asm
        ; Set up GRAPHICS 0 via OS
        lda #$00
        jsr $EFE3            ; OS GR.0 init in XL/XE

        ; OR direct register — write DMACTL + SDLSTL:
        lda #$22          ; GR.0: narrow, pf-on, players off
        sta SDMCTL

        ; GRAPHICS 8 direct:
        lda #<dlist_mode_F
        sta SDLSTL
        lda #>dlist_mode_F
        sta SDLSTL+1
```

---

## §4.5  Advanced / Exotic GTIA Modes

### §4.5.1  HIP / RIP — Interlaced 30-shade × 160 Pixel Display

**HIP** (Hardware Interlace Picture): exploits a GTIA shift-bug that occurs when alternating between GTIA 9 and GTIA 10 per scan line. Each GTIA 10 line is visually shifted by **half a pixel**, and the resulting display produces a 160-pixel wide × 200-line picture at approximately 30 shades. The original HIP format was discovered by HARD Software (1996).

**Display list concept:**

```
DLIST ONE            DLIST TWO
mode 9 GTIA           mode 10 GTIA
mode 10 GTIA          mode 9 GTIA
mode 9 GTIA           mode 10 GTIA
mode 10 GTIA          mode 9 GTIA
   ...                  ...
```

Alternate DLIST sets are displayed every other frame. A DLI kernel switches `PRIOR` between `$00` (GTIA mode F base) and `$40` (GTIA 9) / `$80` (GTIA 10) on each scan line. The effect of GTIA 10 shifting the display by half a pixel produces the 160-pixel wide result from two overlapping 80-pixel wide halves.

**Palette table** (30 shades, using registers $704–$711 for GTIA 10, $712 for GTIA 9 base):

```
 704 $00      708 $08      712 $00    ← GTIA 9 background
 705 $02      709 $0A
 706 $04      710 $0C
 707 $06      711 $0E
```

This palette structure means that 704 and 712 share the background colour, simplifying the DLI kernel to toggle only `PRIOR` rather than alternating both background registers every line — allocating one extra colour register becomes the device background.

**RIP** (Rocky Interlace Picture): RIP extends HIP by modifying the colour registers on each GTIA 10 line inside the DLI routine, producing true multi-colour interlaced pictures rather than the monochrome HIP palette. RIP picture generation requires modifying the GTIA 10 colour registers at the same scan-line rate; the logic is identical to the HIP DLI kernel, but additional `STA COLPFn` writes are interleaved on each GTIA 10 scan line.

**HINT for real picture:** 30 shades is the "average" bit-depth; HIP is 4 bits (16 levels) in mode 9, only 3 bits (8 levels) in the mode 10 lines. The algorithm designers deliberately design the interlace to pick GTIA 9 colour for high-contrast portions and GTIA 10 colour for shaded areas. No two adjacent HIP pixels should differ by more than 2 shade levels to avoid flicker.

```asm
; HIP DLI skeleton — two-zone mode switch per scan line
hip_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC                       ; start of scan line
        lda #$00                        ; PRIOR = 0 → GTIA mode F base
        sta PRIOR                       ; $D01B
        ldx #$40                        ; GTIA 9 value
        nop                             ; ~24 cycles of dead time
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        stx PRIOR                       ; switch to GTIA 9
        nop
        nop
        sta PRIOR                       ; back to F — GTIA confused shows mode E next line
        ; next DLI fires on next scan line — alternate PRIOR between $40 and $80

        pla
        tay
        pla
        tax
        pla
        rti
```

**RIP DLI extension (adding colour per GTIA 10 line):**

```asm
rip_dli_gtia10
        pha
        txa
        pha
        tya
        pha

        sta WSYNC
        lda rip_col_lo,y                ; colour from RIP palette LUT
        sta COLPF0                      ; $D016 — writes colour for this 10-line
        lda #$80                        ; PRIOR = $80 → GTIA mode 10
        sta PRIOR                       ; $D01B
        ; (next DLI will show mode 9 line; colour change persists from previous 10-line)

        pla
        tay
        pla
        tax
        pla
        rti
```

---

### §4.5.2  TIP — Taquart Interlace Picture

TIP adds colour back to HIP by inserting a **GTIA 11 (16-hue) line above each HIP 9/10 pair**. This approximately halves vertical resolution (200 lines → ~100 visible, plus dark lines) but gives TIFF true per-pixel colour on the existing HIP data.

Display list concept:

```
DLIST ONE              DLIST TWO
mode 11 (colour)       mode 11 (colour)
mode 9  (HIP)          mode 10 (HIP)
mode 11 (colour)       mode 11 (colour)
mode 10 (HIP)          mode 9  (HIP)
    ...                    ...
```

Each pair of HIP lines (mode 9 + mode 10) is sandwiched between two mode 11 colour lines that carry the hue for that pixel column. The HIP lines represent luminance, the mode-11 lines represent hue.

**Conversion pipeline from a 24-bit source picture:**

1. Scale/crop source to 160 × 100 pixels (TIP's effective resolution).
2. Map each source pixel to an Atari 256-colour palette.
3. **Extract hue:** take every even raster pixel's hue for DLIST ONE, every odd for DLIST TWO → palette register values written to `COLPFn` in the DLI.
4. **Extract shade (luminance):** HIP de-compress that picture into even/odd nibbles replacing each pixel pair; HIP step re-creates the 30-shade HIP output from the two 16-shade mode-9/10 sets.
5. Write the TIP DLI to select colour (mode 11) vs shade (mode 9/10) per line.

**TIP DLI kernel (colour line):

```asm
tip_colour_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC
        ; Colour stored in a LUT per scan line:
        lda tip_col_tab,y          ; LUT indexed by current scan line
        sta COLPF0                 ; $D016 = hue for this scan line
        lda #$C0                   ; PRIOR = $C0 == GTIA mode 11
        sta PRIOR                  ; $D01B
        ; next scan line = HIP shade line — do not change PRIOR here
        ; result: half-resolution colour + shade interleaved

        pla
        tay
        pla
        tax
        pla
        rti
```

---

### §4.5.3  GTIA 9++ — VSCROL DCTR Trick (Square Pixels, ~½ DMA)

The GTIA 9++ technique, discovered by Fox of Taquart, exploits ANTIC's **Delta Counter (DCTR)** behaviour under VSCROL to make each scan line of a Mode 15/COLBK display appear as 4 separate pixel rows, drastically reducing the apparent DMA cost.

**DCTR mechanism:** DCTR is a 4-bit internal ANTIC counter that governs line-repeat for mode lines. Normally it starts at 0 and counts up to the mode-specific limit, then advances to the next DL instruction. When VSCROLL is enabled, DCTR starts at the value of VSCROL for the first scrolled line, and stops at VSCROL for the last scrolled line.

**The trick:** set `VSCROL = 3` on the *last* scan line of a mode 15 line (reducing that line to 4 visible scan lines out of 8), then immediately write `VSCROL = 13` at the start of the next scan line. Because DCTR is 4-bit, writes of 13 and 3 create a 3→15→3 sequence, causing each real scan line to appear as **4 pixel rows**.

**Display list for GTIA 9++:**

```
$2F  line of mode 15 + VSCROLL, bit5 set   ← last line of pair (set VSCROL=3 at end)
$0F  line of mode 15 + VSCROLL clear       ← normal line (VSCROL=13 on start)
$41  JVB
```

**DLI approach (simplest; one DLI pair per 2 scan lines = quarters the DLI count of Konop's mode):**

```asm
; VSCROL must be written at the narrow boundary between scan lines:
; first DLI fires: set VSCROL=3 for the CURRENT (last) line
; second DLI fires: set VSCROL=13 for the NEXT (normal) line
; cycle budget must allow VSCROL write during the DLI

gtia9pp_vscrol_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC                           ; land on scan-line 0 of pair
        lda #$03                            ; VSCROL = 3 → truncate current row to 4 scan lines
        sta VSCROL                          ; $D405
        pla
        rti                                 ; GTIA shows 4 of last 8 scan lines of mode 15

; --- second DLI fires next scan line ---
gtia9pp_vscrol_dli2
        pha
        txa
        pha
        tya
        pha

        sta WSYNC                           ; land on the NEXT scan line (DCTR wraps 15→0)
        lda #$0D                            ; VSCROL = 13 — header d
```

sta VSCROL                          ; dctr = 13..15,0 → 4 scan rows counted
        pla
        rti

\`\`\`

**DMA savings table (59 visible lines on NTSC):**

| Method | DMA instructions | CPU time per line | Total (59 lines) |
|---|---|---|---|
| Mode 15 native (mode 15) | 6 + width DMA | ~64 cyc | 4 136 cyc |
| GTIA 9++ (DLI per 2 lines) | 1 + width DMA | ~32 cyc | 2 307 cyc |

GTIA 9++ saves ~1 800 cycles (≈ 1 ms per frame). The gain is significant in CPU-constrained games.

**TMC2 40×39 character-mode display extension:** same VSCROL trick applied to ANTIC mode 2 text lines where VSCROLL bit 5 is set on alternating lines. The result is a 40 × 39 character display (each logical character row = 1 scan line * 4 pixel-rows via DCTR). DLI toggles `CHBASE` between two character sets so the 6-pixel-high font (8 pixels logical - 2 rows = 6 visible) renders cleanly.

```asm
tmc2_dli
        pla
        sta WSYNC
        lda line_flag         ; 2 or 5 scan lines shown per character (toggles via 7)
        sta VSCROL
        eor #$07
        sta line_flag
        lda font_flag         ; 0 = $D400, 4 = $D800 (two font banks every 2 rows)
        sta CHBASE            ; $D409
        eor #$04
        sta font_flag
        pla
        rti
```

---

## §4.6  Player / Missile Graphics (P/M Graphics)

### P/M memory layout

P/M graphics use a dedicated memory area selected by `PMBASE`. The data is a vertical bitmap: each byte is one scan line of one player or missile group, with the most significant bit displayed leftmost. Single-line resolution uses a 2 KB aligned area; double-line resolution uses a 1 KB aligned area but each data byte is displayed for two scan lines.

| Object | Standard byte span | Notes |
|---|---|---|
| Missiles | one 256-byte page shared by four 2-bit missiles | Combined through `GRAFM` for direct graphics |
| Player 0-3 | one 256-byte page each | Shape data also writable through `GRAFP0-GRAFP3` |

Enable DMA through ANTIC `DMACTL/SDMCTL`, then enable GTIA rendering through `GRACTL` bit 1 for missiles and bit 2 for players. Horizontal positions use `HPOSP0-HPOSP3` and `HPOSM0-HPOSM3`; widths use `SIZEP0-SIZEP3` and `SIZEM`.

Priority and overlap are controlled by `PRIOR/GPRIOR`. OR-overlap allows two players on the same scan line to create a combined color where their bit patterns overlap. Use it deliberately within a scan line; do not rely on accidental cross-line overlap.

Set `PRIOR bit 3 ($08)` inside a DLI isolate player 3 in a band; combine COLP? from same band DLI to create a "5th ghost player" without a 5th sprite.

**ORA overlapping scanline-RMW pattern (single scan-line two-colour sprite):**

```asm
ora_overlap_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC
        lda sprite0_line,y    ; 1-bit mask for P0 colour = green
        sta GRAFP0            ; $D00D
        lda sprite1_line,y    ; 1-bit mask for P1 colour = grey
        sta GRAFP1            ; $D00E
        ; result = OR of both masks on same scan line → two-colour sprite

        pla
        tay
        pla
        tax
        pla
        rti
```

**Avoid ORA overlapping on adjacent scan lines** without a WSYNC between them — the spec design allows intentional overlap only on the *same* scan line. Overlapping across scan lines produces AND/O-RA-flicker artefact that looks like colour-bleed. Use a new composite-mask table if you want more than two scan-line colours: pre-OR the two sprite-table entries at build time into a third table.

---

## §4.7  P/M Vertical Multiplexing (DLI Bands)

Vertical multiplex: single-player sprite used on multiple non-overlapping Y-bands; DLI changes HPOSn/SIZEn per band boundary.

```asm
; VBI sets top band HPOSP0; DLI band_i: reads band_lut → HPOSP0/SIZEP0
; band_lut indexed by current band number 0..11

; VBI precomputes for 12 bands: band_hpos_lo/hi + band_sizep + band_color
; Page-aligned DLI saves 6 cycles vs 16-bit pointer reload

band_dli
        pha
        txa
        pha
        tya
        pha
        lda band_hpos_lo,y
        sta HPOSP0              ; $D000
        lda band_color,y
        sta COLPF0              ; $D016
        pla
        tay
        pla
        tax
        pla
        rti
```

**Mode 4 player timing gotcha:** on a Mode 4 display list, player 3 lags 1 scan line relative to players 0–2 due to GTIA serialisation — add 6+ scan-line buffer zone; drop WSYNC from non-colour-change DLI code for maximum speed.

---

## §4.8  Collision Detection

| Register | Read | Collision type |
|---|---|---|
| `$D000` / M0PF | Missile 0 ↔ Playfield | Missile-to-playfield |
| `$D004` / P0PF | Player 0 ↔ Playfield | Player-to-playfield |
| `$D008` / M0PL | Missile 0 ↔ Player | Missile-to-player |
| `$D00C` / P0PL | Player 0 ↔ Player | Player-to-player |

**Clear:** write any value to HITCLR (`$D01E`); clears ALL collision flags simultaneously. (Keep track of which bits were set before the write to distinguish between collisions.)

```asm
        lda M0PF              ; $D000 — did missile 0 hit background?
        pha
        lda P0PF              ; $D004 — did player 0 hit background?
        pha
        lda M0PL              ; $D008 — did missile 0 hit any player?
        pha
        lda P0PL              ; $D00C — did any player-to-player collision fire?
        pha
        lda #$00
        sta HITCLR            ; $D01E — clear ALL collision flags
        pla                   ; P0PL → A  
        sta collision_p0pl
        pla                   ; M0PL → A
        sta collision_m0pl
        pla                   ; P0PF → A
        sta collision_p0pf
        pla                   ; M0PF → A
        sta collision_m0pf
```

---

Source notes: GTIA register behavior is summarized from `Altirra-hardware/extracted_chapters/chapter06.md` and `atari-documentation/ANTIC-GTIA/GTIA-Registers.md`. Deep DLI patterns live in `hardware/antic.md` and `graphics/display-lists.md`.
