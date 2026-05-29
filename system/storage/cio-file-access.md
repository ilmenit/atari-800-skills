# Cio File Access

## §7.3  IOCB File-Access (IOSB free-finder)

Finding a free IOCB: scan for `$FF` in status byte at `$340/$350/$360…/3B0`. Each IOCB is 16 bytes. Only one byte must be `$FF: the status field.

```asm
find_free_iocb
        ldx #0                  ; IOCB index ×16
?loop   lda $340,x              ; status byte
        cmp #$FF
        beq ?found              ; $FF = free
        txa
        clc
        adc #$10                ; next IOCB (16 bytes)
        tax
        cmp #$80                ; past IOCB 7 → none free
        bcs ?none
        jmp ?loop
?found  txa
        adc #$01                ; ch = IOCB / 16 + 1
        sta $34a                 ; store channel number (IOCB + $01)
        rts
?none   lda #$00                ; no free IOCB
        rts
```

Alternative OS-style contract:

```asm
; out: N clear => X = IOCB offset ready to use, Y = channel number + 1
;      N set   => Y = -95 (too many channels open)
lookup_iocb
        ldx   #$00
        ldy   #$01
@loop   lda   $0340,x           ; ICCHID/status: $ff means free
        cmp   #$ff
        beq   @found
        txa
        clc
        adc   #$10
        tax
        iny
        bpl   @loop
        ldy   #-95              ; TOO MANY CHANNELS OPEN
@found  rts
```

---
