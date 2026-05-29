# Sqrt Log

## 10.7 16-bit Sqrt + 8-bit Log Table

For general `sqrt(word)` choose one of two patterns:

- For small bounded magnitudes, use the squared-table binary search in §10.10.
- For full 16-bit input without table dependency, use a bit-serial restoring
  square root. It is slower but uses only root/remainder scratch bytes.

```asm
; contract for a table-free restoring sqrt:
; in:  NUMH:NUML unsigned 16-bit
; out: ROOT = floor(sqrt(NUMH:NUML)), REM = remainder
; clobbers: A, X, Y, C
; invariant after return: original_number = ROOT*ROOT + REM
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
