# Undocumented Opcodes

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
