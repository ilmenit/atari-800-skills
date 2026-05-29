# Culling Depth

## 17.7 Object-Space Culling

Rotate face normal into camera Z via 3 LUT lookups (no multiply).
Reject before any per-vertex transform:

```asm
ObjectCull
        ldx    #$00
        lda    #$00
        sta    vis_count

@face   ldy    fn_lo,x            ; fnx index into ROT_M20
        lda    ROT_M20,y          ; m20*fnx
        clc
        adc    ROT_M21,y          ; + m21*fny
        clc
        adc    ROT_M22,y          ; + m22*fnz  = dot(N, M[row2])
        bmi    @hide              ; facing away
        cmp    cull_thresh,x
        bcs    @hide              ; too deep
        txa
        ldy    vis_count
        sta    vis_quad_list,y
        iny
        sty    vis_count
@hide   inx
        cpx    #$60               ; 96 quads
        bne    @face
        rts
```

Saves ~43 K cycles/frame by culling 96 -> ~55 verts before projection.

---

## 17.8 Backface Culling + 8-Bucket Depth Sort

### Backface sign test

```
dx0 = right_top.x - left_top.x
dy1 = left_bot.y  - left_top.y
cross = dx0 * dy1 - dx1 * dy0   (screen space)
positive = front-facing; negative = backface
```

### TORUS3D 8-way bucket sort

Depth keys are 0..255 unsigned bytes. No comparisons required — 3 bit shifts give the bucket index.

```asm
SortVisible
        ldx    #$00
        lda    #$00
        sta    bkt_0..bkt_7       ; all heads = 0

@fill   lda    BUF_DEPTH,x
        tay
        lsr
        lsr
        lsr                      ; depth >> 3 -> bucket 0..7
        tay
        lda    bkt_head,y
        sta    next,x
        lda    vis_quad,x
        sta    bkt_head,y         ; push
        inx
        cpx    vis_count
        bne    @fill

        ; Drain: bucket 7 (far) -> bucket 0 (near)
        ldy    #$07
@bucket lda    bkt_head,y
        beq    @next
        ; follow linked list to sorted output
@next   dey
        bpl    @bucket
```

| Sort | N | Use |
|---|---|---|
| Optimal 8-bit | < 200 | ZP LUT + walk |
| Bucket 8-way | 50–200 | TORUS3D preferred; O(N); zero comps |
| Quicksort 16b | any | add median-of-3 pivot guard |
| CombSort | any | gap = 1 last pass; nearly sorted |

See sorting for full Optimal / CombSort / Quicksort listings.

---
