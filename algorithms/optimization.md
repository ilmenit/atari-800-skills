---
name: atari8bit-6502-optimization
description: >-
  6502 assembly optimization patterns for Atari 8-bit code: tail calls, RTS
  jump tables, split pointer tables, flag-preserving tests, compare-free loops,
  EOR bit blending, stack temporaries, BIT skip tricks, and LUT tradeoffs.
---

# 6502 Optimization Patterns

> **When to load:** The task is to make Atari 8-bit assembly faster, smaller, more constant-time, or easier to fit into a DLI/VBI budget.
> **Do not use for:** CPU opcode legality or cycle tables; load `hardware/cpu.md`.
> **Primary sources:** `articles/6502-optimization.md`, `atari-documentation/tips/6502_tips.txt`, `articles/6502-synthetic-instr.md`.

## Quick Lookup

| Need | See |
|---|---|
| Remove subroutine overhead | §1 |
| Faster pointer/jump tables | §2 |
| Flag-preserving tests | §3 |
| Compare-free loops | §4 |
| LUT speedups | §5 |
| Size-saving tricks | §6 |
| Hardware/register safety | §7 |

## 1. Remove Unneeded Calls

Tail-call a final `JSR` by replacing `JSR target / RTS` with `JMP target`.

```asm
; before
        jsr   SomeRoutine
        rts

; after
        jmp   SomeRoutine
```

Savings: 1 byte and 9 cycles. Use this for dispatchers, state machines, and routines that end by handing control to another routine.

Inline a subroutine that is called exactly once. Prefer a macro if the code is conceptually shared but should expand inline. Be careful when inlining into branch-heavy code because relative branches still have a +/-127 byte reach.

## 2. Pointer and Jump Tables

Split 16-bit pointer tables into low/high byte tables. This avoids `ASL` and indexed 16-bit table fetches.

```asm
        ldx   entry
        lda   PtrLo,x
        sta   ptr
        lda   PtrHi,x
        sta   ptr+1

PtrLo   .byte <State0, <State1, <State2
PtrHi   .byte >State0, >State1, >State2
```

Use the RTS trick for jump tables when stack depth is safe. Table entries must be target-1 because `RTS` increments the pulled address.

```asm
        ldx   entry
        lda   JumpHi,x
        pha
        lda   JumpLo,x
        pha
        rts

JumpLo  .byte <(State0-1), <(State1-1)
JumpHi  .byte >(State0-1), >(State1-1)
```

This avoids a zero-page temp pointer and is reentrant as long as the stack is not near overflow. Do not use inside deep interrupt nesting unless stack depth has been audited.

## 3. Flag-Preserving Tests

Use `BIT` when you need N/V/Z from memory without destroying A.

```asm
        bit   flags       ; N=bit7, V=bit6, Z=(A & flags)==0
```

Use `EOR` instead of `CMP` when equality must preserve carry and A may be clobbered.

```asm
        eor   value
        beq   equal
```

If A must be restored, `EOR value` again on both paths. This is still often faster than `PHP/CMP/PLP`.

Test whether all masked bits are set while preserving carry:

```asm
        eor   #$ff
        and   #%11000011
        beq   all_set
```

Blend selected bits from `src` into `dst` with fewer accumulator operations:

```asm
; dst = ((src ^ dst) & mask) ^ dst
        lda   src
        eor   dst
        and   mask
        eor   dst
        sta   dst
```

## 4. Compare-Free Loops

Choose loop direction and terminal values so `INX/DEX/INY/DEY` flags are enough.

```asm
; X counts 256 iterations
        ldx   #0
loop    ; work
        inx
        bne   loop

; X counts down through 0
        ldx   #count-1
loop2   ; work
        dex
        bpl   loop2
```

Avoid `CMP #0` after any instruction that already sets Z/N (`LDA`, `ADC`, `SBC`, `AND`, `ORA`, `EOR`, `INX`, `DEX`, `INC`, `DEC`, shifts/rotates).

Special constants can be tested by clobbering a register:

```asm
        ldx   value
        inx
        beq   was_ff

        ldx   value
        dex
        beq   was_01
```

## 5. LUT Speedups

Use an identity table when X or Y must act as an operand to A without a temp byte.

```asm
        ldx   foo
        lda   bar
        clc
        adc   Identity,x

Identity
        .byte 0,1,2,3,4,5,6,7
        ; continue through 255
```

Use small LUTs for frequent shifts, row offsets, screen addresses, character offsets, and nibble transforms. A 16-byte `value*16` table can replace four `ASL` instructions when X is free.

## 6. Size-Saving Tricks

Use the stack instead of a temporary byte when speed is not critical and stack depth is safe.

```asm
        lda   foo
        pha
        lda   bar
        ; work
        pla
```

Use a known flag state for relative branches instead of absolute `JMP` when the target is in range.

```asm
        lda   #1
        bne   target       ; Z is known clear
```

Use `BIT` opcode bytes (`$24` zero-page, `$2C` absolute) to skip following one- or two-byte instructions for compact multi-entry routines.

```asm
entry5  lda   #5
        .byte $2c          ; BIT abs skips next 2 operand bytes
entry7  lda   #7
        .byte $2c
entry11 lda   #11
common  sta   target
        rts
```

## 7. Atari Hardware Safety

Some generic 6502 tricks are unsafe on Atari hardware:

- Do not use RMW instructions on hardware registers unless the double-write side effect is intended.
- Do not point `BIT abs` skip operands at read-sensitive hardware addresses.
- Do not use RMW-on-ROM/table tricks on cartridge/PBI/register ranges with bus conflicts or side effects.
- In DLI/VBI code, cycle savings matter only if they do not introduce stack depth, page-cross, or hardware-register hazards.

## See Also

- `algorithms/bit-ops.md` — synthetic instructions, rotates, sign extension, carry/flag idioms.
- `hardware/cpu.md` — cycle timing, dead cycles, undocumented opcodes.
- `tooling/mads-assembler.md` — macros for inlining these patterns safely.
