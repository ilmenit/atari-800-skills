# Sqrt Distance

## 10.10 Distance computation (squared-table + binary-search sqrt)

A common pattern: given 2-D integer offsets (dx, dy) compute Euclidean distance
`sqrt(dx² + dy²)` without FP.

**Lookup multiply — squared table:**

```asm
MAX_VELOCITY = 128

squared_table_lo:
        :MAX_VELOCITY+1 dta l(#*#)
squared_table_hi:
        :MAX_VELOCITY+1 dta h(#*#)

_SQUARED .macro val,res
        ldx :val
        lda squared_table_lo,x
        sta :res
        lda squared_table_hi,x
        sta :res+1
        .endm
```

The example below halves `x` and `y` before squaring so `x*x + y*y` stays inside
the 16-bit search range, then doubles the final magnitude. Remove those shifts
if the caller already clamps both axes.

**Binary-search sqrt:**

```asm
.proc calc_velocity (.byte x .byte y) .var
        lsr x
        _SQUARED x x_squared
        lsr y
        _SQUARED y y_squared
        adw y_squared x_squared y_squared
        sqrt y_squared
        txa
        asl
        rts
x:         .byte 0
y:         .byte 0
x_squared: .word 0
y_squared: .word 0
.endp

; in:  val word, 0..MAX_VELOCITY^2
; out: X = floor(sqrt(val)), result = same value, carry clear
; uses squared_table_lo/squared_table_hi
.proc sqrt (.word val) .var
        mva #0 l
        lda #MAX_VELOCITY
        sta r
loop_hi:
        sec
        lda r
        sbc l
        lsr
        clc
        adc l
        tax
        lda squared_table_hi,x
        cmp val+1
        bcc l_inc
        bne r_dec
        mva #0 l
        lda #MAX_VELOCITY
        sta r
loop_lo:
        sec
        lda r
        sbc l
        lsr
        clc
        adc l
        tax
        lda squared_table_lo,x
        cmp val+0
        bcc l_inc
        bne r_dec
        stx result
        clc
        rts
l_inc:
        inx
        stx l
        lda r
        cmp l
        bcs loop_lo
        bra done
r_dec:
        dex
        stx r
        lda l
        cmp r
        bcs loop_lo
done:
        stx result
        clc
        rts
val:    .word 0
l:      .byte 0
r:      .byte 0
result: .byte 0
.endp
```

Table-sharing note: this square table can also serve range-limited distance,
collision radius checks, and quarter-square multiply variants when the maximum
index covers the needed domain.

---

## 10.12 Fast 16-bit Square Root (table-driven)

This is the fastest general-purpose snippet in this file for `sqrt(word)` when
512 bytes of tables are acceptable.

