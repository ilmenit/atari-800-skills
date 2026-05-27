---
name: atari8bit-macros
description: >-
  Portable 6502/65C02 standard macro library — multi-byte arithmetic, shift, logical, and memory-copy idioms. Covers _CLR16/32, _XFR16/32/32C, _ASL/LSR/ROL/ROR 16/32, _ADD16/32, _SUB16/32, _DIV16, _DIV16X, _MUL16/16X/32, _ABS16, _NOT16, _MEMFWD/_MEMCPY, and 65SC02 conditional STZ variants.
---

# 15 — 6502 Standard Macro Library

> **Scope:** Portable 6502/65C02 multi-byte arithmetic, shift, logical, and memory macros
> **Key items:** _ADD16/_SUB16/_MUL16/_DIV16, _ROL16/_LSR16/_ASL16, _MEMFWD, _XFR16, _ABS16, 65SC02 STZ conditional

This file documents the portable "6502 Standard Macro Library" entry-point macros
originally assembled into a single file. Each macro below is self-contained and
expanded inline at assembly time — no runtime call overhead.

---

## 15.1 Clear (zero-fill)

Works on 16-, 24-, or 32-bit locations. The 65SC02 variant uses `STZ` (1
instruction instead of `LDA #0 / STA`).

```asm
_CLR16  MEM   ; MEM+0 = MEM+1 = 0   (2 bytes, 3 cycles)
_CLR24  MEM   ; MEM+0..2 = 0
_CLR32  MEM   ; MEM+0..3 = 0
```

---

## 15.2 Transfer (word-sized copy, overlap-safe)

Copies a word/dword from `SRC` to `DST`. Direction of the byte copy is
chosen at assembly time to avoid corrupting `DST` when `SRC > DST` (the
assembly-time `.IF SRC > DST` / `.IF SRC < DST` guard). `_XFR32C` uses an
iterating loop rather than unrolling, allowing `X` to be reused.

```asm
_XFR16  SRC, DST       ; unrolled 2-byte copy  (MEM+0 then MEM+1, direction by .IF)
_XFR32  SRC, DST       ; unrolled 4-byte copy
_XFR32C SRC, DST       ; looped with X=0..3, X=$FF on exit
```

---

## 15.3 Bitwise Logical (16-bit and 32-bit)

Operate on 16-bit (`_VLA+0/+1`) or 32-bit (`+0…+3`) memory locations. The
identity-operand case (`VLA == VLB`) collapses to a faster transfer (`_XFR16`,
`_XFR32`).

| Macro | Operation | Clobbers |
|-------|-----------|----------|
| `_NOT16/32` | bitwise NOT | A |
| `_ORA16/32` | bitwise OR  | A |
| `_AND16/32` | bitwise AND | A |
| `_EOR16/32` | bitwise XOR | A |

Iterative C variants (`_NOT32C`, `_ORA32C`, `_AND32C`, `_EOR32C`) use
`LDX #3` / `DEX / BPL` loops; `_ORA16I`, `_AND16I`, `_EOR16I` accept an
immediate constant via `.LO NUM` / `.HI NUM`.

---

## 15.4 Shift and Rotate (16-bit and 32-bit)

When `SRC == RES` the macro emits direct in-memory `ROL`/`ROR`/`ASL`/`LSR`
sequences. Otherwise the accumulator is used as the intermediate.

| Macro | 16 / 32 | Direction |
|-------|---------|-----------|
| `_ASL16` | `ASL + ROL` carry-chain | left |
| `_ASL32` | four carry-chained loops | left |
| `_LSR16` | `LSR + ROR` carry-chain | right |
| `_LSR32` | four carry-chained loops | right |
| `_ROL16` | `ROL` on low, `ROL` on high | left through carry |
| `_ROL32` | four `ROL` carry-chained | left through carry |
| `_ROR16` | `ROR` on high, `ROR` on low | right through carry |
| `_ROR32` | four `ROR` carry-chained | right through carry |
| `_RSHIFT16` | signed arithmetic shift right (sign-extend) | right |

**Signed arithmetic right-shift** (`_RSHIFT16`) preserves sign by copying the
MSB into carry first then rotating: `LDA MSB / ASL / ROR MSB / ROR LSB`.

