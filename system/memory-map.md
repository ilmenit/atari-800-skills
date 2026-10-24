---
name: atari8bit-memory
description: >-
  Atari 8-bit 64 K memory map and chipset register reference. Covers the flat $0000–$FFFF address space, PIA 6520 PORTA/PORTB/PACTL/PBCTL register table, PORTB ROM-banking bits (OS, BASIC, self-test on 400/800/XL/XE), extended RAM windowing (130XE banks 0/1 via ANTIC bit 5, RAMBO 192K/256K/320K/576K, COMPY 320K/576K), zero-page zone maps, ZP idioms (INC/DEC, negative-index loop, fast ISR scratch save), and the inline-parameter JSR trick. Use when the user asks about RAM layout, PIA registers, PORTB banking, extended RAM, zero-page use, stack tricks, or ROM disable.
---

# 02 — Memory Map & System Architecture

> **Scope:** 64K flat map ($0000–$FFFF), PIA 6520, PORTB banking/ROM bits, extended RAM (130XE/RAMBO/COMPY/576K), zero-page idioms, inline-parameter JSR trick
> **Key items:** PORTA $D300, PORTB $D301, PACTL/PBCTL $D302/$D303, ZP $00–$FF, 130XE ANTIC bank-enable bit 5

## Purpose

This file covers the memory map and system architecture for the Atari 8-bit in four progressive layers:
1. **Quick-lookup table** — scan or search for the fact you need; jump to the § directly
2. **Reference tables & register maps** — the dense lookup layer most frequently referenced
3. **Working code examples** — verified ASM/pattern snippets
4. **Deep reference notes** — edge cases, caveats, implementation rules

| Out of scope | See instead |
|---|---|
| DMA contention and cycle-stealing budget | §03-antic (ANTIC DMA section) |
| SIO DCB structure and frame format | §07-disk-file (SIO section) |

**Tip:** browse the Quick-lookup table below first; the § labels are clickable in most markdown viewers.

Only low 4 address bits decoded at $D300–$D3FF; PIA address bits 0-1 select each 4-register bank. Writes to ROM addresses are silently ignored.

## Quick-lookup

| Need | See § |
|---|---|
| 64 K memory map | §2.1 |
| Zero-page zone maps | §2.1 |
| PIA 6520 register table | §2.2 |
| PORTB OS/BASIC/self-test ROM bits | §2.3 |
| Extended RAM 130XE/RAMBO/COMPY and ANTIC bank-enable | §2.3 |
| Spurious IRQ PBCTL CB2 hazard | §2.2 |
| Zero-page idioms (INC/DEC, negative-index loop, ISR scratch) | §2.4 |
| Inline-parameter JSR trick | §2.5 |

---

## 2.1  Full 64 K Memory Map ($0000 – $FFFF)

The Atari 8-bit has a flat 64 K 16-bit address space. Installed RAM, cartridges,
and model-specific ROM banking determine which regions are accessible.

### Map by region

| Region | Purpose |
|---|---|
| `$0000–$00FF` | Zero page — OS, user, FP (floating-point) slots |
| `$0100–$01FF` | Hardware stack — 256 bytes, grows down |
| `$0200–$02FF` | OS database, interrupt vectors, and hardware shadows (`VDSLST`, `VVBLKI`, `SDLSTL`, `CH`) |
| `$0300–$030B` | SIO Device Control Block (DCB), from `DDEVIC` to `DAUX2` |
| `$030C–$033F` | OS I/O workspace and handler table (`HATABS` at `$031A`) |
| `$0340–$03BF` | Eight IOCBs, 16 bytes each |
| `$03C0–$03FC` | Printer buffer and model-dependent OS workspace |
| `$03FD–$047F` | Cassette buffer area (`CASBUF` starts at `$03FD`) |
| `$0480–$05FF` | Application / language / floating-point workspace; includes `LBUFF` at `$0580`, not all freely available |
| `$0600–$06FF` | Page six, normally available for user code unless another resident program uses it |
| `$0700–$7FFF` | RAM for DOS, programs, display memory, and buffers as allocated; consult `MEMLO`/`MEMTOP` |
| `$8000–$9FFF` | RAM or cartridge ROM, depending on cartridge mapping |
| `$A000–$BFFF` | RAM, cartridge ROM, or built-in BASIC ROM on XL/XE when enabled |
| `$C000–$CFFF` | XL/XE OS ROM when enabled; normally unpopulated on stock 400/800 |
| `$D000–$D7FF` | Hardware I/O: GTIA `$D0xx`, PBI `$D1xx` (XL/XE), POKEY `$D2xx`, PIA `$D3xx`, ANTIC `$D4xx`; remaining pages are model/expansion dependent |
| `$D800–$DFFF` | Floating-point ROM (part of the banked OS ROM on XL/XE) |
| `$E000–$FFFF` | 8K OS ROM region; XL/XE also maps OS ROM at `$C000–$CFFF` and `$D800–$DFFF` |

