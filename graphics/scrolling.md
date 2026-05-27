---
name: atari8bit-scroll-detail-ref
description: >-
  Detailed Atari 8-bit scrolling patterns supplementary to antic.md — hardware-assisted vertical parallax DLI, GTIA 9++ pixel-half-scroll, MWP minimum-wrapping-principle, VBlank-driven mouse decoder, joystick RORT nibble decoding, and DLI-with-wide-playfield timing gotcha from scrolling.md and ironman.md.
---

# references/scroll-detail — Scrolling Deep Reference

---

## Purpose

This file is a tier-3 supplement to antic.md §3.3 and master index §§62–72. Covers patterns not in the main file: hardware-assisted pixel-half scrolling, MWP screen-wrapping scheme, VBlank mouse polling with table-driven nibble decoder, and the `ROR`-based joystick bit-field extractor. Install all four subparts for game-level scrolling depth.

---

## Quick-Lookup

| Need | See § |
|---|---|
| HW-assisted parallax scroll (DLI band chain, rate LUTs) | §1.1–§1.3 |
| Half-step pixel scroll (ANTIC-F soft sprite + char-set flip) | §2 |
| MWP screen-wrapping (one row/col-buffer, 2 LMS) | §3 |
| VBlank mouse driver ($D300 nibble read + Amiga/ST tables) | §4 |
| ROR joystick decoder (STICK0 bit-field → dx/dy) | §5 |
| DLI wide+VSCROL=0 DLI-timing gotcha | §6 |
| NVBL deferred VBI RETURN (`SETVBV/XITVBV`) | §7 |

---

## §1  Hardware-Assisted Vertical Parallax Scrolling

### §1.1  Concept

Three screen layers with different scroll speeds (high/low/nil) implemented without double/triple buffer: VBI accumulates each band's scroll accumulator separately; DLI band-i changes `HPOSn` for player used as that band's scroll-sprite for the scan line the DLI fires on.

Unlike "full" parallax (which doubles display memory), this uses the same screen memory twice, offset by `HPOSn` per band.

### §1.2  VBI Rate-LUT Pattern

```asm
; Each band i has band_rate[i] = 0 (no scroll), 1, 2, or 4 pixels/frame
; The LUT lives in ROM or locked page-zero
band_rate_low
        .byte 0,1,2,4,0,1,2,4    ; bands 0..7

vbi_parallax
        pha
        txa
        pha
        tya
        pha

        ldx #8                  ; 8 parallax bands (half the screen lines each)
?bands  lda band_off x            ; offset-accumulator for band i
        clc
        adc band_rate_low,x     ; add this band's speed
        sta band_off,x

        pla
        tay
        pla
        tax
        pla
        rti                     ; do NOT use XITVBV — bands need bare-metal/VDSLST path
```

**Typical band counts and speed selections:**
- Sky band (8 lines): band_rate=0 (table still; no CPU cost)
- Mid-ground (12 lines): band_rate=1 (~3.6 px drift between VBIs)
- Foreground (8 lines): band_rate=2 (faster parallax offset)
- Player sprite (8 lines): band_rate=0 (counter-scroll for sprite shadow)

### §1.3  Five DLI Charge-LUT for Character Mode Flip-Flop

Character-set flick technique without page flip: two character sets (`$E000` vs `$E800`), DLI swaps `CHBASE` mid-screen while HSCROLL steps 1 color clock at a time:

```asm
; DLI flips char-set AND triggers HSCROL step simultaneously
parallax_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC
        lda font_bank_flag     ;0=$E000, 1=$E800
        eor #$01
        sta font_bank_flag
        sta CHBASE             ; $D400 — swap character set mid-screen

        lda #$01               ; advance HSCROL by 1 (= ~half a character shift)
        sta HSCROL              ; $D404

        pla
        tay
        pla
        tax
        pla
        rti
```

Half-step scroll sequence per frame: flip char-set → HSCROL+1 → flip char-set → HSCROL+1 → repeat for `{16/HSCROL_max}` steps, then coarse scroll increments LMS low byte by 0x28 = 40. Total polish rate = same CPU cost as traditional fine-scroll but fullXMAL80-px resolution.

**Half-step and fractional scroll direction note:** HSCROL increment scrolls the viewport LEFT (adds 1 col-clock buffer from the left); HSCROL decrement scrolls RIGHT. The bitmap material is read further right when HSCROL grows, so pixels appear to move left.

---

## §2  MWP (Minimum Wrapping Principle) Scrolling

### §2.1  Concept

Screen memory wraps **onto itself** by duplicating one buffer row at bottom/top (or one column at left/right). Only 2 LMS instructions required. No full-screen copy.

### §2.2  Memory arrangement (vertical wrap)

Assume Mode 4 (40 bytes × 24 lines). Allocate 25 visible rows:

