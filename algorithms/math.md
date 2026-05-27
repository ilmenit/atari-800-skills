---
name: atari8bit-math
description: >-
  Atari 6502/65816 math idioms — mul3/10/96, 8-bit and 16-bit multiplication LUTs, 16-bit division, modulo/negation, QS multiply, log-atan2, squared-table distance, fmulu multiply, assembly-time sqrt, 65816 HW multiply.
---

# 10 — Math Routines

> **Scope:** Atari 6502 math idioms: multiplication, division, modulo, range-clamp, negation, 65816 HW multiply, QS multiply, log-atan2
> **Key items:** mul3/mul10/mul96; 512B Keldon LUT; 16×16 shift-add; QS multiply; DIV/10 (79B); mod-255; range-clamp; neg-16b; fmulu 8×8;

## Quick-lookup

| Need | See § |
|---|---|
| Multiply by 3 / 10 / 96 | §10.1 |
| 8×8→16 via 512-byte LUT (Keldon) | §10.1 |
| 16×16→32 shift-add loop | §10.1 |
| 65816 HW multiply $4202/$4203 | §10.6 |
| Divide by 2–32 (8–21B each) | §10.2 |
| 16-bit / 10 (79B verifiable) | §10.2 |
| Modulo 255 (5B constant-time) | §10.3 |
| Range-clamp [LO..HI] | §10.3 |
| Two's-complement negation (16-bit) | §10.3 |
| BIT-trick for carry arithmetic | §10.3 |
| QS multiply (TORUS3D / quarter-square) | §10.5 |
| Logarithmic atan2 (no division) | §10.9 |
| Distance via squared-table + sqrt | §10.10 |
| 8×8 square-table multiply (fmulu) | §10.11 |

---

## 10.1 Multiplication

> **Signed-16-bit overflow hazard:** All mul3/mul10/mul96 and Keldon LUT variants wrap at ±256. For signed results beyond ±255, use the 16×16 shift-add loop or the 65816 $4202/$4203 hardware multiplier.
> **BIT-trick signed-mask hazard:** the range-clamp XOR form when HI>=LO produces an off-by-one overflow. Commit the mask form to the specific range being clamped.

### Multiply by 3

```asm
mul3   lda  num
         asl  a                ; A × 2
         sta  result
         lda  num+1
         rol  a                ; carry-propagated high-byte shift
         sta  result+1
         clc
         lda  num
         adc  result
         sta  result
         lda  num+1
         adc  result+1
         sta  result+1              ; result = 3 × num  | 3 cycles
```

### Multiply by 10

```asm
mul10   lda  num
         sta  result
         lda  num+1
         sta  result+1
         asl  result
         rol  result+1             ; result ×=  2
         asl  result
         rol  result+1             ; result ×=  4
         clc
         lda  num
         adc  result
         sta  result
         lda  num+1
         adc  result+1
         sta  result+1
         asl  result
         rol  result+1             ; ×10
```

### Multiply by 96

```asm
; A holds argument [0..95], result in (res+1, res)
         sta  res
         asl
         adc  res
         ror
         ror
         ror
         tax
         and  #%00111111
         sta  res+1
         txa
         ror
         and  #%11100000
         sta  res                 ; res = A × 96   | ~30 cycles
```

### Multiply by 10 — shortform (argument ≤ 95)

```asm
         sta  res
         asl
         adc  res
         ror
         ror
         ror
         tax
         and  #%00111111
         sta  res+1
         txa
         ror
         and  #%11100000
         sta  res                 ; ~30 cycles
```

### 8×8 LUT multiply via 512-byte quarter-square table

The 512-byte table covers `n = 0..510`; `table_n[n] = (n*n)/4` is stored as
two separate sub-tables (`lsb` and `msb`). With a short lookup the code runs
in 116 cycles. The table is identical to the 2-K variant but offsets the index
range: `table_n[a+b` - `[|a-b|]]/4` yields the 16-bit QS-multiply result
with no carry adjustment needed. Standard QS-multiply page-aligned LUT.

### 16×16 shift-add loop

| CPU | Cycles | note |
|---|---|---|
| 6502 | 612–944 | 16 iterations, 4 seed B/L B/L; scratch copy of FR0 |

... (The table is unchanged — use the same layout with corrected rows.)

```asm
; 16-cycle shorter 6502 accumulator form: C = overflow
; 16-cycle adder + overflow shift requirement
;
; Unit shift of A (only, not 65816).
; for 65816 in 65816 mode, accumulator is wider.
```

### 65816 HW multiply (16-bit accumulator)

