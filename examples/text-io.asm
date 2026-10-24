; Runnable XEX: OS on, ordinary E: screen initialized, one free IOCB 1..7.
; Writes a prompt, opens K:, reads/echoes a character, closes, returns to DOS.
; No ZP allocation or custom interrupts. example_status is Y from the last
; operation, or the earlier GET/PUT error if cleanup follows a failure.
        icl 'atari.inc'
        org $2000
start
        cld
        lda #<prompt
        sta ICBAL
        lda #>prompt
        sta ICBAH
        lda #prompt_end-prompt
        sta ICBLL
        lda #0
        sta ICBLH
        lda #11
        sta ICCOM
        ldx #0
        jsr CIOV
        sty example_status
        bpl prompt_ok
        rts
prompt_ok
        jsr find_free_iocb
        bcs no_channel
        stx channel
        lda #3
        sta ICCOM,x
        lda #<keyboard_name
        sta ICBAL,x
        lda #>keyboard_name
        sta ICBAH,x
        lda #4
        sta ICAX1,x
        lda #0
        sta ICAX2,x
        jsr CIOV
        sty example_status
        bmi done

read_key
        ldx channel
        lda #7
        sta ICCOM,x
        lda #<key_buffer
        sta ICBAL,x
        lda #>key_buffer
        sta ICBAH,x
        lda #1
        sta ICBLL,x
        lda #0
        sta ICBLH,x
        jsr CIOV
        sty example_status
        bmi close_channel

        ldx #0
        lda #11
        sta ICCOM
        lda #<key_buffer
        sta ICBAL
        lda #>key_buffer
        sta ICBAH
        lda #1
        sta ICBLL
        lda #0
        sta ICBLH
        jsr CIOV
        sty example_status
close_channel
        ldx channel
        lda #12
        sta ICCOM,x
        jsr CIOV
        lda example_status
        bmi done                ; preserve original read/write failure
        sty example_status
done    rts
no_channel
        lda #$86                ; no usable IOCB in this example
        sta example_status
        rts

channel        .byte 0
example_status .byte 0
key_buffer     .byte 0
keyboard_name  .byte 'K:',0
prompt         .byte 'PRESS A KEY: ',$9b
prompt_end
        icl 'routines/find-free-iocb.asm'
        run start
