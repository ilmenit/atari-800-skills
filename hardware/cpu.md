---
name: atari8bit-cpu
description: >-
  MOS 6502/65C02/WDC 65C816 CPU reference for Atari 8-bit. Covers P-register flags, cycle timing, all undocumented NMOS opcodes (KIL/DCP/ISB/SLO/RLA/SRE/RRA), dead write-back cycles, page-cross penalties, IRQ/NMI/BRK dispatch hierarchy, DLI interrupt stacking, 65C02 and 65816 new instructions (BRA/TRB/PHY/BRL/JSL/MVN), full cycle-count table, and BRK-B-flag edge case. Use when the user asks about P-flags, RMW hazards, NMOS opcodes, CPU clock speed, DMA contention, IRQ dispatch, NMI priority, DLI hierarchy, interrupt stack rules, or any 6502/65816 instruction question.
---

# 01 — CPU Architecture

> **Scope:** MOS 6502/65C02/WDC 65C816: flags, cycle timing, DMA, undocumented opcodes, IRQ/NMI/BRK rules
> **Key items:** P-register N/V/C/D/I/Z/B; undocumented opcode map; BRK=7; IRQ/NMI=7+6; DLI/NMI hierarchy; NMIST bits

## Purpose

This file covers CPU architecture for the Atari 8-bit in four progressive layers:
1. **Quick-lookup table** — scan or search for the fact you need; jump to the § directly
2. **Reference tables & register maps** — the dense lookup layer most frequently referenced
3. **Working code examples** — verified ASM/pattern snippets
4. **Deep reference notes** — edge cases, caveats, implementation rules

| Out of scope | See instead |
|---|---|
| 65C02 BCD correction internals intended for swapped/diagonal addends | 65816 native-mode vector extensions and stack beyond basic IRQ — see 65816 ISA supplemental documentation |

**Tip:** browse the Quick-lookup table below first; the § labels are clickable in most markdown viewers.

All values hex ($NN) unless noted decimal. NMOS 6502 does NOT auto-clear D flag on IRQ entry — always CLD in interrupt handlers that use ADC/SBC.

## Quick-lookup

| Need | See § |
|---|---|
| Flag / P-register bits | §1.1 |
| Dead cycles + RMW hazards | §1.1 |
| Page-cross penalty (read vs write) | §1.1 |
| Undocumented 6502 opcodes (KIL/DCP/ISB/SLO/RLA/SRE/RRA) | §1.2 |
| ANC/ASR/ARR/ANE/SHS/LXA/LAS/SBX/SHA/SHX (unstable) | §1.2 |
| 65C02 vs 6502 new + removed instructions | §1.3 |
| 65816 mode detection + opcodes (BRL/JSL/MVN) | §1.4 |
| IRQ/NMI/BRK dispatch + B-flag edge case | §1.5 |
| DLI interrupt hierarchy (DLI-on-DLI, VBI-on-DLI) | §1.6 |
| Cycle counts by addressing mode (table) | §1.7 |
| Branch timing (3/4c + page-cross) | §1.7 |

---

## 1.1  MOS 6502 — Flags, Cycle Timing, DMA Contention

### Clock speeds

| Standard | CPU clock | Cycles / scan line | Cycles / frame |
|---|---|---|---|
| NTSC | 1.789 773 MHz (½ color clock) | 114 | 29 868 |
| PAL | 1.773 447 MHz | 114 | 35 568 |

### Flags (P register)

| Bit | Flag | Description |
|---|---|---|
| 0 | C — Carry | No-borrow indicator; C=1 for SBC means no borrow in |
| 1 | Z — Zero | Set when result = $00 |
| 2 | I — Interrupt mask | Set=IRQs masked; set on reset; NMIs unaffected |
| 3 | D — Decimal | BC correction active for ADC/SBC only |
| 4 | B — Break | Pushed set for BRK, cleared for IRQ/NMI; never directly readable |
| 5 | — | Always reads 1 in P; reused as M flag on 65C816 native |
| 6 | V — Overflow | Signed overflow during ADC/SBC/CMP |
| 7 | N — Negative | Copy of bit 7 of last result |

**Critical nuance — D flag:** NMOS 6502 does NOT auto-clear D on entry to an interrupt. Always `CLD` in interrupt handlers that use ADC/SBC.

### Dead memory cycles

These dummy cycles consume time and cannot be overlapped by DMA. Avoid them when racing against DLI timing:

```
; ❌ Bad in ISR context: INC abs does a write-back dummy cycle
INC $D40E         ; NMIEN — two write cycles; risky at exact cycle deadlines

; ✅ Fine: LDA zp does not produce a dead cycle
LDA $07           ; zero-page read — no dead cycle
```

