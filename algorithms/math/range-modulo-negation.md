# Range Modulo Negation

## 10.3 Modulo, Range, Negation

### Modulo 255 — constant-time 5B

```asm
mod255   clc
         lda   lo_byte
         adc   hi_byte
         adc   #1
         sbc   #0
         sta   result         ; result = (256·HI + LO) mod 255
```

### Range-clamp [LO..HI]

```asm
; clamp A to [LO..HI]: A = clamp(A, LO, HI)
range_clamp
         clc
         adc   #$FF - HI
         adc   #(HI - LO + 1)
         bcs   in_range
         lda   #LO
         rts
in_range
         clc
         eor   #$FF           ; undo mask on A
         rts
```

### Negation

```asm
; Two's complement negation:
neg_16b   clc
          eor   #$FF
          adc   #$1
          sta   value         ; low byte
          lda   value+1
          eor   #$FF
          adc   #$0           ; propagate carry through high byte
          sta   value+1
```

### BIT-trick for carry-heavy multi-byte chains

```asm
; Pre-load C = bit7 of <address> with BIT immediate, then ADC to chain carries:
          bit   #$80           ; C=1
          sbc   value          ; A = value - 1  via C-subtract
          sbc   #$00           ; -0 when C=1, ship-carry via C-subtract
```

---
