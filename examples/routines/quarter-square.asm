; Unsigned 8x8 -> 16, NMOS 6502, binary mode (D=0).
; In: A=a, X=b. Out: prod_lo/prod_hi. Clobbers A/X/Y/N/V/Z/C.
; Scratch: qs_a, qs_b, qs_sum_hi. Non-reentrant; code/tables/scratch in RAM.
; No zero-page allocation. Tables contain 511 entries each (1022 bytes).
; Include after choosing an ORG. Validated exhaustively by scripts/validate.py.
qs_mul8
        sta qs_a
        stx qs_b
        clc
        adc qs_b
        tax
        lda #0
        adc #0
        sta qs_sum_hi           ; ninth bit of a+b must survive

        sec
        lda qs_a
        sbc qs_b
        bcs qs_diff_ok
        eor #$ff
        adc #1                  ; C=0 from negative subtraction
qs_diff_ok
        tay                     ; abs(a-b), always 0..255
        lda qs_sum_hi
        bne qs_upper

        sec
        lda qs_lo,x
        sbc qs_lo,y
        sta prod_lo
        lda qs_hi,x
        sbc qs_hi,y
        sta prod_hi
        rts
qs_upper
        sec
        lda qs_lo+$100,x
        sbc qs_lo,y
        sta prod_lo
        lda qs_hi+$100,x
        sbc qs_hi,y
        sta prod_hi
        rts

qs_a       .byte 0
qs_b       .byte 0
qs_sum_hi  .byte 0
prod_lo    .byte 0
prod_hi    .byte 0
qs_lo      :511 dta l([#*#]/4)
qs_hi      :511 dta h([#*#]/4)
