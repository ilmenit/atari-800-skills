# Bitmap Graphics Modes

## Bitmap Architecture

ANTIC bitmap modes map the screen memory as a raw scan-line buffer with no decode step between address order and pixel position. Graphics 8 (ANTIC E) offers the most compact form: 320 pixels per line, 8 pixels per byte, pixel value held in bits 0–3, the high nibble unused. Graphics 9 through 11 overlay ANTIC F with the graphics processor, allowing per-pixel colour changes in GTIA mode. Graphics 12–14 (ANTIC A, B, C) are the 160‑pixel wide double-line modes, each pixel carrying one colour resolution bit per pixel.

Writes to bitmapped picture memory go direct — no read‑modify‑write cycle, no character cell indirection — because the write address maps directly to the scan line. The programmer writes the numeric colour directly to the byte address: zero clears the pixel, non-zero sets the pixel. Standard palette values written to the high nibble path: $0 is background, $1–$F are the 15 foreground colours.

The picture memory size for each mode:

```
Graphics 8    320 × 192 = 8 192 bytes  ($2000)  — single page, standard
Graphics 9–11 320 × N    = 16 384 bytes ($4000)  — GTIA 9 overlay each pixel colour (reads from COLBK / COLPFx per scan)
Graphics 12    160 × 192 = 7 680 bytes  ($1E00)
Graphics 13    160 × 192 = 7 680 bytes
Graphics 14    160 × 192 = 7 680 bytes
```

Playing against 230 XE extended RAM is practical only with extra screen memory set to the high bank.

## Hires Screen Layout and Addressing

Graphics 8 (ANTIC E) uses scan-line sequential addressing. The screen width is 40 bytes per line (320 pixels ÷ 8). The starting address of line L bytes down is:

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

For 2-bit-pixel modes, four pixels share one byte. Split X into byte offset and pixel-in-byte:

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

Horizontal lines are fastest when the middle bytes are full-byte fills and only the edge bytes are masked. If both endpoints land in the same byte, combine both edge masks before writing.

For extended RAM or cold-start video, initialise the display before the first frame is fetched. The 240-line cold-start sequence must disable screen DMA, install the display list without JVB, point DLI at the line-247 shutdown, set deferred VBI at `$0222`, then re-enable DMA only in the deferred slot after VBLANK has established. The full initialisation is:

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

; --- display list: 99×8 + 99×8 + 38×8 scan lines, no JVB ---
dlist240:
    .byte $0E | $40          ; LMS
    .word screen_a
    :99  .byte $0E           ; 792 pixels = 99 scan lines
    .byte $0E | $40          ; LMS
    .word screen_b
    :99  .byte $0E
    .byte $0E | $40          ; LMS
    .word screen_c
    :38  .byte $0E           ; 38 scan lines → ends at line 247

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
    LDA #%00100000           ; bits 5-7=0, bits 0-1=0 : single-res GR8+DMA
    STA DMACTL
    RTS                      ; returns through JEXITVB
```


## 240-Line Hi-Res Trick

ANTIC can draw only 239 full scan lines in hires before violating vertical hold. The VBLANK interval starts at scan line 248. Hires raster positions 8–247 cover 240 scan lines, but including JVB reach from the display list forces the ANTIC engine to halt at the final line and sync. Drawing the full 240 lines in GR.8 without a blank line at the bottom breaks vertical hold.

The workaround — documented in a reference article on the 240-line hires mode — is a DLI‑gated disable on line 247, a deferred-frame VBI re‑enable before line 8, and no JVB instruction in the display list itself.

### Display List (240 lines, GR.8)

```
dlist:
    .byte $0E | $40          ; LMS
    .word screen_part1
    :99  .byte $0E           ; 99 × 8 = 792 pixels = 99 scan lines

    .byte $0E | $40          ; LMS
    .word screen_part2
    :99  .byte $0E

    .byte $0E | $40          ; LMS
    .word screen_part3
    :38  .byte $0E           ; 38 × 8 = 304 pixels = 38 scan lines  →  line 247

    ; JVB REMOVED — VBI sets DLPTR directly
```

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

    LDA #%00100000           ; screen DMA enabled
    STA DMACTL
    RTS                      ; returns through JEXITVB → OS sets DMACTL shadow
```

DMACTL shadow — the OS VBI writes the offline deferred write to DMACTLS (`$22F`) rather than to DMACTL hardware. The undocumented shadow `$22F` behaves identically to `$D400`: set both bits 4–7 (fine scroll) clear bits 0–3 (no effect); the shadow register is write‑equivalent so hardware is also reset to next screen DMA when the VBI writes the shadow.

## Custom Video Modes

### Narrow Display (32-byte row, ZX Spectrum layout)

Setting ANTIC mode `$4F` or $70 with a repeat of 64 produces a sequence of 64 display rows, each row 32 bytes wide. The programmer swaps the character base pointer every eight rows via DLI, cycling through three separate ANTIC screens in VRAM banked area. This yields a full ZX Spectrum‑compatible physical screen layout: the screen set looks original in layout and output. The DLI cycles three times per frame, swapping CHSBase on each pass to point to a different quadrant of banked display memory. Details in a reference article on non-standard ANTIC graphics modes.

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
