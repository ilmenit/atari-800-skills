# ANTIC Display-List Instructions

ANTIC reads its hardware display-list pointer from DLISTL/H (`$D402/$D403`).
The OS shadows are SDLSTL/H (`$0230/$0231`), copied during VBI. A display list
contains instruction bytes and, for jumps/LMS, little-endian addresses.

## Encoding

The low nibble selects the instruction class. Interpret the high bits only
after identifying that class; `$4x` does not universally mean LMS.

| Low nibble | Meaning | Other bits | Address bytes |
|---|---|---|---|
| 0 | Blank | Bits 4–6 encode height minus one (0–7); bit 7 requests DLI | None |
| 1 | Jump | Bit 6 adds wait-for-vertical-blank; bit 7 requests DLI | Two |
| 2–F | Character/bitmap mode | Bit 4 HSCROL, bit 5 VSCROL, bit 6 LMS, bit 7 DLI | Two only with LMS |

Examples:

| Byte | Meaning |
|---|---|
| `$00` | One blank scanline |
| `$70` | Eight blank scanlines |
| `$01` | Jump to the following address |
| `$41` | Jump and wait for vertical blank (JVB) |
| `$42` | Mode 2 with LMS |
| `$44` | Mode 4 with LMS |
| `$4C` | Mode C with LMS; **not JVB** |
| `$74` | Mode 4 with LMS and both scrolling flags |
| `$8E` | Mode E with DLI on its final scanline |

Display-list fetches wrap within a 1K block, including address operands.
Use a jump to continue into another block; keep all three bytes of that jump
inside the current block. Playfield data has a separate 4K address-wrap rule:
insert LMS instructions before a fetched row would cross it.

`$C1` is JVB with the DLI flag. Its internal replay can request a DLI on every
scanline until vertical blank. Ordinary JVB `$41` does not request DLIs.
A handler that overruns into another DLI can nest and overflow the CPU stack;
there is no universal fixed number of safe nested DLIs.

For normal-width dimensions, see [character modes](../../graphics/character-modes.md)
and [bitmap modes](../../graphics/bitmap-modes.md). A complete 192-line mode-E
list with explicit memory blocks is in [bitmap-dli-vbi.asm](../../examples/bitmap-dli-vbi.asm).

Source: [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §4.6.
