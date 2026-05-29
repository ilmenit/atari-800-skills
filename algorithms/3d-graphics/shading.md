# Shading

## 17.4 Per-Vertex Shading (NdotL)

### Full dot-product (~180 cycles)

```asm
XformShadeOne
        lda    rnx
        ldx    lx
        jsr    SMult8           ; n.x * L.x
        sta    dot

        lda    rny
        ldx    ly
        jsr    SMult8           ; n.y * L.y
        clc
        adc    dot
        sta    dot

        lda    rnz
        ldx    lz
        jsr    SMult8           ; n.z * L.z
        clc
        adc    dot             ; dot = n.L  (full 3x SMult8)

        ; >> 7 via 7 rounds of ASL/ROL
        asl    dot
        rol    A                ; /2
        asl    dot
        rol    A                ; /4
        asl    dot
        rol    A                ; /8
        asl    dot
        rol    A                ; /16
        asl    dot
        rol    A                ; /32
        asl    dot
        rol    A                ; /64
        asl    dot
        rol    A                ; /128  => >>7 complete

        clc
        adc    #$80
        and    #$0F             ; GTIA 9: 15 shade levels
        tax
        lda    SHADE_TAB,x
```

### Equal-light fast path (~60 cycles)

When `lx == ly` no multiply is needed at all:

```
n.L = (rnx + rny + rnz) >> 7 + 128
```

```asm
XformShadeEqualLight
        lda    rnx
        clc
        adc    rny
        clc
        adc    rnz              ; sum replaces 3x SMult8
        tax
        lda    SHADE_SUM_TAB,x   ; direct LUT
```

| Path | Condition | Cycles |
|---|---|---|
| Full dot product | lx != ly | ~180 |
| Equal-light fast path | lx == ly | ~60 |

---

## 17.6 Gouraud Shade Interpolation

WalkEdgeGouraud is identical to WalkEdge, plus shade accumulator `zp_gs_err`.
SHADE_L[y] / SHADE_R[y] hold interpolated shade per scanline.

Dual-path FillSpansGouraud: when `SHADE_L[y] == SHADE_R[y]` → flat fill; when different,
pixel-by-pixel shade Bresenham:

```
shade_cur[y+1] = shade_cur[y] + shade_step
fractional remainder carried in shade_frac ZP accumulator
```

| Path | Cost/pixel | Trigger |
|---|---|---|
| Flat fill | 1 byte write | SHADE_L == SHADE_R |
| Shade Bresenham | 1 add + 1 write | edges differ |

---
