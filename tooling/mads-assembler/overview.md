# Overview

## Quick-lookup

| Need | See § |
|---|---|
| Overview and feature summary | §13.1 |
| Syntax / expression operators / addressing modes | §13.2 |
| .IF/.ELSE/.ENDIF + .REPT/.ENDR + .ALIGN | §13.3 |
| Label scope / .UNDEF / self-modifying labels | §13.4 |
| .MACRO/.ENDM (9 positional + @+ forward-referencing) | §13.5 |
| .PROC/.ENDP (@CALL/@PUSH/@PULL/@EXIT, typed params) | §13.6 |
| .STRUCT/.ENDS, .ENUM/.ENDE, .ARRAY | §13.7 |
| Memory banks \u2014 virtual 64 KB vs hardware 16 KB | §13.8 |
| MEMAC B to PORTB conversion | §13.8 |
| .RELOC, BLK UPDATE, .PUBLIC/.EXT/.LINK | §13.9 |
| SDX block types ($FFFA/end/INI/syms) | §13.9 |
| 65816 addenda STZ/SEP/REP/BRL/JSL/MVN + .A8/.A16/.I8/.I16 | §13.10 |
| Practical MADS examples worth mining | §13.11 |

## 13.1 Overview

MADS is a cross-assembler commonly used for Atari 8-bit projects, with syntax familiar to XASM/FA users. Latest documented stable version in this corpus: **v2.1.5**.

Key features relevant to Atari 8-bit work:
- `.MACRO`, `.PROC` with typed parameters, `@CALL/@PUSH/@PULL/@EXIT`
- `.STRUCT` / `.ENUM` / `.ARRAY` type system
- Virtual 64 KB memory banks (`OPT B-`) + hardware 16 KB bank modes (`OPT B+`)
- relocatable MADS-format output (`.RELOC`) + SpartaDOS X relocatable (`.RELOC` + SDX exchange)
- `.XGET`, `.LEN`, `.SIZEOF` for VBXE `/ML` scratch-read
- `OPT R` — macro command size optimisation

---