```
Row 0: $6000–$6027  40 bytes
Row 1: $6028–$604F
...
Row 22: $68B8–$68DF   (22 is last visible line)
Row 23: $68E0–$690F   DUPLICATE of Row 0 = wrap buffer
```

DLIST has LMS at the top (Row 0) and ALSO at scan line 22 (Row 23). When row 22 scrolls off the bottom, new data is blitted into Row 23, and the DLIST LMS for scan line 22 wraps back to Row 0. BLIT only one 40-byte row per scroll step.

The flag-check after each scroll step: **did we write to row 0 or row 23?** if yes, mirror to the other row immediately.

### §2.3  Memory arrangement (horizontal wrap)

Same principle, but with page-per-line layout (256 bytes/line). Only one column (usually byte 0 / byte 255) needs double-copy. Scroll steps: blit 1 column from off-screen into column 255, mirror column 255 → column 0 if modified:

```asm
 mwp_scroll_left_buffer
        ldx col_ptr            ; current column (0–255 page-wide)
        lda screen_row_0,x     ; read from buffer line
        sta screen_row_0+255,x ; mirror if 255 changed
        dex
        stx col_ptr

 mwp_update_dlist_lms
        ldy #n_lines
?loop   lda dlist_lms_low,y
        dec dlist_lms_low,y    ; scroll left = decrement low byte
        bne ?skip
        dec dlist_lms_high,y   ; page boundary carry
?skip   dey
        bpl ?loop
```

**MWP total CPU per step:** ~80 cycles (blit one row) + ~1200 cycles for 30 lines × 4 = ~1.3 ms on a 1.79 MHz machine. Entire 60-frame cycle = ~78 ms ≈ 13 FPS at single-row scroll — suitable for isometric / puzzle scrolling.

---

## §3  VBlank-Driven Mouse Reader

### §3.1  Register Read

The Atari mouse (ST-compatible or Amiga-compatible, both read via POT0/1 treated as a 4-bit quadrature encoder) is addressed through `$D300` (or via POT0/1 for the Atari ST mouse — see notes in input.md §6.3).

```asm
; VBI mouse poll — REQUIRES that $D300 is read every ~2 ms for reliable tracking
; (VBI is ~16.6 ms — sample on every VBI is sufficient for most application)

 vbi_mouse
        pha
        txa
        pha
        tya
        pha

        lda $D300              ; read quadrature nibble (bits 0–3 = X, bits 4–7 = Y)
        pha                    ; saved for table-driven decode

        ; --- decode X-axis from bits 0-3 ---
        and #$0F
        tay
        lda xtable,y
        cmp #0
        beq ?no_x
        clc
        adc mouse_x_lo         ; signed accumulation (non-linear due to oversample)
        sta mouse_x_lo
        lda mouse_x_hi
        adc #0
        sta mouse_x_hi
?no_x

        ; --- decode Y-axis from bits 4-7 ---
        pla
        and #$F0
        lsr a
        lsr a
        lsr a
        lsr a                   ; shift right nibble to low
        tay
        lda ytable,y
        cmp #0
        beq ?no_y
        clc
        adc mouse_y_lo
        sta mouse_y_lo
        lda mouse_y_hi
        adc #0
        sta mouse_y_hi
?no_y

        pla
        tay
        pla
        tax
        pla
        rti
```

**Table-driven nibble decoding (Amiga compat, from ironman.md):**

```asm
xtable  .byte  0, -1,  1,  0   ; $0=$f
        .byte  1,  0,  0, -1   ; $4=$7
ytable  .byte  0,  1, -1,  0   ; $0=$f
        .byte  1,  0,  0, -1   ; $4=$7
```

**Table-driven nibble decoding (Atari ST compat):**

```asm
xtable  .byte  0,  1,  0, -1   ; $0=$f
        .byte  0, -1,  1,  0   ; $4=$7
ytable  .byte  0,  0, -1,  1   ; $0=$f
        .byte  0,  1, -1,  0   ; $4=$7
```

> **Caveat:** No emulator currently supports the MT mouse hybrid; this only works on real hardware. On $D300, VBI-rate sampling (every 16 ms) causes visible lag in fast/swift motion. For game-quality response, use a timer 1 IRQ at ~1 kHz for quadrature sampling, and accumulate deltas each frame.

---

## §4  ROR-Based Joystick Bit-Field Decoder

`STICK0` (shadow `$278`) encodes 4-direction in bits 0–3 as a 4-bit Gray-coded field:

```
 STICK0 bit 0 = UP
 STICK0 bit 1 = DOWN
 STICK0 bit 2 = LEFT
 STICK0 bit 3 = RIGHT
```

A single `ROR A` shifts the low-order bit into the Carry flag — test each axis pair sequentially:

