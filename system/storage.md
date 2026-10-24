---
name: atari8bit-disk-file
description: >-
  Atari 8-bit SIO frame protocol, 810/1050/XF551/Indus GT drive commands, XEX/ATR/IOCB formats, SpartaDOS X, xBIOS mini-OS file access.
---

# 07 — Disk Drives & File I/O

> **Key items:** SIO DCB fields; Status byte C/E/A/N; DDEVIC/DUNIT/DCMD; IOCB $0340
> **Scope:** SIO frame format, disk drive commands, XEX/ATR binary formats, IOCB, SpartaDOS X relocatable, xBIOS

---

## Quick-lookup

| Need | See § |
|---|---|
| SIO frame format table | §7.1 |
| Drive commands (810/1050/XF551/Indus GT) | §7.2 |
| IOCB structure + free-IOCB-finder snippet | §7.3 |
| XEX binary format header table | §7.4 |
| ATR virtual disk format block structure | §7.5 |
| SDX binary block types ($FFFA/$FFFE/$FFFD/$FFFB) | §7.6 |
| **xBIOS mini-OS file access** | §7.7 |
| Boot/custom loader patterns | §7.9 |
| SIO checksum and peripheral-side protocol | §7.10 |
| DSKINV disk-driver entry | §7.11 |
| DOS/SDX command-line parsing | §7.12 |
| CIO special command numbers | §7.13 |

---

## §7.1  SIO Serial I/O

> ⚠ **SIO timeout:** The POKEY SIO serial port times out after roughly 540 ms of no activity (128-bit clock at 19200 baud ≈ 6.692 ms per byte × 80 bytes ≈ 535 ms). If the drive doesn't ACK the device ID within this window, the calling routine must handle the timeout explicitly rather than retry-loops on a dead channel. Always check the STATUS byte after every SIO transmission before reusing the DCB.

> ⚠ **IOCB status discipline:** After CIO calls, always check the returned status before consuming data or reusing the IOCB. Poll loops that treat any nonzero status as success can race device-handler transitions and lose data.

### Frame format

```
[LEADER] [DEVICE_ID (1)] [COMMAND_FRAME] [ACK/NACK] [DATA_FRAME(s)] [STATUS_FRAME]
```

| Field | Value |
|---|---|
| Device ID | $40–$4F (serial address) |
| Leader byte | $55 AA55 AA55 … (128 bytes of sync) |
| COMMAND frame | 4 bytes: Device-ID + Cmd byte + AUX1 + AUX2 |
| ACK/NACK | 1 byte: device acknowledges or NACK |
| DATA frame | Data bytes + CRC |
| STATUS | Status byte + COMPLETE ($FF) or ERROR ($XX) |

SIO acknowledge byte = device acknowledges ID, then NACK ($00) = fault; COMPLETE (done = $FF). After data transmission: device asserts DONE in status to confirm completion.

### SIO checksum

Every SIO command and data block ends with a one-byte checksum. The checksum
is the end-around-carry sum of all bytes in the block, excluding the checksum
byte itself: add each byte, and when the addition overflows past `$FF`, add
the carry back into the low byte.

```asm
        ldx #$00
        stx CHKSUM
        clc
?loop   lda DATA,x
        adc CHKSUM
        adc #$00        ; fold carry back into the 8-bit sum
        sta CHKSUM
        inx
        bne ?loop       ; 256-byte block
```

Use the same calculation for command frames and data frames. Custom
peripherals should verify the command checksum before ACKing the command,
then verify the data-frame checksum before sending final COMPLETE/ERROR.

---

## §7.2  Disk Drives (810 / 1050 / XF551 / Indus GT)

| Drive | Key features |
|---|---|
| 810 | 1771 FDC; density 128/256; write-protect pin |
| 1050 | Enhanced: 256-byte sector interleave; double-sided |
| XF551 | 512-byte sectors by default; 4 density profiles (180K/360K DS); fast copy-protect |
| Indus GT | Command-based SIO with interrupt; double-sided 192/360 KB; bootable from P3 |

Drive SIO address `$31` unit 1; device type byte `$01` (disk).

---

## §7.3  IOCB File-Access (IOSB free-finder)

Finding a free IOCB: scan for `$FF` in status byte at `$340/$350/$360…/3B0`. Each IOCB is 16 bytes. Only one byte must be `$FF: the status field.

```asm
find_free_iocb
        ldx #0                  ; IOCB index ×16
?loop   lda $340,x              ; status byte
        cmp #$FF
        beq ?found              ; $FF = free
        txa
        adc #$10                ; next IOCB (16 bytes)
        tax
        cmp #$80                ; past IOCB 7 → none free
        bcs ?none
        jmp ?loop
