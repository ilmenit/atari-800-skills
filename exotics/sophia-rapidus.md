---
name: atari8bit-peripherals
description: >-
  Sophia GTIA replacement card, APE-Time RTC, LDW Super 2000/CA-2001 SIO Z80 peripheral on Atari 8-bit.
---
# 16 — Peripheral Exotics & Misc Hardware

> LDW Super 2000 / CA-2001 programming guide (EN) — content fully self-contained.
> **Primary sources:** `Atariki/articles/sophia.md`, `wykrycie_sophii.md`, `ape_time.md`, `programowanie_stacji_ldw_super_2000_i_ca-2001.md`, plus Altirra hardware reference notes.
> **Scope:** Sophia GTIA replacement (A/B/C + Sophia 2), APE-Time RTC (SIO $45/$93), LDW Super 2000/CA-2001 (SIO $58 Z80)
> **Key items:** GRACTL $D01D SPCEN bit7; SOPHIA $D01E signature; APE DCB $45/$01/$93; LDW $58 Z80 @$7F00

## Quick-lookup

| Need | See § |
|---|---|
| Sophia 2: 256-colour regs, GR.10 cycle fix, overscan mask bit5 | §16.1 |
| Sophia 2: detection SPR/GRACTL/CB02/E\u2192C bit (SPCEN) | §16.1 |
| Sophia 1: undetectable (no unique register footprint) | §16.1 |
| APE-Time RTC: SIO DCB test-case $6B DDMMYY+HMMSS | §16.2 |
| LDW Super 2000/CA-2001: SIO $58 upload + execute | §16.3 |
| LDW Z80 ROM functions $00\u2013$14 at $0004 | §16.3 |
| LDW I/O port table $0/$1\u2013$E/$F | §16.3 |

---

## 16.1 Sophia — GTIA Replacement Hardware

> ⚠ **Sophia 1 undetectability:** Sophia 1 exposes no programmable register footprint and cannot be distinguished from stock GTIA at runtime. Any code that probes `SOPHIA ($D01E)` must treat a zero/unknown-signature result as "Sophia 1 or GTIA" — never report "Sophia 2" on that path.

Sophia is a third-party GTIA replacement card (50×45 mm) that fits between the GTIA chip and the mainboard. Core: Altera MAX II CPLD.

### Versions

| Version | Output | Resolution | Palette | ROM flags |
|---------|--------|-----------|---------|-----------|
| Rev A | RGB / YPbPr | standard | 256-col (18-bit) | no |
| Rev B | RGB / YPbPr | standard | 256-col (18-bit) | + separate V-sync, different DAC |
| **Sophia 2** (2020, Simius) | RGB (TTL), VGA 480p/576p | high | 256-col (24-bit on pilot proto) + 16 palettes | non-vol. settings store |

### 256-colour mode

Sophia's colour registers are **8-bit** (vs. GTIA's 7-bit), so a full 256-entry palette is always active. For backward compatibility, the extra luminance bit is gated through bit 3 of `PMCNTL ($D01D)` — `GRACTL bit 3 = 1` enables 8-bit colour mode.

### Hires pixel colour

In contrast to GTIA (which only permits background colour in HIRES mode), Sophia allows setting a per-pixel colour via `COLPF1 ($D016)` even in hires Graphics 8 mode — enabled by `PMCNTL bit 4 = 1`.

### GR.10 cycle shift

Sophia corrects the NTSC cycle-shift bug for Graphics 10 (P/M 2L detailed) which the original GTIA has on the 315/240 register; lines are now off-cycle-corrected relative to ANTIC.

### Overscan mask

`PMCNTL bit 5 = 1` restricts the display to 336 hires pixels, suppressing the overscan artefacts that appear on larger-than-standard creation widths. Bit 3 (`PMCNTL`) gate is active before using bit 5 on Res-C bits; non CONFIG-writable is reset-safe.

### GR.10 pixel positioning

GR.10 pixel positioning is corrected relative to GTIA (lines shifted right by one NTSC cycle).

### Detection: Sophia 1 vs. Sophia 2

> ⚠ **Sophia 1 undetectability:** Sophia 1 exposes no programmable register footprint and cannot be distinguished from stock GTIA at runtime. Any code that probes `SOPHIA ($D01E)` must treat a zero/unknown-signature result as "Sophia 1 or GTIA" — never report "Sophia 2" on that path.

> ⚠ **Sophia 1 undetectability:** Sophia 1** is **not detectable programmatically** — it generates GTIA-compatible signals with no unique register footprint.

**Sophia 2** exposes a programmable bank switchable under `PMCNTL ($D01D)` bit 7 (SPCEN). The standard detection routine is:

```asm
; A = original GRACTL value (caller saves/restores)
; Z=1 → Sophia present, Z=0 → absent or Sophia 1
GRACTL  = $d01d
SOPHIA  = $d01e
REV     = $d015

detect_sophia2 pha                 ; save GRACTL
        lda   GRACTL
        and   #%01111110        ; preserve non-SPCEN bits (no NVRAM write)
        sta   GRACTL
        lda   #%10000000        ; enable Sophia registers (SPCEN=1)
        sta   GRACTL
        ldx   SOPHIA            ; read signature
        ldy   REV               ; read revision
        pla                     ; restore GRACTL via callers' 
        and   #%01111110
        sta   GRACTL            ; deactivate Sophia register bank
        ; Z=1 → Sophia 2 present (signature in X = 'S'=$53)
        cpx   #'S'
        rts
```

