# Overview

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
