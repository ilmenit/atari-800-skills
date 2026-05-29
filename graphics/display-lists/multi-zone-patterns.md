# Multi Zone Patterns

## §4  Multi-Zone DLI Patterns

### §4.1  HW Vertical Parallax Band Chain (VBI pre-sets + DLI swaps)

For "psuedo-side-scrolling" where sky / mid-ground / foreground scroll at different rates:

```asm
        ; VBI pre-computes scroll positions for 12 bands × 4 players
band_hpos = $60           ; 12 × 2 = 24 bytes direct page (HPOS L/H per band)
band_color = $78          ; 12 * 2 bytes      

vbi_parallax
        pha
        txa
        pha
        tya
        pha

        ; --- update sky band 0 — no scroll every frame ---
        lda #$80            ; HPOS0 for sky 
        sta band_hpos

        ; --- update scroll offset for band i (accumulates each frame) ---
        lda scroll_offset
        adc band_speed,x    ; band_speed LUT: 0=sky, 2=mid, 4=fg
        sta band_hpos+12,x

        ; --- install DLI band chain ---
        lda #<band_dli_0
        sta VDSLST
        lda #>band_dli_0
        sta VDSLST+1

        lda #NMIEN_VBI | NMIEN_DLI
        sta NMIEN

        pla
        tay
        pla
        tax
        pla
        rti

; --- band_i DLI (one per band, page-aligned to save 6 cycles) ---
band_dli_0 *= $2100       ; page-aligned
        pha
        txa
        pha
        tya
        pha
        lda band_hpos      ; HPOS L/H from pre-computed LUT
        sta HPOSP0         ; $D000
        lda band_color     ; COLPF? for this band
        sta COLPF0         ; $D016
        pla
        tay
        pla
        tax
        pla
        rti

band_dli_1 *= $2200       ; next page, next band
        ; ... same pattern with band i+1 colour/position
```

**Key design points:**
- Bands must be page-aligned (`*= $2N00`) to save 6 cycles vs 16-bit pointer reload per band.
- Precompute band LUTs in VBI (not in DLI — DLI has very few cycles).
- VBI pushes band positions into page-zero LUT so DLI only reads a single `LDA / STA` pair.

### §4.2  GTIA 9++ — DCTR VSCROL Timing Kernel

GTIA 9++ (GTIA Mode E with DCTR-driven line-repeat): using VSCROL trick to repeat each scan-line as 4 pixel-rows, producing a 32-pixel-high (160-wide) display from only one mode-line half the ROM. Split kernel:

```asm
; VSCROL values at DCTR boundary:
;   DCTR=13 → VSCROL=13 held at end of line → next row-counter = 3 (drops to 4 of 16)
;   DCTR=3  → VSCROL=13 on NEXT line → DCTR counts 3→15, 14 rows (wraps) → ~4 rows/line
;   net result: each real scan line = 4 pixel rows

; DLI fires at the boundary between two DCTR cycles — the only safe moment
; to update VSCROL without disrupting the DCTR counter mid-run

gtia9pp_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC                       ; land at scan line boundary
        lda #$03                        ; DCTR = 3 → only 4 rows visible at end
        sta VSCROL                      ; $D405 — now DCTR counts 3,4,5,6…14,15 wraps
        ; note: only 4 rows shown (3,4,5,6) then next scan line rereloads
        ; 13 rows skipped in the missing 12 rows for next boundary
        nop                             ; wait --- 13 CPU cycles = 13/4 = 3.25 cycle-wrap
        lda #$0D                        ; set to 13 for next repetition to start
        sta VSCROL                      ; next: DCTR counts 13,14,15,0 → 4 rows again

        ; Optional: alternate PRIOR between $40 (mode 9) / $00 (mode F base)
        lda #$40                        ; GTIA 9
        sta PRIOR                       ; $D01B
        ; next DLI on next scan line does the same, alternating

        pla
        tay
        pla
        tax
        pla
        rti
```

**DCTR state diagram (one full VSCROL cycle through one pair of mode lines):**

```
Row-counter: 13 →14 → 15 →  [wrap @0] → 0 → 1 → 2 → 3 -- VSCROL=13->3--> -- next-VSCROL@13--row-count 3→15 wrap 4-pixel-row visible
```

**Cycle budget inside the DLI:**
```
PHA/TXA/PHY    =  6 cycles
WSYNC          =  7 cycles (CPU halts until cycle 105)
LDA #0 / STA VSCROL =  4+4 =  8 cycles
...NOPs        = 13 cycles (fill to align DCTR boundary)
LDA #1 / STA VSCROL =  8 cycles
LDA #$40 / STA PRIOR = 8 cycles
PLA/PLX/PLA/RTI     = 16 cycles
TOTAL          ≈ 57 cycles — fits in ~97 cycles/line on Mode E
```

**Caveats:**
- VSCROL cannot be written at scan line 240+ (JVB wraps — use `CMP VCOUNT` to detect before writing).
- DCTR is not directly readable; verify the DLI by counting how many rows are shown on a test pattern.
- Mid-frame LMS at scan line 95 on a 192-line Mode E kernel can disrupt VSCROL — guard with `CMP VCOUNT` at boundary.

---

## §5  ORA Overlapping Scanline-RMW Pattern

From ironman.md §Soft Sprites → ORA overlapping for colour: two players overlaid on the *same scan line* produce a colour where the OR of their masks falls:

```asm
        ; Two 1-bit players, same Y-band
        ; P0 = left-half colour; P1 = right-half colour
        ; → left half = P0; right half = P1; overlap = P0|P1

player0_mask: .byte $FF,$00,$FF,$00   ... ; 8 scan lines, alternating colour
player1_mask: .byte $00,$FF,$00,$FF   ... ; shifted by 1 scan line

        ; GPRIOR = $01  (player 0 over playfield; player 1 ALSO over playfield)
        ; No 5th-player trick here — just raw ORA overlap

ora_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC
        lda player0_mask,y
        sta GRAFP0              ; $D00D
        lda player1_mask,y
        sta GRAFP1              ; $D00E

        pla
        tay
        pla
        tax
        pla
        rti
```

**Practical type sizes for ORA overlap:**
- 1-bit mask (2 colors): use bit 0 = P0 colour, bit 1 = P1 colour → OR mask is 3-colour sprite with no fifth player needed
- Extend to 3 players (6-colour sprite) by adding P2 at bit 2 in a shared mask table

---
