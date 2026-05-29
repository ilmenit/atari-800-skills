# Xex Atr Formats

## §7.4  XEX Binary Load Format

| Field | Magic |
|---|---|
| Block 1 header | `FF FF` (standard Atari binary load file) |
| Segment header | start_lo start_hi end_lo end_hi, inclusive |
| INIT vector | segment writes `$02E2/$02E3`; DOS calls it after loading that segment |
| RUN vector | segment writes `$02E0/$02E1`; DOS jumps there after loading completes |

XEX files are the native Atari binary format. A file may contain several load segments. `$FF $FF` is a marker, not a universal per-block command byte; after it, the loader expects start/end address pairs and raw bytes. For reversing, build a segment map and watch writes to `INITAD ($02E2)` and `RUNAD ($02E0)`.

Assembler/source implications:

- A DOS binary loader identifies the file from the first `$ff $ff` marker, so
  the first emitted segment should use the full six-byte header.
- Later segments may use start/end pairs directly, though many tools still emit
  `$ff $ff` before each segment for tolerance.
- Every `ORG`/`.org` can become a separate segment. A file may be a valid
  display setup with no executable opcodes if it only loads display memory,
  display-list bytes, and OS shadow-register values.
- For reverse engineering, do not assume the first loaded address is code.
  Identify the actual entry from `INITAD`, `RUNAD`, or a boot loader jump.

---

## §7.5  ATR Virtual Disk Format

| Field | Value |
|---|---|
| ATR magic | `$96 $02` header size = 0x80 bytes |
| Sector size | 128 bytes (SD) or 256 bytes (DD) |
| Sector count | (file size − header_size) / sector_size |
| Double-sided (1050) | 180K → 720 KB (360 Tracks × 16 Sectors × 256 × 2 sides) |

Boot and loader notes:

- The first three sectors are commonly 128-byte boot sectors even on enhanced-density images.
- Boot disks may load code before any DOS filesystem is active.
- Custom loaders often bypass CIO and call `SIOV` with direct sector commands.
- Directory entries are DOS-dependent; do not infer MyDOS/SpartaDOS/DOS 2.x layout without identifying the DOS.

---
