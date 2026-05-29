# Registers Colors

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
| `$D01D` | —    | GRACTL | $0F | W: P/M display enable: bit 0=missiles, bit 1=players, bit 2=trigger latch |
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
