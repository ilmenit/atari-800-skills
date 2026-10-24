; Runnable 64K XL/XE XEX: temporarily OS-off with a ROM-enabling NMI bridge.
; Entry contract: standard OS VBI enabled, DLI disabled, BASIC disabled.
; First checks immediate VBI with I set, then deferred VBI with I clear.
; POKEY IRQ sources are disabled; entry requires normal OS-disabled PIA IRQs.
; No CIO/SIO. Claims RAM vectors; restores mapping/VBI/POKEY IRQ mask/NMI.
        icl 'atari.inc'
        org $2000
start
        php
        sei
        cld
        lda #0
        sta NMIEN
        sta IRQEN               ; no hardware IRQ source during the I=0 phase
        lda VVBLKD
        sta saved_vbi
        lda VVBLKD+1
        sta saved_vbi+1
        ldx #>deferred_vbi
        ldy #<deferred_vbi
        lda #7
        jsr SETVBV
        lda PORTB
        sta saved_portb
        and #$fe
        sta PORTB
        lda #<os_nmi_bridge
        sta $fffa
        lda #>os_nmi_bridge
        sta $fffb
        lda #<park
        sta $fffc
        lda #>park
        sta $fffd
        lda #<masked_irq
        sta $fffe
        lda #>masked_irq
        sta $ffff
        lda #$40
        sta NMIEN
        ldx #3
next_frame
        lda RTCLOK+2
wait    cmp RTCLOK+2
        beq wait
        dex
        bne next_frame
        lda deferred_ticks
        sta masked_ticks        ; should still be zero: OS stage 2 was skipped
        cli
wait_deferred
        lda deferred_ticks
        cmp #3
        bcc wait_deferred
cleanup
        sei
        lda #0
        sta NMIEN
        lda saved_portb
        sta PORTB
        ldx saved_vbi+1
        ldy saved_vbi
        lda #7
        jsr SETVBV
        lda POKMSK
        sta IRQEN
        lda #$40
        sta NMIEN
        plp
done    rts
park    jmp park
masked_irq
        rti                     ; IRQs must remain masked in this example
saved_portb .byte 0
saved_vbi   .word 0
masked_ticks .byte 0
deferred_ticks .byte 0
deferred_vbi
        inc deferred_ticks
        jmp XITVBV
        icl 'routines/os-nmi-bridge.asm'
        run start