RAM is only present up to the installed size. DOS, cartridges, and resident
handlers may reserve otherwise usable RAM; check ownership before using it.
Reference: [cc65 Atari definitions](https://github.com/cc65/cc65/blob/master/asminc/atari.inc), OS RAM variables and hardware equates.

### Zero page zones

| Zone | Range | Notes |
|---|---|---|
| OS workspace | `$00–$7F` | Includes timers, pointers, CIO zero-page IOCB (`$20–$2F`), and editor workspace; not generally free |
| Language / application workspace | `$80–$D3` | Availability depends on BASIC, DOS, and other resident software; reserve explicitly |
| Floating-point workspace | `$D4–$FF` | Reuse only if no active code needs the OS floating-point routines |

Joystick/paddle shadows live in page two (for example, `PADDL0 $0270` and
`STICK0 $0278`); `WSYNC` is hardware at `$D40A`, not a zero-page shadow.

### PIA 6520 (Peripheral Interface Adapter)

Address range: `$D300–$D3FF`, only bits 0–1 decoded → 4 mirrored locations:  
`$D300/$D301/$D302/$D303` / `$D304/$D305/$D306/$D307` / … / `$D3FC/$D3FD/$D3FE/$D3FF`

| Register | Address | Function |
|---|---|---|
| PORTA | `$D300` | Joystick directions ports 1/2 (read); data direction chg when DDRA bit2=0 |
| PORTB | `$D301` | Port data; banking/ROM enable on XL/XE (output: bits 0,1,4,6,7); joystick ports 3/4 on 400/800 |
| PACTL | `$D302` | Port A control register (data direction + interrupt enable) |
| PBCTL | `$D303` | Port B control register (same layout as PACTL) |
| DDRA | bit=write to $D300 when PACTL.bit2=0 | Data direction: 0=input, 1=output |
| DDRB | bit=write to $D301 when PBCTL.bit2=0 | Data direction: 0=input, 1=output |

**PORTA PACTL X Micro**

```asm
        ; Typical PACTL/PBCTL init on XL/XE
        lda #$34             ; CA2 low, CB2 low, interrupts disabled
        sta PACTL
        sta PBCTL
```

**400/800 RESET key:** RNMI asserted on leading edge of VBLANK → OS warm-start.  
**XL/XE RESET key:** Assert reset lines on CPU, ANTIC, FREDDIE, PIA; cold-restarts at `$FFFC`.

---

## 2.2  Power-On / Reset

| Condition | Behavior |
|---|---|
| Warm boot (400/800) | RNMI → OS `$FED6` — warm-start, keeps RAM |
| Cold boot (all) | RESET line → `$FFFC` vector; all registers undefined |
| PIA on 400/800 | Only reset on power-on; not by RESET key |
| PIA on XL/XE | Reset on power-on AND RESET key; all regs cleared to $00 |

**RAM power-up bias:** DRAM decays after power-off → power-on produces block patterns (often `$00/$FF` alternating). Treat RAM as undefined until explicitly initialized.

**Floating data bus:** On 800 (secondary I/O bus), on XL/XE without pull-ups: un-decoded reads return the last byte on the data bus (often from the *previous* cycle). On XL/XE with pull-ups: undecoded reads return `$FF`.

---

## 2.3  BANK Switching & Extended Memory (XL/XE $4000–$7FFF)

All banking is driven by PORTB (`$D301`).

### PORTB bits for ROM / extended RAM window

| Bit | Function | 1 = | 0 = |
|---|---|---|---|
| 0 | OS ROM at `$C000–$CFFF` + `$D800–$FFFF` | **enabled** | disabled |
| 1 | BASIC ROM at `$A000–$BFFF` | disabled | **enabled** (inverted) |
| 4 | Extended RAM window `$4000–$7FFF` | disabled | **enabled** (inverted) |
| 6 | XEGS game ROM `$A000–$BFFF` | disabled | **enabled** (inverted) |

```asm
        ; Disable all system ROMs — full 62 K RAM
        lda PORTB
        and #$FE             ; clear bit 0 (OS ROM off)
        ora #$02             ; set bit 1 = BASIC disabled (inverted)
        and #$7F             ; clear bit 7 = self-test off
        sta PORTB
```

### Extended RAM window — bits 2–3 for 130XE bank select

| PORTB[2:3] | 130XE bank |
|---|---|
| `00` / `10` | Bank 0 (`$4000–$7FFF` → RAM) |
| `01` / `11` | Bank 1 (pseudo-SRAM, visible as `$4000–$7FFF`) |

Separate ANTIC access (130XE only): bit 5 enables ANTIC's view of extended RAM independently.

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

### Extended RAM Detection Code

The following routine detects the size of extended memory non-destructively. It returns the number of extra 16k banks in `Y` (0 if base 64K only) and populates the `banks` array with valid `PORTB` values.

```asm
ext_b  = $4000
portb  = $d301

detect_ext
       lda portb
       pha
       lda #$ff
       sta portb
       lda ext_b
       pha

       ldx #$0f       ; Save bytes from 16 possible 64k blocks
_p0    jsr setpb
       lda ext_b
       sta bsav,x
       dex
       bpl _p0

       ldx #$0f       ; Zero them out
_p1    jsr setpb
       lda #$00
       sta ext_b
       dex
       bpl _p1

       stx portb      ; Eliminate base memory (X=$FF)
       stx ext_b
       stx $00

       ldy #$00       ; Loop counting 64k blocks
       ldx #$0f
_p2    jsr setpb
       lda ext_b      ; If ext_b != 0, block already counted
       bne _n2
       dec ext_b      ; Mark as counted
       lda ext_b
       bpl _n2        ; Hardware check
       lda portb      ; Write PORTB value to array for bank 0
       sta banks,y
       eor #%00000100 ; Banks 1, 2, 3
       sta banks+1,y
       eor #%00001100
       sta banks+2,y
       eor #%00000100
       sta banks+3,y
       iny:iny:iny:iny
_n2    dex
       bpl _p2

       ldx #$0f       ; Restore memory
_p3    jsr setpb
       lda bsav,x
       sta ext_b
       dex
       bpl _p3

       stx portb      ; X=$FF
       pla
       sta ext_b
       pla
       sta portb
       rts

setpb  txa            ; Map X index to PORTB bits
       lsr:ror:ror:ror
       adc #$01       
       ora #$01       ; OS ROM enabled
       sta portb
       rts

banks  .ds 64


> **SpartaDOS X compatibility:** The `detect_ext` routine banks in descending PORTB order,
stepping X from `$0F` to `$00` via `setpb`. This ordering is the opposite of SpartaDOS X's
bank allocation, which hands out extended RAM starting from the highest bank. Running
`detect_ext` inside an SDX session without accounting for SDX's reservation layout can corrupt
an active RAM disk. For SDX-aware software: use the SDX memory-management API
(`MXRAM`, `PFCOM`) instead of raw PORTB probing, or call `detect_ext` only before SDX
has loaded.

bsav   .ds 16
```

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

### PIA port B — spurious IRQ hazard (PBCTL CB2)

> ⚠ **PBCTL-CB2 spurious IRQ:** Writing `$08` (CB2 low output) into `PBCTL ($D303)` then switching CB2 back to input mode (any `0xx` setting) causes bit 6 to be set and an IRQ is requested if the PIA interrupt is enabled (`PBCTL[3]=1`). This firing corresponds to the normal SIO command byte reception transition — every SIO packet on the POKEY serial port carries this same mode-change pattern. Safety rule: disable PIA IRQ before switching PBCTL direction and clear the IRQ flag manually before re-enabling.

Writing `$08` (CB2 low output) into `PBCTL ($D303)` then switching CB2 to input mode (any `0xx` setting) causes bit 6 to be set and an IRQ is requested if PIA interrupt is enabled (`PBCTL[3]=1`).
This corresponds to the normal SIO protocol command byte reception — the transition is part of every SIO packet on the POKEY serial port.
**Safety rule**: disable PIA IRQ before switching PBCTL direction; clear the IRQ flag manually before re-enabling.

### Writes to ROM are silently discarded

> ⚠ **ROM-write trap:** Writes to any address currently mapped to ROM (OS/BASIC/cartridge/self-test) are silently ignored. The underlying RAM is not accessible at the same address (no write-through as on some other platforms). On the 400/800, only PIA reset-on-power-on clears PIA registers — the RESET key bypasses the PIA, so PBCTL/PACTL must be explicitly reinitialized after warm-boot.

Writes to any address that is currently mapped to ROM (OS / BASIC / cartridge / self-test) are **ignored** — the underlying RAM is not accessible via the same address. It is not possible to write-through ROM as on some other platforms. On the 400/800, only PIA reset on power-on clears PIA registers; the RESET key does not.

---

## 2.4  Zero-Page Idioms

| Idiom | Example | Notes |
|---|---|---|
| Increment/decrement 16-bit (hi carries if lo overflows) | `INC ptr: INC ptr+1: BNE skip` / `DEC ptr+1: BNE skip` | `INC/DEC ZP` takes 5 cycles, RMW side effect |
| Bit flag set/clear | `ORA #$80` / `AND #~$80` | LSB/OMSB of bit-index using `:ROL`, `:LSR`, 7 or 0 |
| Negative-index backwards loop | `LDY #-n: … DEY: BPL loop` | Zero-page table walk backwards wrapped at $00FF |
| Fast ISR scratch save | `STA save_a: STX save_x: STY save_y` | Hardware stack is fastest; ZP shadow nearby |
| 16-bit load with skip | `LDA #<val: STA ptr: LDA #>val: STA ptr+1` | Separate LDA avoids page-cross on HIGH byte |

---

## 2.5  Stack & Subroutine Parameters

6502 stack: 256 bytes at `$0100–$01FF`, `TSX/TXS` to read/write pointer.

**Parameter-inline trick:** A subroutine can read own return-address off the stack to find embedded data tables after the JSR, avoiding zero-page allocation:

```asm
        ; Caller:
        jsr my_routine
        .byte $01, $02, $03   ; data table after JSR

        ; Callee:
my_routine
        pla                  ; pop low byte of return PC
        sta data_ptr
        pla                  ; pop high byte
        sta data_ptr+1
        ; Now data_ptr → .byte table past JSR
        rts
```

---

*Content fully self-contained. All key facts are present in this file.
