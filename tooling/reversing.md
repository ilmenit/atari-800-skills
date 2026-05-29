---
name: atari8bit-reversing
description: >-
  Atari 8-bit XL/XE reversing workflow: XEX/ATR triage, segment maps,
  INIT/RUN vectors, depackers, listing files, Altirra tracing, hardware
  register breakpoints, DLI/VBI diagnosis.
---

# Reversing Atari 8-bit Programs

> **When to load:** The task is to understand, port, patch, debug, or document an existing XEX/ATR/source/listing/demo.
> **Do not use for:** Pure register lookup; load `hardware/*` instead.
> **Primary sources:** `atari-documentation/XEX-FORMAT/xex-format.md`, `Altirra-hardware/extracted_chapters/chapter03.md`, `chapter04.md`, `chapter09.md`, `chapter10.md`, `atari-documentation/code-examples/`, `torus-project/`.

## Quick Lookup

| Need | Use |
|---|---|
| XEX segment map | §1 |
| ATR/disk triage | §2 |
| Listing/source recovery | §3 |
| Depacker recognition | §4 |
| Interrupt/raster tracing | §5 |
| Hardware breakpoints | §6 |
| Compatibility audit | `system/compatibility.md` |

## 1. XEX Triage

Atari binary load files are segment streams. Build a load map before interpreting code.

| Bytes | Meaning |
|---|---|
| `FF FF` | Optional binary file marker; may appear before later segments too |
| `lo hi lo hi` | Start/end address of a data segment, inclusive |
| Segment data | Stored directly to RAM from start through end |
| `$02E2/$02E3` (`INITAD`) | If written by a segment, DOS calls this init routine after the segment |
| `$02E0/$02E1` (`RUNAD`) | If written, DOS jumps here after loading completes |

Reverse workflow:

1. Parse all segments and note overlaps.
2. Mark any segment writing `INITAD`, `RUNAD`, `DOSINI`, `DOSVEC`, `VDSLST`, `VVBLKI`, `VVBLKD`, `SDLSTL`, or `NMIEN`.
3. If a segment loads over display RAM, charset RAM, PMG RAM, or zero page, label it as data until control flow proves otherwise.
4. If the first executable entry only depacks or relocates, trace until the final jump after memory writes stop.
5. Treat "programs" made only of load segments as valid: some files install
   screen data, a display list, colors, and shadows without containing CPU
   opcodes. In those cases the load map is the behavior.

Common addresses:

| Address | Meaning |
|---|---|
| `$02E0` | `RUNAD`, run address |
| `$02E2` | `INITAD`, init address |
| `$0200` | `VDSLST`, DLI vector |
| `$0222/$0224` | VBI vectors (`VVBLKI`, `VVBLKD`) |
| `$0230/$0231` | `SDLSTL`, OS display-list shadow |
| `$D40E` | `NMIEN`, DLI/VBI enable |

## 2. ATR and Disk Triage

An ATR image is a sector container, not a filesystem by itself. First identify sector size and boot behavior.

| Item | Check |
|---|---|
| ATR header | `$96 $02`, 16-byte header |
| Sector size | Usually 128 or 256 bytes; first three boot sectors are commonly treated as 128-byte sectors |
| Boot disk | Sector 1 boot flag/count can load a boot program before DOS |
| DOS files | Need DOS type knowledge before mapping directory entries |
| Custom loader | Watch SIO/DCB calls and direct sector reads |

For game/demo reversing, boot sectors and custom SIO loaders often matter more than DOS directories. Trace `SIOV` calls and DCB fields before assuming CIO file access.

## 3. Source, LST, and Symbol Recovery

MADS and x-asm listings usually reveal enough structure to recover intent:

- Treat labels ending in `_vbl`, `_dli`, `irq`, `nmi`, `init`, `main`, `depack`, `copy`, `make_dl`, `screen`, `font`, `tab`, `sin`, `cos` as high-value anchors.
- Cross-reference writes to `$D000-$D7FF`; these are hardware control, not ordinary memory.
- Separate code from tables by looking for branch targets and entry points. Sine, square, font, charset, PMG, and display-list tables often look like valid opcodes by accident.
- In self-modifying code, label patched operands separately from instruction opcodes.

## 4. Depacker and Relocator Recognition

Likely depacker traits:

| Trait | Meaning |
|---|---|
| Tight `(src),y` / `(dst),y` loops | Stream copy/depack |
| Frequent `iny/bne/inc src+1` | Page-crossing stream reader |
| Bit-buffer shifts through carry | LZ/DEFLATE-style token reader |
| Backward copy from already-written output | LZ match copy |
| Writes to `RUNAD`/entry vector after copy | Stub transfers to unpacked program |
| Large writes to `$4000-$7FFF` with PORTB changes | Extended RAM or banked asset load |

After depacking, set the new entry point at the final `jmp`/`rts` target. Do not spend time naming the stub before locating the real code.

## 5. DLI/VBI and Raster Debugging

Key distinction:

- `VDSLST ($0200/$0201)` is the DLI vector used by the OS NMI dispatcher.
- `VVBLKI ($0222/$0223)` and `VVBLKD ($0224/$0225)` are VBI vectors installed through `SETVBV`.
- DLI handlers normally end in `RTI`.
- Deferred VBI handlers normally end through `XITVBV`, not raw `RTI`.

Trace order for display bugs:

1. Display list pointer: `SDLSTL`/`DLISTL`.
2. Display-list bytes: DLI bit `$80`, LMS bit `$40`, VSCROL `$20`, HSCROL `$10`.
3. `VDSLST` target before `NMIEN` bit 7 is enabled.
4. Shadow vs hardware writes: DLI must write hardware registers directly.
5. `WSYNC` placement and available cycles on the target scan line.

## 6. Hardware Breakpoint Targets

Use write breakpoints on these addresses to discover behavior quickly:

| Address | Why |
|---|---|
| `$D400` / `$022F` | DMACTL / SDMCTL display DMA changes |
| `$D402/$D403` / `$0230/$0231` | Display-list pointer |
| `$D404/$D405` | HSCROL/VSCROL fine scrolling |
| `$D40A` | WSYNC timing kernels |
| `$D40E` | NMI enable changes |
| `$0200/$0201` | DLI vector changes |
| `$0222-$0225` | VBI vector changes |
| `$D000-$D01F` | GTIA colors, PMG positions, priorities |
| `$D200-$D20F` | POKEY sound, timers, keyboard/SIO |
| `$D301` | PORTB ROM/RAM banking |

## 7. Output of a Reverse Pass

A useful agent reverse summary should include:

- machine assumptions: XL/XE, RAM, PAL/NTSC, upgrades;
- load map: segments, entry points, overwritten vectors;
- interrupt map: DLI/VBI/IRQ ownership and return paths;
- memory map: screen, charset, PMG, tables, zero-page allocations;
- I/O map: CIO/SIO/DCB use, disk sectors, device dependencies;
- depacker/relocator status: packed entry vs real entry;
- risks: timing-sensitive kernels, OS ROM off, bank switching, undocumented opcodes.
