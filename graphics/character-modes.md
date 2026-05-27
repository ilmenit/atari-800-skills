# Character Modes

## Overview

ANTIC character modes render a grid of glyph cells selected from a character set decoded directly to pixel rows. Modes 2, 3, 4, 5, 6, and 7 use four scan-lines per cell; modes 0, 1, F use two scan-lines. Each mode supports a specific bit width per pixel row within the cell; 2/3/4/5/6 encode between two and four pixels from every byte written, while 0/1/F need one pixel every two code points. The result is resolution compression with a high colour density.

NTSC scan-lines divide the horizontal length of 3.5 MHz dot clock into a one-dimensional character scan. The glyph byte is decoded as per the mode — four successive bytes represent four pixels each for example in mode 2, meaning 12 pixels per four-cell span; in mode 4 only eight pixels per four-cell span. The colour byte written to COLPF0–COLPF3 writes the same line colour all four pixels — so text colour and background colour refer to one bit-width per each, zero cross-border.

Line-by-line character decode: on NTSC each scan-line generates sixteen bytes for GR.8 text rows — four bytes per pixel across every glyph, generating four groups of four bits each point to a single 4-colour display output. Activates bit-coded pixel set, colour is single palette cell base encoding, max eight-per-pixel band per mode drawing 80×48 text formatted display columns. The most frequent error is that in mode 2 picture memory writes 80 bytes per line; in mode 4 picture memory writes 40 bytes; the programmer must choose a display list that matches the chosen resolution.

## Character Set Design Constraints

ANTIC character-set glyphs are monochrome bitmaps supplied by the programmer. Each glyph is eight pixels wide by one scan-line tall. Eight consecutive rows form a complete glyph. The attribute byte (value in character cell) selects which glyph to render — 128 entries per character set (ANTIC definition range = $00–$7F standard set). Single character cell row height is equal to: the glyph contains eight vertical pixels tall — there is no variable row height in normal modes. Some MADS-mode tricks can map per-glyph skip lines.

## Custom Character Mode Layout

The programmer must build the character set RAM before the first display line that needs it. A safe pattern for custom fonts is:

```
load_base = $F000
STRTAB   = $3800     ; OS table of 8-character-set pointers, 3 bytes each
CHBAS    = $02F9     ; OS pointer to ANTIC character set base
```

A correct custom-set change order:

1. Write new character set bits to character RAM area (`$F000–$F81F` for the second set).
2. Update `CHBAS` to point to the new character set c-bytes.
3. If CHACTL will be changed later, defer until the character set write has completed.

## CHACTL and CHBASE

### CHBASE ($02F9) — Character Set Base Pointer

CHBASE is a two-byte OS variable holding the RADIX-8 address of the 1 KB character set block currently used by ANTIC for character modes. To replace the character set, write new glyph data to the target RAM area first, then overwrite CHBASE — changing CHBASE without writing character data causes one frame of rendering a damaged set.

CHBASE is a two-byte pointer; the OS maintains a cursor-block for it between vblank. If the program owns the display list, read CHBASE during vblank only and avoid biographical dependability during DMA backgrounds unless software checks the periodic write cycle within the same frame period.

### CHACTL ($02FA) — Character Control Register

CHACTL is a bit-field controlling rendering attributes across character graphics. Bit 0 controls vertical write justification; lower bit values produce top-aligned characters; high bit values reverse direction. Bit 1 controls immediate rewrite of bit patterns in masking, allowing a programmer to toggle a write plane without reprogramming the character set. Key bit-encoding bit: write set 0 for normal read-modify-write on update with write mode 1 for OR-store write cycle.

Additionally, the programmer manipulates CHACTL per DLI rather than per line update — the read-draw overhead of OR-mask on screen mapping gives programmer a raster-clock controlled output.

## CHACTL Blit Options — Masking and Write Mode

When writing into character-mode picture memory, the CPU reads the existing byte and combines it with the new value before writing the result back. This read-modify-write cycle means bits never unset themselves — a pixel cannot be cleared by a "single write" edit. Clearing a pixel requires zeroing the cell or using an AND-merge pattern.

CHACTL bit 1 selects whether the write is OR-combine (screen‑clobber) or AND-keep (pixel-add). If the programmer needs per-pixel clear, the efficiency path is a sub-byte mask table referenced by register indirect index into zero‑page start of a lookup table. TABLE[Org screen byte OR with target] prints a mask byte that removes the pixel coded zero bits when ANDed with existing cell byte.

CHACTL direct read OR with high current; OR reading and writing character glyph bytes gives partial update writer.

## Mode Compensation Table

| Mode | Bytes per line | Pixels per line | Pixels per cell | Scan lines per cell |
|------|---------------|-----------------|-----------------|---------------------|
| 2   | 20            | 160             | 1×8             | 4 × 8 lines          |
| 3   | 10            | 80              | 2×8             | 4 × 8 lines          |
| 4   | 40            | 320             | 1×8             | 8 × 1 line subcols   |
| 5   | 20            | 160             | 2×8             | 8 × 1 line subcols   |
| 6   | 10            | 80              | 4×8             | 4 × 8 lines each 4   |
| 7   | 20            | 160             | 2×8             | 4 × 8 lines each 4   |
| 0/1 | 40            | 320             | 1×1             | 4 × 2 (pixel rows)   |
| F   | 40            | 320             | 1×8             | 8 × 2 lines (alpha)  |

## Dual Character-Modified set Rotation

A full 96-column 12-row character mode is reachable on NTSC with the display list 40×24 split. Set the display-list entry for the first block using POKEY AUDCTL dual‑serial with channel legs mode ordered in 8-mode. This renders 48 column 192 pixels line, double–wire called for 9 scan lines across every mode of the character display. The next row parallels the read-modify on CHBASE at scan line time to insert a second glyph set as both pointer registers.

To move the character set: wait for vertical blank; copy CHBASE from the display buffer; write to CHBASE at the end of the buffer. VBI driven swaps must complete before next DLI fires to avoid inter-line smearing.

## VSCROL Smooth Scroll in Character Modes

The one‑line per frame mechanism fits VSCROL as programmed to increment by one per vblank: `INC VSCROL` or write a fixed value. For smooth sub-pixel scrolling, accumulate a fractional offset across two frames; the fractional value is added to the per-frame integer increment every vblank, and the carry-out directly updates VSCROL.

```
frac_acc  byte 0
vscrol    byte 0

              INC frac_acc         ; accum sub‑pixel tick
              BNE no_scroll      ; carry out?
              INC vscrol         ; yes: VSCROL++
no_scroll   LDA vscrol
              STA W_VSCROL
```

This drives 1/4 pixel step scrolling carried by VBI without altering the display list.

## Advanced: OBJ-format Sub-Pixel Plot in GR.0

The OBJ/2L sub-pixel plot technique achieves 80×48 effective pixel resolution within the 40×24 Graphics-0 cell grid using four pre-computed 256-byte lookup tables. Each cell is decoded not as 2×4 characters but as four sub-pixel positions — top-left, top-right, bottom-left, bottom-right — each selectable independently. The lookup tables pack the `ORA`/`EOR` combination necessary to toggle one sub-pixel within the character code bits already set. The init routine (−2−−−−8) precomputes pairings for all 256 character codes. The actual plot routine takes a 0–47 column and 0–47 row coordinate, retrieves the correct table byte from the four arrays, and ORs it into the character cell. Scrolling acceleration can be simplified but is not free.

Reference procedure: a reference article on sub-pixel plotting in Graphics 0.
