# Zero Page and Stack

## Allocation

Use the [base-map ownership table](base-map.md#zero-page-zones). OS zero page
is not a general scratch area while OS services or interrupts are active.
Declare each routine's scratch bytes and whether they may be shared with an ISR.

## Multi-byte operations (partial snippets)

```asm
; Increment an unsigned little-endian word modulo 65536. Clobbers N/Z.
        inc ptr
        bne increment_done
        inc ptr+1
increment_done

; Decrement a word modulo 65536. Clobbers A/N/Z; leaves C unchanged.
        lda ptr
        bne decrement_low
        dec ptr+1
decrement_low
        dec ptr
```

Do not increment the high byte unconditionally. INC/DEC do not propagate carry.
A `DEY/BPL` loop only naturally covers counts up to 128; larger byte spans
need a loop whose termination contract handles the full unsigned range.

## Inline parameters after JSR

JSR pushes the address of its final operand byte. Adding one locates the first
inline data byte. If a callee consumes inline parameters, it must also advance
the saved return address past them and preserve/rebuild the caller's stack.
Simply pulling both return bytes and executing RTS discards the return address
and makes RTS consume unrelated stack contents.

Prefer ordinary A/X/Y parameters or an explicitly allocated pointer unless an
inline convention provides a demonstrated size advantage. Document parameter
length, pointer scratch, stack effects, and interrupt/reentrancy assumptions.
