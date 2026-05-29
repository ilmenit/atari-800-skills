# Opcode Reference

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
