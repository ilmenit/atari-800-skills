---
name: atari8bit-crt-editor
description: >-
  Atari 8-bit ATASCII screen-code table, CIO GET/PUT/PRINT via CIOV, key scancodes, number-base on-screen rendering.
---

# 08 — CRT Editor & Screen I/O

> **Key items:** ATASCII $1B/$9B/$7D/$7E/$7F; CIOV $E456; IOCB $0340; KBCODE; ATASCII vs screen codes
> **Scope:** ATASCII screen codes, CIO GET/PUT/PRINT, key scancodes, number formatting

## Quick-lookup

| Need | See § |
|---|---|
| ATASCII screen codes table | §8.1 |
| IOCB table + CIO GET/PUT/PRINT boilerplate | §8.2 |
| Raw KBCODE read and modifier bits | §8.3 |
| Hexadecimal digit encoding | §8.4 |
| Decimal buffer sizing and conversion contracts | §8.4 |

## 8.1 ATASCII Screen Code Table

ATASCII is the byte-oriented character/control encoding used by OS text I/O.
ANTIC screen RAM uses a different code order. For example, ATASCII space is
`$20`, but the corresponding screen code is `$00`. Bit 7 has mode-dependent
attribute behavior; do not treat all control bytes as printable glyphs.

**ATASCII to Screen Code Mapping:**

| ATASCII | Screen Codes |
|---|---|
| `$00..$1F` | `$40..$5F` |
| `$20..$5F` | `$00..$3F` |
| `$60..$7F` | `$60..$7F` |
| `$80..$9F` | `$C0..$DF` |
| `$A0..$DF` | `$80..$BF` |
| `$E0..$FF` | `$E0..$FF` |

**Control Characters (16 codes):**

| Code | Dec | Name | Behaviour |
|------|-----|------|-----------|
| `$1B` | 27 | ESCAPE | Disables interpretation of control characters (except EOL). Next char is printed raw. |
| `$1C` | 28 | CURSOR UP | Move cursor up. Wraps to bottom if at top. |
| `$1D` | 29 | CURSOR DOWN | Move cursor down. Wraps to top if at bottom. |
| `$1E` | 30 | CURSOR LEFT | Move cursor left. Wraps to right if at left edge. |
| `$1F` | 31 | CURSOR RIGHT | Move cursor right. Wraps to left if at right edge. |
| `$7D` | 125 | CLEAR | Clears screen and homes cursor to top-left. |
| `$7E` | 126 | BACKSPACE | Deletes char to the left of cursor and moves cursor left. |
| `$7F` | 127 | TAB | Moves cursor to next tab stop. |
| `$9B` | 155 | END OF LINE | Ends the current text record and advances to the next line. |
| `$9C` | 156 | DELETE LINE | Deletes current logical line. Text below moves up. |
| `$9D` | 157 | INSERT LINE | Inserts blank line at cursor. Lines below move down. |
| `$9E` | 158 | CLEAR TAB | Clears tab stop at current cursor position. |
| `$9F` | 159 | SET TAB | Sets tab stop at current cursor position. |
| `$FD` | 253 | BELL | Generates a beep sound. |
| `$FE` | 254 | DELETE CHAR | Deletes char at cursor. Text to the right moves left. |
| `$FF` | 255 | INSERT CHAR | Inserts space at cursor. Text to the right moves right. |

**ANTIC encoding:** In modes 2/3, bits 0–6 select one of 128 glyphs; bit 7
controls the CHACTL-dependent inversion/blanking attribute. Other character
modes assign the high bits differently; see [character modes](../graphics/character-modes.md).

---

## 8.2 Keyboard and Screen I/O through CIO

Use the canonical [IOCB layout and lifecycle](os-vectors-handlers.md#3-cio-and-iocb-lifecycle).
`CIOV=$E456`; X is the IOCB byte offset (`channel * 16`), not the channel number.
Channels are opened on device names, not hardwired to K: or S:.

- OPEN = 3, GET record = 5, GET character(s) = 7, PUT record = 9,
  PUT character(s) = 11, CLOSE = 12.
- Set the command at `$0342,x`, buffer address at `$0344/5,x`, and transfer
  length at `$0348/9,x`. Check returned Y/status, not carry.
- A normal OS launch already has IOCB0 open on E:. A nonzero channel for K:
  must be opened first and closed when finished.
- ATASCII end-of-line is `$9B`, not a CR/LF pair.

[text-io.asm](../examples/text-io.asm) is a complete program that writes a
prompt through E:, finds and opens a K: channel, reads one character into a
buffer, echoes it, and closes the channel. It includes equates and RUNAD.

Source: [cc65 Atari definitions](https://github.com/cc65/cc65/blob/8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d/asminc/atari.inc),
command constants and IOCB fields; Atari XL OS CIO/keyboard handlers.

---

## 8.3 Key Scancodes

The Atari keyboard matrix produces scan codes at `KBCODE ($D209)`. Bits 0–5
are the base code; bits 6 and 7 latch Shift and Control with the keypress.
`SKSTAT ($D20F)` bit 2 is active-low key-down status, and bit 3 is active-low
live Shift status. `$D01C` is GTIA's `VDELAY`, unrelated to keyboard modifiers.
The OS translates scan codes to ATASCII through CIO `GET` from `K:`.

```asm
        ; Raw held-key decode (no CIO); SKCTL=$03 already configured
        lda SKSTAT             ; $D20F — keyboard/serial status
        and #$04               ; bit 2 is clear while a key is held
        bne @no_key
        lda KBCODE             ; $D209 — last latched scan code
        and #$3F                ; strip shift flags
        ; now A = base scancode 0-63; translate via table
        ; ... process key here ...
@no_key
```

`KBCODE` retains its value after release. Do not use `$FF` as a no-key test:
Shift+Control+A can produce `$FF`. See [keyboard input](input.md#63-keyboard-input)
for the complete matrix, OS `CH` polling, and a hardware polling routine.
Reference: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §5.8.

---

## 8.4 Formatting Numbers

For CIO output, hexadecimal digits are ATASCII `0123456789ABCDEF`. A nibble
can index that 16-byte table after `AND #$0F`; the caller must supply A and
accept X/A/flags being clobbered. Direct screen-RAM output needs screen codes
instead: `$10–$19` for digits, `$21–$26` for A–F in the standard set.

For decimal output, reserve five digits for an unsigned 16-bit value (0–65535)
and a separate terminator if the chosen I/O operation needs one. A six-byte
buffer cannot be declared as two bytes and then indexed through six positions.
Use a complete conversion routine with explicit quotient/remainder and buffer
contracts; do not assume an undeclared `div_10_16` helper exists.
