# Mnemonics

## Available 6502 Instructions

```none
LDA   LDX   LDY   STA   STX   STY   ADC   AND
ASL   SBC   JSR   JMP   LSR   ORA   CMP   CPY
CPX   DEC   INC   EOR   ROL   ROR   BRK   CLC
CLI   CLV   CLD   PHP   PLP   PHA   PLA   RTI
RTS   SEC   SEI   SED   INY   INX   DEY   DEX
TXA   TYA   TXS   TAY   TAX   TSX   NOP   BPL
BMI   BNE   BCC   BCS   BEQ   BVC   BVS   BIT
```

## Available Illegal 6502 Instructions

```none
ASO   RLN   LSE   RRD   SAX   LAX   DCP   ISB
ANC   ALR   ARR   ANE   ANX   SBX   LAS   SHA
SHS   SHX   SHY   NPO   CIM
```

## Available 65816 Instructions

Naturally, 6502 instructions are available, along with the following:

```none
STZ   SEP   REP   TRB   TSB   BRA   COP   MVN
MVP   PEA   PHB   PHD   PHK   PHX   PHY   PLB
PLD   PLX   PLY   RTL   STP   TCD   TCS   TDC
TSC   TXY   TYX   WAI   WDM   XBA   XCE   INA
DEA   BRL   JSL   JML
```

## Mnemonic Extensions

It is possible to use **XASM**-style mnemonic extensions `a:`, `z:`, and `r:`, e.g.:

```
XASM        MADS
lda a:0     lda.a 0
ldx z:0     lda.z 0

org r:$40   org $40,*
```

It is possible to use a mnemonic extension after a dot `.` for instructions like `LDA`, `LDX`, `LDY`, `STA`, `STX`, and `STY`:

```
.b or .z          BYTE
.a or .w or .q    WORD
.t or .l          TRIPLE, LONG (24bit)
```

e.g.

```
lda.w #$00   ; A9 00 00
lda   #$80   ; A9 80
stx.w $f2    ; 8E F2 00
```

Exceptions are the following instructions, where the register size cannot be changed in absolute addressing (some assemblers do not require the `#` character for these instructions, but **MADS** does):

* `#$xx` for `SEP` `REP` `COP`

* `#$xxxx` for `PEA`

Another exception is the long indirect addressing mode, represented by square brackets `[]`. As we know, these brackets are also used for evaluating expressions; however, if the assembler encounters a `[` character first, it will treat it as long indirect addressing mode. If we haven't signaled the intention to use *65816*, an **Illegal addressing mode** error will occur. To "trick" the assembler, simply place a `+` sign before the opening square bracket `[`:

```
lda [2+4]     ; lda [6]
lda +[2+4]    ; lda 6
```
