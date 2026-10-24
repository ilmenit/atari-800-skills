# Multiplication

Use [multiplication.asm](../../examples/routines/multiplication.asm) for the
maintained table-free routines. These are include-only building blocks; the
caller chooses an ORG and includes the data/scratch definitions with the code.

## Contracts

All entries require NMOS 6502 binary mode (D=0), preserve Y, and may clobber
A/X and arithmetic flags. They share writable scratch and are non-reentrant.
No zero-page addresses are reserved. Results are little-endian in `mul_result`.

| Entry | Input | Output / overflow | Validation |
|---|---|---|---|
| `mul3_u16` | `mul_a`, unsigned word | Low 16 bits of 3*a | All 65,536 inputs |
| `mul10_u16` | `mul_a`, unsigned word | Low 16 bits of 10*a | All 65,536 inputs |
| `mul96_u8` | A, unsigned byte | Exact 16-bit A*96; overwrites `mul_a` | All 256 inputs |
| `mul8_u16` | A and X, unsigned bytes | Exact 16-bit A*X | All 65,536 pairs |
| `mul16_u32` | `mul_a` and `mul_b`, unsigned words | Exact 32-bit product; destroys `mul_b` | Boundary matrix and 512 seeded cases |

The 8-bit reference performs eight shift/add iterations; the 16-bit version
performs sixteen. Addition paths depend on multiplier bits, so cycle counts
are data-dependent. Measure the assembled variant before claiming a speed or
size advantage; include JSR/RTS, addressing modes, page crossings, and DMA.

## Table-based alternative

[Quarter-square multiplication](quarter-square.md) trades 1022 bytes of tables
for fewer arithmetic operations. Its sum index needs nine bits even though both
operands are bytes. It is also checked against every unsigned byte pair.

These implementations prioritize an explicit contract and reproducible tests.
Specialized self-modifying square-table routines can be faster, but need their
own initialization, writable-code, carry, table-boundary, and timing validation.
The former unsupported 14-cycle/512-byte claims are not portable guarantees.

## 65816 arithmetic

The W65C816S has a 16-bit ALU but no built-in multiplier and no intrinsic
registers at `$4202/$4203`. Memory-mapped arithmetic units belong to particular
host systems or expansions; their addresses are not portable CPU features.
Use software arithmetic on Atari unless the selected expansion explicitly
provides and documents an arithmetic unit.

Source: [WDC W65C816S datasheet, 2024-03-13](https://www.westerndesigncenter.com/wdc/documentation/w65c816s.pdf),
processor block diagram and instruction set. Run [the validation suite](../../tooling/validation.md)
for the implementation-specific checks above.
