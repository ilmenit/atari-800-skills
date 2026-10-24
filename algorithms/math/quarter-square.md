# Quarter-Square Multiplication

For unsigned bytes a and b:

```
a*b = floor((a+b)^2/4) - floor(abs(a-b)^2/4)
```

The two arguments have the same parity, so integer truncation cancels exactly.
`a+b` ranges from 0 to 510 and needs **nine bits**. Putting only its low byte
in X silently breaks products whose operand sum exceeds 255.

Use [quarter-square.asm](../../examples/routines/quarter-square.asm), the
canonical include-only implementation. It selects the lower or upper 256-entry
part of each table using the saved carry from the sum.

- Input: A and X are unsigned bytes; decimal mode must be clear.
- Output: `prod_lo/prod_hi` hold the unsigned 16-bit product.
- Clobbers: A/X/Y and arithmetic flags; three private scratch bytes.
- Memory: 511 low bytes + 511 high bytes = 1022 table bytes, plus code and scratch.
- Ownership: writable scratch, non-reentrant; use separate storage or serialization
  if main code and an interrupt can both call it.
- Validation: all 65,536 operand pairs are checked by `scripts/validate.py`.

For signed inputs, preserve the result sign, convert operands to unsigned
magnitudes, multiply, then negate the 16-bit result if needed. Include -128
in signed boundary tests. Table-free alternatives are in [multiplication.md](multiplication.md).
