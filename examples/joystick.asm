; Runnable XEX: OS on, default 40-column E: display, joystick port 1.
; Shows direction nibble and trigger as screen-code digits at top-left.
; Uses existing SAVMSC pointer read-only; no private ZP. START returns to DOS.
        icl 'atari.inc'
        org $2000
start
        cld
frame
        lda RTCLOK+2
wait    cmp RTCLOK+2
        beq wait
        lda STICK0
        and #15
        tax
        lda hex_screen,x
        ldy #0
        sta (SAVMSC),y
        lda STRIG0
        clc
        adc #$10
        iny
        sta (SAVMSC),y
check_exit
        lda CONSOL
        and #1
        bne frame
done
        rts
hex_screen .byte $10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$21,$22,$23,$24,$25,$26
        run start
