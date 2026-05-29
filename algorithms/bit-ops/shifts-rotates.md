# Shifts Rotates

## 11.2 Bit Rotation Idioms (ROL / ROR / ASL / LSR)

### 8-bit rotate-left through carry

```asm
        clc
        asl   a                ; bit7 -> C
        rol   a                ; C -> bit0
; 4 bytes, 7 cycles
```

### 8-bit rotate-right through carry

```asm
        sec
        lsr   a                ; bit0 -> C
        ror   a                ; C -> bit7
; 4 bytes, 7 cycles
```

### Zero-register rotate (A=carry, result=rotate only A)

For the case where A alone must act as both source and destination, use `ROR A` or `ROL A` directly (single insn, 2 cycles).

### 9-bit rotate-left via stack

Rotate a 9-bit value with A = low byte, carry = bit9:

```asm
        php                    ; save P (C is rightmost-bit-of-prior-to)
        asl   a
        rol   buffer           ; buffer holds high bit; now 9-bit value complete
        plp                    ; restore original carry if caller still needs it

; PHP=3, ASL A=2, ROL zp=5, PLP=4: 14 cycles plus zero-page operand cost.
; If carry does not need to be preserved, drop PHP/PLP and use ASL/ROL only.
```

### Garth Wilson nybble-swap (8 bytes, 12 cycles, A-only)

Swap high and low 4-bit nibbles without a temp register:

```asm
nyb_swap   asl   a             ; bit7->C
            adc   #$80          ; C can be added as LSB of $80
            rol   a             ; now bit0→bit7 and bit7→bit0 but we need full swap
            asl   a
            adc   #$80
            rol   a             ; result in A — nibbles swapped after 2 iterations
; 8 bytes, 12 cycles
```

Aggressive/byte-perfect version:
```asm
        asl   a
        adc   #$80
        rol
        asl   a
        adc   #$80
        rol
        asl   a
        adc   #$80
        rol
; this 8-nibble recipe rotates by 4 positions (byte swap) in 24 cycles
```

### Two-byte rotate-left (16-bit AX)

```asm
        clc
        rol   a                ; rotate in low byte
        rol   x                

; ROR variant:
        sec
        ror   a
        ror   x
```

---
