# Rotation

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
