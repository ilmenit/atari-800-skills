---
name: atari8bit-compatibility
description: >-
  Atari 8-bit compatibility matrix: 400/800 vs XL/XE, PAL/NTSC, RAM
  expansions, CPUs, CTIA/GTIA, stereo POKEY, VBXE, Sophia, Rapidus.
---

# Compatibility and Detection

> **When to load:** Code must run across Atari 400/800/XL/XE, PAL/NTSC, RAM sizes, or optional upgrades.
> **Primary sources:** `Altirra-hardware/extracted_chapters/chapter01.md`, `chapter02.md`, `chapter04.md`, `chapter06.md`, and Atariki articles on 65C816 mode detection, VBXE detection, Sophia detection, and stereo POKEY detection.

## Quick Matrix

| Feature | 400/800 | XL/XE | Agent risk |
|---|---|---|---|
| RESET key | ANTIC RNMI path | CPU RESET line | Reset-survival code differs |
| Joystick ports | Four ports on many models | Two ports | Paddle/port assumptions differ |
| PORTB banking | Joystick ports 3/4 role | ROM/RAM banking on XL/XE | Do not use XL/XE banking on 400/800 |
| BASIC ROM | Cartridge/ROM model differs | Often controlled by PORTB | Preserve BASIC bit if returning to OS |
| Self-test ROM | Not XL/XE-style | PORTB-controlled | Can collide with bank switching |
| ANTIC/GTIA timing | Same family, revision differences | Same family, revision differences | Raster kernels need real target testing |

## PAL/NTSC

- ANTIC determines frame timing: NTSC is 262 scan lines at 59.94 Hz; PAL/SECAM is 312 scan lines at 49.86 Hz.
- CPU clock differs slightly: NTSC about 1.7897725 MHz, PAL/SECAM about 1.7734470 MHz.
- GTIA/FGTIA determines color encoding and the `$D014` PAL flag result.
- PAL and SECAM are usually software-compatible for timing; SECAM FGTIA has fewer luminance levels in GTIA mode 9.
- Mixed ANTIC/GTIA systems exist; do not assume frame timing and color standard always match.

Detection choices:

| Method | Works on | Meaning |
|---|---|---|
| `PALNTS` `$0062` | XL/XE OS only | `0` = NTSC, `1` = PAL/SECAM |
| GTIA `PAL` `$D014` | 400/800/XL/XE | Bits 1-3 clear = PAL/SECAM; bits 1-3 set = NTSC |
| ANTIC `VCOUNT` `$D40B` | 400/800/XL/XE | Max about `130` NTSC, `155` PAL/SECAM |

Prefer `PALNTS` only for XL/XE OS-resident code. For portable 400/800/XL/XE
software, either test `$D014 & $0E` for color-standard detection or measure
`VCOUNT` when frame timing is what matters.

```asm
; XL/XE OS quick path: A=0 NTSC, A=1 PAL/SECAM
        lda   $62              ; PALNTS

; Hardware color-standard path: C clear = PAL/SECAM, C set = NTSC
detect_gtia_pal
        lda   $d014            ; PAL flag from CTIA/GTIA/FGTIA
        and   #$0e
        cmp   #$0e             ; bits 1-3 set => NTSC
        rts
```

VCOUNT timing detection should sample a whole frame and record the maximum
value. Do not wait for `VCOUNT == 155` unless PAL is already known; that locks
on NTSC. Use threshold logic such as `max_vcount >= 150 => PAL/SECAM`.

Compatibility consequences:

- VBI-driven game logic runs about 16.8% slower on PAL/SECAM if authored for NTSC, or about 20.2% faster on NTSC if authored for PAL.
- Immediate VBI budget is much smaller on NTSC: about 2508 cycles versus about 8208 cycles on PAL/SECAM when using a 240-scanline display.
- Deferred whole-frame budget is about 29859 cycles NTSC versus 35568 cycles PAL/SECAM before display DMA differences.
- PAL display lists that exceed NTSC visible/timing capacity can flicker or fail on NTSC.
- NTSC artifact-color graphics in high-resolution ANTIC modes do not look the same on PAL/SECAM.
- Timing-based loaders and copy protection can fail across standards.

Avoid equality-only waits on `VCOUNT`; use range/threshold waits so PAL code
does not lock on NTSC or vice versa. Normalize game timers, music row clocks,
sample cadences, and animation speeds after detecting the target timing.

## RAM and Banking

| Type | Notes |
|---|---|
| 48K/64K base | Most XL/XE code should assume no extended RAM unless detected |
| 130XE | 16K window at `$4000-$7FFF`; selected through PORTB bits |
| RAMBO/COMPY | Similar windowing, more banks, different PORTB encodings |
| VBXE RAMBO core | Can expose RAMBO-style memory through VBXE-related banking |

Rules:

- Save original `PORTB` before bank switching.
- Preserve OS/BASIC/self-test bits unless intentionally disabling ROM.
- Do not probe extended RAM destructively while DOS or SpartaDOS X owns banks.

## CPU

| CPU | What changes |
|---|---|
| 6502 | Baseline target |
| 65C02 | Adds opcodes; fixes some NMOS quirks |
| 65C816 | Native/emulation mode, 16-bit A/X/Y widths, 24-bit addressing |
| Rapidus | Accelerator context; timing-sensitive code needs conservative assumptions |

Use CPU-specific opcodes only after detection or when the target explicitly requires that CPU.

MADS example `detect_cpu.asm` uses a transparent 65816 probe: `INC A` differentiates 6502 behavior, then `XBA` confirms 65816. For portable generated code, hide this behind a small routine and return a capability byte instead of assembling 65816 opcodes into baseline paths.

```asm
        opt c+                 ; allow 65C02/65816 mnemonics in MADS
        lda #0
        inc @                  ; transparent probe idiom from the MADS example
        cmp #1
        bcc is_6502
        xba                    ; only meaningful on 65816
        dec @
        xba
        inc @
        cmp #2
        beq is_65816
is_6502
```

## Video and Audio Upgrades

| Upgrade | Detection/use |
|---|---|
| CTIA/GTIA | GTIA modes require GTIA; very old CTIA lacks them |
| Stereo POKEY | Detect before writing second POKEY address range |
| VBXE | Probe FX core at `$D600`/`$D700`; see `exotics/vbxe.md` |
| Sophia | Detection uses Sophia-specific signature behavior; see `exotics/sophia-rapidus.md` |

If an effect requires an upgrade, code should either fail cleanly, fall back to stock hardware, or state the requirement in the binary/demo notes.

Stereo POKEY detection patterns are summarized in `hardware/pokey.md`: timer IRQ alias, RANDOM-reset, and keyboard-register compare. Prefer timer/RANDOM detection; the keyboard compare is small but ambiguous while primary `KBCODE` is `$00`. Do not leave `$D20E`, `$D20F`, `$D21E`, `$D21F`, `$D40E`, or IRQ state modified after probing.

## Compatibility Checklist

Before generating final code, state:

- target family: 400/800, XL/XE, or both;
- TV timing: PAL, NTSC, or adaptive;
- required RAM and bank scheme;
- required CPU;
- required video/audio upgrades;
- whether OS ROM remains enabled;
- whether DOS/SDX must survive.
