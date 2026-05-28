## Macro Commands

 [REQ, RNE, RPL, RMI, RCC, RCS, RVC, RVS](#req)

 [SEQ, SNE, SPL, SMI, SCC, SCS, SVC, SVS](#seq)

 [JEQ, JNE, JPL, JMI, JCC, JCS, JVC, JVS](#jeq)

 [ADD, SUB](#add)

 [ADB, SBB](#adb)

 [ADW, SBW](#adw)

 [PHR, PLR](#phr)

 [INW, INL, IND, DEW, DEL, DED](#inw)

 [MVA, MVX, MVY](#mva)

 [MWA, MWX, MWY](#mwa)

 [CPB, CPW, CPL, CPD](#cpb)

The purpose of macro commands is to reduce programming time and shorten the listing itself. Macro commands replace groups of frequently repeated mnemonics.

<a name="req"></a>
### REQ, RNE, RPL, RMI, RCC, RCS, RVC, RVS

The above macro commands refer by their names to the corresponding *6502* mnemonics: `BEQ`, `BNE`, `BPL`, `BMI`, `BCC`, `BCS`, `BVC`, and `BVS`, respectively. They have an additional property of jumping to the previously assembled instruction, e.g.:

```
   lda:cmp:req 20           ->      lda 20
                            -> wait cmp 20
                            ->      beq wait

   ldx #0                   ->      ldx #0
   mva:rne $500,x $600,x+   -> loop lda $500,x
                            ->      sta $600,x
                            ->      inx
                            ->      bne loop
```

<a name="seq"></a>
### SEQ, SNE, SPL, SMI, SCC, SCS, SVC, SVS

The above macro commands refer by their names to the corresponding *6502* mnemonics: `BEQ`, `BNE`, `BPL`, `BMI`, `BCC`, `BCS`, `BVC`, and `BVS`, respectively. They have an additional property of jumping to the next assembled instruction, e.g.:

```
   lda #40         ->       lda #40
   add:sta  $80    ->       clc
   scc:inc  $81    ->       adc $80
                   ->       sta $80
                   ->       bcc skip
                   ->       inc $81
                   ->  skip
```

<a name="jeq"></a>
### JEQ, JNE, JPL, JMI, JCC, JCS, JVC, JVS

The above macro commands refer by their names to the corresponding *6502* mnemonics: `BEQ`, `BNE`, `BPL`, `BMI`, `BCC`, `BCS`, `BVC`, and `BVS`, respectively. They have an additional property of conditional jumping to a specified address. With their help, we can jump not only in the range of -128..+127 bytes but in the entire **64kB** range, e.g.:

```
 jne dest   ->  beq *+4
            ->  jmp dest
```

If the jump is short (range -128..+127), **MADS** will use a short jump: `BEQ`, `BNE`, `BPL`, `BMI`, `BCC`, `BCS`, `BVC`, or `BVS`, respectively.

<a name="add"></a>
### ADD, SUB

The above macro commands perform an increment/decrement of a memory byte respectively, without saving the result (the result remains in the *CPU* accumulator).

```
  ADD -> CLC         SUB -> SEC
      -> ADC ...         -> SBC ...
```

<a name="adb"></a>
### ADB, SBB

The above macro commands perform an increment/decrement of a memory byte respectively, and save the result.

```
  ADB SRC #$40 -> LDA SRC       ADB A B C  -> LDA A
               -> CLC                      -> CLC
               -> ADC #$40                 -> ADC B
               -> STA SRC                  -> STA C

  SBB SRC #$80 -> LDA SRC       SBB A B C  -> LDA A
               -> SEC                      -> SEC
               -> SBC #$80                 -> SBC B
               -> STA SRC                  -> STA C
```

<a name="adw"></a>
### ADW, SBW

The above macro commands perform an increment/decrement of a memory word respectively, and save the result.

```
  ADW SRC #$40 -> CLC             ADW A B C  -> CLC
               -> LDA SRC                    -> LDA A
               -> ADC #$40                   -> ADC B
               -> STA SRC                    -> STA C
               -> SCC                        -> LDA A+1
               -> INC SRC+1                  -> ADC B+1
                                             -> STA C+1

  ADW SRC #$40 SRC -> CLC
                   -> LDA SRC
                   -> ADC #$40
                   -> STA SRC
                   -> LDA SRC+1
                   -> ADC #$00
                   -> STA SRC+1

  SBW SRC #$4080 -> SEC           SBW A B C  -> SEC
                 -> LDA SRC                  -> LDA A
                 -> SBC <$4080               -> SBC B
                 -> STA SRC                  -> STA C
                 -> LDA SRC+1                -> LDA A+1
                 -> SBC >$4080               -> SBC B+1
                 -> STA SRC+1                -> STA C+1
```

<a name="phr"></a>
### PHR, PLR

The above macro commands refer by their names to the corresponding *6502* mnemonics: `PHA` and `PLA`, respectively. They perform pushing and pulling of the `A`, `X`, and `Y` registers to/from the stack.

```
  PHR  -> PHA         PLR  -> PLA
       -> TXA              -> TAY
       -> PHA              -> PLA
       -> TYA              -> TAX
       -> PHA              -> PLA
```

<a name="inw"></a>
### INW, INL, IND, DEW, DEL, DED

Macro commands `INW`, `INL`, and `IND` increment a memory word (`.WORD`), long word (`.LONG`), and double word (`.DWORD`), respectively.

Macro commands `DEW`, `DEL`, and `DED` decrement a memory word (`.WORD`), long word (`.LONG`), and double word (`.DWORD`), respectively. They use the *CPU* accumulator for this purpose (the accumulator's content changes after executing `DEW`, `DEL`, or `DED`).

```
    inw dest  ->       inc dest    ->   inc dest
              ->       bne skip    ->   sne
              ->       inc dest+1  ->   inc dest+1
              ->  skip             ->

    dew dest  ->       lda dest    ->   lda dest
              ->       bne skip    ->   sne
              ->       dec dest+1  ->   dec dest+1
              ->  skip dec dest    ->   dec dest
```

<a name="mva"></a>
### MVA, MVX, MVY

Macro commands `MVA`, `MVX`, and `MVY` are used to move memory bytes (`.BYTE`) using the *CPU* registers `A`, `X`, and `Y`, respectively. Using the `OPT R+` option allows for potential reduction of the resulting code for consecutive `MVA`, `MVX`, or `MVY` macro commands.

```
    lda src    ->  mva src dst
    sta dst    ->

    ldy $10,x  ->  mvy $10,x $a0,x
    sty $a0,x  ->

    ldx #$10   ->  mvx #$10 dst
    stx dst    ->
```

<a name="mwa"></a>
### MWA, MWX, MWY

Macro commands `MWA`, `MWX`, and `MWY` are used to move memory words (`.WORD`) using the *CPU* registers `A`, `X`, and `Y`, respectively. Using the `OPT R+` option allows for potential reduction of the resulting code for consecutive `MWA`, `MWX`, or `MWY` macro commands.

```
    ldx <adr    ->  mwx #adr dst
    stx dst     ->
    ldx >adr    ->
    stx dst+1   ->

    mwa #0 $80  ->  lda #0           mwy #$3040 $80  ->  ldy <$3040
                ->  sta $80                          ->  sty $80
                ->  sta $81                          ->  ldy >$3040
                                                     ->  sty $81

    mwa ($80),y $a000,x  ->  lda ($80),y
                         ->  sta $a000,x
                         ->  iny
                         ->  lda ($80),y
                         ->  sta $a001,x
```

<a name="cpb"></a>
### CPB, CPW, CPL, CPD

Macro commands `CPB`, `CPW`, `CPL`, and `CPD` perform a comparison of values of the respective types: `.BYTE`, `.WORD`, `.LONG`, and `.DWORD`.

```
 cpw temp #$4080
 bcc skip

 cpd v0 v1
 beq skip
```
