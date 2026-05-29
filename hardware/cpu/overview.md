# Overview

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
| 6502 vs 65C02 vs 65C816 detection | §1.3 |
| 65816 mode detection + opcodes (BRL/JSL/MVN) | §1.4 |
| IRQ/NMI/BRK dispatch + B-flag edge case | §1.5 |
| DLI interrupt hierarchy (DLI-on-DLI, VBI-on-DLI) | §1.6 |
| Cycle counts by addressing mode (table) | §1.7 |
| Branch timing (3/4c + page-cross) | §1.7 |

---