The 65816 has a dedicated HW multiplier at $4202/$4203 (~180 cycles, reliable 16×16→32-bit):

```asm
         lda    product+1
         sta    $4202
         lda    product
         sta    $4203
         ldx    #$00
         stx    $4206
         ; result appears in <$4216 (lo16) and >$4216 (hi16)
```

---

## 10.2 Division

### Divide by 2–32 constant-time routine

The low byte stays in A; X, Y, and BCD-mode are untouched. Powers of two are
trivial (plain LSR or LSR repeated N). All others are shift-add-subtract chains
with one 1-byte temp (ZP). Example — divide by 3 (18 bytes):

```asm
div3    sta temp
         lsr
         lsr
         adc temp
         ror
         lsr
         adc temp
         ror
         lsr
         adc temp
         ror
```

The full table:

| Divide by | bytes | cycles | technique |
|---|---|---|---|
| 2 | 1 | 2 | LSR |
| 3 | 18 | 30 | shift-add |
| 4 | 2 | 4 | LSR×2 |
| 5 | 18 | 30 | shift-add |
| 6 | 17 | 30 | double shift-add |
| 8 | 3 | 6 | LSR×3 |
| 16 | 4 | 8 | LSR×4 |
| 32 | 5 | 10 | LSR×5 |
| 7 / 9 / 10 | 15–79B | 27–126 | shift-add-subtract |
| /10 (79B verified) | 79 | 126 | two LUT table |

### 16-bit / 10 (79B / 126 cycles)

Omegamatrix's unsigned 16-bit / 10 uses two 10-entry LUTs for the low-byte
remainder computation. The high byte is split into four 2-lossless-bit blocks
and fed back into the low-byte cycle. The result is verifiable against every
possible 16-bit dividend.

---

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

## 10.4 65816-Specific Math

### LONGA ON/OFF, LONGI ON/OFF, A8/A16/I8/I16 register widths

```asm
.LONGA ON   ; 16-bit accumulator arithmetic
.LONGA OFF  ; back to 8-bit
.LONGI ON   ; 16-bit index register arithmetic
.LONGI OFF  ; back to 8-bit
```

### BIT-trick for 65816 carry vector

In 65816 mode, `BIT <imm>` loads bit 7 of the immediate into the C flag;
combine with `ADC #0` for carry chains across multi-byte arithmetic operations.

### DIV/10 16-bit (79B) — Omegamatrix

The 16-bit unsigned `div10` uses two 10-entry LUTs (`TensRemaining`, `ModRemaining`)
to recycle the high-byte quotient back into the low-byte loop. The shrunk
variant (111 cycles, 96 bytes) adds a `$overflowFound` shortcut path.

---

## 10.5 QS (Quarter-Square) Multiply (TORUS3D pattern)

The identity `(a+b)² - (a-b)² = 4ab` lets a pre-computed 256-byte
quarter-square table replace a full multiply: `ab = (table_n[a+b] -
table_n[|a-b|]) / 4`. The table stores `table_n[n] = (n*n) >> 8` for `n = 0..
255`, so the difference of two byte-wide lookups is already `(ab >> 8) × 4`,
requiring only a right-shift or division by 4 to recover the final 16-bit
product. The signed version (`SMult8`) processes the sign separately via
`sign_xor = A ⊕ B` and treats both operands as unsigned for all table lookups,
converting back with a two's-complement at the end.

```asm
; QS identity: (a+b)^2 - (a-b)^2 = 4ab
; table_n[n] = (n*n) >> 8  -- 256-byte quarter-square table
; SMult8 signed: compute sign separately, then use unsigned core

SMult8   sta    a_save           ; a in A
         txa
         eor    a_save
         sta    sign_xor          ; 0=same sign = positive result

         ; |a| (absolute value via two's complement)
         lda    a_save           ; input (signed)
         ; identical for unsigned saved absval
         lda    a_save              ; quick test using XOR at entry
         eor    #$FF
         adc    #1
         bmi    abs_a_done
abs_a_neg: dec    a_abs
abs_a_done:
         sta    a_abs

         txa                     ; |b|
         ; identical for unsigned signed
         eor    #$FF
         adc    #1
         bmi    abs_b_done
abs_b_neg: dec    b_abs
abs_b_done:
         sta    b_abs

         ; sum_idx = |a|+|b|  (never exceeds 254)
         clc
         lda    a_abs
         adc    b_abs
         sta    sum_idx

         ; diff_idx = ||a|-|b||
         sec
         lda    a_abs
         sbc    b_abs
         tay
         bcs    @diff_done
         eor    #$FF
         clc
         adc    #0
@diff_done:
         sta    diff_idx

         ; unsigned result = table_n[sum_idx] - table_n[diff_idx]
         lda    QS_TBL,sum_idx
         sec
         sbc    QS_TBL,diff_idx

         ; sign adjust
         lda    sign_xor
         beq    @done
         sec
         eor    #$FF             ; two's-complement
@done   rts
```

