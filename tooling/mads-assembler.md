---
name: atari8bit-mads
description: >-
  MADS assembler syntax for Atari 8-bit and 65C816 work: directives,
  macros, procedures, structures, memory banks, relocatables, and SDX.
---

# 13 — MADS Assembler

> **Scope:** 6502/65C02/65C816 syntax, directives, macros, procedures, memory banks, relocatable code, SDX
> **Key items:** .A8/.A16/.I8/.I16; .MACRO/.ENDM; .PROC/.ENDP; .STRUCT/.ENDS; OPT B+/B-; .RELOC; $FFFA/$FFFE/$FFFD/$FFFB SDX types
> **Primary sources:** `mad-assembler-mkdocs-master/docs/en/docs/`, `atari-documentation/mads/mads.txt`

## Quick-lookup

| Need | See § |
|---|---|
| Overview + changelog v1.6.5\u2192v2.1.5 | §13.1 |
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

Changelog highlights (v1.6.5 → v2.1.5):
- v2.1.5: `.UNDEF` / `.IFDEF` fix; nested `.REPT`; `.LOCAL +full_path`; self-modify labels
- v2.0.8: `.LONGA` / `.LONGI` (65816 register sizes); C-style hex `0xNNNN`
- v2.0.6: `.DEFINE` single-line macros; `.ARRAY` multi-dim
- v2.0.1: `.ZPVAR` auto-allocate ZP; `.ENUM` / `.ENDE`
- v1.9.2: `.SIZEOF` / `.LEN` added
- v1.8.5: `COS` pseudo command; `.A8`/`.A16`/`.I8`/`.I16`/`.AI8`/`.IA8`/`.AI16`/`.IA16`; 65816 mnemonics
- v1.7.0 – 1.8.9: major feature expansion (`.WHILE`, `.TEST`, `.ENUM`, `.STRUCT`, additivity)

---

## 13.2 Syntax and Operands

Numbers: `#$NN` hex, `%NNNNNNNN` binary, `#NN` decimal. String literals in `.BYTE`, `.CBM`, `.SB` are ASCII ATASCII.

String expansion: immediate value can be two chars: `lda #'AB'`, `mwa #'XY' $80`.

**Expression operators:** `+ - * / MOD AND OR XOR SHL SHR NOT < <= = >= > <> ==`

Expressions use 64-bit signed arithmetic internally; results truncated to 32-bit unsigned for memory addresses.

**Addressing modes:**
```
lda #$01             ; immediate
lda $80              ; zero page
lda $0200            ; absolute
lda ($80,x)          ; indexed indirect (zp,X)
lda ($80),y          ; indirect indexed (zp),Y
lda $0200,x          ; absolute indexed X
lda $0200,y          ; absolute indexed Y
lda ($0200),y        ; (abs),Y indirect indexed
```

---

## 13.3 Directives and Control Flow

| Directive | Purpose |
|-----------|---------|
| `.ORG addr[, *]` | Set assembly origin; `*` = load origin |
| `.A8 / .A16` | Set 65816 accumulator width (8/16 bits) |
| `.I8 / .I16` | Set 65816 index register width (8/16 bits) |
| `.ALIGN N[,fill]` | Align to N-byte boundary; optional fill byte |
| `.NOWARN` | Suppress warning for the current line |
| `.PRINT / .ECHO` | Compile-time text output |
| `.ERROR / ERT` | Compile-time error halt |
| `.RND` | Random value 0..255 at assembly time |
| `.PAGES N / .ENDPG` | Page boundary markers (listing) |
| `.FILEEXISTS('fn')` | Returns 1 if file exists, 0 otherwise |
| `.LEN('fn')` | Returns file length |

### Conditional assembly

```asm
.IFDEF    label           ; true if label is defined
.IFNDEF   label           ; true if undefined
.IF       expr            ; assembly if expr ≠ 0
.ELSE                    ; alternative branch
.ENDIF                   ; end conditional block
.ELIF expr              ; shorthand for .ELSE .IF
```

