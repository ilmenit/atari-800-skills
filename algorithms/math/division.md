# Division

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
