# SIO and Disk Access

## OS call versus wire protocol

SIOV (`$E459`) consumes the 12-byte DCB at `$0300–$030B`. DSKINV (`$E453`)
is the OS disk-driver wrapper that supplies standard disk fields before calling
SIO. [disk-read.asm](../../examples/disk-read.asm) initializes the complete DCB
and performs a read-only SIO call; [OS services](os-disk-services.md) describe DSKINV.

| DCB field | Address | Meaning for a sector read |
|---|---|---|
| DDEVIC | `$0300` | Disk class `$31` |
| DUNIT | `$0301` | Drive unit, e.g. 1 |
| DCOMND | `$0302` | `$52` ('R') |
| DSTATS | `$0303` | `$40` (peripheral-to-computer); overwritten with result |
| DBUFLO/HI | `$0304/5` | Destination buffer |
| DTIMLO | `$0306` | Command timeout; initialize for each operation |
| DUNUSE | `$0307` | Unused, initialize to zero |
| DBYTLO/HI | `$0308/9` | Transfer byte count |
| DAUX1/2 | `$030A/B` | Little-endian sector number |

Check returned Y (negative = error) and DSTATS before consuming a buffer.
Timeout behavior is controlled by OS routines, command fields, and device
response timing; POKEY has no universal 540 ms inactivity timeout.

## Command and data frames

The computer asserts COMMAND and sends device ID, command, AUX1, AUX2, and an
end-around-carry checksum. There is no cassette-style 128-byte sync leader.
The device then responds with ASCII protocol bytes:

| Byte | Meaning |
|---|---|
| `$41` ('A') | ACK |
| `$4E` ('N') | NAK |
| `$43` ('C') | COMPLETE |
| `$45` ('E') | ERROR |

The data direction determines the order of data transfer and acknowledgements.
Data frames carry an end-around-carry checksum, not a CRC. Device IDs depend
on peripheral type (disk drives commonly `$31–$38`), not a universal `$40–$4F` range.

## Stock drive geometry

| Drive / format | Typical logical sectors | Bytes per sector | Data capacity |
|---|---:|---:|---:|
| 810 single density | 720 | 128 | 90 KiB |
| 1050 single density | 720 | 128 | 90 KiB |
| 1050 enhanced density | 1040 | 128 | 130 KiB |
| XF551 double-sided double density | 1440 | 256 | 360 KiB nominal |

The stock 1050 is single-sided; enhanced density does not mean 256-byte
sectors. Modified drives can expose other formats. The first three boot-sector
transfers and the ATR storage layout require special handling; see
[XEX/ATR formats](xex-atr-formats.md). Do not infer filesystem capacity from
physical geometry alone.

Sources: [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf),
chapters 9–10; [cc65 Atari equates](https://github.com/cc65/cc65/blob/8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d/asminc/atari.inc), DCB and SIO status.
