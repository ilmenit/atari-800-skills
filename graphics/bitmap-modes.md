---
name: atari8bit-bitmap-modes
description: >-
  Atari ANTIC and GTIA bitmap graphics modes: hires and multicolor screen memory,
  line addressing, 240-line modes, GTIA overlays, plotting, and custom layouts.
---

# Bitmap Graphics Modes

## Bitmap Architecture

ANTIC bitmap modes map the screen memory as a raw scan-line buffer with no decode step between address order and pixel position. Graphics 8 is ANTIC F: 320 pixels per line, 8 one-bit pixels per byte, 40 bytes per scan line. Graphics 15 is ANTIC E: 160 pixels per line, four 2-bit pixels per byte, also 40 bytes per scan line. Graphics 9 through 11 are GTIA interpretations of ANTIC F bytes. Graphics 12–14 (ANTIC A, B, C) are the 160-pixel wide double-line modes.

Writes to bitmapped picture memory go direct — no read‑modify‑write cycle, no character cell indirection — because the write address maps directly to the scan line. The programmer writes the numeric colour directly to the byte address: zero clears the pixel, non-zero sets the pixel. Standard palette values written to the high nibble path: $0 is background, $1–$F are the 15 foreground colours.

The picture memory size for each mode:

```
Graphics 8    ANTIC F, 320 × 192, 1 bpp = 7 680 bytes ($1E00)
Graphics 15   ANTIC E, 160 × 192, 2 bpp = 7 680 bytes ($1E00)
Graphics 9–11 GTIA over ANTIC F bytes; same memory size as GR.8
Graphics 12–14 160-wide double-line modes; memory depends on visible rows
```

Using 130XE extended RAM for extra screens is practical only when the display
buffer is mapped into the active `$4000-$7FFF` window before ANTIC fetches it.

## Hires Screen Layout and Addressing

Graphics 8 (ANTIC F) and Graphics 15 (ANTIC E) use scan-line sequential addressing. The screen width is 40 bytes per line. The starting address of line L bytes down is:

```
screen_addr = screen_base + (L × 40)
```

For game code, precompute line-address tables instead of multiplying by 40 during drawing:

```asm
line_lo  .byte <(screen+0*40), <(screen+1*40), <(screen+2*40)
line_hi  .byte >(screen+0*40), >(screen+1*40), >(screen+2*40)

screen_ptr_for_y
        ldy   y_pos
        lda   line_lo,y
        sta   screen_ptr
        lda   line_hi,y
        sta   screen_ptr+1
        rts
```

## Bitmap Plotting Primitives

For 2-bit-pixel modes such as Graphics 15, four pixels share one byte. Split X
into byte offset and pixel-in-byte:

```asm
; byte_x = x / 4, pixel = x & 3
        lda   x_pos
        lsr   a
        lsr   a
        tay

        lda   x_pos
        and   #3
        tax
```

Use masks for partial-byte writes at the left and right edges of spans:

```asm
left_mask
        .byte %00000000, %11000000, %11110000, %11111100
right_mask
        .byte %00111111, %00001111, %00000011, %00000000
pixel_mask
        .byte %00111111, %11001111, %11110011, %11111100

; color2 contains the 2-bit color replicated into the selected pixel position.
put_pixel_2bpp
        lda   (screen_ptr),y
        and   pixel_mask,x
        ora   color2,x
        sta   (screen_ptr),y
        rts
```

Table-driven Graphics 15 plot, 160x192:

```asm
COLOR = 1
adr   = $80

; in: Y = y, X = x
plot_g15
        lda   lnadl,y
        sta   adr
        lda   lnadh,y
        sta   adr+1
        ldy   byteoff,x
        lda   (adr),y
        and   bytemask,x
        ora   bytepxl,x
        sta   (adr),y
        rts

lnadl    :192 .byte <(screen+40*#)
lnadh    :192 .byte >(screen+40*#)
byteoff  :160 .byte #/4
bytemask :160 .byte ~(%11 << (6 - ((# & %11) * 2)))
bytepxl  :160 .byte COLOR << (6 - ((# & %11) * 2))
```

