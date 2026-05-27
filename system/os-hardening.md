---
name: atari8bit-system
description: >-
  Atari 8-bit OS-ROM disable, trampoline handler, VCOUNT/WSYNC, RESET survival, SpartaDOS X DOSVEC/SDLSTL integration.
---

# 09 - System Hardening

> **Primary sources:** Atariki RESET-survival and SpartaDOS X startup articles, summarized here in English, plus Altirra hardware timing notes.
> **Scope:** OS-ROM disable, trampoline handler, VCOUNT, WSYNC, RESET survival, SpartaDOS X
> **Key items:** PORTB $D301; NMIEN $D40E; NMIST $D40F; VCOUNT $D40B; WSYNC $D40A; SDLSTL $0230

## Quick-lookup

| Need | See § |
|---|---|
| OS-ROM disable / re-enable | §9.1 |
| Trampoline handler skeleton | §9.1 |
| VCOUNT vs VBLANK; PAL VBI split | §9.2 |
| RESET survival 400/800 vs XL/XE | §9.3 |
| Warm-flag cold-boot detection | §9.3 |
| SDLSTL re-entry for embedded SDX | §9.3 |
| SpartaDOS X DOSVEC detection | §9.4 |
| SDX binary block types ($FFFA/\u2026) | §9.4 |

## 9.1 OS-ROM Disable & Trampoline Handler

### Disable OS ROM on XL/XE

PORTB at `$D301` bit 0 controls the OS ROM:
- **Bit 0 = 0** -- OS ROM disabled (software vectors and CIO/VBI/DLI unavailable)
- **Bit 0 = 1** -- OS ROM enabled (default)

```asm
        lda PORTB
        and #$FE              ; clear bit 0 -> OS ROM off
        sta PORTB

; Re-enable:
        lda PORTB
        ora #$01
        sta PORTB             ; OS ROM back on
```

With OS ROM off, all software interrupts (keyboard scan, SIO, VBI/DLI dispatch) stop. You must provide your own NMI/IRQ handler trampoline.

### Trampoline handler

The trampoline re-enables the OS ROM, enters the correct OS handler path, then restores the OS-off state before returning:

```asm
os_trampoline_handler
        pha
        txa
        pha
        tya
        pha
        lda PORTB
        sta trampoline_PORTB_save

        lda #$01
        sta PORTB             ; force OS ROM on

        lda NMIST              ; $D40F
        and #$80               ; DLI?
        beq @chk_vbi
        jsr os_dli_entry
        bne @done             ; always branch

@chk_vbi lda NMIST
        and #$40               ; VBL?
        beq @done
        jsr os_vbi_entry

@done   pla
        tay
        pla
        tax
        pla
        sta PORTB              ; restore ROM-off state
        rti
```

**Key insight:** NMIST bits are sticky -- they accumulate until the register is read and cleared. Always read NMIST to both identify and acknowledge the pending source.

---

## 9.2 VBI / VCOUNT Timing with OS-ROM Off

Without the OS running, RTCLOK is unavailable. `VCOUNT` at `$D40B` is the substitute for all frame-sync and vertical-hold logic.

```asm
wait_scanline_80
        ldx #$50               ; target scan line
@poll   lda VCOUNT             ; $D40B -- increments every scan line
        cpx VCOUNT
        bne @poll              ; loop until VCOUNT == X
        rts
```

| Counter | NTSC range | PAL range | Reset |
|---------|-----------|-----------|-------|
| `VCOUNT` | 0--227 | 0--311 | wraps at VBLANK start |
| VBI split point | line 228 | line 250 | -- |
| Horizontal sync | cycle 0 (per line) | cycle 0 (per line) | -- |

Notes:
- VCOUNT is **not** reset by the RESET key; use a warm-flag in RAM to differentiate cold boot from warm restart see section 9.3.
- On a hardware reset, VCOUNT holds an indeterminate value -- do not read it until frame 1.
- `WSYNC` causes the CPU to stall until the NEXT horizontal sync. Cycle count variance depends on where the write lands within the current 114-cycle line.

---

## 9.3 RESET-Resistant Programs

On 400/800 hardware, RESET is an NMI event; RAM is fully preserved.
On XL/XE hardware, the RESET button triggers a hardware CPU RESET to `$FFFC`; RAM is indeterminate after power-on.