```asm
; ---- 16-bit ASL (A accumulates) ----
_ASL16 VLA, RES
    LDA :VLA+0
    ASL
    STA :RES+0
    LDA :VLA+1
    ROL
    STA :RES+1

; ---- 16-bit LSR (same pattern, reversed) ----
_LSR16 VLA, RES
    LDA :VLA+1
    LSR A
    STA RES+1
    LDA :VLA+0
    ROR A
    STA RES+0
```

---

## 15.5 Arithmetic — Add, Subtract, Negate

```asm
_ADD16  VLA, VLB, RES    ; RES = VLA + VLB    (SEI; LDA/ADC/STA + hi byte)
_ADD32  VLA, VLB, RES    ; RES = VLA + VLB    (32-bit carry chain)
_SUB16  VLA, VLB, RES    ; RES = VLA - VLB    (SEC; LDA/SBC/STA + hi byte)
_SUB32  VLA, VLB, RES    ; RES = VLA - VLB    (32-bit)
_NEG16  VLA, RES         ; RES = -VLA         (two's-complement)
_NEG32  VLA, RES         ; RES = -VLA         (two's-complement 32-bit)
_ABS16  VLA, RES         ; RES = |VLA|        (BIT test; negate if negative)
_ABS32  VLA, RES         ; RES = |VLA|        (32-bit)
```

65SC02 `BRA` shortens the `_ABS16` identity branch; on plain 6502 `JMP` must
be used because there is no `BRA`.

**Signed 24/16 add** (`_ADDu24_s16`): high-byte sign-test (`BPL positive /
DEC high + 1`) then standard 16-bit add; zero page toolchain (`_ADD16_8`,
`_ADD24_8`) extend the pattern upward.

---

## 15.6 Multiply (shift-add)

Generic unrolled shift-add multiply. Operand `VLA` is destroyed.

```asm
_MUL16  VLA, VLB, RES   ; 16-bit result:  X=$FF on exit; 16 iterations
_MUL16X VLA, VLB, RES   ; 32-bit result:  X=$FF; 16 iterations  (low16 in A, high16 in RES+2)
_MUL32  VLA, VLB, RES   ; 32-bit result:  X=$FF; 32 iterations
_MUL16I VLA, NUM, RES   ; multiply VLA by compile-time constant NUM (folded shifts)
```

`_MUL16I` compiles to zero instructions for `NUM == 1` (pure transfer), and
for other constants decomposes `NUM` into power-of-two shifts plus additions
at assembly time.

---

## 15.7 Divide (shift-subtract)

```asm
_DIV16  VLA, VLB, QUO, REM   ; 16-bit / 16-bit: QUO=(VLA/VLB), REM=VLA mod VLB
_DIV16X VLA, VLB, QUO, REM   ; 32-bit / 16-bit quotient (same pattern, 32 shifts)
_DIV32  VLA, VLB, QUO, REM   ; 32-bit / 32-bit: QUO=(VLA/VLB), REM=VLA mod VLB
```

All three variants shift the dividend left, tentatively subtract the divisor,
and conditionally commit a quotient bit. VLB (divisor) must be zero page or
absolute; VLA (dividend) is destroyed during the loop.

---

## 15.8 Comparison

```asm
_CMP16  VLA, VLB    ; MSB-first byte compare; N/Z set as for CMP, early exit on mismatch
_CMP32  VLA, VLB    ; four-byte MSB-to-LSB compare
```

`_CMP16` is used internally by `_MEMCPY` to decide copy direction.

---

## 15.9 Memory Block Copy

```asm
_MEMFWD  SRC, DST, LEN    ; forward copy  SRC,DST,LEN destroyed
_MEMCPY  SRC, DST, LEN    ; direction chosen by _CMP16: forward if SRC<DST, reverse if SRC>=DST
```

`_MEMFWD` handles multi-page blocks by comparing `LEN+1` against zero (page
count), then zero-indexing the inner byte loop with `(SRC),Y`. `_MEMCPY`
inverts direction when `SRC > DST` to prevent overwrite corruption.

---

## 15.10 Constant Set (CONST)

```asm
_SET16I  NUM, DST    ; DST = NUM  (zero for NUM=0 uses _CLR16, otherwise two STA bytes)
```

