# Synthetic Instructions

## 11.7 Synthetic Instructions and Pseudo-Ops

These are reusable instruction idioms from `articles/6502-synthetic-instr.md`. Turn them into MADS macros when used repeatedly, but keep the flag clobbers visible in timing-critical code.

### Negate and Reverse Subtract

```asm
; A = -A
        eor   #$ff
        sec
        adc   #0

; A = value - A
        eor   #$ff
        sec
        adc   value

; A = 255 - A
        eor   #$ff
```

If carry is known clear before negation, `EOR #$FF / ADC #1` also works.

### Sign Extension

Generate the high byte for an 8-bit signed value in A:

```asm
        asl   a             ; sign bit -> C
        lda   #$00
        adc   #$ff          ; A=$00 if C=1, A=$ff if C=0
        eor   #$ff          ; A=$ff for negative, $00 for positive
```

For adding an 8-bit signed delta to a 16-bit value, decrement the high byte first if the delta is negative, then add the low byte as unsigned.

Extend a signed sub-byte field to 8 bits. Example: A contains a signed 5-bit
value in bits 0..4:

```asm
        and   #$1f
        clc
        adc   #$f0
        eor   #$f0              ; A is now signed 8-bit
```

General rule: mask off unused bits, add a constant that moves the sign bit into
carry, then EOR the same top-bit mask back into place.

### Arithmetic Shift Right

```asm
; A = signed A / 2
        cmp   #$80          ; C = sign bit
        ror   a

; memory operand
        lda   value
        asl   a             ; sign bit -> C
        ror   value
```

### True Arithmetic Shift Left

`ASL` does not set V for signed overflow. Use `ADC` with a copy when signed
overflow matters:

```asm
; A = A * 2, V reflects signed overflow
        clc
        sta   temp
        adc   temp
```

For multi-byte signed values, shift low/intermediate bytes normally, then use
`ADC msb` on the high byte so V reflects the sign change of the whole value.

### True 8-Bit Rotate

6502 `ROL/ROR` are 9-bit rotates through carry. Preload carry when a true 8-bit rotate is needed.

```asm
; 8-bit rotate left A
        cmp   #$80
        rol   a

; alternate rotate left
        asl   a
        adc   #0

; 8-bit rotate right A
        pha
        lsr   a             ; bit0 -> C
        pla
        ror   a
```

Nybble swap is two double-left rotates:

```asm
        asl   a
        adc   #$80
        rol   a
        asl   a
        adc   #$80
        rol   a
```

### 16-Bit Increment and Decrement

```asm
; ++word
        inc   word
        bne   done
        inc   word+1
done

; --word
        lda   word
        bne   nodec
        dec   word+1
nodec   dec   word
```

The increment sequence leaves Z set only when the full 16-bit value wrapped to zero, which is useful for loop control.

### X/Y as A Operands

Use a 256-byte identity table when X or Y must be used as an operand without storing to a temporary byte.

```asm
        cmp   Identity,x     ; compare A with X
        eor   Identity,x     ; EOR X
        adc   Identity,y     ; ADC Y
```

### Carry, Overflow, and NZ Helpers

```asm
; toggle carry, clobbers N/Z
        rol   a
        eor   #$01
        ror   a

; set V using BIT on any byte with bit6 set, e.g. RTS opcode $60
        bit   v_source
v_source
        rts

; refresh N/Z from A without affecting carry
        ora   #$00

; refresh N/Z from X
        inx
        dex
```

### Range Test

Unsigned inclusive range test, result in carry, A destroyed:

```asm
; C=1 if min <= A <= max
        clc
        adc   #$ff-max
        adc   #max-min+1

; C=0 if min <= A <= max
        sec
        sbc   #min
        sbc   #max-min+1
```

### Count Set Bits

Count set bits in A using shifts; result in X and A.

```asm
        ldx   #$ff
more    inx
loop    asl
        bcs   more
        bne   loop
        txa
```

---

See also: `system/memory-map.md` §2.4 (zero-page idioms), `system/os-hardening.md` §9.1 (PORTB safety), `algorithms/optimization.md` (size/speed tradeoffs).
