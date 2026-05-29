# Rasterizer

## 17.5 Span-Buffer Rasterizer

Vertices in screen space (BUF_SCR_X, BUF_SCR_Y). Walk left and right edges per scanline,
store span edges in SPAN_XL[y] / SPAN_XR[y], then fill interior.

### WalkEdge (Bresenham edge walk)

```asm
WalkEdge
        cmp    #$00
        beq    @done
        sta    err
        lda    x_l
        sta    cur_x
        ldy    y_top

@next   tya
        sta    SPAN_XL,y
        dey
        bpl    @line_ok
        rts                     ; off bottom

@line_ok
        sec
        lda    cur_x
        sbc    x_r
        bcs    @pos
        eor    #$FF
        clc
        adc    #$01
@pos    sta    SPAN_XR,y
        sec
        lda    cur_x
        sbc    x_r_frac
        sta    cur_x
        bcc    @borrow
        dec    err
        bne    @next
        rts
@borrow inc    err
        bne    @next
```

### FillSpans (nybble-aware, GTIA 9++ — 2 pixels per byte)

```asm
FillSpans
        tya
        tax
        lda    SPAN_XL,x        ; left pixel coords
        ldx    SPAN_XR,x
        cpx    #$00
        beq    @done

        and    #$01             ; left on odd-byte boundary?
        beq    @full1
        lda    (dst_ptr),y      ; preserve high nibble
        sta    (dst_ptr),y
        inc    SPAN_XL,y

@full1  lda    SPAN_XL,y
        ldx    SPAN_XR,y
@flp    sta    (dst_ptr),y
        iny
        cpy    SPAN_XR,y
        bne    @flp

        lda    SPAN_XR,y
        and    #$01
        bne    @done            ; already even
        sec
        lda    SPAN_XR,y
        sbc    #$01
        sta    (dst_ptr),y       ; preserve low nibble

@done   rts
```

> Keep SPAN buffer within a single 256-byte page to avoid DEY/BPL page-cross penalties.

---