Dead cycle sources: second cycle of implied ops (TXA), ALU cycle of RMW opcodes (INC abs, DEC abs, ASL abs…), second-to-last cycle of zp,X or abs,X indexed reads/writes, conditional branches that cross a page boundary.

**Dangerous addresses for dead-cycle writes:** PIA `$D300–$D3FF` (reads clear pending IRQs); cartridge control `$D500–$D5FF`; PBI `$D100–$D1FE` and `$D600–$D7FF`.

### Page-crossing penalty

Abs indexed reads (`LDA abs,X`, `AND abs,Y`, `(zp),Y`) speculate the fetch: read low-byte page first then retry at correct page if carry. Takes +1 cycle on page-cross. **Write operations always take the +1 cycle** — there is no speculative write.

Branches that cross a page take 4 cycles instead of 3 — even including BEQ issued near the target.

### DMA performance

| Display config | CPU bandwidth |
|---|---|
| No display DMA | 100% |
| GR.0 (narrow, no scroll) | 64% |
| GR.0 (narrow) max | 92% |
| PAL (all modes) | faster (DMA 5/6 as often) |

---

## 1.2  Undocumented 6502 Opcodes

All NMOS-only. None operate on the 65C02/65C816. Opcodes from the the reference manual full opcode table.

---

### Merged RMW + ALU opcodes (stable)

| Canonical name | Opcode | BF equivalent | Description |
|---|---|---|---|
| DCP | `$C7/$D7/$CF/$DF/$CB/$DB/$C3/$D3` | DEC+CMP | DEC, then CMP result; N/Z/C set from CMP |
| ISB | `$E7/$F7/$EF/$FF/$EB/$FB/$E3/$F3` | INC+SBC | INC, then SBC result; SENSITIVE to D flag |
| SLO | `$07/$17/$0F/$1F/$13/$1B/$03/$23` | ASL+ORA | ASL, then ORA A result; N/Z from ASL |
| RLA | `$27/$37/$2F/$3F/$33/$3B/$23/$33` | ROL+AND | ROL, then AND |
| SRE | `$47/$57/$4F/$5F/$43/$5B/$4B/$5B` | LSR+EOR | LSR, then EOR |
| RRA | `$67/$77/$6F/$7F/$7B/$6B` (wait) | ROR+ADC | ROR, then ADC; SENSITIVE to D flag |

Full opcode map (all 256 encodings): see the the reference manual full opcode map (Tables 2/3/4).

---

### Other stable undocumented opcodes

| Name | Opcode | Description |
|---|---|---|
| **LAX** | `$A3/$A7/$AF/$B3/$B7/$BF` | LDA + LDX simultaneously; N/Z set |
| **SAX** | `$87/$8F/$97/$9F` | AND A,X → store; no flags |
| **ANC** | `$0B` | AND #imm; C = bit7 of result |
| **ASR** | `$4B` | AND + LSR; N = bit 6 → C, Z from AND |
| **ARR** | `$6B` | ADC + AND + ROR; complex flag result |
| **ANE** | `$8B` | A AND X AND #imm → A; ⚠ UNSTABLE on real hardware |
| **SHS** | `$9B` | TXS + STA abs,Y with high byte ANDed |
| **LXA** | `$AB` | LDA + TAX; ⚠ UNSTABLE (immediate → A,X w/o AND on some chips) |
| **LAS** | `$BB` | LDA + TSX: A=X=S MEM AND S; N/Z set |
| **SBX** | `$CB` | AND #imm → X; then CMP X,#imm; C for SBC without borrow |
| **SHA** | `$93` | AND A,X AND high-byte-of-base-addr → store (abs,Y); ⚠ UNSTABLE on some chips |
| **SHX** | `$9E` | AND X AND high-byte-of-base-addr+1 → store (abs,Y) |

---

### Opcodes that lock up the CPU

```
KIL  $02 $12 $22 $32 $42 $52 $62 $72 $92 $B2 $D2 $F2
```
**Never branch to or fall through a KIL opcode; only RESET restores execution.**

---

## 1.3  65C02 (CMOS)

New stable instructions vs NMOS:

```
BRA  $80  — relative branch (2 bytes, 1 extra cycle over Bcc)
STZ  $64+ — store zero to abs/abs,X/zp/zp,X
TRB  $14+ — test+reset bits; TSB $04+ — test+set bits
BIT zp    — new zero-page form
BIT abs,X — new absolute form
BIT #imm  — immediate query (N/MSB, Z, V unchanged)
PHY/PLY $5A/$7A — push/pull Y
PHX/PLX $DA/$FA — push/pull X
WAI $CB — wait for IRQ
STP $DB — stop clock
```

