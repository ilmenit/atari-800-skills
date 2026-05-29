# Player Missile

## §4.6  Player / Missile Graphics (P/M Graphics)

### P/M memory layout

P/M graphics use a dedicated memory area selected by `PMBASE`. The data is a vertical bitmap: each byte is one scan line of one player or missile group, with the most significant bit displayed leftmost. Single-line resolution uses a 2 KB aligned area; double-line resolution uses a 1 KB aligned area but each data byte is displayed for two scan lines.

| Object | Standard byte span | Notes |
|---|---|---|
| Missiles | one 256-byte page shared by four 2-bit missiles | Combined through `GRAFM` for direct graphics |
| Player 0-3 | one 256-byte page each | Shape data also writable through `GRAFP0-GRAFP3` |

Enable DMA through ANTIC `DMACTL/SDMCTL`, then enable GTIA rendering through `GRACTL` bit 0 for missiles and bit 1 for players. Horizontal positions use `HPOSP0-HPOSP3` and `HPOSM0-HPOSM3`; widths use `SIZEP0-SIZEP3` and `SIZEM`.

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
