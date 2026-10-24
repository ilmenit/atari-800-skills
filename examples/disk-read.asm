; Runnable read-only XEX: OS on, D1: present, reads sector 1 (128 bytes).
; No DOS filesystem assumptions. No disk writes. Buffer is inside this XEX.
; example_status is SIO's Y result; buffer is valid only on success (Y<128).
        icl 'atari.inc'
        org $2000
start
        cld
        lda #$31
        sta DDEVIC
        lda #1
        sta DUNIT
        sta DAUX1
        lda #'R'
        sta DCOMND
        lda #$40
        sta DSTATS
        lda #<sector_buffer
        sta DBUFLO
        lda #>sector_buffer
        sta DBUFHI
        lda #7
        sta DTIMLO
        lda #128
        sta DBYTLO
        lda #0
        sta DUNUSE
        sta DBYTHI
        sta DAUX2
        jsr SIOV
        sty example_status
done
        rts
example_status .byte 0
sector_buffer  .ds 128
        run start