Graphics 8 hires plot, 320x192. Pass the high X bit in carry and low 8 bits in
X; this avoids a 16-bit X coordinate in memory:

```asm
COLOR = 1
adr   = $80

; in: Y = y, X = x low byte, C = x bit 8
plot_g8
        lda   lnadl,y
        sta   adr
        lda   lnadh,y
        sta   adr+1
        bcs   @x1xx
@x0xx   ldy   byteoff,x
        lda   (adr),y
        and   bytemask,x
        ora   bytepxl,x
        sta   (adr),y
        rts
@x1xx   ldy   byteoff+$100,x
        lda   (adr),y
        and   bytemask,x
        ora   bytepxl,x
        sta   (adr),y
        rts

lnadl    :192 .byte <(screen+40*#)
lnadh    :192 .byte >(screen+40*#)
byteoff  :320 .byte #/8
bytemask :256 .byte ~(1 << (7 - (# & %111)))
bytepxl  :256 .byte COLOR << (7 - (# & %111))
```

Horizontal lines are fastest when the middle bytes are full-byte fills and only the edge bytes are masked. If both endpoints land in the same byte, combine both edge masks before writing.

For extended RAM or cold-start video, initialise the display before the first frame is fetched. A true 240-line hires/GTIA display must disable playfield DMA before the end of scan line 247 and re-enable it at scan line 8. Keep the display list free of `JVB`; the VBI resets `DLPTR/SDLSTL` for the next frame.

Display-list height choices:

| Mode | 240-line form |
|---|---|
| ANTIC 2 text/hires character rows | 30 rows * 8 scan lines |
| ANTIC 3 text rows | 24 rows * 10 scan lines |
| ANTIC F / Graphics 8 / GTIA 9-11 | 240 one-scanline mode bytes |

The full initialisation pattern is:

```
init_240lines:
    SEI                     ; block IRQ during setup
    LDA #$00
    STA NMIEN                ; disable NMI (DLI+VBL)
    STA DMACTL               ; disable screen DMA — blank screen now

    ; --- set display list (no JVB; VBI sets DLPTR each frame) ---
    LDA #<dlist240
    STA SDLSTL               ; $0230
    LDA #>dlist240
    STA SDLSTH

    ; --- install DLI at line 247 ---
    LDA #<dli_247
    STA VDSLST               ; $200 — DLI vector
    LDA #>dli_247
    STA VDSLST+1
    LDA #%11000000          ; enable DLI + VBL
    STA NMIEN               ; $D40E

    ; --- install deferred VBI at $0222 ---
    LDA #<vbi_deferred
    STA $0222               ; VVBLKD (deferred)
    LDA #>vbi_deferred
    STA $0223

    CLI                     ; re-enable IRQ
    RTS

    ; --- display list: 30 ANTIC 2 rows = 240 scan lines, no JVB ---
dlist240:
    .byte $02 | $40          ; LMS
    .word screen
    :28  .byte $02
    .byte $02 | $80          ; DLI on final 8-scanline row

; --- DLI: fires at the top of scan line 248 (last drawn is 247) ---
dli_247:
    PHA
    STA WSYNC               ; hold at end of line 247
    LDA #$00                 ; DMACTL bits 0-1 cleared = screen DMA off
    STA DMACTL
    PLA
    RTI

; --- deferred VBI: re-enables DMA before scan line 8 ---
vbi_deferred:
    LDX VCOUNT
    CPX #4                   ; scan line 8 = VCOUNT = 4
    BNE vbi_deferred
    LDA #%00100010           ; display-list DMA + normal playfield DMA
    STA DMACTL
    RTS                      ; returns through JEXITVB
```


## 240-Line Hi-Res Trick

ANTIC can draw only 239 full scan lines in hires before violating vertical hold. The VBLANK interval starts at scan line 248. Hires raster positions 8–247 cover 240 scan lines, but including JVB reach from the display list forces the ANTIC engine to halt at the final line and sync. Drawing the full 240 lines in GR.8 without a blank line at the bottom breaks vertical hold.