Sophia 2 returns **`$53='S'`** at `SOPHIA ($D01E)`, the revision byte at `REV ($D015)` (nibbles BCD: major 4..7, minor 0..9).

---

## 16.2 APE-Time Real-Time Clock

> ⚠ **APE-Time RTC DCB signature:** DCB command $6B is an END-DCM-level signature query; the response payload is 7 bytes (DDMMYY + HMMSS — Day-Month-Year + Hour-Minute-Second) not 8. A read using DCB $45 expects 8 bytes but the APE-Time returns 7 — the caller must handle the trailing byte by discarding it. The $01/$93 DCB variants write the short-form BCD time-clear pattern: $01/$01/$93 (PROMPT/STATUS/TIME).

APE-Time is a SIO real-time clock peripheral implementing a simple date/time query protocol.

| DCB field | Value |
|-----------|-------|
| DDEVIC | `$45` |
| DUNIT | `$01` |
| DCMND | `$93` |
| DSTATS | `$40` |
| DBUFA | address of 6-byte buffer |
| DAUX1 | `$EE` |
| DAUX2 | `$A0` |

Upon `JSIOINT ($E459)` with the above DCB, the RTC writes 6 bytes to `DBUFA`:

| Byte | Meaning |
|------|---------|
| 0 | Day (DD, BCD 01–31) |
| 1+2 | Month and year (MM-YY; YY is BCD offset from 2000) |
| 3 | Hour (HH, BCD 00–23) |
| 4 | Minute (MM, BCD 00–59) |
| 5 | Second (SS, BCD 00–59) |

---

## 16.3 LDW Super 2000 / CA-2001 Positioning Device

> ⚠ **LDW Z80 timing:** The LDW SIO $58 upload response requires a 2-second USR-break watchdog on the host; if the host timeout is less than the Z80 loader block-send window the transfer flushes with corrupted ROM. Z80 ROM function IDs are 0–14 only (RST vectors at $0004 point to function-handlers beyond $0020 for the 15-entry table); function $15 and above are reserved and produce undefined results.

LDW Super 2000 (and compatible clone CA-2001) is a position-digitiser peripheral with a Z80 CPU, communicating over SIO command `$58`. The Z80 firmware runs at 4 MHz; code is uploaded to address `$7F00` in the device RAM.

### Command `$58` — two phases

**Phase 1 — upload firmware:**
| DCB field | Value |
|-----------|-------|
| DDEVIC | `$31` |
| UNIT | station number |
| DCMND | `$58` ('X') |
| DSTATS | `$80` (write) |
| DBUFA | buffer address in Atari RAM |
| DTIMLO | sector-timeout (8 = typical) |
| DBYT | ≤ 256 bytes |
| DAUX2 | `$01` (download-to-device-RAM) |

Busy lamp lights on the device console during upload. A second command must NOT be sent between upload and execute.

**Phase 2 — execute firmware:**

Same DCMND `$58`, but `DBUFA` → data buffer, `DSBY` = expected result byte count, `DTIMLO` = timeout. `DSTATS` determines the data transfer direction:

| DSTATS | Meaning |
|--------|---------|
| `$00` | No data exchange |
| `$40` | Read result bytes from device (`DBUFA`) |
| `$80` | Write additional input bytes to device |
| `$C0` | Bidirectional |

**Z80 ROM function table** (at `$0004` in device address space):

| FN | Description |
|----|-------------|
| `$00` | Return ROM version (major×256 + minor) in (DE) |
| `$01` | Return head / idle |
| `$02` | Seek head to track (D = track × 2) |
| `$03` | Read sector (E) from track (D) |
| `$04` | Write sector (E) to track (D) |
| `$05` | Receive byte from SIO (C = return) |
| `$06` | Transmit byte to SIO (A = value) |
| `$07` | Receive record of length (B) from SIO into (DE); B=0 → 256 bytes |
| `$08` | Transmit record of length (B) from (DE) to SIO |
| `$09` | Convert digit for display (A in/out) |
| `$0A` | Decimal conversion (A → DE, 2-digit) |
| `$0B` | Hex conversion (A → DE, 2-digit) |
| `$0C` | Motor on/off (CF=1 → on; CF=0 → off) |
| `$0D` | Update switch status / detect disk change |
| `$0E` | Return current buffer address (→BC) |
| `$0F` | Return control-flag byte address (→IX) |
| `$10` | Audio beep |
| `$11` | Update the display |
| `$12` | Return register addresses (read and write controller) (→BC, →DE) |
| `$13` | Set write density for current mode |
| `$14` | Return status / current track (→DE, →IX; track × 2) |

**Z80 I/O ports:**

| Port | I/O | Description |
|------|-----|-------------|
| `$0/$1` | IN | Audio signal |
| `$2/$3` | IN | Index impulse tracking enable |
| `$4/$5` | IN | Invert TxD |
| `$6/$7` | IN | Invert RxD |
| `$8/$9` | IN | Generation / set DDEN for FDC |
| `$A/$B` | IN | Motor |
| `$C/$D` | IN | Index impulse output |
| `$E/$F` | IN | RAM charger switch (maps $0000–$7FFF RAM → RAM → ROM) |

---

*All facts are self-contained in this file. Reference articles covering Sophia, Sophia II, APE-Time RTC, and LDW Super 2000/CA-2001 — content fully embedded in this file.