### Repeat loops

```
.REPT N [, #,...          ; repeat N times, optional param # = counter
.rept 10,#*2             ; * counter × 2 = address offset
.label:1                 ; counter replacement: LABEL0, LABEL1...
.ENDR                    ; end repeat
```

Multi-dimensional loop:
```
.REPT 10
  lda  table,x
  inx
.ENDR
```

### Multi-pass zero-page auto-selection

MADS automatically selects free ZP addresses across multiple assembly passes when no explicit address is given — useful for procedure-local scratch variables.

---

## 13.4 Labels and Scope

```asm
global_label:             ; global by default
.local local_area
  local_label:            ; local to local_area
  ?temporary:             ; temporary (OPT ?- implicit); auto-cleared each pass
.endl

; Self-modifying label
        lda  label:#$40     ; assembles as LDA immediate $40,
                            ; but linker form keeps label as data in-situ*
        ; generally only writes T2 instruction reads
.UNDEF  macro_name         ; removes single-line macro definition
```

---

## 13.5 Macros (.MACRO/.ENDM)

Up to 9 positional parameters. Anonymous forwarded labels `@+[1..9]` / `@-[1..9]` for forward/backward branching within macros.

```asm
.macro  draw_bar  color,  xpos,  width
        lda   #:color
        sta   COLPM0
        ldy   #:xpos
        mva   #:width bar_len
@bar    sta   (ptr),y
        iny
        dec   bar_len
        bne   @+              ; loop (auto uses @+1 backward)
.endm

; Anonymous forward label
@      lda  bar_length,x
       bne  @-              ; @- loops back to nearest @

; Invocation:
; @BAR on forward (0-based relative to last @)
```

### Macro commands (built-in pseudo-ops)

| Macro command | Expansion semantics |
|---------------|-------------------|
| `MVA src, dst` | `LDA src / STA dst` — mov A-destination |
| `MWA src, dst` | `LDA src+1 / STA dst+1; LDA src / STA dst` — word move |
| `ADW ptr, val` | `CLC / LDA val / ADC ptr / STA ptr; LDA val+1 / ADC ptr+1 / STA ptr+1` |
| `SBW ptr, val` | `SEC / LDA ptr / SBC val / STA ptr` (high byte borrow cleared) |
| `INW / DEW` | 16-bit inc/dec on ZP word |
| `MVX / MVY` | Move X-register or Y-register directly |
| `ADW ptr,ptr2,result` | ptr+ptr2 → result |

---

## 13.6 Procedures (.PROC/.ENDP)

`.PROC` blocks localise scope; parameters pass via `.REG` or `.VAR`.

```asm
; .REG passes through CPU registers; .VAR allocates ZP scratch vars
draw_line .PROC (.BYTE x0, y0, x1, y1) .REG
    mva x0, current_x
    mva y0, current_y
    ; ...
    @EXIT           ; early exit from procedure
.endp

; call:
draw_line #10, #20, #100, #80
@CALL draw_line
```

Typed parameters: `.BYTE` /`.WORD` / `.LONG` / `.DWORD` can be declared. Multi-dimensional arrays pass via `.PROC`, optionally with `@PUSH`/`@PULL`.

```asm
.proc copy (.WORD src+1, dst+1) .var
src   lda   $ffff
dst   sta   $ffff
       iny
       bne   src
       rts
.endp

copy.ToDst #$a080, #$b000   ; explicit sub-proc call
copy      #$a360            ; default call
```

Nesting: `.PROC` blocks can be nested.
```
.proc outer
    .proc inner
    .endp
.endp
```

---

## 13.7 Data Types (.STRUCT/.ENDS, .ENUM/.ENDE)

