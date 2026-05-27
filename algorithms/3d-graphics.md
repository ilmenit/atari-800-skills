---
name: atari8bit-3d-graphics
description: >-
  Atari 8-bit 3D-rendering idioms — rotation matrix + look-up tables, perspective
  projection, per-vertex NdotL lighting, span-buffer rasterizer, Gouraud shade
  interpolation, object-space and backface culling, bucket sort depth-order.
---

# 17 — 3D Graphics

> **Scope:** Rotation matrix, LUT build, projection, lighting, rasterizer, culling, sort
> **Key items:** SMult8/UMult8; double-fill 8x256x2B; RECIP_z; SHADE_TAB; WalkEdge+FILL; 8-bucket sort

## Quick-lookup

| Need | See § |
|---|---|
| Rotation matrix (Ry-Rx, Q3.9, 4x SMult8) | §17.1 |
| Double-fill rotation LUT (8x256x2B) | §17.2 |
| Perspective projection (RECIP_z, ortho-X / perspective-Y) | §17.3 |
| Per-vertex NdotL (equal-light fast path vs full dot product) | §17.4 |
| Span-buffer rasterizer (WalkEdge + FillSpans) | §17.5 |
| Gouraud shade interpolation (WalkEdgeGouraud) | §17.6 |
| Object-space culling (pre-transform dot product reject) | §17.7 |
| Backface culling + depth bucket sort (TORUS3D 8-way) | §17.8 |

---

## 17.1 Rotation Matrix

All vertex coordinates and matrix elements are **signed Q3.9 bytes** — value x 512 = integer, >>9 divides by 2.
Q3.9 range: −4.0 … +3.998, suitable for torus major-radius 50 / minor-radius 24 (clamped to +/-127).
Ry and Rx are computed fresh each frame from pitch thetaX and yaw thetaY.

```
Ry = [ cy   0   -sy ]        Rx = [ cx   sx   0 ]
     [ 0    1    0  ]             [ -sx  cx   0 ]
     [ sy   0    cy ]             [  0   0   1 ]

Ry-Rx = [ cy*cx     cy*sx     -sy   ]
        [ -sx        cx         0    ]
        [ sy*cx     sy*sx      cy   ]
```

All products use SMult8 then >>7; the Q-factor restores the unit range.

### CalcMatrix ASM (~210 cycles)

```asm
; Inputs:  angleX ($D0), angleY ($D2) as Q7.9 angle indexes
; Outputs: rotM[9] at ZP $D4..$DC — signed bytes

CalcMatrix
        ldx    angleY
        lda    COS_Y,x          ; cy
        sta    mat_m00
        ldx    angleX
        lda    SIN_Y,x          ; sx
        sta    tmp1
        lda    SIN_X,x          ; sx  (negated to -sx below)
        eor    #$FF
        clc
        adc    #$00
        sta    tmp2

        lda    mat_m00          ; cy
        ldx    tmp2             ; cx
        jsr    SMult8           ; cy*cx
        sta    mat_m00

        lda    COS_X,x
        sta    mat_m01

        lda    SIN_Y,x
        eor    #$FF
        clc
        adc    #$00
        sta    mat_m02          ; -sy

        lda    tmp2
        sta    mat_m10          ; -sx
        lda    COS_X,x
        sta    mat_m11
        lda    #$00
        sta    mat_m12

        lda    SIN_Y,x
        sta    mat_m20
        ldx    tmp2
        jsr    SMult8           ; sy*cx
        sta    mat_m20
        rts
```

> D flag must be clear at call sites; SMult8/SBC sequences are incompatible with decimal mode.

---

## 17.2 Rotation Look-Up Tables

The double-fill technique halves the init cost. Each of 8 ROT_M?? tables has 256 signed-byte entries; each value is written to two consecutive locations.

### BuildOneTable skeleton

```asm
; Writes TABLE[2k] and TABLE[2k+1], advances accumulator by 2xdelta
; Self-modify: patches target address and add-lo/add-hi immediates

BuildOneTable
        ldy    #$00
        sty    offset_store+1
        sty    offset_store2+1

@step   lda    sin_tbl,y
        asl
        adc    step_delta_lo+1
        sta    step_delta_lo+1
        sta    step_delta_hi+1

@st1a   sta    (zp_table_lo),y   ; TABLE[2k]
@st1b   iny
        sta    (zp_table_lo),y   ; TABLE[2k+1]
        dey
        cpy    #$FF
        bne    @step
        rts
```

Max error ±1 unit (~0.29 px); 75% exact. Build once at init, not per frame.

| Table | Size | Use |
|---|---|---|
| ROT_M00..ROT_M22 | 512 B each | signed LUT: matrix element x vertex |
| Combined total | 8 KB | 8 tables x 256 entries x 2 bytes |

---

## 17.3 Perspective Projection

Precompute RECIP_z at init: `RECIP_z[k] = round(FOCAL*256 / (k + CAM_DIST))` for k = 1..255.  
256-byte table; index = zi = rz + CAM_DIST. Clamp zi to 1..255.

**Orthographic in X, perspective in Y** (classic 2.5D trick — saves one multiply):

```
scrX = CX +/- |rx|                      (no RECIP)
scrY = CY - (ry * RECIP_z[zi]) >> 8     (perspective in Y)
```

```asm
project_vertex_y
        lda    rz
        clc
        adc    CAM_DIST        ; zi
        tax                    ; X = zi

        lda    ry
        bpl    @ry_pos
        eor    #$FF
        clc
        adc    #$00
        sta    ry_abs
        lda    RECIP_Y,x
        jsr    UMult8
        lsr
        lsr
        sec
        lda    CY
        sbc    A
        sta    scrY
        rts

@ry_pos sta    ry_abs
        lda    RECIP_Y,x
        jsr    UMult8
        lsr
        lsr
        sec
        lda    CY
        sbc    A
        sta    scrY
```

> zi guard: clamp to 1..255 before lookup; zi = 0 gives undefined RECIP.

---

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

## See also

- `algorithms/math.md` — SMult8/UMult8 quarter-square multiply and fast sqrt.
- `algorithms/sorting.md` — depth sort alternatives and bucket-sort patterns.
