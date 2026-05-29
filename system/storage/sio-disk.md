# Sio Disk

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