?found  txa
        adc #$01                ; ch = IOCB / 16 + 1
        sta $34a                 ; store channel number (IOCB + $01)
        rts
?none   lda #$00                ; no free IOCB
        rts
```

---

## §7.4  XEX Binary Load Format

| Field | Magic |
|---|---|
| Block 1 header | `FF FF` (standard Atari binary load file) |
| Segment header | start_lo start_hi end_lo end_hi, inclusive |
| INIT vector | segment writes `$02E2/$02E3`; DOS calls it after loading that segment |
| RUN vector | segment writes `$02E0/$02E1`; DOS jumps there after loading completes |

XEX files are the native Atari binary format. A file may contain several load segments. `$FF $FF` is a marker, not a universal per-block command byte; after it, the loader expects start/end address pairs and raw bytes. For reversing, build a segment map and watch writes to `INITAD ($02E2)` and `RUNAD ($02E0)`.

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

## §7.6  SpartaDOS X Relocatable Code

SDX strips binary into relocatable blocks. The block header types:

```
*dta a($FFFF),a(str_adr),a(end_adr)   ; non-relocatable binary block (standard DOS)
*dta a($FFFA),a(str_adr),a(end_adr)   ; SDX non-relocatable (identifies SDX loader)
*dta a($FFFE),b(blk_num),b(blk_id)
          a(blk_off),a(blk_len)       ; relocatable block
*dta a($FFFD),b(blk_num),a(blk_len)   ; address-update block
*dta a($FFFB),c'SMB_NAME',a(blk_len)  ; symbol update block
*dta a($FFFC),b(blk_num),a(smb_off)
          c'SMB_NAME'                 ; definition block (new symbol)
```

`blk_id` bits: bits 1–5 = memory type ($00=main RAM, $02=ext RAM/RAMBO); bit 7 = absence-of-data flag. The SDX loader computes `new_addr = block_addr_abs + (loaded_addr − blk_off)` for every address field in the relocatable block.

---

## §7.7  xBIOS — Mini-OS File Access

xBIOS is a compact disk I/O layer that can run from low memory and provides file read/write without the full DOS overhead.

**What xBIOS provides:** open, read, write, seek, and file-size query through SIO-compatible structures. It is useful for compact loaders and games that need file access without keeping a full DOS resident.

**DCB access for xBIOS:** identical to standard Atari 810 SIO DCB format: $09 command / $0A AUX1 / $0B AUX2; uses the same serial bus protocol as Atari DOS — xBIOS translates IECBUS calls to SIO internally by passing the DCB directly, then uses the OS handler sequence `SIOV` to call and poll.

```asm
                ; xBIOS-style DCB init for READ — file already on disk/drive_1_unit
                ; dcb must be in zero page for rapid SIO access

dcb_dev     = $00           ; device ID (e.g. $31 for drive-1)
dcb_cmd     = $02           ; $52 = read record
dcb_aux1    = $03           ; buffer address low
dcb_aux2    = $04           ; buffer address high
dcb_buf_lo  = $05           ; buffer page-lo (page aligned preferred)
dcb_buf_hi  = $06           ; buffer page-hi
dcb_len     = $09           ; buffer length (2-byte)

init_xbios_read
        lda #$31               ; DDEVIC = drive 1, SIO device
        sta dcb_dev
        lda #$52               ; DCMD = $52 (read-sector / get-verify record)
        sta dcb_cmd
        lda #<read_buffer
        sta dcb_aux1
        lda #>read_buffer
        sta dcb_aux2

        jsr SIOV               ; $E459 — call SIO handler via OS vector
        bcs ?error             ; carry = SIO error
        ; ... read_buffer now holds the sector
?error  rts

; read_buffer must be sector-aligned: 128 bytes for SD disks (Atari 810 format)
```

**xBIOS vs native CIO:** CIO is the OS-level handler layer (`CIOV`); SIO is the serial-bus layer (`SIOV`). xBIOS bypasses standard DOS file handling and uses SIO-compatible access patterns with a smaller runtime API.

---

---

## §7.8 Loader and Depacker Reversing Notes

Use this section with `tooling/reversing.md`.

| Symptom | Likely meaning |
|---|---|
| `SIOV` calls with changing AUX sector numbers | Direct sector loader |
| Writes to `RUNAD` or final indirect `JMP` | Loader transfers to real program |
| `(src),y` and `(dst),y` stream loops | Copy/depack stub |
| Bit-buffer shifts through carry | LZ/DEFLATE-style token reader |
| Writes to `$D301` around `$4000-$7FFF` copies | Extended RAM/banked asset transfer |
| CIO `D:` opens only during init | DOS file load before custom runtime |

Minimum reverse output:

- sector/file source;
- destination address range;
- final entry point;
- whether OS/DOS vectors are restored;
- whether the loader requires a specific DOS, drive, or SIO timing.

## §7.9 Loader Patterns

Boot-sector loaders run before DOS file APIs are active. They normally use
the OS disk entry or direct `SIOV` calls to read sectors into memory:

```asm
        org $0700
