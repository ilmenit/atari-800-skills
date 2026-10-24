; CPU-test fixture, not a replacement Atari OS or a runnable XEX.
; Matches the NMI/DVNM stack convention in Atari XL OS Rev.2.
        icl '../examples/atari.inc'
        org $c000
stub_nmi
        bit NMIST
        bpl stub_vbi
        jmp (VDSLST)
stub_vbi
        cld
        pha
        txa
        pha
        tya
        pha
        sta NMIRES
        inc RTCLOK+2            ; stage 1 runs even when interrupted I was set
        tsx
        lda $0104,x             ; same saved-P test as XL OS IVN3
        and #4
        bne stub_exit           ; IRQ-masked code skips deferred VBI
        jmp (VVBLKD)
stub_exit
        pla
        tay
        pla
        tax
        pla
        rti
        org XITVBV
        jmp stub_exit
        org $fffa
        .word stub_nmi
