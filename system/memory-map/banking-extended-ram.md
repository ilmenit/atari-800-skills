# Banking Extended Ram

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

### PIA port B — spurious IRQ hazard (PBCTL CB2)

> ⚠ **PBCTL-CB2 spurious IRQ:** Writing `$08` (CB2 low output) into `PBCTL ($D303)` then switching CB2 back to input mode (any `0xx` setting) causes bit 6 to be set and an IRQ is requested if the PIA interrupt is enabled (`PBCTL[3]=1`). This firing corresponds to the normal SIO command byte reception transition — every SIO packet on the POKEY serial port carries this same mode-change pattern. Safety rule: disable PIA IRQ before switching PBCTL direction and clear the IRQ flag manually before re-enabling.

Writing `$08` (CB2 low output) into `PBCTL ($D303)` then switching CB2 to input mode (any `0xx` setting) causes bit 6 to be set and an IRQ is requested if PIA interrupt is enabled (`PBCTL[3]=1`).
This corresponds to the normal SIO protocol command byte reception — the transition is part of every SIO packet on the POKEY serial port.
**Safety rule**: disable PIA IRQ before switching PBCTL direction; clear the IRQ flag manually before re-enabling.

### Writes to ROM are silently discarded

> ⚠ **ROM-write trap:** Writes to any address currently mapped to ROM (OS/BASIC/cartridge/self-test) are silently ignored. The underlying RAM is not accessible at the same address (no write-through as on some other platforms). On the 400/800, only PIA reset-on-power-on clears PIA registers — the RESET key bypasses the PIA, so PBCTL/PACTL must be explicitly reinitialized after warm-boot.

Writes to any address that is currently mapped to ROM (OS / BASIC / cartridge / self-test) are **ignored** — the underlying RAM is not accessible via the same address. It is not possible to write-through ROM as on some other platforms. On the 400/800, only PIA reset on power-on clears PIA registers; the RESET key does not.

---