```asm
; Structure definition
.struct point
    x   .byte
    y   .byte
.ends

; Instantiate
player     dta   point [1]    ; allocate one point struct
enemies    dta   point [8]    ; array of 8 point structs

; Enumeration
.enum color_set
    black = 0
    red   = 2
    green = 4
    blue  = 6
.ende

    lda   #color_set(red | green)    ; == #color_set.red | color_set.green
```

### .ARRAY

```
.array  scr   .byte
    1,4,6                    ; [0..2]
    [12] = 9,3              ; [12..13]
.enda
```

---

## 13.8 Memory Banks — Virtual vs Hardware

### Virtual 64 KB bank mode (`OPT B-`, default)

MADS supports virtual 64 KB memory banks — each bank is independently addressable but memory model does not include bank-switching hardware.

### Hardware 16 KB bank mode (`OPT B+`) — Atari 130XE / banked cartridges

```asm
opt    b+                    ; activate 16 KB hardware banks
        .LMB $80             ; load memory bank counter (D301 bit 6)
        .NMB $a0             ; next-memory-bank label:
        .RMB $b0             ; run-memory-bank label:
```

Bank identifiers: writing to `PORTB ($D301)` bits 1-4 selects 16 KB memory bank. `:a` and `:b` operators allow direct switching per access in MADS expressions. The `LMB`/`NMB`/`RMB` pseudo-ops emit hardware bank-select code at assembly time.

Practical 130XE bank layout, from the MADS example usually named `xms_banks.asm`:

```asm
        opt b+

@TAB_MEM_BANKS = $0400       ; table filled by @mem_detect
@PROC_ADD_BANK = $0600       ; helper outside the bank window

        org $2000
detect  jsr @mem_detect
        beq no_ext_ram

* bank #1 in the $4000-$7FFF window
        lmb #1
        .pages $40           ; assert a 16 KB page budget
bank1   ; code/data assembled for the banked window
        @bank_jmp :bank2
        .endpg

* bank #2
        lmb #2
        .pages $40
bank2   @bank_jmp :bank1
        .endpg

* resident RAM, outside $4000-$7FFF
        rmb
main    @bank_jmp bank1

        icl 'macros/@bank_jmp.mac'
        run main
        icl 'macros/@bank_add.mac'
```

Rules for generated code:
- Keep `@BANK_JMP_PROC`, NMI/VBI code, and any bank-switch return path outside `$4000-$7FFF`.
- Save and restore `PORTB` if DOS, SDX, BASIC, or OS ROM must survive.
- Use `.PAGES $40` or explicit `ERT` checks so a bank cannot silently overflow the 16 KB window.
- Treat `LMB/NMB/RMB` as assembly-layout tools; they do not replace runtime `PORTB` discipline.

### MEMAC B ↔ PORTB conversion (VBXE, chapter02)

```asm
; VBXE bank register MACRO B ->_PORTB
        ; MEMAC B = 32 KB address window
; PORTB desired = (MEMAC B / 2) >>> 3
```

---

## 13.9 Relocatable Code (MADS Format + SDX)

### MADS `.RELOC` format

```asm
.reloc
    lda   ptr             ; relocatable reference
ptr  .word $0000           ; label: will be patched by linker

; .PUBLIC / .EXT / .LINK
.public  exported_sym
.extrn   imported_sym .word
.link     lib_file
```

`BLK UPDATE` chain produces the relocatable segment. `.PUBLIC` labels appear in the SDX symbol block (`$FFFB`).

Host-link pattern, from the MADS examples usually named `tetris_reloc.asm` and `tetris_reloc_example.asm`:

```asm
; library/module source
        .reloc
        .public main

main    jsr init
        rts

; host program
        org $3127
        .link 'module.obx'
        run main
```

Use this when an example should be relocatable without manually rewriting every absolute reference. Export only the entry points needed by the host and keep fixed hardware/register addresses as constants, not relocatable symbols.

### SpartaDOS X integration

