# Multiplication

## 10.1 Multiplication

> **Signed-16-bit overflow hazard:** All mul3/mul10/mul96 and Keldon LUT variants wrap at ±256. For signed results beyond ±255, use the 16×16 shift-add loop or the 65816 $4202/$4203 hardware multiplier.
> **BIT-trick signed-mask hazard:** the range-clamp XOR form when HI>=LO produces an off-by-one overflow. Commit the mask form to the specific range being clamped.

### Multiply by 3

```asm
mul3   lda  num
         asl  a                ; A × 2
         sta  result
         lda  num+1
         rol  a                ; carry-propagated high-byte shift
         sta  result+1
         clc
         lda  num
         adc  result
         sta  result
         lda  num+1
         adc  result+1
         sta  result+1              ; result = 3 × num  | 3 cycles
```

### Multiply by 10

```asm
mul10   lda  num
         sta  result
         lda  num+1
         sta  result+1
         asl  result
         rol  result+1             ; result ×=  2
         asl  result
         rol  result+1             ; result ×=  4
         clc
         lda  num
         adc  result
         sta  result
         lda  num+1
         adc  result+1
         sta  result+1
         asl  result
         rol  result+1             ; ×10
```

### Multiply by 96

```asm
; A holds argument [0..95], result in (res+1, res)
         sta  res
         asl
         adc  res
         ror
         ror
         ror
         tax
         and  #%00111111
         sta  res+1
         txa
         ror
         and  #%11100000
         sta  res                 ; res = A × 96   | ~30 cycles
```

### Multiply by 10 — shortform (argument ≤ 95)

```asm
         sta  res
         asl
         adc  res
         ror
         ror
         ror
         tax
         and  #%00111111
         sta  res+1
         txa
         ror
         and  #%11100000
         sta  res                 ; ~30 cycles
```

### 8×8 LUT multiply via 512-byte quarter-square table

The table covers `n = 0..510` and stores `floor(n*n/4)` as low and high byte
pages. The product is:

```
a*b = qs[a+b] - qs[abs(a-b)]
```

Required tables:

```asm
qs_lo  :511 dta l((#*#)/4)
qs_hi  :511 dta h((#*#)/4)
```

The lookup is exact for unsigned 8×8→16 multiplication. Keep both table pages
page-aligned if the hot path uses absolute indexed addressing.

### Smallest 8×8 multiply — 16 bytes, no tables

Use this only when code size matters more than speed. It is repeated addition:
average runtime is roughly 1545 cycles.

```asm
; unsigned 8x8 -> 16, 16 bytes
; in:  X = multiplicand, immediate at multiplier = multiplier byte
; out: A = low byte, Y = high byte
; clobbers: X, C
mult_small
        lda #0
        tay
        inx
@outer  clc
@loop   dex
        beq @done
multiplier = *+1
        adc #0              ; self-modify this operand before call
        bcc @loop
        iny
        bcs @outer
@done   rts
```

### Fast 8×8 multiply — square tables, ~45 cycles average

This variant trades memory for speed. It uses one 511-entry square table and a
256-entry correction table, both split into low/high byte pages. Call
`mult_fast_init` once before the first multiply.

```asm
result    = $04             ; two bytes, result low/high
lmul0     = $06             ; ZP pointer to squaretable1_lsb
lmul1     = $08             ; ZP pointer to squaretable1_msb
prod_low  = $0a

        .align $100
squaretable1_lsb
        :511 dta l((#*#)/4)
        .byte 0
squaretable1_msb
        :511 dta h((#*#)/4)
        .byte 0

        .align $100
squaretable2_lsb
        .byte 0
        :255 dta l((((256-(#+1))*(256-(#+1)))/4)-1)
squaretable2_msb
        .byte 0
        :255 dta h((((256-(#+1))*(256-(#+1)))/4)-1)

; unsigned 8x8 -> 16
; in:  X = multiplier, Y = multiplicand
; out: prod_low = low byte, A = high byte
; clobbers: X, A, C
mult_fast
        stx lmul0
        stx lmul1
        tya
        sec
        sbc lmul0
        tax
        lda (lmul0),y
        bcc @negative_diff
        sbc squaretable1_lsb,x
        sta prod_low
        lda (lmul1),y
        sbc squaretable1_msb,x
        rts
@negative_diff
        sbc squaretable2_lsb,x
        sta prod_low
        lda (lmul1),y
        sbc squaretable2_msb,x
        rts

mult_fast_init
        lda #>squaretable1_lsb
        sta lmul0+1
        lda #>squaretable1_msb
        sta lmul1+1
        rts
```

