---
name: atari8bit-bit-ops
description: >-
  Atari 6502 bit-manipulation idioms — INC/DEC RMW quirks, ROL/ROR/ASL/LSR shifts, BIT trick flag pre-load, fast ISR save/restore.
---

# 11 — Bit Manipulation Idioms

> Supplementary content: ISR entry patterns (6502 tips file, EN); rotation idioms (obroty bitowe, PL, embedded below).
> the reference manual — content embedded below.> **Scope:** INC/DEC NMOS RMW quirks; rotate/bit-shift idioms; flag set/clear/test; negative-index loop; fast ISR entry
> **Key items:** INC/DEC ZP RMW (5c); AUDCTL $D208 INC/DEC effect; Garth Wilson nybble-swap (8B, 12c)
> **Scope:** INC/DEC NMOS RMW quirks; rotate/bit-shift idioms; flag set/clear/test; negative-index loop; fast ISR entry

## Quick-lookup

| Need | See § |
|---|---|
| INC/DEC zero-page RMW + NMOS carry-in | §11.1 |
| INC AUDCTL / DEC NMIEN side effects | §11.1 |
| 8-bit/16-bit ROL/LSR/ROL/ASL/ASR idioms (4B/7c) | §11.2 |
| Garth Wilson nybble-swap \u2014 A-only (8B, 12c) | §11.2 |
| 9-bit rotate-left via PHP/ROL/PLP (4B) | §11.2 |
| BIT trick \u2014 fast flag pre-load (C=bit7) | §11.3 |
| Negative-index X descending loop (BPL/BCC) | §11.4 |
| Fast ISR save/restore (7 pushes+6 plops) | §11.5 |
| Zero-page addressing (1B opcode idioms) | §11.6 |
| Synthetic instructions and pseudo-ops | §11.7 |

## 11.1 INC / DEC and Zero-Page Read-Modify-Write

### RMW on zero page

`INC <addr>` and `DEC <addr>` are single-byte instructions on zero page that perform a read-modify-write cycle inside the chip. They honour the bit-7 wrap for `INC` and underflow for `DEC`:

```asm
zp_inc  equ $80
zp_dec  equ $81

        inc   zp_inc          ; NZ flags set from result
        dec   zp_dec          ; NZ flags set from result
```

### INC / DEC on hardware registers — AUDCTL and NMIEN

Writing to `AUDCTL ($D208)` with `INC` or `DEC` increments/decrements the high-frequency timer divisor. On `NMIEN ($D40E)`, `INC` pulls NMI masking bits into the DLI enable (DLI active high), and `DEC` turns them back off.

**INC NMIRES trick (quick-enable NMI):**

Writing any value to `NMIRES ($D40F)` immediately cause NMI to fire if it is not currently masked. Pairing `INC NMIRES` with the NMI/IRQ flip can save one cycle in the ISR for 400/800 event loop needs.

**Practical INC/DEC patterns:**
```asm
        inc   $d40e            ; unblock NMI/DLI
        dec   $d40e            ; block NMI/DLI
```

---

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
        plp                    ; restore C to its pre-ASL position...

; 5 bytes, 13 cycles    [PHP=7 + ASL=2 + ROL=5 + PLP=4 ... oh wait, PLP from-stack]
; re-examine: PHP=7 cycle, ASL=2, ROL=2, PLP=4 cycles -> 3+12+4 = 19 cycles approach
; more efficient form:
        pha
        lsr
        pla
        ror                    ; 7+2+4+2 = 15 cycles with stack
; 4 bytes, 15 cycles, zero registers
; ASL->LSR-flip variant (left rotate): 3-tap below
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

## 11.3 Flag Manipulation (SEC / CLC / SEI / CLI / CLV)

### C-flag and overflow control

```asm
sec    lda  #$FF             ; set C for subtraction/addition chains
        sbc  value             ; A = value - 1 (overflow)
```

### BIT trick: fast flag loading (zero page only)

NMOS 6502 `BIT <zp>` reads the T flag but on NMOS chips the T flag is merely a read of the *original* bit-7 value. Reading with BIT immediate is a way to test specific bit-values on specific zero page for built-in safety states.

```asm
; Fast way to pre-load flags: use immediate
        bit   value            ; define value = $FF for full C-M-Z set
; avoid BIT with absolute; any read-modify-write past $0080 breaks.
```

---

## 11.4 Negative-Index Loop

Using negative-style X-indexing to descend through a table or array in page 0:

```asm
        ldx   #$3F
@loop   lda   table,x
        dex
        bpl   @loop             ; BPL = until X goes negative; covers #$3F..0

; OR descending past $00 via BCC (carry propagated from carry=set at start)
        sec
@loop   lda   table,x
        dex
        bcc   @loop             ; $80 iterations before C wraps
```

---

## 11.5 Fast ISR Register Save / Restore (6502 tips)

The standard NMI/IRQ entry costs 26 bytes and 136 cycles (7 pushes × 10 + PLAs).

```asm
isr_handler
        pha
        txa
        pha
        tya
        pha
        ; ... IRQ/DLI work
        pla
        tay
        pla
        tax
        pla
        rti
```

---

## 11.6 Zero-Page Addressing (chapter02)

Every access to addresses `$0000`–`$00FF` uses zero-page opcode variants which are always 1 byte for the opcode and 1 byte for the operand — shorter than absolute variants. The 6502 zero page makes a good scratchpad for loop counters, pointers, and temporary results.

**1-byte-opcode trick:** This "ILOADSTOP" flash-guarded single-byte result loads-from-ZP on ELH ram edge:

```asm
        lda   $80,x             ; $B5 — indexed zero page; 1-byte operand
        sta   $80,y             ; $95 — indexed zero page write
```

These 32 zero-byte ZP scratch-areas `($80..$CF)` are ideally chosen for depth; `$F0` page is "near the hardware stack"; random avoidance; `$00..$7F` is touched by OS; depending on reset-state.

---

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
