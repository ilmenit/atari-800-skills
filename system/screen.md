---
name: atari8bit-crt-editor
description: >-
  Atari 8-bit ATASCII screen-code table, CIO GET/PUT/PRINT via CIOV, key scancodes, number-base on-screen rendering.
---

# 08 — CRT Editor & Screen I/O

> earlier coverage on CIO key input, text record editing, character output, string printing, and editor control codes (all summaries in inline reference)> **Scope:** ATASCII screen codes, CIO GET/PUT/PRINT, key scancodes, number-base conversion on screen
> **Key items:** ATASCII $1B/$9B/$7D/$7E/$7F; CIOV $E456; IOCB $0340; KBCODE; hex_lookup table
> **Scope:** ATASCII screen codes, CIO GET/PUT/PRINT, key scancodes, number-base conversion on screen

## Quick-lookup

| Need | See § |
|---|---|
| ATASCII screen codes table | §8.1 |
| IOCB table + CIO GET/PUT/PRINT boilerplate | §8.2 |
| RAW key scancode read (KBCODE\u2192shifter) | §8.3 |
| Binary-to-hex digit lookup | §8.4 |
| 16-bit decimal-to-screen with EOL $9B | §8.4 |

## 8.1 ATASCII Screen Code Table

ATASCII has 128 code points ($00–$7F); character codes map 1:1 with ATASCII in text modes — the byte value is both the ATASCII code and the character-set index.

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
| `$9B` | 155 | END OF LINE | Moves cursor to start of next line. Cancels auto-repeat on shift keys. |
| `$9C` | 156 | DELETE LINE | Deletes current logical line. Text below moves up. |
| `$9D` | 157 | INSERT LINE | Inserts blank line at cursor. Lines below move down. |
| `$9E` | 158 | CLEAR TAB | Clears tab stop at current cursor position. |
| `$9F` | 159 | SET TAB | Sets tab stop at current cursor position. |
| `$FD` | 253 | BELL | Generates a beep sound. |
| `$FE` | 254 | DELETE CHAR | Deletes char at cursor. Text to the right moves left. |
| `$FF` | 255 | INSERT CHAR | Inserts space at cursor. Text to the right moves right. |

**ANTIC encoding:** In text modes (Modes 2/3), ANTIC uses the screen byte value as an 8-bit index into the character set. GTIA modes and Graphics 0/8/9/+ are different; See ANTIC display processor.

---

## 8.2 Keyboard & CRT Editor I/O (CIO)

CIO channels on XL/XE run through IOCB table at `$0340` (IOCB0 starts at `$0340`, offset 16 bytes per channel).

```asm
; --- CIO GET — read one character (IOCB #1 = keyboard) ---
        GET    #1
        ldx    #$01               ; IOCB #1 hardwired to keyboard
        lda    #$05               ; $05 = CIO GET verb
        sta    $0340,x            ; CIO command byte
        jsr    CIOV               ; $E456 (XL/XE)
        bmi    ?err               ; negative = error
        lda    $0342,x            ; buffer+2 = character
        ; A = key in ATASCII ($9B = EOL in token form)

; --- CIO PUT — write one character to screen (IOCB #2 = screen) ---
        lda    #$09               ; CIO PUT verb
        sta    $0350,x            ; IOCB #2 command
        jsr    CIOV

; --- CIO PRINT — write string + EOL to screen ---
        ; MADS macro syntax:
        PRINT  "HELLO WORLD!",$0D0A
```

**IOCB table (offsets from base `$0340 + N*16`):**

| Offset | Field | Notes |
|--------|-------|-------|
| `+0` | Command / status byte | Write verb here before CIOV |
| `+2` | Buffer address, low byte | Where the character / data is stored |
| `+3` | Buffer address, high byte | |
| `+4` | Buffer length | For GET: ignored; for PUT/PRINT: number of bytes |
| `+5` | Device ID | `$01` = keyboard, `$02` = display, `$03` = printer |
| `+6` | Status / auxiliary | |

`CIOV` at `$E456` dispatches the verb at `(IOCB+0)`.

---

## 8.3 Key Scancodes

The Atari keyboard matrix produces scancodes at `$D209` (KBCODE register), key modifiers at bit-mapped registers `$D01C` (SHIFT `$D209`). The OS maps scancodes to ATASCII in `GET` — raw scancodes are only needed when bypassing CIO:

```asm
        ; Raw key-code decode (no CIO)
        ldx KBCODE              ; $D209 — raw scan code
        cpx #$FF                ; no key?
        beq @no_key
        txa
        and #$3F                ; strip shift flags
        ; now A = base scancode 0-63; translate via table
```

---

## 8.4 Number Base On Screen

### Binary-to-hex digit

Convert low nibble in A to a single hex ASCII digit, then write it to screen RAM:

```asm
hex_lookup
        .byte  "0123456789ABCDEF"
to_ascii_hex
        and    #$0F             ; isolate nibble
        tax
        lda    hex_lookup,x     ; A = ASCII '0'-'F'
        rts
```

### Decimal to screen (16-bit unsigned, right-aligned)

Result written to a 6-byte screen-memory buffer, terminated with EOL ATASCII `$9B`. Exercise the divide-by-10 routine from the math routines section §10; write each digit to screen via CIO PUT:

```asm
; AX = 16-bit value; buffer points at screen RAM
dec_to_screen
        ldx    #5               ; 6 digits, right-aligned
@next   lda    #$20             ; pre-fill with SPACE
        sta    buffer,x
        dex
        bpl    @next
        ldx    #0
@loop   jsr    div_10_16        ; AX = AX / 10; A = remainder
        ora    #$30             ; convert digit to ATASCII
        sta    buffer+5,x       ; write right-to-left
        inx
        cpx    #6
        bne    @loop
        lda    #$9B             ; EOL
        sta    buffer+6
        rts

buffer  .byte  5,0              ; e.g. screen row buffer, 6 chars wide
```

### Routine reference

Dividing a 16-bit value by 10: See math routines §10.2 (16-bit ÷10, 79 or 96 bytes depending on space/speed trade-off).

---

*earlier coverage (full content in inline reference):*
*ATASCII table §8.1; CIO GET/PUT/PRINT §8.2; scancodes §8.3; number base conversion §8.4.*
Source notes: character output, string printing, editor control codes, key scancodes, and ATASCII/screen-code conversion are summarized from the Atariki screen I/O articles in English.
