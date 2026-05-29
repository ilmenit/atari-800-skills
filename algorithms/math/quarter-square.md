# Quarter Square

## 10.5 QS (Quarter-Square) Multiply (TORUS3D pattern)

The identity `(a+b)^2 - (a-b)^2 = 4ab` lets a square table replace shift-add
multiplication. For an exact 8×8→16 result, store `floor(n*n/4)` for
`n=0..510`, then subtract the `abs(a-b)` entry from the `a+b` entry. This is
the same table shape described in §10.1.

```asm
; unsigned 8x8 -> 16
; in:  A=a, X=b
; out: prod_lo/prod_hi
; tables: qs_lo/qs_hi for floor(n*n/4), n=0..510
; clobbers: A, X, Y, C
qs_mul8
        sta a_save
        stx b_save
        clc
        adc b_save
        tax                    ; X = a+b

        sec
        lda a_save
        sbc b_save
        bcs @diff_ok
        eor #$ff
        adc #1                 ; A = abs(a-b)
@diff_ok
        tay

        sec
        lda qs_lo,x
        sbc qs_lo,y
        sta prod_lo
        lda qs_hi,x
        sbc qs_hi,y
        sta prod_hi
        rts

a_save  .byte 0
b_save  .byte 0
prod_lo .byte 0
prod_hi .byte 0
```

For signed inputs, save the sign bit with `a eor b`, convert both inputs to
absolute values, call the unsigned core, then two's-complement the 16-bit
product if the saved sign bit has bit 7 set.

---