### 16×16 shift-add loop

Use this when the operands or result can exceed byte range and the table cost
is not acceptable. The example follows the Atari FP-package convention: `fr0`
and `fr1` hold the operands, and the 32-bit result is returned in `fr0..fr0+3`.
`fr1+2/fr1+3` are used as a temporary copy of the multiplicand.

```asm
; unsigned 16x16 -> 32
; in:  fr0/fr0+1, fr1/fr1+1
; out: fr0..fr0+3
; clobbers: A, X, C; destroys fr1; uses fr1+2/fr1+3
int16mul
tmp     = fr1+2

        lda fr0
        ora fr0+1
        beq @clear
        lda fr1
        ora fr1+1
        beq @clear

        lda fr0
        sta tmp
        lda fr0+1
        sta tmp+1

        jsr @clear
        ldx #16
@mul    lsr fr1+1
        ror fr1
        bcc @no_add
        clc
        lda fr0+2
        adc tmp
        sta fr0+2
        lda fr0+3
        adc tmp+1
        sta fr0+3
@no_add ror fr0+3
        ror fr0+2
        ror fr0+1
        ror fr0
        dex
        bne @mul
        rts

@clear  ldx #3
        lda #0
@cl     sta fr0,x
        dex
        bpl @cl
        rts
```

### 65816 HW multiply (16-bit accumulator)

The 65816 has a dedicated HW multiplier at $4202/$4203 (~180 cycles, reliable 16×16→32-bit):

```asm
         lda    product+1
         sta    $4202
         lda    product
         sta    $4203
         ldx    #$00
         stx    $4206
         ; result appears in <$4216 (lo16) and >$4216 (hi16)
```

---

## 10.11 8×8 Square-table multiply (fmulu)

The square-table multiply (attributed to Fox/Tqa) pre-computes four 512-byte
tables at load time and then subtracts two table-lookup results to produce an
8×8→16 product in 14 cycles (vs ~29 cycles for the QS-multiply). The four
tables are page-aligned, making the zero-page self-modifying addressing
overhead zero:

```asm
.align $100
sq1l .ds $200
sq1h .ds $200
sq2l .ds $200
sq2h .ds $200
```

The multiply fast-path (`fmulu`) works as follows: when A and X (the two
factors) enter the routine, two byte-wide table lookups are performed on the
pre-built tables; the high-byte subtraction alone produces the sign-extended
16-bit product:

```asm
; A = factor1, X = factor2  →  A:Y = A×X (A = hi, Y = lo)
.proc fmulu (.byte a,x) .reg
        sta l1+1
        sta h1+1
        eor #$ff
        sta l2+1
        sta h2+1
        sec
l1      lda sq1l,x
l2      sbc sq2l,x
        tay
h1      lda sq1h,x
h2      sbc sq2h,x
        rts

init    ldx #0
        stx sq1l
        stx sq1h
        stx sq2l+$ff
        stx sq2h+$ff
        ldy #$ff
msq1    txa
        lsr @
        adc sq1l,x
        sta sq1l+1,x
        sta sq2l-1,y
        sta sq2l+$100,x
        lda #0
        adc sq1h,x
        sta sq1h+1,x
        sta sq2h-1,y
        sta sq2h+$100,x
        inx
        dey
        bne msq1
msq2    tya
        sbc #0
        ror @
        adc sq1l+$ff,y
        sta sq1l+$100,y
        lda #0
        adc sq1h+$ff,y
        sta sq1h+$100,y
        iny
        bne msq2
        rts
.endp
```

The `.init` routine populates all four LUTs at boot (108 iterations, zero
overlap), after which `fmulu(a, x)` calls cost 14 cycles regardless of operand
values.

| Variant | Table memory | Code bytes | Cycles |
|---|---|---|---|
| QS multiply | 512 B (one quarter-square LUT) | ~46 B | ~29 |
| `fmulu` | 2048 B (four 512 B LUTs) | ~46B | **14** |

Shared-table win: if a program already maintains page-aligned square tables for
distance, collision, or transform code, choose a table layout that can be reused
by both `fmulu` and squared-distance lookup instead of keeping duplicate LUTs.

---
