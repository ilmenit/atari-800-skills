# Overview

## Purpose

This file is a tier-3 deep-dive supplement to antic.md (§§3.6/3.8/3.10). When an agent has exhausted the main §3.6 DLI boilerplate and §3.8 multiple-DLI patterns and still has timing bugs, wrong register writes, or NMI storm crashes, load this file. Covers every gotcha that bites in practice: shadow-vs-hardware, VSCROL deadline table, JVB stack-depth limit, rainbow marching, and two heavy case-studies: (a) HW-assisted vertical parallax DLI chain, (b) GTIA 9++ DCTR VSCROL kernel.

---

## Quick-Lookup

| Need | See § |
|---|---|
| Mandatory PHA/TXA/PHY/PLA/RTI boilerplate | §1 |
| Shadow vs hardware register table (PRIOR/COLPFn) | §2 |
| VSCROL deadline table (cycle 0/108/5) | §2.1 |
| Wide playfield + HSCROL + VSCROL=0 timing gotcha | §2.2 |
| JVB DLI storm — stack depth limit | §3 |
| Rainbow / colour-march on blank-line ROR | §4.4 |
| HW vertical parallax DLI band chain | §4.1 |
| GTIA 9++ DCTR VSCROL timing kernel | §4.2 |
| ORA overlapping scanline RMW pattern | §5 |
| NVBLNV deferred VBI return (SETVBV/XITVBV) | §6 |

---
