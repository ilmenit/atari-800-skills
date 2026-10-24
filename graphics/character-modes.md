---
name: atari8bit-character-modes
description: >-
  Atari ANTIC character modes, font alignment, CHBASE/CHACTL, screen-code
  attributes, and custom character sets for text and tile rendering.
---

# Character Modes

ANTIC first fetches character names from the playfield, then fetches glyph
rows from the character set. Modes 0 and 1 are blank/jump commands; F is a
bitmap mode. They are not character modes.

## Normal-width mode table

| ANTIC | Columns / bytes per row | Scanlines per row | Logical pixels across | Font bytes / alignment |
|---|---:|---:|---:|---|
| 2 | 40 | 8 | 320 | 1024 / 1024 |
| 3 | 40 | 10 | 320 | 1024 / 1024 |
| 4 | 40 | 8 | 160 | 1024 / 1024 |
| 5 | 40 | 16 | 160 | 1024 / 1024 |
| 6 | 20 | 8 | 160 | 512 / 512 |
| 7 | 20 | 16 | 160 | 512 / 512 |

Narrow/wide playfields change the number of bytes fetched; scrolling can widen
the DMA window. Do not confuse OS GRAPHICS numbers with ANTIC mode nibbles.

## Glyphs and attributes

- Modes 2/3: bits 0–6 select one of 128 eight-byte glyphs. Bit 7 selects the
  inversion/blanking behavior controlled by CHACTL. Mode 3 adds descender rows;
  it is not simply mode 2 with every row stretched.
- Modes 4/5: bits 0–6 select a glyph. Each two-bit pixel selects background,
  PF0, PF1, or PF2; character bit 7 substitutes PF3 for PF2. Mode 5 doubles
  each glyph scanline vertically.
- Modes 6/7: bits 0–5 select one of 64 glyphs; bits 6–7 select foreground
  PF0–PF3. Zero glyph bits show background. Mode 7 doubles rows vertically.

A glyph contains eight consecutive row bytes. Mode-specific pixel decoding
and scanline repetition determine its displayed width/height.

## Font base and character control

`CHBASE ($D409)` is a **one-byte high address**, not a two-byte pointer.
`CHBAS ($02F4)` is its OS shadow. For example, a mode-2 font at `$3000`
requires CHBAS=`$30`; mode 2 ignores CHBASE's lowest two bits for 1K alignment.
A 512-byte font in modes 6/7 uses one additional address bit.

`CHACTL ($D401)` and its OS shadow `CHART ($02F3)` control character attributes:

| Bit | Function |
|---|---|
| 0 | Blank cells whose name bit 7 is set (modes 2/3); software toggles this for blinking |
| 1 | Invert cells whose name bit 7 is set (modes 2/3) |
| 2 | Reflect glyph rows vertically (all character modes) |

CHACTL does not choose CPU OR/AND drawing operations. CPU stores replace RAM
bytes; the rendering routine must implement any masking or merging itself.

## Custom-font workflow

1. Reserve a correctly aligned RAM block that does not overlap DOS, display
   lists, screen memory, PMG, or active code.
2. Copy/generate the full font before exposing it to DMA. ROM data cannot be
   modified in place; RAM under OS ROM is unavailable until banking changes.
3. With OS VBI active, write CHBAS during setup. For an immediate raster change
   in a DLI, write CHBASE and arrange the shadow value for subsequent frames.
4. Restore the previous font shadow when returning to the OS. Changing fonts
   and rewriting glyphs in place need synchronization if tearing matters.

Screen names are [screen codes, not ATASCII](../system/screen.md#81-atascii-screen-code-table).
For tile/sprite composition, see [software sprites](software-sprites.md).

Source: [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §§4.4 and 14.6.
