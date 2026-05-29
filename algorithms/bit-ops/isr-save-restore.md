# Isr Save Restore

## 11.5 Fast ISR Register Save / Restore

The standard DLI/IRQ pattern saves A/X/Y on the stack. It is reentrant and safe
for nested interrupts, but costs 29 cycles for the save/restore wrapper:

```asm
isr_handler
        pha
        txa
        pha
        tya
        pha
        jsr service_irq_source  ; acknowledge device before re-enabling IRQ/NMI
        pla
        tay
        pla
        tax
        pla
        rti
```

For very dense DLI chains, save into private bytes instead. This is faster but
not reentrant; nested interrupt handlers must use different save locations.

```asm
; 18 cycles total for save+restore, plus handler body.
; Works when this handler cannot be interrupted by another handler using
; the same save bytes.
enter
        sta   @restore_a+1
        stx   @restore_x+1
        sty   @restore_y+1
        ; ... handler body ...
@restore_a
        lda   #0
@restore_x
        ldx   #0
@restore_y
        ldy   #0
        rti
```

If the routine has multiple exits, zero-page save bytes are often clearer:

```asm
zp_a = $80
zp_x = $81
zp_y = $82

        sta   zp_a
        stx   zp_x
        sty   zp_y
        ; ... any exit path ...
        lda   zp_a
        ldx   zp_x
        ldy   zp_y
        rti
```

If the whole DLI handler is placed in zero page, the `STA/STX/STY zp` saves one
cycle each versus absolute addressing. This can matter for per-scanline or
every-other-scanline DLIs.

When a subroutine must preserve X/Y but return a value in A, reserve A's stack
slot first and overwrite it before returning. The adjusted `TSX/INX/INX/INX`
form is safe even if the stack pointer wrapped while saving registers:

```asm
        pha
        tya
        pha
        txa
        pha
        ; ... compute result in A ...
        tsx
        inx
        inx
        inx
        sta   $0100,x          ; replace saved A with result
        pla
        tax
        pla
        tay
        pla                    ; result restored into A
        rts
```

---