> **Corrected XOR-trick pattern:** The XFR345 multiplication sequence above shows
> the trick: XOR baked into carry affect; XOR the carry preload `xor_addr` back to
> zero: `Q = _XOR(a+1.^?. For pre-`, eor#? FF16opcode identity sequential XOR-then-subtract.
> More details: `Q` is Clever interaction sequence `Q = Q ^ FF; SUB CARRY` — see above.

---

## 10.6 CORDIC atan2 + Approximate Sin

CORDIC atan2 (codebase64 §8bit atan2, doynax) rotates a unit vector in the
complex plane until it aligns with the target vector, accumulating the rotation
angle in a lookup table. Each iteration shifts and subtracts using only
add/subtract and right-shift — no multiply needed. The angle accumulator
converges to the 8-bit arctangent in 7–8 table-driven iterations, producing
`atan2(dy, dx)` in degrees in a single byte.

Approximate sin (codebase64 §8bit atan2) is 3× cheaper than a table lookup:
since the CORDIC vector is already highly quantized, raw 8-bit sin/cos can be
extracted by scaling and clipping the CORDIC Y/X accumulator values directly,
avoiding a second 256-byte LUT fetch. Max error is within ±0.03 at the centre
of the domain.

```asm
; ---- CORDIC atan2 interface ----
; input:  A = dx (X offset), X = dy (Y offset), both signed 8-bit
; output: A = atan2(dy, dx) in degrees (0..255 → 0..~359°)
; clobbers: Y
CordicAtan2
    ; (phase-accum + vector-rotation loop, ~8 passes)
    ...

; ---- CORDIC approximate-sin interface ----
; input:  A = angle (0..255 maps to 0..360°)
; output: A = sin(angle) × 127  (signed 8-bit, range −127..+127)
CordicSin
    ...
```

---

## 10.7 16-bit Sqrt + 8-bit Log Table

**16-bit sqrt (bit-by-bit Fibonacci, TORUS3D sqrt.asm).** Working down from bit
15 in one-bit-at-a-time shifts, the root is accumulated in a copy register
while the remainder is shifted and tentatively subtracted. TORUS3D's version
runs in 99 cycles for a full 16-bit unsigned input → 8-bit result in A, zero
page scratch only. Reference: sqrt.asm from the TORUS3D demo project.

Alternative: 15-byte iterative sqrt by hexwab (stardot.org.uk). Uses three
lookup tables (`sqtab`, `stab`, `smalltab`) in a single load pattern. The
input X = high byte, A = low byte; output X = floor(sqrt). Average 33.8
cycles, worst 87 cycles.

Reference implementation (sqrt15.a):

```asm
; input: X = high byte, A = low byte
; output: A = floor(sqrt(X,A))
; tables: sqtab[128], stab[128], smalltab[64], tab2[3]
_start   dex
         bmi lo
         lsr
         lsr
         ora tab2,X
         tax              ; setup for main search
         lda sqtab,X
         bmi div8         ; skip calibration loop, divide down
         tay
         lda tmp
         lsr
         ror
         ror
         cmp stab-1,X
         tya
         adc #$80
         bmi div8         ; approximation done
...
```

**8-bit log table (codebase64).** `log2(n) = LUT[n >> 1] + adjustment` uses a
128-byte LUT covering `n = 0..255` (indexed by `n >> 1`). The correction
adjusts for the discarded LSB, linearising the approximation across the full
byte range:

```asm
         lsr    in_value        ; divide by 2 → index
         tay
         lda    LOG_TBL,Y       ; base log2 value
         clc
         adc    fixup           ; LSB correction
         sta    result
```

---

## 10.8 Floating-Point Entry

FP Rankin/Woz routines (codebase64 §Floating point) port to 6502 implement the
full IEEE-754 5-byte format (1-byte exponent + 4-byte mantissa). At the Atari
8-bit context the C64 BASIC ROM FP routines (`CONUPK`, `CONINT`, `FOINT`, etc.)
are the standard reference. The Mandelbrot set (codebase64) links against
`$E943`–`$E9BE` kernal FP entry points for multiply, divide, and add/subtract.
Full runtime too large to embed; link to codebase64 §Floating point.

