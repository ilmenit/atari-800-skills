---
name: atari8bit-software-sprites
description: >-
  Atari XL/XE software sprite engines for bitmap and character playfields:
  save/restore buffers, XOR sprites, pre-shift tables, character-sprite
  cells, dirty rectangles, and constant-time sprite collision tests.
---

# Software Sprites

> **Scope:** CPU-rendered sprites in ANTIC bitmap or character playfields.
> **Do not use for:** Hardware player/missile setup; use `graphics/pm-graphics.md`.

## Quick-Lookup

| Need | See |
|---|---|
| Engine choices | §1 |
| Bitmap masked sprite loop | §2 |
| XOR sprite loop | §3 |
| Character-cell sprites | §4 |
| Dirty restore buffers | §5 |
| Sprite-vs-sprite collision | §6 |

## §1 Engine Choices

| Technique | Memory | Speed | Best use |
|---|---:|---:|---|
| Masked bitmap sprite | shape + mask or mask LUT | Medium | Sprites over non-destructive backgrounds |
| XOR sprite | one shifted buffer per active sprite | Fast | Single-color effects where XOR artifacts are acceptable |
| Save/restore bitmap sprite | background save buffer per sprite | Fast with RAM | Arcade sprites over mutable backgrounds |
| Character-cell sprite | spare chars + DLI CHBASE rows | Very fast after setup | Tile games and narrow playfields |
| Hardware P/M overlay | PMG memory | Fastest, limited width/count | Bullets, player, highlights, masks |

The usual game loop is:

1. Restore old sprite footprints from last frame.
2. Run AI/input and update sprite positions.
3. Draw visible sprites into the hidden or active playfield.
4. Swap display buffers or wait for VBI before showing the updated buffer.

## §2 Bitmap Masked Sprite Loop

Use one extra destination byte when the X coordinate is not byte-aligned. For 2-bit pixels, four pixels live in one byte, so `x & 3` selects a 0/2/4/6-bit shift. Precompute shift tables rather than rotating the shape every frame.

```asm
; X = source byte, returns shifted high/low contribution from tables
ShiftRight2H  .res 256
ShiftRight2L  .res 256
ShiftRight4H  .res 256
ShiftRight4L  .res 256
ShiftRight6H  .res 256
ShiftRight6L  .res 256

; For each touched byte:
;   dst = (dst & mask_from_shape) | pixels_from_shape
draw_masked_byte
        ldx   shape_byte
        lda   (screen_ptr),y
        and   mask_table,x
        ora   pixel_table,x
        sta   (screen_ptr),y
        rts
```

For multicolor modes, build `mask_table` so transparent pixels keep the destination bits and opaque pixels clear the destination before OR-ing the sprite color bits.

## §3 XOR Sprite Loop

XOR sprites are compact because drawing the same shifted image twice erases it. Keep two buffers: previous shifted shape and current shifted shape. Each frame XORs both footprints into the screen, then swaps the buffer selector.

```asm
; Erase old and draw new with the same EOR primitive.
eor_span
        ldy   #sprite_bytes-1
?loop   lda   (sprite_ptr),y
        eor   (screen_ptr),y
        sta   (screen_ptr),y
        dey
        bpl   ?loop
        rts
```

This is excellent for monochrome or deliberately stylized sprites. It is a poor fit for opaque multicolor arcade sprites because overlap and background colors invert.

## §4 Character-Cell Sprites

Character sprites use spare character codes as movable sprite cells. A 12x21 pixel sprite in ANTIC 4/5 can be represented as a 2x4 character block with per-row charset changes.

Pattern:

- Reserve ordinary playfield chars for the map, then reserve a range for sprite cells.
- For each active sprite, write the sprite cell codes into the character map.
- Update the corresponding glyph bytes in one or more custom character sets.
- Use DLI to change `CHBASE` per character row when more sprite glyph variants are needed than one 1 KB character set can hold.

```asm
; 2x2 cell stamp, preserving bit 7 if inverse/video flags live there.
stamp_2x2
        lda   (screen_ptr),y
        and   #$80
        ora   sprite_char0
        sta   (screen_ptr),y
        iny
        lda   (screen_ptr),y
        and   #$80
        ora   sprite_char1
        sta   (screen_ptr),y
        ldy   #playfield_width
        lda   sprite_char2
        sta   (screen_ptr),y
        iny
        lda   sprite_char3
        sta   (screen_ptr),y
        rts
```

Keep each group of sprite character codes inside a page-friendly block. Avoid using character `$7F` when the character-set base would make its glyph overlap CPU vectors at `$FFF8-$FFFF`.

## §5 Dirty Restore Buffers

For opaque bitmap sprites over mutable backgrounds, save the exact screen bytes under each sprite before drawing. On the next frame, restore only those bytes, then draw the new sprite position.

```asm
save_footprint
        ldy   #sprite_bytes-1
?loop   lda   (screen_ptr),y
        sta   (save_ptr),y
        dey
        bpl   ?loop
        rts

restore_footprint
        ldy   #sprite_bytes-1
?loop   lda   (save_ptr),y
        sta   (screen_ptr),y
        dey
        bpl   ?loop
        rts
```

Two screen buffers plus one clean background buffer are a strong layout for games: restore the hidden buffer from the clean background, draw sprites there, then switch display lists during VBI.

## §6 Constant-Time Sprite Collision

Pixel-perfect collision is expensive. Many arcade engines use bounding boxes centered on each sprite because the cost is independent of sprite bitmap size.

```asm
; A = abs(pos_x[y] - pos_x[x]); compare with calibrated width threshold.
abs_dx
        lda   sprite_x,y
        sec
        sbc   sprite_x,x
        bpl   ?positive
        eor   #$ff
        clc
        adc   #1
?positive
        cmp   #collision_width
        rts
```

Run this before drawing if collision response affects animation state; run it after movement if collision should reflect final frame positions.

## Source Notes

Patterns summarized from the local MADS sprite examples under `examples/sprites`: bitmap save/restore engines, XOR bitmap/character engines, character-cell engines, and P/M multiplex examples. The patterns above are written as standalone 6502/Atari XL/XE guidance.
