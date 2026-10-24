; Binary-mode NMOS 6502 routines. No private zero page.
; Shared writable scratch makes these non-reentrant. Include after an ORG.
; All clobber A/X/N/Z/C/V unless stated otherwise; Y is preserved.

; In: mul_a (16-bit). Out: mul_result (16-bit), modulo 65536.
mul3_u16
        lda mul_a
        asl
        sta mul_result
        lda mul_a+1
        rol
        sta mul_result+1
        clc
        lda mul_result
        adc mul_a
        sta mul_result
        lda mul_result+1
        adc mul_a+1
        sta mul_result+1
        rts

; In: mul_a (16-bit). Out: mul_result (16-bit), modulo 65536.
mul10_u16
        lda mul_a
        sta mul_result
        lda mul_a+1
        sta mul_result+1
        asl mul_result
        rol mul_result+1
        asl mul_result
        rol mul_result+1
        clc
        lda mul_result
        adc mul_a
        sta mul_result
        lda mul_result+1
        adc mul_a+1
        sta mul_result+1
        asl mul_result
        rol mul_result+1
        rts

; In: A (unsigned byte). Out: mul_result (16-bit), exactly A*96.
; Also overwrites mul_a, which is scratch for this entry.
mul96_u8
        sta mul_a
        lda #0
        sta mul_a+1
        jsr mul3_u16
        ldx #5
mul96_shift
        asl mul_result
        rol mul_result+1
        dex
        bne mul96_shift
        rts

; In: A and X (unsigned bytes). Out: mul_result (16-bit), exactly A*X.
; Table-free reference implementation; eight iterations, data-dependent adds.
mul8_u16
        sta mul_b
        stx mul_work
        lda #0
        sta mul_work+1
        sta mul_result
        sta mul_result+1
        ldx #8
mul8_loop
        lsr mul_b
        bcc mul8_skip
        clc
        lda mul_result
        adc mul_work
        sta mul_result
        lda mul_result+1
        adc mul_work+1
        sta mul_result+1
mul8_skip
        asl mul_work
        rol mul_work+1
        dex
        bne mul8_loop
        rts

; In: mul_a, mul_b (16-bit unsigned). Out: mul_result (32-bit exact product).
; Destroys mul_b, uses mul_work (4 bytes); sixteen iterations.
mul16_u32
        lda mul_a
        sta mul_work
        lda mul_a+1
        sta mul_work+1
        lda #0
        sta mul_work+2
        sta mul_work+3
        sta mul_result
        sta mul_result+1
        sta mul_result+2
        sta mul_result+3
        ldx #16
mul16_loop
        lsr mul_b+1
        ror mul_b
        bcc mul16_skip
        clc
        lda mul_result
        adc mul_work
        sta mul_result
        lda mul_result+1
        adc mul_work+1
        sta mul_result+1
        lda mul_result+2
        adc mul_work+2
        sta mul_result+2
        lda mul_result+3
        adc mul_work+3
        sta mul_result+3
mul16_skip
        asl mul_work
        rol mul_work+1
        rol mul_work+2
        rol mul_work+3
        dex
        bne mul16_loop
        rts

mul_a      .word 0
mul_b      .word 0
mul_work   .ds 4
mul_result .ds 4