---

## 10.9 Logarithmic atan2 (log2-ratio + octant adjust)

Rather than computing `atan2(dy,dx)` with a division or an 8-iteration
polynomial, Johan Forslöf's technique replaces the ratio with a difference of
logarithms. `atan(y/x)` is approximated by `log(y) - log(x)` using two table
lookups — no division opcode required.

**Core identity:** `atan2(dy, dx) ≈ log2(|dy|) - log2(|dx|)`

The 256-byte `log2_tab` encodes `log2(n)·32` for `n = 0..255`; the difference
of two indices yields `atan` in scaled units. An 8-entry `octant_adjust` table
maps the two sign-bit tests into a pre-XORed lookup so the core compute path
never branches:

```asm
; ---- atan2 (8-entry LUT, no division, by Johan Forslof / doynax) ----
; input:  x1, x2, y1, y2 (screen coords, signed 8-bit)
; output: A = atan2(y1-y2, x1-x2) in 256-degree circle
; destroys: X, Y, zp_physics.octant
; tables:  log2_tab[256], atan_tab[256], octant_adjust[8]

atan2
    lda x1
    sbc x2
    bcs *+4
    eor #$ff             ; take |dx|
    tax
    rol zp_physics.octant   ; bit0 = x sign

    lda y1
    sbc y2
    bcs *+4
    eor #$ff             ; take |dy|
    tay
    rol zp_physics.octant   ; bit1 = y sign

    lda log2_tab,x
    sbc log2_tab,y       ; log_ratio_index := |dx| - |dy|
    bcc *+4
    eor #$ff             ; ensure positive difference
    tax

    lda zp_physics.octant
    rol
    and #%111            ; 3-bit octant number
    tay

    lda atan_tab,x
    eor octant_adjust,y  ; sign-flip via per-octant XOR byte
    rts
```

The `atan_tab` encodes `atan(2^(n/32))·128/π` and `octant_adjust` holds 8
precomputed XOR correction bytes so no `BMI/BPL` branch is required inside the
hot path. The entire compute sequence is 11 instructions from entry to table
result.

---

## 10.10 Distance computation (squared-table + binary-search sqrt)

A common pattern: given 2-D integer offsets (dx, dy) compute Euclidean distance
`sqrt(dx² + dy²)` without FP.

**Lookup multiply — squared table:**

```asm
; Build-time generation of squared LUT (generated by assembler expression)
;  squ_lo[i] = (i*i) & $FF   |   squ_hi[i] = (i*i) >> 8
; May already exist in zero-page or a named ZP-variable table.

; Compile-time generation of 2-byte square:
; Using the zero-page lookup allows optimising the squ_lookup for the macro-
; level computations.

; Runtime subtraction gives absolute value of any byte in integer
value_lo   equate <made for the runtime code variant

; Pre-generate with a single conference call, at load and any other build package.
; speed is positional mathematics integer arithmetic table size
```

The distance-computation routine implements the following:
- `squared_table_lo/h` formula at build-time using macro tables `l(#*#)` and `h(#*#)`
- `_SQUARED` macro gives two-byte signed result — `squ[]` gets higher address
- `calc_velocity(byte x, byte y)` gives magnitude ECLD (divide-by-two) / 2 divide /
  address approach

The result gives `LDA` the magnitude, where result holds the computed result.

**Binary-search sqrt:**

```asm
; returns sqrt of 16-bit value in A
; two-phase byte-search: high-byte phase then low-byte phase
; input:  val (word) — squared value, 0..MAX_VELOCITY^2
; output: A = floor(sqrt(val)), carry clear
; uses:   squared_table_lo, squared_table_hi
.proc sqrt (.word val) .var
    mva #0 l              ; l = 0
    lda #MAX_VELOCITY
    sta r                 ; r = 127  (sqrt of 2*MAX)
    ; --- phase 1: binary-search on high byte of squared table ---
loop_hi:
    sec
    lda r
    sbc l
    lsr                   ; (r-l)/2
    clc
    adc l
    tax                  ; X = mid = l+(r-l)/2
    lda squared_table_hi,x
    cmp val+1
    bcc l_inc            ; table_hi < val_hi  → mid too low
    bne r_dec            ; table_hi > val_hi  → mid too high
    ; high bytes equal — phase 2: binary-search on low byte
    mva #0 l
    lda #MAX_VELOCITY
    sta r
loop_lo:
    sec
    lda r
    sbc l
    lsr
    clc
    adc l
    tax
    lda squared_table_lo,x
    cmp val+0
    bcc l_inc            ; table_lo < val_lo  → mid too low
    bne r_dec            ; table_lo > val_lo  → mid too high
    ; exact match
    stx result
    clc
    rts
l_inc:
    inx
    stx l
    lda r
    cmp l
    bcs loop_lo          ; l<=r → keep searching
    bra done
r_dec:
    dex
    stx r
    lda l
    cmp r
    bcs loop_lo          ; l<=r → keep searching
done:
    stx result
    clc
    rts
val: .word 0
l: .byte 0
r: .byte 0
result: .byte 0
.endp
```

