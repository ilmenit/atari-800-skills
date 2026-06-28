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

An ATR image is a sector container, not a filesystem by itself. First identify sector size, image structure, and boot behavior.

### 2.1 ATR Header Structure (16 bytes)

The ATR file starts with a 16-byte header. The magic identifier is `0x96 0x02` (representing the sum of the ASCII values of the string `'NICKATARI'`).

| Offset | Type | Name | Description |
|---|---|---|---|
| `$00` | WORD | `wMagic` | `$96 $02` (little-endian identifier, `$0296`) |
| `$02` | WORD | `wPars` | Image size (excluding header) in paragraphs (size in bytes / 16) |
| `$04` | WORD | `wSecSize` | Sector size in bytes (commonly `$80` = 128, `$0100` = 256, `$0200` = 512) |
| `$06` | WORD/BYTE | `wParsHigh`/`btParsHigh` | SIO2PC: High word of paragraphs. APE: High byte of paragraphs. |
| `$07` | BYTE/DWORD | `dwCRC` (first byte) | APE: 32-bit file CRC (valid if bit 1 of flags at offset `$0F` is set) |
| `$08` | BYTE | `btFlags` / `dwCRC` | SIO2PC: Flags (bit 4 = copy protected, bit 5 = write protected). APE: Part of CRC |
| `$09` | WORD | `wBad` / `dwCRC` | SIO2PC: Number of first bad sector (if bit 4 is set). APE: Part of CRC |
| `$0B` | DWORD | `dwUnused` / `dwUnused` | Unused bytes (usually `$00000000`) |
| `$0F` | BYTE | `btFlags` / `btFlags` | SIO2PC: Unused. APE: Flags (bit 0 = read-only, bit 1 = dwCRC is valid) |

Most commonly, ATR files follow the APE style or contain zero bytes for `$07` through `$0F`.

### 2.2 Boot Sector Layouts for 256-byte (Double Density) Disks

Standard Atari Double Density (DD) floppies use 256-byte sectors, but the Atari OS boot loader always reads the first three boot sectors as 128-byte sectors. ATR image creators handle this in four different ways:

1. **Short (Type 2 / Standard)**
   - **Structure:** Sectors 1–3 are stored as exactly 128 bytes each, followed immediately by 256-byte sectors.
   - **Header Size:** `(sectors - 3) * 256 + 384` (not a multiple of 256).
   - **Offsets:**
     - Sectors 1–3: `Offset = 16 + (sector - 1) * 128` (Sector 1: 16, Sector 2: 144, Sector 3: 272)
     - Sectors 4+: `Offset = 16 + 384 + (sector - 4) * 256` (Sector 4: 400, Sector 5: 656)

2. **Even (Type 1)**
   - **Structure:** Sectors 1–3 are allocated 256 bytes in the file, but only the first 128 bytes are used. The second 128 bytes are padded with zeros.
   - **Header Size:** `sectors * 256` (multiple of 256).
   - **Offsets:**
     - All Sectors: `Offset = 16 + (sector - 1) * 256`
     - Sectors 1–3: Size is 128 bytes (S1: 16–143, S2: 272–399, S3: 528–655). The ranges 144–271, 400–527, and 656–783 are padding zeros.
     - Sectors 4+: Size is 256 bytes (S4: 784–1039, etc.).

3. **Packed**
   - **Structure:** Sectors 1–3 are stored as 128 bytes each, followed by 384 bytes of zero padding, followed by 256-byte sectors.
   - **Header Size:** `sectors * 256` (multiple of 256).
   - **Offsets:**
     - Sectors 1–3: `Offset = 16 + (sector - 1) * 128` (S1: 16, S2: 144, S3: 272)
     - Sectors 4+: `Offset = 16 + 768 + (sector - 4) * 256` (S4: 784, etc.)

4. **Full**
   - **Structure:** All sectors (including 1–3) are stored as full 256-byte sectors.
   - **Header Size:** `sectors * 256` (multiple of 256).
   - **Offsets:**
     - All Sectors: `Offset = 16 + (sector - 1) * 256`

#### Programmatic Layout Detection
When parsing a DD ATR image (`wSecSize = 256`):
1. Compute the disk size: `size = wPars * 16`.
2. If `size % 256 != 0`, it is **Short**.
3. If `size % 256 == 0`, read the first 768 bytes after the header:
   - If bytes 384–767 are all zero, it is **Packed**.
   - If bytes 128–255, 384–511, and 640–767 are all zero, it is **Even**.
   - Otherwise, it is **Full**.

### 2.3 Copy Protection & SIO2PC Bad Sectors

If bit 4 of `btFlags` (offset `$08` in SIO2PC headers) is set, the ATR image contains copy-protected bad sectors starting at sector `wBad` (offset `$09`).
For these sectors, instead of raw floppy sector data, the file contains a 16-byte metadata block simulating floppy disk timing errors and command statuses:

| Offset | Type | Name | Description |
|---|---|---|---|
| `$00` | DWORD | `dwSign` | Signature bytes: `$C2 $1C $3D $1E` |
| `$04` | BYTE[4] | `btaErrStatus` | SIO status response (`$53`) for a BAD read (in reverse order) |
| `$08` | BYTE | `btCmdResp` | Command response status (`"A"` = ACK, `"N"` = NACK, or `_` / no effect) |
| `$09` | BYTE | `btDataResp` | Data block response (`"C"` = Complete, `"A"` = ACK, `"E"` = Error) |
| `$0A` | BYTE | `btChksumInfo` | Checksum verification state (`"G"` = Good checksum, `"B"` = Bad checksum) |
| `$0B` | BYTE | `btResDelay` | Read/write response delay for a GOOD sector in jiffies (1/18.2 Hz) |
| `$0C` | BYTE | `btErrResDelay` | Read response delay for a BAD sector in jiffies |
| `$0D` | BYTE[4] | `btaStatus` | SIO status response (`$53`) for a GOOD read (in reverse order) |

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