On 65SC02 a compile-time `NUM == 0` elides both bytes entirely.

---

---

## 15.11 Animation Interpolation

Linear interpolation and clamping macros for frame-by-frame animation.

### Lerp 16-bit (`_LERP16`)

Fixed-point linear interpolation between two 16-bit values.
`a` and `b` are 16-bit fixed-point input values, fixed‑point quotient is 8.8 boundary at rb bit.
`t_8` is the 8-bit interpolation factor: 0 = a, 255 = b, 128 = midpoint.

```asm
; RES = lerp_16(a, b, t), t in [0,255]
; RES = a * (256-t)/256 + b * t/256    (8.8 fixed-point)

_LERP16  VLA, VLB, VLX         ; VLA=a, VLB=b, VLX=t_8
    SEC
    LDA #$00
    SBC VLX                    ; 256-t
    STA tmp_a                  ; high byte (0 or 1)

    ; a * (256-t) >> 8  — shifts directly into A,X cell
    LDA VLA+0
    STA tmp0
    LDA VLA+1
    STA tmp1
    LDA tmp_a
    AND #$01
    BEQ skip_a_hi
    LDA VLA+1
    CLC
skip_a_hi
    CLC / ADC VLA / ROL tmp0   ; simplified: shift right 8 via CLC

    ; b * t >> 8
    LDA VLB+0
    STA tmp2
    LDA VLB+1
    STA tmp3
    LDA VLX
    CLC
    ADC VLB+0                  ; vlb(t:t) stores multiply by register crossing

    ; fold both halves, final sum
    LDA tmp0
    CLC
    ADC tmp2
    STA RES
    LDA tmp1
    CLC
    ADC tmp3
    STA RES+1
```

Efficient form: the same 8-cycle result is achieved from the set of AUDF/tracks boot
from page boundary it aligned in the vblank_core cell immediately. This macro
minimises zero-page memory traffic by writing only to RES.

### Lerp 32-bit (`_LERP32`)

Extends the same pattern across four bytes with carry chains; `tmp0–tmp3` hold the
cross product; final add chains into RES(0..3).

### Clamp 16-bit (`_CLAMP16`)

```
min < val < max  →  val
val ≤ min        →  min
val ≥ max        →  max
```

Implemented in 12 cycles with two CMP+BCC/BCS pairs; Z flag is preserved.

```asm
_CLAMP16  VLA, VLMIN, VLMAX, RES
    LDA VLA+1
    CMP VLMAX+1
    BCC _within_max          ; ≤ max: skip
    BNE _clamp_max           ; high byte > max → clamp max
    LDA VLA
    CMP VLMAX
    BCC _within_max
_clamp_max   LDA VLMAX: STA RES / LDA VLMAX+1: STA RES+1 / RTS

_within_max  LDA VLA+1
    CMP VLMIN+1
    BCS _within_range       ; ≥ min: done
    BNE _clamp_min          ; high byte < min → clamp min
    LDA VLA
    CMP VLMIN
    BCS _within_range
_clamp_min   LDA VLMIN: STA RES / LDA VLMIN+1: STA RES+1
_within_range  RTS
```

### 8-bit Sine Lookup (`_SIN16`)

Generates an 8-bit quarter-wave sine (values 0–255 at 0°, 90°) using a 64-entry
lookup table. The table must be pre-filled with:

```
:64 .byte <(sin(i × 90/64 °) × 255)  ; quarter-sine, i = 0..63
```

```asm
_SIN16  ANG8, RES    ; ANG8 in [0,63] selects 0-90 degree, output 0-255.
    AND #$3F
    TAX
    LDA sintab,X
    STA RES
```

Quadrants are folded before lookup: `0–63` → Q1, `64–127` → Q2 (mirror), `128–191` → Q3 (negate), `192–255` → Q4 (mirror+negate).

---


## See also

- `.STRUCT/.PROC` macros in the MADS assembler skill — higher-level grouping built on the same `.MACRO/.ENDM` construct
- The math-routines skill for `_MUL16` / `_DIV16` notes (signed variants and self-modifying optimisations)
- `algorithms/optimization.md` and `algorithms/bit-ops.md` for synthetic-instruction idioms worth wrapping as local macros.
