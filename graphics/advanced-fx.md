---
name: atari8bit-advanced-graphics-effects
description: >-
  Atari advanced graphics effects: HIP, RIP, TIP, GTIA 9++, interlaced shade and
  colour modes, DLI palette switching, conversion constraints, and timing hazards.
---

# Advanced Graphics Effects (HIP, RIP, TIP, GTIA 9++)

## HIP / RIP — Interlaced 30-shade × 160 Pixel Display

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

## TIP — Taquart Interlace Picture

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

**TIP DLI kernel (colour line):**

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

## GTIA 9++ — VSCROL DCTR Trick (Square Pixels, ~½ DMA)

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
        sta VSCROL                          ; dctr = 13..15,0 → 4 scan rows counted
        pla
        rti
```

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
