# Projection

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