boot_hdr
        .word $0001             ; boot sector count, low byte used
        .word boot_hdr          ; load address
        .word $ffff             ; CASINI-related field

        lda #$ff
        sta $d301               ; disable BASIC / map RAM on XL/XE
        lda #1
        sta $0301               ; DUNIT = drive 1
        lda #'R'
        sta $0302               ; DCMD = read
        mwa #main_start $0304   ; DBUF
        mwa #main_sector $030a  ; DAUX sector number

load    jsr $e453               ; DSKINV — OS disk handler (SIOV is $E459)
        bmi error
        adw $0304 #$80          ; next 128-byte buffer
        inw $030a               ; next sector
        ; decrement sector counter...
        jmp load
error   jmp $e477               ; OS SIO error handling path
```

Use this only for ATR/boot-disk workflows. DOS file APIs are not active yet,
and the first three boot sectors are normally 128 bytes even on
enhanced-density disks.

This example uses `DSKINV`, which supplies the standard disk DCB fields.
A direct `SIOV ($E459)` call instead requires the caller to initialize the
complete DCB, including `DDEVIC`, transfer direction, timeout, and byte count.
See [cc65's Atari OS vector definitions](https://github.com/cc65/cc65/blob/master/asminc/atari.inc).

Dual-address loader stub:

```asm
source = $2000
dest   = $0700

        org source
        ; copy several pages from source to dest, then jump dest

        org dest,source         ; run as if at dest, store bytes at source
go      ; code that expects to execute at dest
```

This MADS `ORG run,load` form is the correct way to write self-relocating loaders: labels resolve to the execution address, while the bytes are emitted for the file/load address. When reversing, look for early copy loops followed by `JMP dest`; the real code addresses are usually the second `ORG` operand, not the initial file segment address.

For analyzer tools, read 16-bit block headers, distinguish standard XEX
segments from `$FFFA-$FFFE` SDX control blocks, and report update/symbol
records rather than flattening the file into raw load ranges.

## §7.10 SIO Peripheral-Side Protocol

A custom SIO peripheral sees a command phase followed by an optional data
phase. A command frame has:

| Byte | Meaning |
|---|---|
| 0 | Device ID and unit |
| 1 | Command byte |
| 2 | `DAUX1` |
| 3 | `DAUX2` |
| 4 | Checksum |

For a write-style command:

1. Wait for SIO COMMAND asserted.
2. Receive the 4-byte command plus checksum.
3. Wait for COMMAND deasserted.
4. If device ID, command, and checksum match, send ACK (`'A'`); otherwise send NAK (`'N'`).
5. Receive the data frame plus checksum.
6. ACK or NAK the data frame.
7. Perform the operation.
8. Send COMPLETE (`'C'`) or ERROR (`'E'`).

Common timing in simple microcontroller implementations is about 1000 us
before ACK/NAK and about 250 us before COMPLETE/ERROR. Treat these as
conservative software delays, not proof that all devices can collapse timing.

## §7.11 DSKINV Disk-Driver Entry

`DSKINV` is the OS disk-driver entry at `$E453`. It fills standard DCB fields
for basic disk operations and then uses `SIOV ($E459)`. Status is returned in
`DSTATS ($0303)` and in `Y`; negative status (`N=1`) means error.

The disk driver uses:

| Variable | Address | Purpose |
|---|---|---|
| `DSKTIM` | `$0246` | Long timeout, mainly formatting |
| `DSCTLN` | `$02D5/$02D6` | Sector size |
| `DCOMND` | `$0302` | Requested disk command |

Supported direct commands:

| Command | Meaning |
|---|---|
| `$21` / `'!'` | format disk |
| `$50` / `'P'` | put sector without verification |
| `$52` / `'R'` | read sector |
| `$53` / `'S'` | read status |
| `$57` / `'W'` | write sector with verification |

Any other command is effectively treated as a read-sector setup by the disk
driver; use a manually prepared DCB and `SIOV` for nonstandard drive commands.

Read/write sector setup:

```asm
        lda #1
        sta DUNIT
        lda #'R'        ; or 'P' / 'W'
        sta DCOMND
        ldx #<buffer
        ldy #>buffer
        stx DBUF
        sty DBUF+1
        ldx #<sector
        ldy #>sector
        stx DAUX1
        sty DAUX2
        jsr DSKINV
        bmi error
