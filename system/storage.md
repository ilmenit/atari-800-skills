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
| MADS boot/custom loader examples | §7.9 |

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

## §7.9 MADS Loader Patterns from the Example Corpus

Boot-sector loader, from the MADS example usually named `Boot.asm`:

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

load    jsr $e453               ; SIOV
        bmi error
        adw $0304 #$80          ; next 128-byte buffer
        inw $030a               ; next sector
        ; decrement sector counter...
        jmp load
error   jmp $e477               ; OS SIO error handling path
```

Use this only for ATR/boot-disk workflows. DOS file APIs are not active yet, and the first three boot sectors are normally 128 bytes even on enhanced-density disks.

Dual-address loader stub, from the MADS example usually named `file_loader.asm`:

```asm
source = $2000
dest   = $0700

        org source
        ; copy several pages from source to dest, then jump dest

        org dest,source         ; run as if at dest, store bytes at source
go      ; code that expects to execute at dest
```

This MADS `ORG run,load` form is the correct way to write self-relocating loaders: labels resolve to the execution address, while the bytes are emitted for the file/load address. When reversing, look for early copy loops followed by `JMP dest`; the real code addresses are usually the second `ORG` operand, not the initial file segment address.

The SDX/FAS block tracer example usually named `trace2.fas` is a good model for analyzer tools: read 16-bit block headers, distinguish standard XEX segments from `$FFFA-$FFFE` SDX control blocks, and report update/symbol records rather than flattening the file into raw load ranges.

## Source Notes

Primary references: `Altirra-hardware/extracted_chapters/chapter09.md`, `chapter10.md`, `atari-documentation/XEX-FORMAT/xex-format.md`, MADS SDX docs, MADS examples usually named `Boot.asm`, `file_loader.asm`, and `trace2.fas`, plus Atariki CIO/SIO/file articles summarized here in English.