```asm
; unsigned 16-bit sqrt
; in:  X = high byte, A = low byte
; out: A = floor(sqrt(X:A))
; size: about 512 bytes including tables
; timing: best 19 cycles, average about 34, worst about 87
tmp = $00

sqrt_fast
lt4     dex
        bmi lo
        lsr
        lsr
        ora tab2,x
        tax
        lda sqtab,x
        bmi div8
        tay
        lda tmp
        lsr
        ror
        ror
        cmp stab-1,x
        tya
        adc #$80
        bmi div8
preone  ldy #div2-bra-2
        txa
        bcs one
no      sta tmp
        cpx #$10
        bcs preone
        cpx #$04
        bcc lt4
        ldy #div4-bra-2
        txa
two     asl tmp
        rol
        asl tmp
        rol
one     asl tmp
        rol
        asl tmp
        rol
        sty bra+1
        tax
        lda sqtab-$40,x
        bmi bra
        tay
        lda tmp
        cmp stab-$41,x
        tya
        adc #$80
bra     bmi bra

lo      cmp #$40
        bcc nolo
        tax
        lda sqtab-$40,x
        ora #$80
div16   lsr
div8    lsr
div4    lsr
div2    lsr
done    rts
nolo    asl
        cmp #$20
        bcc nolo2
        asl
        tax
        lda sqtab-$40,x
        lsr
        ora #$40
        bne div16
nolo2   tax
        lda smalltab,x
        rts

sqrt15  cpx #$40
        bcc no
        ldy sqtab-$40,x
        bmi skip
        cmp stab-$41,x
        tya
        adc #$80
        rts

XXX = $10
stab
        .byte     $01,$04,$09,$10,$19,$24,$31
        .byte $40,$51,$64,$79,$90,$a9,$c4,$e1
skip    tya
        rts

        .byte         $21,$44,$69,$90,$b9,$e4
        .byte XXX,$11,$40,$71,$a4,$d9,XXX,$10
        .byte $49,$84,$c1,XXX,XXX,$41,$84,$c9
        .byte XXX,$10,$59,$a4,$f1,XXX,$40,$91
        .byte $e4,XXX,$39,$90,$e9,XXX,$44,$a1
        .byte XXX,XXX,$61,$c4,XXX,$29,$90,$f9
        .byte XXX,$64,$d1,XXX,$40,$b1,XXX,$24
        .byte $99,XXX,$10,$89,XXX,$04,$81,XXX
        .byte XXX,$81,XXX,$04,$89,XXX,$10,$99
        .byte XXX,$24,$b1,XXX,$40,$d1,XXX,$64
        .byte $f9,XXX,$90,XXX,$29,$c4,XXX,$61
        .byte XXX,XXX,$a1,XXX,$44,$e9,XXX,$90
        .byte XXX,$39,$e4,XXX,$91,XXX,$40,$f1
        .byte XXX,$a4,XXX,$59,XXX,$10,$c9,XXX
        .byte $84,XXX,$41,XXX,XXX,$c1,XXX,$84
        .byte XXX,$49,XXX,$10,$d9,XXX,$a4,XXX
        .byte $71
tab2
        .byte     $00,$40,$80
        .byte                 $11,$e4,XXX,$b9
        .byte XXX,$90,XXX,$69,XXX,$44,XXX,$21
        .byte XXX
smalltab
        .byte     $00,$e1,$01,$c4,$01,$a9,$01
        .byte $90,$02,$79,$02,$64,$02,$51,$02
        .byte $40,$02,$31,$03,$24,$03,$19,$03
        .byte $10,$03,$09,$03,$04,$03,$01,$03
sqtab
        .byte $80,$00,$01,$02,$03,$04,$05,$06
        .byte $07,$08,$09,$0a,$0b,$0c,$0d,$0e
        .byte $8f,$90,$10,$11,$12,$13,$14,$15
        .byte $96,$16,$17,$18,$19,$1a,$9b,$1b
        .byte $1c,$1d,$1e,$9f,$a0,$20,$21,$22
        .byte $a3,$23,$24,$25,$26,$a7,$27,$28
        .byte $29,$aa,$2a,$2b,$2c,$ad,$2d,$2e
        .byte $af,$b0,$30,$31,$b2,$32,$33,$34
        .byte $b5,$35,$36,$b7,$37,$38,$b9,$39
        .byte $3a,$bb,$3b,$3c,$bd,$3d,$3e,$bf
        .byte $c0,$40,$c1,$41,$42,$c3,$43,$44
        .byte $c5,$45,$46,$c7,$47,$48,$c9,$49
        .byte $4a,$cb,$4b,$cc,$4c,$4d,$ce,$4e
        .byte $cf,$d0,$50,$d1,$51,$52,$d3,$53
        .byte $d4,$54,$55,$d6,$56,$d7,$57,$58
        .byte $d9,$59,$da,$5a,$db,$5b,$5c,$dd
        .byte $5d,$de,$5e,$df,$e0,$60,$e1,$61
        .byte $e2,$62,$e3,$63,$64,$e5,$65,$e6
        .byte $66,$e7,$67,$e8,$68,$69,$ea,$6a
        .byte $eb,$6b,$ec,$6c,$ed,$6d,$ee,$6e
        .byte $ef,$f0,$70,$f1,$71,$f2,$72,$f3
        .byte $73,$f4,$74,$f5,$75,$f6,$76,$f7
        .byte $77,$f8,$78,$f9,$79,$fa,$7a,$fb
        .byte $7b,$fc,$7c,$fd,$7d,$fe,$7e,$ff
```

---
