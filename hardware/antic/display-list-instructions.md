# Display List Instructions

## 3.2  Display List Instructions (Bitmask Encoding)

DL is a stream of 1-byte or 3-byte instructions; pointer held in `DLISTL/DLISTH` at `$230/$231`. The instruction register (ANTIC internal) is loaded each scan line.

### Instruction byte format

```
D7 D6 D5 D4 D3 D2 D1 D0
DL LMS VSC HSC MODE3..0
```

| Bit | Name | Set → |
|---|---|---|
| 7 | DLI | Fire DLI on last scan line of this instruction |
| 6 | LMS | Load Memory Scan counter (requires 2 extra address bytes, LSB first) |
| 5 | VSCROLL | Enable vertical fine-scroll for this mode line |
| 4 | HSCROLL | Enable horizontal fine-scroll for this mode line |
| 3–0 | MODE | `$0`=blank, `$1`=JVB, `$2–$F`=ANTIC modes 2–15 |
### Display-list instruction byte — complete encoding (8-bit)

Each DL instruction is read into the internal Instruction Register (IR) and executed
at the start of the mode line. LMS and JVB instructions span 2 extra bytes (LSB first).

```
    D7  D6  D5  D4  D3  D2  D1  D0
    ┌───┬───┬───┬───┬───┬───┬───┬───┐
    │DL │LMS│VSC│HSC│ IR mode (0-3)  │
    └───┴───┴───┴───┴───┴───┴───┴───┘
```

| Byte value | IR mode | DL | LMS | VSC | HSC | Extended bytes | Description |
|---|---|---|---|---|---|---|---|
| `$0x` | 0 (blank) | n/a | 0 | 0 | 0 | 0 | Blank mode line (x=blank scan count 0–15) |
| `$4x` | 0 (blank) | 0 | 1 | 0 | 0 | 2 | Blank + LMS (load memory scan address) |
| `$1x` | 1 (JVB/JMP) | n/a | x | x | x | 2 | Jump to new DL address; `$41` also suspends DMA |
| `$2x` | 2 | 0 | 0 | 0 | 0 | 0 | Mode line mode 2 (40-col, 1 KB, 2 colors) |
| `$3x` | 3 | 0 | 0 | 0 | 0 | 0 | Mode line mode 3 (40-col, 1 KB, 2 colors, 10-line) |
| `$4x` | 4 | 0 | 1 | 1 | 0 | 2 | Mode 4 + vertical-scroll + LMS |
| `$5x` | 5 | 0 | 1 | 0 | 0 | 2 | Mode 5 + LMS |
| `$6x` | 6 | 0 | 0 | 0 | 0 | 0 | Mode 6 (20-col, 512 B, 5 colors) |
| `$7x` | 7 | 0 | 1 | 0 | 0 | 2 | Mode 7 + LMS |
| `$8x` | 8 | 0 | 0 | 0 | 0 | 0 | Mode 8 (40 px, 4 colors, 4×8) |
| `$9x` | 9 | 0 | 0 | 0 | 0 | 0 | Mode 9 (80 px, 2 colors, 2×4) |
| `$Ax` | A | 0 | 0 | 0 | 0 | 0 | Mode A (80 px, 4 colors, 2×4) |
| `$Bx` | B | 0 | 0 | 0 | 0 | 0 | Mode B (160 px, 2 colors, 1×2) |
| `$Cx` | C | 0 | 0 | 0 | 0 | 0 | Mode C (160 px, 2 colors, 1×1) |
| `$Dx` | D | 0 | 0 | 0 | 0 | 0 | Mode D (160 px, 4 colors, 1×2) |
| `$Ex` | E | 0 | 0 | 0 | 0 | 0 | Mode E (160 px, 4 colors, 1×1) |
| `$Fx` | F | 0 | 0 | 0 | 0 | 0 | Mode F (320 px, 2 colors hires, 1×1) |

**Blank mode lines — IR mode 0:** Bits 4–6 encode a scan-line repeat count 1–8;
`$00`–`$07` = 1–8 blank lines with DLI permitted if bit 7 set.

**JVB — IR mode 1 + bit 6 set (`$41`):** Suspends display-list DMA until vertical blank;
re-executes every scan line 8–248 of the *next* frame. DLI bit 7 set on JVB = 241 DLIs/frame
(stack depth ~25 — never stack DLIs beyond that depth).

**LMS (Load Memory Scan) — IR mode 2–F + bit 6 set:** Two extra bytes (LSB first) write to
the memory scan counter for the next scan line. Used for page-per-line scrolling or to cross
4K playfield boundaries. Minimum one LMS at top of every display list to initialize playfield address.

**Display list cannot cross 1K boundary.** DLISTL/DLISTH wrap within 1K unless the current
instruction is JVB, in which case new values are loaded from the two address bytes.

### Instruction summary

| IR | Type | Extra bytes | Notes |
|---|---|---|---|
| `$x0` | Blank line | 0 | high nibble = blank scan line count (1–8) |
| `$x1` | Jump | 2 addr | loads `DLISTL/ DLISTH`; `$41`=JVB (wait-for-VBI, re-executed) |
| `$x2–$xF` | Mode line | 0 (or +2 if LMS) | `$44`=Mode4+LMS, `$74`=Mode4+VSC+HSC+LMS |

JL command `$x1` followed by LMS bit 6 (`$41`/`$46`) = "Jump and Wait for Vertical Blank"; display list DMA is suspended and re-execution occurs at cycle 0 of scan line 8 of the *next* frame. **DLI on JVB = DLI every scan line 8–248 (241 possible DLIs), stack depth limited to ~25.**

### Playfield modes at a glance

| IR | OS Mode | Colors | Resolution | Pixels/line (normal) |
|---|---|---|---|---|
| 2 | 0 | 2 (BAK/PF2) | 40×24 chars | 320 |
| 4 | n/a | 4+1 (BAK, PF0–2, optional PF3) | 40×24 chars | 160 |
| 5 | 1 | 4+1 | 20×12 chars | 80 |
| 6 | 2 | 5 (BAK + PF0–3) | 20×24 chars | 160 |
| 7 | 3 | 5 | 10×12 chars | 80 |
| 8–F | 8–15 | 2–4 hires fill | 40–320 dots | 40–320 |

---
