---
name: atari8bit-scroll-detail-ref
description: >-
  Detailed Atari 8-bit scrolling patterns supplementary to antic.md — hardware-assisted vertical parallax DLI, GTIA 9++ pixel-half-scroll, MWP minimum-wrapping-principle, and DLI-with-wide-playfield timing cross-references from scrolling.md and ironman.md.
---

# references/scroll-detail — Scrolling Deep Reference

---

## Purpose

This file is a tier-3 supplement to antic.md §3.3 and master index §§62–72. Covers patterns not in the main file: hardware-assisted pixel-half scrolling and MWP screen-wrapping schemes. Input decoding, OS VBI return rules, and deep DLI timing are cross-referenced instead of duplicated here.

---

## Quick-Lookup

| Need | See § |
|---|---|
| HW-assisted parallax scroll (DLI band chain, rate LUTs) | §1.1–§1.3 |
| Half-step pixel scroll (ANTIC-F soft sprite + char-set flip) | §2 |
| MWP screen-wrapping (one row/col-buffer, 2 LMS) | §3 |
| Input decoders used by scroll engines | `system/input.md` |
| DLI wide+VSCROL=0 DLI-timing gotcha | `graphics/display-lists.md` §2.2 |
| NVBL deferred VBI RETURN (`SETVBV/XITVBV`) | `system/os-vectors-handlers.md` §1 |

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

## §3  Related Engine Inputs and Timing

Scrolling engines often consume input deltas and run from VBI/DLI paths, but those details belong to narrower references:

- Joystick and mouse decode: `system/input.md`
- Deferred VBI install/return: `system/os-vectors-handlers.md`
- DLI timing edge cases for wide playfields, HSCROL, and VSCROL: `graphics/display-lists.md`

---

## §4  MWP One-Row/Single-Column Blit Pattern (Full Code)

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

*This file is references/scroll-detail.md — tier-3 supplement for antic.md §3.3 and master index §§62–72. MWP and half-step scroll details remain here; input, OS VBI, and DLI timing details are linked to their narrower reference files.*
