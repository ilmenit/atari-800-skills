---
name: atari8bit-os-vectors-handlers
description: >-
  Atari XL/XE OS vectors, interrupt handlers, CIO/SIO entry points, IOCB
  lifecycle, device-handler hooks, and safe vector ownership rules.
---

# OS Vectors and Handlers

> **When to load:** The task touches VBI/DLI/CIO/SIO vectors, DOS entry points, device handlers, or OS coexistence.
> **Do not use for:** Bare register timing; load `hardware/antic.md`, `hardware/pokey.md`, or `hardware/cpu.md`.
> **Source note:** This file is self-contained; use the internal hardware references named above for register timing.

## Quick Lookup

| Need | See |
|---|---|
| DLI/VBI ownership | §1 |
| Deferred VBI install/return | §1.1 |
| OS entry vectors | §2 |
| CIO/IOCB lifecycle | §3 |
| SIO/DCB calls | §4 |
| Device handlers | §5 |
| Safe hook rules | §6 |

## 1. Interrupt Vectors

| Address | Name | Purpose |
|---|---|---|
| `$0200/$0201` | `VDSLST` | Display List Interrupt vector |
| `$0222/$0223` | `VVBLKI` | Immediate VBI vector |
| `$0224/$0225` | `VVBLKD` | Deferred VBI vector |
| `$D40E` | `NMIEN` | NMI enable: bit 7 DLI, bit 6 VBI |
| `$D40F` | `NMIST/NMIRES` | Read NMI status / write reset |

Rules:

- Set `VDSLST` before enabling `NMIEN` bit 7.
- DLI code entered through `VDSLST` normally saves A/X/Y itself and returns with `RTI`.
- Install VBI code with `SETVBV`; return deferred VBI code through `XITVBV`.
- Do not use `VDSLST` as a VBI vector.
- If multiple systems need DLI ownership, chain by changing `VDSLST` inside each DLI band or centralize ownership in one raster manager.

### 1.1 Deferred VBI via SETVBV / XITVBV

Install deferred VBI handlers through `SETVBV` and leave them through `XITVBV`. The OS path restores registers and completes the VBI chain; a raw `RTI` from a deferred VBI can break later VBI/DLI delivery.

```asm
init_deferred_vbi
        ldx   #>my_vbi
        ldy   #<my_vbi
        lda   #$07            ; deferred VBI slot
        jsr   SETVBV
        rts

my_vbi
        ; frame work here; OS NMI entry already saved A/X/Y

        jmp   XITVBV          ; not RTI
```

Use immediate VBI only for short hardware-critical work. Put ordinary frame updates, input snapshots, music ticks, and buffer swaps in deferred VBI unless the program owns the whole NMI path.

## 2. OS Entry Points and User Vectors

| Entry | Address | Use |
|---|---|---|
| `CIOV` | `$E456` | CIO command dispatch through IOCB |
| `SIOV` | `$E459` | Serial I/O call using DCB |
| `SETVBV` | `$E45C` | Install VBI vector |
| `SYSVBV` | `$E45F` | OS immediate VBI processing |
| `XITVBV` | `$E462` | Exit OS VBI path |
| `DOSVEC` | `$000A/$000B` | DOS entry vector |
| `DOSINI` | `$000C/$000D` | DOS initialization vector |
| `RUNAD` | `$02E0/$02E1` | Binary load run address |
| `INITAD` | `$02E2/$02E3` | Binary load init address |

These addresses point to callable three-byte JMP vectors. `$E457` is an operand
byte of the CIOV vector, not an alternative entry. Use symbolic equates.

## 3. CIO and IOCB Lifecycle

IOCBs start at `$0340`, eight slots, 16 bytes each. CIO uses `X = channel * 16`.

Typical fields:

| Offset | Meaning |
|---|---|
| `+0` | ICHID: handler index (`$FF` = closed/free) |
| `+1` | ICDNO: device unit |
| `+2` | ICCOM: command |
| `+3` | ICSTA: returned status |
| `+4/+5` | ICBAL/ICBAH: buffer address |
| `+6/+7` | ICPTL/ICPTH: handler PUT-byte address minus one |
| `+8/+9` | buffer length |
| `+10/+11` | auxiliary parameters |

Lifecycle:

1. Find a free IOCB (`+0 == $FF` is commonly used as free marker).
2. Write command, device name buffer, length, and AUX fields.
3. Call `CIOV` with X set to IOCB offset.
4. Check Y (`BMI` immediately after the call detects a negative error status); carry is not the CIO success contract.
5. Close the channel when finished.

Common devices: `E:` screen editor, `S:` screen, `K:` keyboard, `D:` disk, `C:` cassette, `P:` printer, `R:` serial.

## 4. SIO and DCB

SIO is below CIO. Use it for sector/device-level work and custom peripherals.

Important DCB fields:

| Field | Use |
|---|---|
| `DDEVIC` | Device ID, e.g. disk drive class |
| `DUNIT` | Unit number |
| `DCOMND` | Command byte |
| `DSTATS` | Direction/status |
| `DBUFLO/DBUFHI` | Data buffer |
| `DTIMLO` | Timeout |
| `DBYTLO/DBYTHI` | Byte count |
| `DAUX1/DAUX2` | Command-specific parameters |

Reverse rule: direct sector loaders usually call `SIOV`, not `CIOV`. Watch DCB writes before `SIOV` to recover file layout.

## 5. Device Handlers

The OS routes CIO device names through a handler table. A handler provides open, close, get, put, status, and special-command entry points.

Agent guidance:

- If code patches a handler table, treat it as OS integration, not ordinary vector use.
- If code opens `D:` through CIO, file semantics are DOS-dependent.
- If code calls `SIOV`, the program is likely bypassing DOS and using sectors or custom device commands.

## 6. Safe Hook Rules

- Save and restore previous vectors unless the program owns the whole machine.
- Disable NMI while changing `VDSLST`, display lists, or DLI chains.
- Do not call OS ROM routines while OS ROM is banked out; use a trampoline that restores PORTB first.
- Preserve registers according to the vector path: DLI handlers save what they use; OS VBI path has its own restore expectations.
- Separate shadow registers from hardware registers. VBI may update shadows; DLI must write hardware registers for immediate raster effects.

Sources: [Atari XL OS Rev.2 source](https://github.com/ilmenit/A800-OS-XL-Rev2),
`NMI`, `DVNM`, and the OS vector table; [cc65 Atari equates](https://github.com/cc65/cc65/blob/8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d/asminc/atari.inc).
The OS `NMI` saves A/X/Y for the VBI path; `DVNM` (via `XITVBV`)
pops Y/X/A and executes RTI. Extra pushes must be balanced before that jump.