| Machine | Reset mechanism | RAM state | Survival trick |
|---------|----------------|-----------|----------------|
| 400/800 | /RNMI signals NMI -- `$FED6` warm-start | Preserved | Set warm flag in ZP; patch VDSLST to jump to main loop |
| XL/XE | Hardware RESET -- CPU vector `$FFFC` | Undefined (power-on) | Detect cold boot; re-load from disk/cart or recover from warm-flag in TMPVEC RAM |

```asm
; Cold boot detection on XL/XE
cold_boot_detect
        lda warm_flag
        beq cold_boot_entry    ; flag not set -> power-on RESET
        ; warm restart: restore display list
        ldx #<saved_dll
        lda #>saved_dll
        stx SDLSTL
        sta SDLSTH
        jmp main_loop

cold_boot_entry
        jsr reload_from_disk
        rts

warm_flag    .byte   0           ; set this in RAM before any unexpected RESET
saved_dll    .byte   0,0          ; saved SDLSTL/SDLSTH pointer
```

The `/RNMI` ROM shortcut on 400/800 hardware resumes execution directly in the warm-start stub; no reload from disk is needed.

---

## 9.4 SpartaDOS X Integration

### SDX detection via the DOSVEC protocol

DOSVEC at `$000A` points at the standard DOS entry point. Its third byte (`+3`) is a JMP opcode (`$4C`) pointing to the parameter reader.

```asm
boot_?  = $09
dosvec  = $0a

detect_sdx
        lda boot_?
        lsr
        bcc _no_dos
        lda dosvec+1
        cmp #$c0
        bcs _no_dos
        ldy #$03
        lda (dosvec),y
        cmp #$4c              ; JMP opcode?
        bne _no_dos
        clc                   ; CLI + SDX present
        rts
_no_dos sec
        rts
```

SDX extends the standard DOS XL protocol with its own richer parameter-parsing library (available from DOSVEC+3), including automatic string-to-integer conversion, repeated option reads, and environment-variable substitution -- see the SDX Programmer's Guide section on parameter parsing.

### SDX autoboot and runtime types

| Startup path | Action |
|---|---|
| `AUTOEXEC.BAT` | Executed automatically at SDX boot |
| `RUN.BAT` | Executed after `AUTOEXEC.BAT` |
| Program `sa` loader | Calls SDX library `UPDATE NEW`, `UPDATE SYMBOL`, `BLK UPDATE EXTRN` for resolver |
### SDX cross-process save and load

SDX provides a shared save area accessible from any process by standard CRT
mechanism. The programmer stores data in a contiguous RAM block topped by a header
byte and optionally terminated by a session identifier. Session identifiers permit
multiple concurrent processes to keep independent save slots active without collision:

```
; --- store session data ---
save_session
    lda session_id        ; 1 byte session tag
    sta save_hdr+0
    lda #<save_data
    sta save_hdr+1
    lda #>save_data
    sta save_hdr+2
    ; header written, data available in RAM block $7000–$7FFF

; --- retrieve session data ---
load_session
    lda save_hdr+0
    cmp session_id
    bne no_session         ; session tag mismatch — data absent
    lda save_hdr+1
    sta ptr_lo
    lda save_hdr+2
    sta ptr_hi
    ; ptr now points to session data in shared RAM

no_session
    ...
```

Shared save blocks are not persistent — data lives only in RAM unless the caller
explicitly invokes `SAVE 0, filename` to write the block to disk. For persistence
across a session boundary: call `SAVE` before the process exits and `LOAD` on
next invocation. The save area should be kept outside of BASIC's zero-page workspace
and outside of the OS page-2 stack to prevent silent corruption by the `D`x
iovector.

SDX session save areas should be aligned to 256-byte boundaries to prevent page
transition cache breaks in the process loader.

The `INIT` preamble resets a session pointer held at `$6E00` used by the library.

| SDX binary EXE header | `$FFFA` = start, `$FFFE` = end, `$FFFC` = INI block, `$FFFB` = symbol block |
| `PUBLIC`/`EXT` MADS symbols | Emitted by MADS assembly, reloaded by `BLK UPDATE` chain |

Key equivalences:
- SDX formal parameter: `DT_xxx` types for `DCB` fields; workflow-type parameters passed as `DCB` command structures.
- MADS `SAVE`/`RUN` blocks; generated from `.BYTE`/`.WORD`/`.LONG`/`.SAV`/`.SAV offset,length`.
- `BLK UPDATE EXTRN` mirroring all `PUBLIC`/`.EXT` symbol entries from assembly.
