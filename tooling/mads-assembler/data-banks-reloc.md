# Data Banks Reloc

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
