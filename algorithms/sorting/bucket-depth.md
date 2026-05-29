# Bucket Depth

## 18.3 Bucket Sort — 3D Depth Order (TORUS3D preferred)

TORUS3D uses an 8-way bucket sort for its 50–96 visible quads. Depth keys are
0–255 unsigned bytes — index = depth >> 3 into 8 buckets. Zero comparisons.

```asm
SortVisible
        ldx    #$00
        lda    #$00
        sta    bkt_0..bkt_7

@fill   lda    BUF_DEPTH,x
        tay
        lsr                   ; depth >> 3
        lsr
        lsr
        tay
        lda    bkt_head,y     ; current tail
        sta    next,x
        lda    vis_quad,x
        sta    bkt_head,y     ; push into bucket
        inx
        cpx    vis_count
        bne    @fill

        ; Drain bucket 7 (far) to bucket 0 (near)
        ldy    #$07
@bucket lda    bkt_head,y
        beq    @next
        ; follow linked list into sorted output array
@next   dey
        bpl    @bucket
```

| | |
|---|---|
| Buckets | 8 (depth >> 3) |
| Bucket storage | BKT_HEAD[8] ZP |
| Link storage | NXT_PTR[96] |
| Cycles | ~500 (96 verts, single pass) |
| Comparisons | 0 |

---