```

Read status sets `DSTATS` for read, `DBYT` to 4, `DBUF` to `DVSTAT ($02EA)`,
and timeout to about seven seconds. Formatting uses `DSKTIM`; after a format,
the buffer receives a list of bad sector numbers ending with `$FFFF`, and
`DBYT` returns the list length excluding the terminator.

## §7.12 DOS and SpartaDOS X Command Lines

Several DOSes expose command-line parameter retrieval through the OSS/DOS XL
protocol. Detect it by checking that DOS is loaded, `DOSVEC ($000A)` points
below ROM, and `(DOSVEC)+3` contains opcode `$4C` (`JMP`). The callable
parameter reader is at `(DOSVEC)+3`.

The parameter reader places the next parameter in `COMFNAM` at `(DOSVEC)+33`.
The returned string starts with a device name and ends with EOL `$9B`. The
routine does not by itself report end-of-line; compare the buffer offset
before and after the call to detect that no more parameters were consumed.

SpartaDOS X also provides a richer parsing library:

- `U_SLASH` parses a group of adjacent slash switches as a set, not as a
  sequence of separate ordered tokens.
- `/X /A 23 /Q`, `/XA 23 /Q`, and `/AX 23 /Q` can be equivalent to
  `U_SLASH` for switch detection.
- If a switch such as `/A` requires the following numeric parameter, check
  which switch occurred last before calling `U_GETNUM`.
- In SDX 4.47 and later, `U_SLASH` returns the ATASCII code of the last
  switch in `A`.
- SDX command lines are limited to 64 characters. For persistent option
  sets, parse an environment variable first, then restore and parse the real
  command line.

Environment-variable parse pattern:

1. Save `LBUF` and `BUFOFF`.
2. Call `GETENV` for the variable name.
3. Copy the returned text from the floating-point buffer area to `LBUF`.
4. Set `BUFOFF` to zero and run the same parser used for command-line text.
5. Restore the saved `LBUF` and `BUFOFF`.
6. Parse the actual command-line arguments.

The environment-variable text is constrained by the same 64-character command
buffer limit.

## §7.13 CIO Special Commands by Device

CIO special commands are device-handler specific. Do not assume a command
number has the same meaning across `D:`, `E:`, `P:`, and `S:`.

Common `D:` special commands:

| CMD | Meaning on common DOS handlers |
|---|---|
| `$20` / 32 | rename file |
| `$21` / 33 | delete file |
| `$22` / 34 | DOS-dependent: unerase, lock disk, make directory, or unsupported |
| `$23` / 35 | lock file or directory |
| `$24` / 36 | unlock file or directory |
| `$25` / 37 | POINT / seek |
| `$26` / 38 | NOTE / tell |
| `$27` / 39 | DOS-dependent: get file length or binary load |
| `$28` / 40 | binary load on many DOSes |
| `$29` / 41 | DOS-dependent: binary save, set current directory, or pick directory |
| `$2A` / 42 | make directory |
| `$2B` / 43 | remove directory |
| `$2C` / 44 | change directory |
| `$2D` / 45 | set boot file |
| `$2F` / 47 | get disk info |
| `$30` / 48 | get current directory |
| `$31` / 49 | set attributes on SpartaDOS X-style handlers |
| `$FD-$FF` / 253-255 | formatting variants on some DOSes |

`E:` and `P:` normally have no standard special commands, but XEP80 handlers
add device-specific commands. Typical XEP80 `E:` commands include:

| CMD | Meaning |
|---|---|
| `$14` / 20 | send command |
| `$15` / 21 | set normal or burst transmit mode |
| `$16` / 22 | send input command |
| `$18` / 24 | enable 80-column mode, with optional clear-screen |
| `$19` / 25 | disable 80-column mode |

The graphics-screen `S:` handler implements:

| CMD | Meaning |
|---|---|
| `$11` / 17 | `DRAWTO` using `CRSCOL`, `CRSROW`, and `ATACHR` |
| `$12` / 18 | `FILLTO`, like `DRAWTO` plus horizontal fill using `FILDAT` |

When writing portable DOS code, gate special commands by DOS/handler
detection. If the command is not supported, expect a device error rather than
quiet no-op behavior.