Removed: all 6502 undocumented opcodes have NOP or reassigned replacements.

Decimal mode: N flag = bit7 of result (same as binary); V flag likewise. ADC/SBC take +1 cycle in D mode. D flag auto-clears on reset/IRQ on 65C02 unlike 6502.

---

## 1.4  WDC 65C816 / 65C816

### Mode detection

```asm
        ; Set D, then check if D self-clears → 65816 native (C flag = not 65C02)
        sed
        cld
        bcc ?is_65816     ; C=0 means D was auto-cleared → 65C816 native
        ; C=1 → 65C02; C=0 → 65816

?is_65816
        ; Check native vs emulation: REP #$10 clears X-flag if 16-bit mode
        sep #$10          ; set X flag
        cpx #$10
        bne ?emulation
        ; We are in native 16-bit mode
```

On 65C816, BRK stores **E-flag bit 4** profile byte (not B-flag); reading back from stack gives bit-4 = native-mode(0)/emulation(1).

### New 65816-only opcodes

```
COP  immediate  — co-processor call (same vector as BRK for OS-level in Atari context)
BRL rel16     — branch to absolute, long (3-byte offset)
JSL abs24     — jump to absolute, long (call)
JML abs24     — jump to absolute, long (RTS-able through bank boundary)
PHD/PLD   — push/pull 16-bit direct-page register (D)
PHK       — push program bank register (PBR)
PHB/PLB   — push/pull data bank register (DBR)
PEA abs16 — push effective address onto stack
PER rel16 — push PC+rel16 onto stack
STZ zp/abs/abs,X — guaranteed zero store (no flags affected)
REP #imm  — clear bits in M/X status flags (1-byte immediate = mask to clear)
SEP #imm  — set bits in M/X status flags
MVN/ MVP  — block move
```

### Size-prefixed mnemonics (65816, MADS / TASM syntax)

```
LDA.b  #$80    ; 8-bit accumulator  (A8 / M=0)
LDA.w  label   ; 16-bit accumulator (A16 / M=1)
LDX.b  $80      ; 8-bit index        (I8 / X=0)
LDY.w  $1234   ; 16-bit index       (I16 / X=1)
```

MADS directives to set mode: `.A8`, `.A16`, `.I8`, `.I16`, `.AI8`, `.AI16`, `.IA8`, `.IA16`.

---

### 65C816 DLI-safe interrupt rules

* Set VDSLST **before** setting NMIEN bit 7 ($80) on XL/XE.
* WSYNC provides horizontal blank; legal DLI width on first scanline of Mode 4 = ~10 CPU cycles.
* 16-bit registers must be saved/restored if using native mode inside ISR.
* `RTI` restores E/M/X flags from stack — correct for emulation-mode return.

---

## 1.5  Interrupts — IRQ / NMI / BRK

### IRQ (maskable)

- **Level triggered** — IRQ line must remain asserted; the 6502 responds when I-flag is clear.
- The IRQ must be **cleared at the device** before `CLI`, else IRQ handler re-enters immediately.
- **Branch delay:** a taken non-page-crossing branch delays IRQ acknowledge by 1 cycle. Cross-page branch = 4 cycles, no extra delay.
- **Overlapping IRQ + NMI:** IRQ acknowledged at cycle 4–8 can be hijacked by NMI; NMI executes with B flag set on stack if overlapping a BRK.

### NMI (edge‑triggered, non‑maskable)

On the 400/800: `RNMI` asserted only once on leading edge of VBLANK → OS warm-start handler (`$FED6`). On XL/XE: RESET button asserts `RESET` line directly (not RNMI); NMIST bit 5 stays latched until NMIRES write.

**NMIST (`$D40F`) bit layout**:  
- bit 7 = DLI occurred  
- bit 6 = VBI occurred  
- bit 5 = RNMI / SYSTEM RESET (400/800 only)  
- bit 4–0 = unused / reserved

DLI and VBI bits are mutually exclusive; DLI bit is cleared at scan line 248; VBI bit cleared whenever a DLI fires. NMIRES write does NOT suppress the pending interrupt — it only resets the status bit.

**Critical: never set NMIEN bit 7 before `VDSLST` is valid:**

```asm
        lda #<my_dli        ; set vector FIRST
        sta VDSLST
        lda #>my_dli
        sta VDSLST+1
        lda #$C0            ; NMIEN: $40=VBI, $80=DLI
        sta NMIEN           ; NOW enable
```

### BRK edge case

