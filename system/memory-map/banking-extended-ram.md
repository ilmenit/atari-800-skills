## 2.3  BANK Switching & Extended Memory (XL/XE $4000–$7FFF)

Stock XL/XE ROM and 130XE extended-RAM banking use PORTB (`$D301`).
Other expansion families can use their own registers.

### PORTB bits for ROM / extended RAM window

| Bit | Function | 1 = | 0 = |
|---|---|---|---|
| 0 | OS ROM at `$C000–$CFFF` + `$D800–$FFFF` | **enabled** | disabled |
| 1 | BASIC ROM at `$A000–$BFFF` | disabled | **enabled** (inverted) |
| 4 | Extended RAM window `$4000–$7FFF` | disabled | **enabled** (inverted) |
| 5 | 130XE ANTIC extended window `$4000–$7FFF` | disabled (base RAM) | **enabled** |
| 6 | XEGS game ROM `$A000–$BFFF` (when BASIC is off) | disabled | **enabled** |
| 7 | Self-test ROM `$5000–$57FF` (when OS ROM is on) | disabled | **enabled** |

```asm
        ; XL/XE: disable OS/BASIC/self-test; cartridge ROM is independent
        lda PORTB
        and #$FE             ; clear bit 0 (OS ROM off)
        ora #$02             ; set bit 1 = BASIC disabled (inverted)
        ora #$80             ; set bit 7 = self-test disabled
        sta PORTB
```

### Extended RAM window — bits 2–3 for 130XE bank select

| PORTB[2:3] | 130XE bank |
|---|---|
| `00` | Extended bank 0 |
| `01` | Extended bank 1 |
| `10` | Extended bank 2 |
| `11` | Extended bank 3 |

On a stock 130XE, clear bit 4 for CPU extended access and clear bit 5 for
ANTIC extended access. A set enable bit selects base RAM for that processor.
Both processors use the same bank selected by bits 2–3; the enable controls
are independent. The 130XE has four extra 16K banks, not two.

Source: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §2.7 and PORTB reference.

| Total Size | Type | Extra Banks | Separate CPU/ANTIC | Bank Bits | Notes |
|---|---|---|---|---|---|
| 128k | Atari | 4 | YES | 2,3 | 130XE standard |
| 192k | Compy Shop | 8 | YES | 2,3,6 | |
| 192k | RAMBO | 8 | NO | 2,3,6 | |
| 256k | Karen | 12 | Partial | 2,3,5,6 | Only 4 of 12 banks visible to ANTIC |
| 256k | RAMBO (TOMS) | 12 | NO | 2,3,5,6 | Some bit combinations overlap |
| 256k | RAMBO | 12 | NO | 2,3,5,6 | Some bits map to base RAM (Newell/Wizztronics/ICD) |
| 320k | RAMBO | 16 | NO | 2,3,5,6 | |
| 320k | Compy Shop | 16 | YES | 2,3,6,7 | Bit 7 selects banks if bit 4/5 is 0, else SELF TEST |
| 576k | RAMBO (tf_hh) | 32 | NO | 2,3,5,6,7 | Bit 7 selects banks if bit 4 is 0, else SELF TEST |
| 576k | RAMBO | 32 | NO | 1,2,3,5,6 | Bit 1 selects banks if bit 4 is 0, else BASIC |
| 576k | Compy Shop | 32 | YES | 1,2,3,6,7 | Bits 7 & 1 select banks if bit 4/5 is 0 |
| 1088k | RAMBO | 64 | NO | 1,2,3,5,6,7 | Bits 7 & 1 select banks if bit 4 is 0 |
| 2112k | RAMBO | 128 | NO | 0,1,2,3,5,6,7 | Bit 0 also used (conflicts with OS ROM enable) |
| 4144k | RAMBO | 256 | NO | 0,1,2,3,4,5,6,7 | All bits used, BASIC/SELF-TEST cannot be enabled |

### Extended RAM Detection and Ownership

A bank probe writes RAM, even when it intends to restore it. Do not run one
after DOS, a RAM disk, or an expansion manager has allocated those banks.
Use the documented DOS/expansion allocation API when sharing memory.

For a stock-130XE-only probe, keep the routine, stack, save table, and active
display outside the CPU window. Keep ANTIC on base RAM while probing CPU banks.
Save original PORTB and all bytes that will be touched, including base RAM;
mark candidate banks, identify aliases, restore every touched byte, then restore
PORTB. Do not borrow `$00` or another OS byte as an unrecorded marker.

A generic expansion probe must additionally account for board-specific bank
encodings and ROM/self-test control bits. A routine for one wiring scheme does
not establish that all rows of the expansion table have been detected correctly.
No raw destructive probe is provided as a validated routine here.

### Axlon-Style Extended RAM

Axlon-style RAM was designed mainly for Atari 400/800 machines. Like 130XE
memory, it exposes 16K banks at `$4000-$7FFF`, but it does not provide
separate CPU and ANTIC banking. The bank-control register is write-only at
`$CFFF`.

Important decode caveat: original-style Axlon hardware incompletely decodes
the register. It can respond across `$CFC0-$CFFF` and, more dangerously,
`$0FC0-$0FFF`. Avoid placing code, stack-sensitive data, or unrelated I/O
there when probing Axlon hardware.

| Write to `$CFFF` | Visible bank |
|---|---|
| `$00` | base/home bank |
| nonzero | one extended 16K bank |

This allows up to 255 extra 16K banks, about 4080K extra RAM. Some XL/XE
expansions emulate Axlon-style banking with `$CFFF` decoded only in ROM space
when the OS ROM control bit leaves that address visible.

Axlon detection rules:

- Detection code must run entirely outside `$4000-$7FFF`.
- Save one byte from each candidate bank, mark banks, count consecutive banks
  that preserve the marker, then restore all saved bytes.
- Return `$00` to `$CFFF` before leaving so the base bank is visible again.
- Under SpartaDOS X, avoid raw probing after DOS has allocated extended RAM;
  use DOS memory-management calls when coexistence matters.

### PIA Control-Line IRQ Transition

After CB2 has switched from low output to high output (PBCTL bits 5–3:
`110` → `111`), changing it to an input mode (`0xx`) can set interrupt status
bit 6. An IRQ follows if that input interrupt is enabled. `$08` selects an
interrupt-enabled input mode; it is not an output-low command.

Keep unused PIA interrupts disabled. If a handler deliberately changes modes,
clear pending status by reading the port's data/input register with control
bit 2 set; reading the DDR does not clear it. See the Altirra manual §2.5.

### Writes to ROM

Writes to enabled OS/BASIC/cartridge/self-test ROM do not write through to
underlying RAM on the stock machines. Change the appropriate mapping before
accessing that RAM. The current CPU mapping and ANTIC mapping can differ on a
130XE; establish both when transferring display data.

Source: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §§2.5–2.7.
