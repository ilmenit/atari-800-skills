; XL/XE, 6502, OS ROM initially off. Entry: hardware NMI via RAM $FFFA vector.
; Requires code, helpers, and stack outside ROM/banked/self-test windows.
; Keeps PORTB bits other than OS-enable unchanged; does not own IRQ/RESET.
; Preserves A/X/Y/P/SP and exact PORTB value. Nested calls use stack storage.
; OS NMI handlers must obey their normal RTI/XITVBV contracts.
; Do not JSR this entry, or JSR an OS interrupt dispatcher expecting RTS.
os_nmi_bridge
        pha
        txa
        pha
        tya
        pha
        lda PORTB
        pha                     ; save mapping on this interrupt's stack
        ora #$01
        sta PORTB               ; expose OS NMI vector and ROM

        ; Build an RTI frame so the OS returns to bridge_resume.
        lda #>bridge_resume
        pha
        lda #<bridge_resume
        pha
        ; OS VBI checks I in its stacked status to decide whether to run stage 2.
        ; Copy the ORIGINAL hardware frame's P, not current P (NMI set I).
        ; Seven bytes separate SP from original P; wrap within the stack page.
        tsx
        txa
        cld                     ; NMOS NMI entry does not clear decimal mode
        clc
        adc #7
        tax
        lda $0100,x
        and #$ef                ; synthetic hardware frame, B clear
        pha
        jmp ($fffa)             ; OS NMI dispatcher, now ROM is visible

bridge_resume
        pla
        sta PORTB               ; restore mapping BEFORE original A
        pla
        tay
        pla
        tax
        pla
        rti                     ; original hardware interrupt frame
