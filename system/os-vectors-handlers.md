---
name: atari8bit-os-vectors-handlers
description: >-
  Atari XL/XE OS vectors, interrupt handlers, CIO/SIO entry points, IOCB
  lifecycle, device-handler hooks, and safe vector ownership rules.
---

# OS Vectors and Handlers

> **When to load:** The task touches VBI/DLI/CIO/SIO vectors, DOS entry points, device handlers, or OS coexistence.
> **Do not use for:** Bare register timing; load `hardware/antic.md`, `hardware/pokey.md`, or `hardware/cpu.md`.
> **Primary sources:** `atari-documentation/memory-map/details.txt`, `overview.txt`, Atariki CIO/file-access articles, `Altirra-hardware/extracted_chapters/chapter03.md`, `chapter04.md`, `chapter09.md`.

## Quick Lookup

| Need | See |
|---|---|
| DLI/VBI ownership | §1 |
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

## 2. OS Entry Points and User Vectors

| Entry | Address | Use |
|---|---|---|
| `CIOV` | `$E456`/`$E457` family in OS docs | CIO command dispatch through IOCB |
| `SIOV` | `$E459` family | Serial I/O call using DCB |
| `SETVBV` | `$E45C` family | Install VBI vector |
| `SYSVBV` | `$E45F` family | OS immediate VBI processing |
| `XITVBV` | `$E462` family | Exit OS VBI path |
| `DOSVEC` | `$000A/$000B` | DOS entry vector |
| `DOSINI` | `$000C/$000D` | DOS initialization vector |
| `RUNAD` | `$02E0/$02E1` | Binary load run address |
| `INITAD` | `$02E2/$02E3` | Binary load init address |

Use symbolic labels from the assembler include file when available; OS listings and assemblers sometimes document entry labels at the vector byte before the callable `JMP` target.

## 3. CIO and IOCB Lifecycle

IOCBs start at `$0340`, eight slots, 16 bytes each. CIO uses `X = channel * 16`.

Typical fields:

| Offset | Meaning |
|---|---|
| `+0` | command/status byte |
| `+1` | device handler index / unit |
| `+2/+3` | buffer address |
| `+4/+5` | put/get routine or length depending on command context |
| `+8/+9` | buffer length |
| `+10/+11` | auxiliary parameters |

Lifecycle:

1. Find a free IOCB (`+0 == $FF` is commonly used as free marker).
2. Write command, device name buffer, length, and AUX fields.
3. Call `CIOV` with X set to IOCB offset.
4. Check carry/status after return.
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