```asm
record_joystick_vbi
        lda STICK0            ; $D278 (shadow)
        cmp #$0F
        bcs ?none             ; $0F = centered (all bits high = open-collector grounded)
        sta latest_joystick

?none   lda STRIG0            ; $D284 — trigger button
        bne ?done
        lda #1
        sta delay_count        ; ludicrous speed!
?done   rts

record_joystick_vbi        ; also polled in VBI/VBI-driver
process_joystick
        lda #0
        sta joystick_x
        sta joystick_y

        lda latest_joystick
        ror a                  ; bit 0 = UP → goes to Carry
        bcs ?up_clear          ; carry clear = pressed → skip
        dec joystick_y        ; UP = decrement (wraps to $FF)
?up_clear
        ror a                  ; bit 1 = DOWN → Carry
        bcs ?down_clear
        inc joystick_y        ; DOWN = increment
?down_clear
        ror a                  ; bit 2 = LEFT → Carry
        bcs ?left_clear
        dec joystick_x        ; LEFT = $FF
?left_clear
        ror a                  ; bit 3 = RIGHT → Carry
        bcs ?next
        inc joystick_x        ; RIGHT = $01 — NOTE ROR (LSR) confirm bit ordering
?next   lda #0
        sta latest_joystick

        rts
```

> **Note on encoding direction:** Some CX85-trackball/430S hardware uses bit=high for pressed. If arrows seem inverted, swap the BNE/BEQ branching. The `STICK0` returned from the register itself is **high=off / low=on** (active-low from open-collector), so is `LDA STICK0; CMP #$0F` (not CMP #$00) tests the centered 2-state.

---

## §5  DLI Wide Playfield + HSCROL + VSCROL=0 — Timing Gotcha

From scrolling.md §JVB-VSCROL-0: When using a DLI on the last scrolled line AND HSCROL is wide AND VSCROL=0, ANTIC has only ~10 CPU cycles on the first scan line of a Mode 4 + wide + HSCROL line. This is because: (a) wide playfield gives 48 bytes/line (+8 DMA steal), (b) HSCROL adds another +8 byte DMA window (4 left + 4 right buffer), (c) Mode 4's first scan line steals font-generation cycles — Net = <10 cycles for any authored DLI body.

### Mitigation options

| Option | Cost | Use case |
|---|---|---|
| VSCROL ≥ 1 | Gives ≥ 2 scan lines on the DLI line | Works with any DLI body; the simplest fix |
| Normal-width playfield (DMACTL $22) | Remove 8-cycle wide DMA steal | Status-line DLI still works; scrolling playfield loses 8 color clocks |
| Page-aligned DLI on next scan line | DLI fires on scan line 2, not line 1 | Sufficient cycles line 2 |

**Recommended approach for game engine:** In VBI, ensure VSCROL is always ≥ 1 before leaving; reset to 0 *only during the VBI* right after writing HSCROL/VSCROL for the next frame.

```asm
vbi_end
        lda vert_scroll        ; check we worked around this
        ora horz_scroll        ; if BOTH are non-zero fine
        bne ?ok
        lda #$01               ; VSCROL floor = 1
        sta VSCROL
?ok     jmp XITVBV
```

---

## §6  NVBLNV — SETVBV / XITVBV Deferred VBI  

(scrolling.md §NVBL deferred VBI return)

The OS provides two entry points for the deferred vertical blank interrupt: `SETVBV` installs it (X=high-byte of handler, Y=low-byte), `XITVBV` exits via the OS path, which restores A/X/Y and performs the CHKHCLK/VDSLST setup for the next VBI.

```asm
init_deferred_vbi
        ldx #>my_vbi
        ldy #<my_vbi
        lda #$07               ; defer flag + VBI enabled
        jsr SETVBV             ; $E45C on XL/OS-A

my_vbi
        pha
        txa
        pha
        tya
        pha

        ; [... do work ...]

        jmp XITVBV             ; $E462 — correct deferred VBI return path
```

**Why not `RTI`:** `XITVBV` hands the accumulator restore to the OS VBI chain so the deferred mechanism keeps running across VBI boundaries. `RTI` from a VBI executes at cycle 0 of the visible area, before the OS can set up the NMI return chains.

---

## §7  MWP One-Row/Single-Column Blit Pattern (Full Code)

```asm
; mode 4 per-row blit + DLIST pair  — update BLIT after each scroll step
mwp_scroll_step_v
        ldy #scroll_row_count   ; 24 visible lines
?loop   lda blit_row_00,y       ; read which source row maps to line i
        sta blit_row_00+25,y     ; mirror to bottom buffer
        bne ?no_mirror
        lda blit_row_24,y       ; also read from bottom buffer
        sta blit_row_00,y       ; mirror to top (only if col 24 was modified)
?no_mirror
        dey
        bpl ?loop

        ; LMS pointers handled in dlist_blit array — no full-page copy needed
        rts
```

---

*This file is references/scroll-detail.md — tier-3 supplement for antic.md §3.3 and master index §§62–72. MWP, half-step scroll, VBlank mouse, joystick ROR decode, and DLI wide+VSCROL=0 timing gotcha are not in the main file but originate from ironman.md and scrolling.md.*