BRK = 7-cycle interrupt sequence, B-flag set on stack. If an NMI fires during cycles 4–8 of the BRK sequence, the NMI vector executes **with B-flag set**. Therefore a robust NMI/IRQ handler must check BRK first, then fall through to VBI in both:

```asm
dli_handler
        pha                  ; save A
        txa
        pha
        tya
        pha
        lda NMIST
        bpl ?vbi             ; B clear → IRQ/BRK
        ; BRK path: check RTI return
        bne ?dli             ; don't care about BRK here, VBI applies or DLI
?dli    lda NMIST
        and #$80
        beq ?end             ; no DLI
        ; ... DLI handler body ...
?end    pla
        tay
        pla
        tax
        pla
        rti
```

---

## 1.6  DLI Interrupt Hierarchy (Summary)

| Event | Effect on In-Progress DLI | Notes |
|---|---|---|
| **DLI while another DLI running** | First DLI saved; second executes; first resumes several lines later → artifacts if too slow | DLI stack: max 25 DLI frames before VBI |
| **WSYNC + interrupt gotcha** | Interrupt processing + ANTIC font cycles consume the first WSYNC → extra scan line of old color | Don't put WSYNC at top of DLI if already behind |
| **VBI while DLI running** | DLI resumes on first scan line of the *next frame* after VBI completes | VBI is highest priority |
| **DLI while VBI running** | VBI resumes; DLI fires on scan line 24 of *following* frame | Delayed delivery |
| **JVB `$C1` + DLI** | DLI on *every* scan line 224–248; up to 24 DLIs stack; unwind after VBI | DLI must be extremely short (~12-20 cycles) |

---

## 1.7  Opcode Quick Reference

| Addressing mode | Cycles | Notes |
|---|---|---|
| Implied / accumulator | 2 | `TXA`, `INX`, `DEY` … |
| Immediate (`#imm`) | 2 | `LDA #$FF` … |
| Zero page (`$NN`) | 3 | `LDA $80`, `STA $80` … |
| Zero page,X / Zero page,Y | 4 | +1 vs ZP |
| Absolute / absolute,X | 4 | `LDA $D016` |
| Absolute,Y (read) / absolute indexed | 4 (+1 if page cross) | `LDA $D000,Y` — +1 speculative read retry |
| Absolute indexed write | 5 (always) | `STA $D000,X` — no speculative write |
| `(zp)` / `(zp),Y` / `(abs)` | +1 for `(abs)`, 6+ for `(zp),Y` page-cross | JMP `(abs)` is the infamous indirect bug |
| Immediate → A (`LDA #`) | 2 | |
| RMW opcode (INC abs, ASL abs) | 6 | dead write cycle included |
| Branch (taken, same page) | 3 | |
| Branch (taken, cross page) | 4 | always accrues penalty |
| Branch + branch (two taken) | 4 + 3/4 | wait-for-sequential-issue pipeline |
| BRK / IRQ / NMI entry | 7 | stacks PSB; sets B flag on BRK paths |
| First instruction in IRQ handler | +6 | `LSR abs` = +6 expects the `BRK` to be set-to |
| JSR | 6 | |
| RTS / RTI | 6 | pops+1 each |
| PHP / PLP | 3 / 4 | |

| Opcode class | Cycle range | Comments |
|---|---|---|
| `LDA/STA/STY/STX` absolute | 4 | RMW-avoiding: 6+ |
| `ADC / SBC` (accumulator) | 2 | +1 in decimal mode on 65C02 |
| `CMP / CPX / CPY` immediate | 2 | |
| `CMP` zero-page | 3 | similar latency to `LDA` zero-page |
| `BEQ/BNE/BCC/BCS` | 2 (not taken) / 3 (taken) / 4 (page-cross) | |
| `ROL/ROR/ASL/LSR` / memory | 6 | 5 on zero page |
| `BIT zero-page` | 3 | 0x24; advanced ZP-only forms added by 65C02 |
| `BIT absolute` (65C02) | 4 | |

**NMOS-only page-cross penalty summary**:
- Reads (`LDA abs,Y`, `AND abs,Y`, etc.) speculate on page-cross: read wrong page → carry → retry (5 cycles total if wrong).
- Writes (`STA abs,Y`) always 5 cycles speculatively; no retry; the first cycle is a dummy-read.
- `(abs)` indirect (`JMP (abs)`) has a well-documented hardware bug when the low byte of the target address is `$FF` — the high byte is fetched from `$xx00` instead of `$xx+1`.

---

*Primary references: see index for full map; Altirra hardware reference (EN) — embedded into SKILLS.md*
