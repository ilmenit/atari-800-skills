; Runnable XEX: OS on, stock POKEY. Claims all four audio channels globally.
; Plays an approximate A4 square wave for one PAL/NTSC second, then silences.
; SIO changes POKEY configuration; do not run concurrent SIO/music players.
        icl 'atari.inc'
        org $2000
start
        cld
        lda #3
        sta SKCTL
        lda #0
        sta AUDCTL
        lda #72                 ; NTSC ~438Hz; PAL slightly lower
        sta AUDF1
        lda #$a8
        sta AUDC1
        ldx #50
        lda $d014               ; GTIA PAL flag; assumes matched ANTIC/GTIA
        and #$0e
        beq next_frame          ; PAL flag = 0
        ldx #60
next_frame
        lda RTCLOK+2
wait    cmp RTCLOK+2
        beq wait
        dex
        bne next_frame
        lda #0
        sta AUDC1
done
        rts
        run start
