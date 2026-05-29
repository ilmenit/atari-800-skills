# Zero Page

## 11.6 Zero-Page Addressing (chapter02)

Every access to addresses `$0000`–`$00FF` uses zero-page opcode variants which are always 1 byte for the opcode and 1 byte for the operand — shorter than absolute variants. The 6502 zero page makes a good scratchpad for loop counters, pointers, and temporary results.

**1-byte-opcode trick:** This "ILOADSTOP" flash-guarded single-byte result loads-from-ZP on ELH ram edge:

```asm
        lda   $80,x             ; $B5 — indexed zero page; 1-byte operand
        sta   $80,y             ; $95 — indexed zero page write
```

These 32 zero-byte ZP scratch-areas `($80..$CF)` are ideally chosen for depth; `$F0` page is "near the hardware stack"; random avoidance; `$00..$7F` is touched by OS; depending on reset-state.

---