The workaround is a DLI-gated disable on line 247, a deferred-frame VBI
re-enable before line 8, and no JVB instruction in the display list itself.

### Display List Notes

A conventional hires/GTIA display list with JVB can safely use 239 scan lines
and leave one blank line at the bottom. For true 240 lines, remove JVB and use
the DLI/VBI DMA gate above. For Graphics 8/GTIA 9-11, use ANTIC `$0F` bytes
instead of `$02` rows and place the DLI bit on the last visible mode byte.

### DLI (line 247, disables DMA)

```
dlint:
    PHA
    LDA #%00000000           ; WSYNC
    STA WSYNC
    LDA #%00000000           ; disable screen DMA (DMACTL bits 0–1 = 0)
    STA DMACTL
    PLA
    RTI
```

VBI (deferred, re-enables DMA before line 8):

```
vbint:
    LDA VCOUNT
    CMP #4                   ; wait until scan line 4 (line 8 ÷ 2)
    BNE vbint

    LDA #%00100010           ; display-list DMA + normal playfield DMA
    STA DMACTL
    RTS                      ; returns through JEXITVB → OS sets DMACTL shadow
```

Keep the OS shadow `SDMCTL/DMACTLS ($022F)` with screen DMA disabled while using this trick. The OS VBI copies shadows to ANTIC before deferred VBI runs; if the shadow already enables playfield DMA before scan line 8, vertical sync can break again. The deferred VBI should wait for `VCOUNT=4` (physical scan line 8) and then write hardware `DMACTL ($D400)` to re-enable display DMA for the visible area.

## Custom Video Modes

### Narrow Display (32-byte row, ZX Spectrum layout)

Setting ANTIC mode `$4F` or `$70` with 32-byte rows produces a narrow playfield
layout suitable for ZX Spectrum-style screen conversions. Swap `CHBASE` every
eight scan lines via DLI and cycle through three character sets or screen
regions so the ANTIC row order matches the source layout. Keep each target
charset on a 1 KB boundary and update the hardware `CHBASE` register directly
inside the DLI.

### Acorn Electron / 6845 Mode Emulation

By selecting a 32-byte wide display list with DLI‑driven character swap, the programmer recreates the 6845 text/graphics mode 4 — 80×32 -character display in a foreign pixel encoding. DLI routine redirects the character base register (`CHBAS`) at each line boundary to another character set compiled in alternate font data member. This particular technique was used in demos that ran both a text overlay and a simultaneous hires sprite layer — the lower region occupied a high-res data region (base flipped by DLI) while the upper half ran character mode simultaneously zero.

## VSCROL and HSCROL in Bitmap Modes

HSCROL operates identically in bitmap and character modes.

Writes to HSCROL take effect **after** the next WSYNC. Any WSYNC write after HSCROL is redundant and may cause tearing.

```
LDA #4
STA HSCROL      ; fine scroll by 4 pixels
STA WSYNC       ; may be omitted; HSCROL auto-syncs at line start
```

VSCROL behaves similarly: a write increments the decrement count at the start of the next line. The DMA engine compensates for the scroll offset by pulling the DMA fetch address from the start of the picture memory minus the VSCROL*fine_rate feedforward.

Continuous scrolling: change HSCROL/VSCROL every VBI. The VBI-deferred write ensures the display is stable before the scan-line engine reads the new values.

## Bitmap-to-Text Overlay Pattern

Combine Graphics 8 picture memory with the OS character bitmap ROM set at `$E000–$E3FF`. Write text glyphs directly into the picture memory using the character set code value — this maps each glyph row onto the pixel row at the same address, stacking character overlay on top of the bitmap RGB. The colour for each glyph pixel is encoded in the attribute byte set in the character set area; this overlay works only when the programmer has defined a one-glance lookup table from character code → pixel pairs to screen byte. Once the overlay table is pre-initialized, text blitting becomes a `STA (screen_pointer), Y` operation at the cost of copying about 1,024 bytes of character‑set data direct from overlay font table to screen pixel plane.