```asm
blk     sparta     $2000  ; SDX binary, loaded at $2000
        ; code here
blk     reloc      0     ; relocatable block (SDX chunks)
        ; further code here
```

SDX block types in the binary:
```
$FFFE  end-of-segment marker
$FFFA  start (run) address
$FFFC  INI (initialisation code) block
$FFFB  symbol table (PUBLIC .EXT)
$FFFD  switch block (bank IDs for 16 KB banks)
```

---

## 13.10 65816 Addenda (mnemonics.md)

New mnemonics and modes not in 6502/65C02:

| Mnemonic | 6502 equivalent | Notes |
|----------|----------------|-------|
| `STZ dst` | `LDA #0 / STA dst` | Zero destination directly |
| `SEP #imm` | `SET P` | Set status-register bits (1 byte) |
| `REP #imm` | `CLR P` | Clear status-register bits (1 byte) |
| `BRL rel16` | long `BRA` | Relative branch across bank boundary |
| `JSL addr24` | `JSR abs24` | Long subroutine call |
| `JML addr24` | `JMP abs24` | Absolute long jump |
| `MVN src, dst` | block move N-1 → N-2 | Memory copy N bytes |
| `MVP src, dst` | block move N-1 → N-2 | Memory copy N bytes |
| `PEA #imm` | `LDA #imm / PHA` | push 16-bit immediate |
| `PER rel16` | `LDA rel16 / PHA` | push PC-relative address |

Size-prefixed mnemonics: `LDA.b`, `LDA.w`, `LDA.l` — `.b` forces 8-bit, `.w` forces 16-bit, `.l` forces 24-bit operand.

```asm
.a8  .i16                ; A=8-bit, X/Y=16-bit
lda  #$1234              ; LDA #$34  (truncated to 8 bits)
ldx  #$5678              ; LDX #$5678  (16-bit index register)
```

---

*See §13.9 for SDX block types; spartadosx EN doc content embedded in this file.*

---

## 13.11 Practical MADS Example Patterns

Use the user-provided MADS examples corpus as a pattern library, not as cargo-cult source. If the examples are not already present in the workspace, ask the user for their location. These examples are especially valuable:

| Need | Example file | Technique to extract |
|---|---|---|
| Command-line parameters under DOS | `command_line.asm` | Check `BOOT`, validate `DOSVEC`, call the DOS parser through an indirect vector, copy ATASCII `$9B`-terminated args. |
| Compile-time flow | `if_else.asm`, `while.asm`, `rept.asm` | `IFT/ELI/ELS/EIF`, `#while/#end`, `.REPT` with `#` counter and label suffixes. |
| Scoped names | `macro_proc_local.asm`, `local*.asm` | Put macros/procs in `.LOCAL` namespaces; know that macro-local labels are uniquified per expansion. |
| Typed layout | `struct_enum.asm` | `.ENUM` values can define byte-sized types; `.STRUCT` fields can be used in `.VAR/.ZPVAR` and arrays. |
| Dual-address loader stubs | `file_loader.asm` | `ORG run_address,load_address` assembles for one address while storing bytes at another. |
| Boot disk loader | `Boot.asm` | Raw boot sector at `$0700`, direct `SIOV` sector reads, first three sectors treated as 128-byte boot sectors. |
| SDX/FAS inspection | `trace2.fas` | Parse `$FFFA/$FFFB/$FFFC/$FFFD/$FFFE` blocks and print segment/update/symbol metadata. |
| POKEY timer IRQ raster split | `irq_mcp.asm` | Use DLI to arm POKEY timer IRQ at a stable scanline offset after `WSYNC`/`STIMER`. |
| Tracker relocation | RMT/MPT/CMC/TMC relocator examples | Include player once, relocate module data with a macro, call init/play/silence through fixed vector offsets. |

When summarizing or porting Polish-commented examples, translate comments into precise English and keep the code idiom only if it still matches the target OS/DOS/hardware constraints.