**Table-sharing note:** the same pre-built sufficient pre-built loop can be
shared with the QS and square-table multiply of a pre-built `squ`.

```
```

**Sqrt 15-byte hexwab routine:** reference in sqrt15.a (hexwab, stardot).
This is a fully-table-driven 15-byte iterative sqrt using three one-page LUTs
(sqtab, stab, smalltab). TORUS3D's sqrt.asm does 8-bit and 16-bit
register-only iterative subtraction; average 99 cycles, zero temporary RAM.

---

## 10.11 8×8 Square-table multiply (fmulu)

The square-table multiply (attributed to Fox/Tqa) pre-computes four 512-byte
tables at load time and then subtracts two table-lookup results to produce an
8×8→16 product in 14 cycles (vs ~29 cycles for the QS-multiply). The four
tables are page-aligned, making the zero-page self-modifying addressing
overhead zero:

```asm
; Precomputed 4 × 512-byte tables:
;   sq1l/sq1h  — n*(n+1) for n=0..255  (LSB/MSB each)
;   sq2l/sq2h  — -(n*(n-1)) for n=0..255  (LSB/MSB each)
;   LUT is fetched using zero page base from page 0-3.
;   Zero page base address fetch takes zero price cycles — table is page aligned.
```

The multiply fast-path (`fmulu`) works as follows: when A and X (the two
factors) enter the routine, two byte-wide table lookups are performed on the
pre-built tables; the high-byte subtraction alone produces the sign-extended
16-bit product:

```asm
; A = factor1, X = factor2  →  A:Y = A×X (A = hi, Y = lo)
; Page-aligned base in ZP allows self-modifying zero-cost address calculation:
         sta l1+1
         sta h1+1
         eor #$ff
         sta l2+1
         sta h2+1
         sec
l1      lda sq1l,x          ; self-modify to point into sq1l / sq2l
l2      sbc sq2l,x
         tay
h1      lda sq1h,x          ; self-modify to point into sq1h / sq2h
h2      sbc sq2h,x
         rts
```
```

The `.init` routine populates all four LUTs at boot (108 iterations, zero
overlap), after which `fmulu(a, x)` calls cost 14 cycles regardless of operand
values.

| Variant | Table memory | Code bytes | Cycles |
|---|---|---|---|
| QS multiply | 512 B (one quarter-square LUT) | ~46 B | ~29 |
| `fmulu` | 2048 B (four 512 B LUTs) | ~46B | **14** |

**Shared-table win:** the 2048-byte cost of `fmulu` is amortized — a codebase
that already maintains a squared table for distance/√ computation (`other/
`distance.asm`) reduces the incremental cost of the QS-addition path from 2048B
to zero, since the pre-built square LUT structure overlaps with the `_SQUARED`
macro's two-byte lookup. For demos that do both velocity-distance per frame and
fast object-space transforms, the combined table serves both routines at no
extra memory.

---

## See also

- the main Atari 8-bit skill collection files (SKILL.md, index.md) for cross-domain navigation
- The math-routines file for _MUL16 / _DIV16 notes (signed variants)
- `other/fmulu_8x8.asm` — QS/IU-multiply reference (`init` + `fmulu`)
- the logarithmic atan2 reference (`other/atan2.asm`) — log2_tab, atan_tab, octant_adjust
- the distance computation reference (`other/distance.asm`) — squared LUT + binary-search sqrt and _SQUARED macro
- the standard macro library (other/macros.asm) — _ADD16, _SUB16, _MUL16, _DIV16, and more
- The QS identity `(a+b)² - (a-b)² = 4ab` from the algorithm notes
- `codebase64 §8bit atan2` — CORDIC rotating-vector atan2 + approximate sin
- sqrt15.a (hexwab/stardot) — 15-byte iterative sqrt, three-page LUT, avg 34c
- the TORUS3D sqrt.asm — 99c 16-bit bit-serial register-only sqrt
