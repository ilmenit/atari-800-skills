# Mad-Assembler

**Mad-Assembler (MADS)** is a MOS 6502/MOS 65C02/WDC 65816 cross-assembler by [Tomasz Biela (tebe)](https://github.com/tebe6502).

The latest releases for Windows is available on [Github](https://github.com/tebe6502/Mad-Assembler/releases). Releases for other operating systems platform are published periodically as part of the [WUDSN IDE Tools](https://github.com/peterdell/wudsn-ide-tools/tree/main/ASM/MADS).

# Change Log

## [2.1.5](https://github.com/tebe6502/Mad-Assembler/releases/tag/2.1.5)  <a name="2.1.5"></a> 

- fixed implementation of `.UNDEF` and `.IFDEF`
- fixed implementation of nested `.REPT` loops
- added ability to combine local areas, `.LOCAL +full_path_to_local`
- added coloring of console messages
- added labels for self-modifying code, e.g. `lda label:#$40`

## [2.1.3](https://github.com/tebe6502/Mad-Assembler/releases/tag/2.1.3)  <a name="2.1.3"></a> 

- added directive `.RND` returning a random value in the range 0..255
- added warning message **'Register A is changed'** for pseudo commands `DEW`, `DEL`, `DED`
- added command line option `-bc` for **'Branch condition test'**. It activates warning messages in case the branch target is out of range or exceeds a memory page boundary

## [2.1.0](https://github.com/tebe6502/Mad-Assembler/releases/tag/2.1.0)  <a name="2.1.0"></a> 

- added warning message **'Buggy indirect jump'** when using the command `JMP(ABS)`
- added directive `.FILEEXISTS('filename')` returning 1 if file in specified path exists, 0 if it does not exist
- extended message **'Value out of range (VALUE must be between X and Y)'**

## 2.0.9  <a name="2.0.9"></a> 

- added `.CBM 'text'` directive to define text in Commodore C64 screen code
- fixed an error when a `.PROC` procedure located in a `.LOCAL` block was not marked 'for assembly' even though it was referenced from a `.MACRO` macro in a `.LOCAL` block
- fixed that temporary labels `?label` were marked 'for relocation'

## 2.0.8 <a name="2.0.8"></a> 

- generate shorter object code for `#CYCLE`
- fixes for `.BY` `.WO` `.HE` `.SB` `.CB` `.FL`
- added error message **'Improper syntax'** when using `.BY` `.WO` `.HE` `.SB` `.CB` `.FL` in a `.STRUCT` block
- added directives `.LONGA ON|OFF` `.LONGI ON|OFF` for **WDC 65816** 
- fixed register size tracking for **WDC 65816** when `OPT T+` is set
- added command line option `-fv:value` to set the memory fill value when `OPT F+` is set.
- added option to specify an immediate argument as a string of two characters (previously only 1 character), e.g. `lda #'AB'` , `mwa #'XY' $80`

## 2.0.7 <a name="2.0.7"></a> 

- fixed object code generation for illegal opcodes `DOP` and `SHA`
- added **WDC 65816** directives `.A8` `.A16` `.I8` `.I16` `.AI8` `.IA8` `.AI16` `.IA16` to set the size of `AXY` registers
- added **WDC 65816** directives `.ASIZE` `.ISIZE` returning the current size of `AXY` registers
- in **WDC 65816** mode, the command `JMP` is changed to `JML` only when the jump concerns a different 64KB bank than the current one
- added command line option `-ml:value` for **'margin-left property'** (Set left margin) to change the left margin of the generated listing to a value in the range of 32 to 128 characters

## 2.0.6 <a name="2.0.6"></a> 

- fixed parsing of macro parameters used in labels

```
.macro test currentRow, previousRow
    .print Tmp%%currentRowAllowed
    .print Tmp%%previousRowAllowed
.endm
```

- fixed the `.ARRAY` memory allocation in case there is no size specified or it is a multi-dimensional array
- increased number of passes for `.PROC` to prevent that for `xa .reg` the parameter is misinterpreted under certain conditions
- added directive `.DEFINE` to define sinlge-line macros (can be defined multiple times in the same pass)

```
.DEFINE macro_name expression

.DEFINE write .print %%1+%%2
write (5,12)

.DEFINE text .sb
text 'atari'
```

- added directive `.UNDEF macro_name` to remove the definition of the single-line macro `macro_name`.

## 2.0.5 <a name="2.0.5"></a> 

- array definitions with `.ARRAY` in unused `.PROC` block are omitted if the `-x` **Exclude unreferenced procedures** option is specified
- using `.ARRAY` in `.STRUCT` blocks will no longer generate zeros in the resulting file
- added directive `.XGET` to read a file into the **MADS** memory buffer and further modify its bytes provided they are different from zero (useful for **VBXE**)

## 2.0.4 <a name="2.0.4"></a> 

- fixed bug causing incorrect writing of the update block for the high byte of the address in a `.RELOC` block
- removed directives `.DB`  and `.DW`
- added directive `.DBYTE <word>` which stores the bytes of a word in high / low order (MSB/LSB)
- added direcvivs `.WGET` to read **WORD** values, `.LGET` to read **LONG** values and `.DGET` to read **DWORD** values from **MADS** memory buffer
- fixed implementation of `ADW` and `SBW` macro commands, e.g.:

```
adw (tmp),y #1 posx
adw (tmp),y ptr2 ptr4
```

## 2.0.2 <a name="2.0.2"></a>
- fixed data allocation for `.SB [+<byte>],<bytes|string|char>`

## 2.0.1 <a name="2.0.1"></a>

- fixed data allocation for `.ARRAY` when type is larger than `.BYTE`
- directive `.SIZEOF` now also returns the size for built-in types `.BYTE` `.WORD` `.LONG` `.DWORD`
- added relocatable version of **MPT** player `examples_players_player_reloc.asm`
- fixed implementation of `.DS` directive in **SDX** `blk sparta $xxx` blocks that are not relocatable

## 1.9.8 <a name="1.9.8"></a>

- fixed **WDC 65816** commands `PEA`, `PEI`, `PER`
- added ability to specify code for `.RELOC` [.BYTE|WORD] [TYPE]

## 1.9.7 <a name="1.9.7"></a>

- the `.DEF` directive defines labels with local scope; if preceded by `:`, it's global
- fixes for floating-point numbers `.FL`, corrected zero encoding, rounding to 10 decimal places
- for **Sparta DOS X** blocks `blk reloc` and `blk empty`, added ability to specify memory types other than `$00` (main), `$02` (extended), e.g.:

```
blk reloc $40
```
- fix allowing the use of `.PRINT` directive after `blk empty`
- added ability to define multi-dimensional arrays `.ARRAY`, e.g.:

```
.array scr [24][40]
  [11][16] = "atari"
.enda

  mva #"!" scr[11][22]
```

- added ability to define `.ARRAY` via `.DS` directive, e.g.:

```
tmp .ds .array [5][12][4] .word
```

- added ability to define `.ARRAY` via `EQU` (=) pseudo command, e.g.:

```
fnt = $e000 .array [128] [8] .byte
```

- fixed `ADW` macro command operation in combination with `SCC` macro command, etc.
- fixes for `.REPT`, including multi-line comment `/* */` being properly recognized

## 1.9.6 <a name="1.9.6"></a>

- improved anonymous labels for mnemonics joined with `:`, e.g.:

```
       ldx #8
@      lda:cmp:req 20
       dex
       bne @-
```

- added `COS` (centre,amp,size[,first,last]) pseudo command to generate cosine values
- added **Improper syntax** error message when using `.DS` directive in a `.STRUCT` block
- fixed `ORG` pseudo command operation, e.g.:

```
opt h-
ORG [a($ffff),d'atari',c'ble',20,30,40],$8000,$a000
```

- additive `.LOCAL` blocks receive consecutive addresses; previously the address was set based on the first occurrence of such a block
- added warning message when creating another additive `.LOCAL` block with the same name: **Ambiguous label LOCAL_NAME**
- added mnemonics `PER` (PEA rell), `PEI` (PEA (zp)) for **WDC 65816**
- added new data types M (most significant byte of **LONG**) and G (most significant byte of **DWORD**) for `DTA` pseudo command, e.g.:

```
dta m($44556677)   ; -> $55
dta g($44556677)   ; -> $44
```

- `.LEN` and `.SIZEOF` directives extended to support data allocated via `DTA STRUCT_NAME`, e.g.:

```
.STRUCT free_ptr_struct
  prev .WORD
  next .word
.ENDS

free_ptr_t dta free_ptr_struct [3]

.print .sizeof(free_ptr_t)    ; free_ptr_struct [0..3] = 16 bytes
```

- changes for file read operations via `ICL`, `INS`, etc. The file for read/write will be searched first in the path leading to the currently open file, then in the path from which the main assembled file was run, and finally in the paths specified with the `-i` parameter (additional include directories)
- improved case sensitivity recognition when the `-c` switch (case sensitive) is activated for structures, e.g.:

```
.struct fcb
sEcbuf  .byte
.ends

data dta fcb [1] (0)

    lda     data[0].sEcbuf
```


- extended `.REPT` directive to allow nesting, e.g.:

```
.rept 2,#*2              ;  1 - $0000
                         ;  2 - $0000
.print '1 - ',#          ;  1 - $0001
                         ;  2 - $0000
.rept :1                 ;  2 - $0001
.print '2 - ',.r         ;  2 - $0002
.endr                    ;
                         ;
.endr
```
- shorter version of `#WHILE` loop without expression; the loop continues as long as `LABEL <> 0`:

```
#while .word label
#end
```

## 1.9.5 <a name="1.9.5"></a>

- added pseudo command `SET` to redefine a label, similar action to temporary labels starting with `?`, e.g.:

```
temp set 12
     lda #temp

temp set 23
     lda #temp
```

- added ability to force **XASM** style addressing mode `a:` and `z:`, e.g.:

```
XASM        MADS
lda a:0     lda.a 0
ldx z:0     lda.z 0
```

- added ability to specify a new code relocation address in  **XASM** style `r:`, e.g.:

```
XASM        MADS
org r:$40   org $40,*
```

- fixed implementation of the `-x` option **Exclude unreferenced procedures**, so `.VAR` variables are not allocated when the procedure is not used

- added extended syntax for single-line `:rept` loops, so it is now possible use of loop counter as `:1` or `%%1` parameter, e.g.:

```
line0
line1
line2
line3

ladr1 :4 dta l(line:1)
hadr1 :4 dta h(line:1)

ladr2 :4 dta l(line%%1)
hadr2 :4 dta h(line%%1)
```

- added warning message when using unstable illegal **6502** opcodes like `CIM`
- added new functionality for `RUN` and `INI` pseudo commands, so they now retain the current assembly address. Previously they switched the assembly address to `$2E0` (RUN) or `$2E2` (INI)
- added support for **anonymous labels** `@` `@+[1..9]` (forward) `@-[1..9]` (backward), in the interest of code clarity use such labels is restricted to conditional branches and up to 10 forward/backward occurrences, e.g..:

```
@ dex   <------+---+
  bne @+ --+   |   |
  stx $80  |   |   |
@ lda #0 <-+   |   |
  bne @- ------+   |
  bne @-1  --------+
```

- extended directives `#IF` and `#WHILE` to include variables declared by `.VAR`, previously it was required to specify the type of the variable, e.g.:

```
 .var temp .word

 #if temp>#2100       ;Now
 #end

 #if .word temp>#2100 ;Before
 #end
```

## 1.9.4 <a name="1.9.4"></a>

- added path normalization for files to work under **Unix**, `\` characters are replaced with `/`
- improved passing directives as parameters to procedures and macros; directives were not recognized when the `-c` (case sensitive) switch was on
- improved `.USE` and `.USING` operation
- added **WARNING** message for a label causing an infinite number of assembly passes: **INFINITE LOOP**
- added writing of two header bytes `FF FF` for a file containing a block with load address `$FFFF`
- comments after mnemonics not requiring an argument will be treated as an error, except for joining commands in **xasm** style via `:`, e.g.:

```
 pla $00          ->  ERROR: Extra characters on line
 pha:pla $00      ->  OK
```

- extended macro syntax to allow using names as parameters instead of just decimal numerical values, e.g.:

```
.macro SetColor val,reg
 lda :val
 sta :reg
.endm

.macro SetColor2 (arg1, arg2)
 lda #:arg1
 sta :arg2
.endm
```

- fixed label definition for the following situation; the first label will not be ignored:

```
temp  label = 100
```

## 1.9.3 <a name="1.9.3"></a>

- improved processing of `.PROC` blocks, which under certain circumstances could be skipped during assembly
- improved `BLK EMPTY` writing for **SDX** files if the declaration of such a block was made via `.DS`
- fixes regarding end-of-line testing
- added `.FILESIZE`, `.SIZEOF` directives as equivalents to the existing `.LEN` directive
- extended syntax for `.STRUCT` fields, e.g.:

```
.struct name
 .byte label0
 .byte :5 label1
 label2 .byte
 label3 :2 .word
.ends
```

## 1.9.2 <a name="1.9.2"></a>

- ability to specify an address for `.ZPVAR = $XX`
- improved references to enumeration labels `.ENUM`, e.g. `enum_label(field0, field1)`
- added ability to generate a block for external symbols `BLK UPDATE EXTRN` for **DOS** files (previously only for `.RELOC` files), e.g.:

```
.extrn vbase .word
org $2000
lda #$80
sta vbase+$5d

blk update extrn
```

- added **Could not use NAME in this context** error message for command references to `.MACRO`, `.ENUM`, `.STRUCT` blocks
- fixed a bug that prevented the use of `EQU` in a label name
- added `.CB +byte,.....` directive; the last byte of the character string is stored in inverse
- added segment support via `.SEGDEF`, `.SEGMENT`, `.ENDSEG` directives
- added new `#CYCLE #N` directive generating **6502** code with a specified number of cycles `N`
- added support for illegal **6502** CPU instructions; example in `.\examples\test6502_illegal.asm`
- updated Notepad++ configuration files in `..\syntax\Notepad++`
- improved `LST` file writing
- fixed memory allocation for structural variables, extended syntax for `.STRUCT`:

```
.struct LABEL
 x,y,z .word     // multiple variables of the same type in one line
 .byte a,b
.ends

.enum type
  a=1,b=2
.ende

.struct label2
  x type
  type y
.ends
```


## 1.9.0 <a name="1.9.0"></a>

- fixed writing lines with `/* */` comments to the `*.LST` listing file; previously such lines were not saved
- fix for labels declared from the command line `-d:label`; previously such labels were only seen in the first pass
- in case of additive `.LOCAL` blocks, only the first address from such blocks is saved
- fixes regarding macro parsing; previously labels starting with `END` could be interpreted as the `END` pseudo command
- fix for reading an empty relocatable file; previously a **Value out of range** error occurred
- fixes for `.USING`, `.USE`

## 1.8.8 - 1.8.9 <a name="1.8.8_1.8.9"></a>

- updated software sprite engine `..\EXAMPLES\SPRITES\CHARS` with 8x24 sprites
- if no file extension is provided and the file does not exist for `ICL 'filename'`, the `*.ASM` extension will be assumed by default: `ICL 'filename.asm'`
- improved `/* */` comments operation in `.MACRO` and `.REPT` blocks
- fixed a bug preventing correct assembly of `#IF` and `#WHILE` blocks for expressions joined by `.OR` and `.AND`
- command line switches can only be preceded by the `-` character; previously `/` was also allowed, but there were problems with this character on **MacOSX**
- corrected scope of the `.USING` directive, for the current namespace and subsequent ones contained within that namespace

## 1.8.6 - 1.8.7 <a name="1.8.6_1.8.7"></a>

- improved `/* */` comment recognition in expressions
- default address for `.ZPVAR` set to `$0080` (previously `$0000`)
- added new `.ELIF` directive as a shorter equivalent to `.ELSEIF`
- extended `.LEN` directive to allow passing a filename as a parameter; the length of that file is then returned
- improved `.DEF` directive operation in `.IF`, `.IFDEF`, `IFNDEF` condition expressions

## 1.8.5 <a name="1.8.5"></a>

- added macro for relocating **RMT** modules `...\EXAMPLES\MSX\RMT_PLAYER_RELOCATOR\`
- added syntax test for non-assembled `.PROC` procedures when the `-x` switch (**Exclude unreferenced procedures**) is active
- improved `-d:label[=value]` switch operation; providing a value for the label is now optional, MADS will assign value 1 by default
- `.DS` and `.ALIGN` directives will not cause allocation of variables defined by `.VAR`
- `.VAR` variable allocation before a new `ORG` block will not occur if the `ORG` block is inside a `.LOCAL` or `.PROC` block
- fixed line breaking with the `\` character in strings enclosed in parentheses `()`
- fixed bug causing address relocation for the `.ERROR` / `ERT` directive expression
- fixed observed bugs in command line parameter parsing
- fixed observed bugs regarding optimization of macro command code length (`MVA`, `MWA`, etc.)
- improved code implementing `.PROC` block nesting
- improved code implementing `IFT`, `ELI`, `ELS`, `EIF` condition pseudo commands
- added **'#' is allowed only in repeated lines** message for cases of using the loop counter `#` (`.R`) outside a loop
- fixed bug causing incorrect allocation of variables declared by the `.VAR` directive during macro execution
- to unify syntax, references to enumeration type labels are possible only via the dot `.` character (previously also via `::`)
- shorter references to enumeration types possible: `enum_label(fields)`, e.g.:

```
.enum typ
 val0 = 1
 val1 = 5
 val2 = 9
.ende

 lda #typ(val0|val2)  ; == "lda #typ.val0|typ.val2"
```

- extended `.SAV` directive syntax, e.g.:

```
.sav 'filename',offset,length
.sav 'filenema',length
.sav [offset] 'filename',offset2,length
.sav length
.sav offset,length
```

- extended `.ARRAY` directive syntax; if the maximum array index is not provided, it will be calculated based on the number of elements entered; elements can be entered without having to precede them with an `[expression]` index, e.g.:

```
.array temp .byte
 1,4,6                  ; [0..2]   = 1,4,6
 [12] = 9,3             ; [12..13] = 9,3
 [5]:[8] = 10,16        ; [5..6]   = 10,16 ; [8..9] = 10,16
 0,0,\                  ; [14..17] = 0,0,1,1
 1,1
.enda                   ; 18 elements, TEMP [0..17]
```

- added ability to allocate a structural type variable using `.VAR` and `.ZPVAR` directives, e.g.:

```
.struct Point
 x .byte
 y .byte
.ends

 .var a,b,c Point
 .zpvar Point f,g,i

```
- added ability to allocate an enumeration type variable using `.VAR` and `.ZPVAR` directives, e.g.:

```
.enum Boolean
 false = 0
 true = 1
.ende

 .var test Boolean
 .zpvar Boolean test
```

- added ability to declare structure fields using enumeration types, e.g.:

```
.enum EState
  DONE, DIRECTORY_SEARCH, INIT_LOADING, LOADING
.ende

.struct SLoader
    m_file_start .word
    m_file_length .word

    m_state EState
.ends
```

## 1.8.3 - 1.8.4 <a name="1.8.3_1.8.4"></a>

- new software sprite engine with minimal memory requirements, without additional screen memory buffers `...EXAMPLES\SPRITES\CHARS_NG`
- new version of **Huffman** packer (compatible with **Free Pascal Compiler**, `fpc -MDelphi sqz15.pas`) and **Huffman** decompressor SQZ15 `...EXAMPLES\COMPRESSION\SQUASH`
- improved code generated for `MVP`, `MVN`, `PEA`, `BRA` (**WDC 65816**)
- added new `BRL`, `JSL`, `JML` commands (**WDC 65816**) as equivalents for long jump commands `BRA`, `JSR`, `JMP`
- external label update block extended to save the low and high byte of the address of such a label
- improved `.USE` and `.USING` directive operation; works independently of the namespace in which it is used
- fixed a bug that caused skipping assembly of the `#IF` / `#WHILE` block in certain situations
- added ability to define variables via `.DS` directive or `ORG` pseudo command before a `.RELOC` block
- added an additional syntax form for the `.VAR` directive, though for this case there is no way to specify the address of variables in memory

```
 .VAR .TYPE lab1 lab2 lab3 .TYPE lab4 .TYPE lab5 lab6 ...

 .var .byte a,b,c .dword i j
```

- added ability to define single structural type variables in a shorter way than before via `DTA`

```
.struct @point
 x .byte
 y .byte
.ends

pointA  @point    ; pointA dta @point [0] <=> pointA dta @point
pointB  @point    ; pointB dta @point [0] <=> pointB dta @point

points  dta @point [100]
```

- added new `.ZPVAR` directive allowing automatic allocation of space for variables on the zero page

```
 .ZPVAR TYPE label1, label2 label3 = $80  ; LABEL1=$80, LABEL2=LABEL1+TYPE, LABEL3=LABEL2+TYPE
 .ZPVAR label4, label5 TYPE     ; LABEL4=LABEL3+TYPE, LABEL5=LABEL4+TYPE

 .print .zpvar
```

- improved `.ERROR` directive and `ERT` pseudo command operation; it is possible to place additional information in the line similar to `.PRINT` / `.ECHO`, e.g.:

```
  ERT *>$6000 , 'OOPS, we exceeded memory range by ' , *-$6000 , ' bytes'
```


- added ability to nest `.PROC` procedure blocks; the same code can be called with different parameters, e.g.:

```
.proc copySrc (.word src+1) .var

 .proc ToDst (.word src+1, dst+1) .var
 .endp

  ldy #0
src lda $ffff,y
dst sta $ffff,y
  iny
  bne src

  rts
.endp

  copySrc.ToDst #$a080 #$b000

  copySrc #$a360
```

- added new `.ENUM`, `.ENDE`, `.EEND` directives

```
.enum days_of_the_week

  monday = 1
  tuesday, wednesday = 5, thursday = 7
  friday
  saturday
  sunday

.ende

ift day==days_of_the_week::tuesday
.print 'tuesday'
eif
```

- extended multi-line comments `/* */` functionality to allow placing them anywhere

```
lda #12+ /* comment */ 23
```

- enabled relocation of addresses defined with the `.DEF` directive

```
.reloc
.def label=*
lda label
```

- added ability to use `{ }` characters to mark a block (except for `.MACRO` blocks); the `{` / `}` character is recognized at the beginning of a new line, e.g.:

```
#while .word ad+1<=#$bc40+39
{
ad  sta $bc40

  inw ad+1
}

.proc lab
{
  .local temp2
  {
  }

  .array tab [255] .long
  {}
}
```

## 1.8.2 <a name="1.8.2"></a>

- removed file length restriction for `INS` pseudo command (previously the length of the read file was limited to 65536 bytes)
- added **The referenced label ... has not previously been defined properly** error message for labels that were not fully defined, e.g. only in the first pass with an undefined value
- added new `.ECHO` directive as an equivalent to the `.PRINT` directive; additionally, information generated by `.PRINT` / `.ECHO` is now also saved in the `*.LST` listing
- added new `.ALIGN` directive allowing alignment to a specified memory range; additionally, a value to fill memory with can be specified:

```
[label] .ALIGN N[,fill]
```

- added new `-U` switch (Warn of unused labels)


## 1.8.1 <a name="1.8.1"></a>

- extended backslash `\` character operation; placing it at the end of a line means continuing the current line from a new line, e.g.:

```
macro_temp \

_____________________________________parameter1________________________________________________\
_____________________________________parameter2________________________________________________\
_____________________________________parameter3________________________________________________

lda\
 #____________________________________label________________________________________\
 +__________________________________expression___________________________________
```

- changed testing for infinite macro calls, after which an **Infinite loop** error will occur
- fixed writing labels to the `*.LAB` file; the error occurred after adding additivity of `LOCAL` areas
- improved `SIN` pseudo command operation (code borrowed from **XASM**)
- improved directive recognition when the -C switch (Case sensitive) is on
- improved reading of `.REPT` (pointing to the correct line with the error) and `.MACRO` blocks
- blocked the use of `.VAR` in a `.REPT` block
- enabled nesting and multiple runs (via macros) of `.REPT` / `:repeat` loops (previously a **Use .REPT directive** message occurred)
- enabled passing parameters to the `.REPT` block, e.g.:

```
.REPT 10, #
label:1           ; LABEL0, LABEL1, LABEL2 ... LABEL9
.ENDR

.REPT 5, $12,$33,$44,$55,$66
 dta :1,:2,:3,:4,:5            ; $12,$33,$44,$55,$66
 dta :5,:4,:3,:2,:1            ; $66,$55,$44,$33,$12
.ENDR
```

## 1.7.9 - 1.8.0 <a name="1.7.9_1.8.0"></a>
- fixed error in `-f` option description, previously **Label at first column**, correct description is **CPU command at first column**
- rewritten handling of `.DS` directive and `OPT F+` option (added ability to use RUN and INI blocks)
- rewritten handling of `OPT ?+` option (local labels in **MAE** standard)
- added ability to publicize arrays declared by `.ARRAY` and `.STRUCT` declarations in PUBLIC blocks
- the directive generating **6502** code for decision `.TEST` has been replaced by the `#IF` directive, and the `.ENDT` directive by `#END`; additionally, the `#ELSE` directive can be used, e.g.:

```
 # if .byte i>#8 .and .byte i<#200
 # else
       #if .word j = #12
       #end
 # end
```

- the directive generating **6502** code for iteration `.WHILE` has been replaced by the `#WHILE` directive, and the `.ENDW` directive by `#END`, e.g.:

```
 lda 20               ->       lda 20
 # while .byte @=20   ->  wait cmp 20
 # end                ->       sne
                      ->       jmp wait
```

- `#IF` / `#WHILE` directives accept two additional operators: `==`, `!=`
- added `.EXITM` directive as an equivalent to `.EXIT`
- added `.FI` directive as an equivalent to `.ENDIF`
- added `.IFDEF` directive as a shorter equivalent to `.IF` / `.DEF` directives
- added `.IFNDEF` directive as a shorter equivalent to `.IF` / `.NOT` / `.DEF` directives
- enabled defining macros in the area of a `.PROC` procedure; in summary, it is now permissible to define a macro in the `.LOCAL` / `.PROC` area
- occurrence of any warning during assembly will not change the exit code (exit_code=0); the change is dictated by the need for compatibility with Linux makefiles
- unified method of declaring local and global labels; "white spaces" before the label name will not force defining such a label as global; only the `.DEF :LABEL` directive will enable this
- improved `@CALL.MAC` / `@CALL_2.MAC` macros; global temporary variable `?@stack_offset` is now modified by the `.DEF` directive
- discontinued `-E` (Eat White spaces) option; currently this option is always on
- improved display of the line number with the error in the currently executed macro
- shortened names of labels created during macro execution (easier identification in the `*.LAB` file)
- improved `OPT H-` option operation
- added new macro commands: `INL` (increase LONG), `IND` (increase DWORD), `DEL` (decrease LONG), `DED` (decrease DWORD)
- added new macro commands: `CPB` (compare BYTE), `CPW` (compare WORD), `CPL` (compare LONG), `CPD` (compare DWORD)
- improved and extended operation of `#IF` / `#WHILE` directives based on code generated by `CPB`, `CPW`, `CPL`, `CPD` macro commands; `#IF` / `#WHILE` directives for expressions `=#0`, `<>#0` generate the shortest object code
- added optimization of generated code length for `MWA`, `MWX`, `MWY` macro commands
- added new `OPT R` option optimizing macro command code (`MWA`, `MWX`, `MWY`, `MVA`, `MVX`, `MVY`) based on register contents, e.g.:

```
                opt r-        opt r+
mva #0 $80  ->  lda #$00  ->  lda #0
mva #0 $81  ->  sta $80   ->  sta $80
                lda #$00  ->  sta $81
                sta $81   ->
```

- extended `.DEF` directive functionality to allow assigning a value to a newly declared label, e.g.:

```
.def label = 1
```
- extended `.DEF` directive functionality to allow defining a global label regardless of the current local area, e.g.:

```
.def :label
```

- enabled additivity of `.LOCAL` areas, i.e., there can be multiple local areas with the same name; symbols contained in such areas will belong to a common namespace, e.g.:

```
.local namespace

 .proc proc1
 .endp

.endl

.local namespace

 .proc proc2
 .endp

.endl
```

## 1.7.8 <a name="1.7.8"></a>

- added `.MEND`, `.PGEND`, `.REND` directives as equivalents to `.ENDM`, `.ENDPG`, `.ENDR`
- currently macro declaration must end with the `.ENDM` or `.MEND` directive (previously use of the `.END` directive was allowed)
- improved macro execution method, allowing the execution of the `.ENDL` directive from within a macro
- fixed observed bugs regarding older bytes of the relocated address and the public symbol update block
- added new `.USING` / `.USE` directive allowing to specify the search path for label names
- improved `.LOCAL` / `.DEF` directives operation, whose incorrect operation manifested in special cases
- improved jump macro commands operation (`SNE`, `RNE`, etc.), whose incorrect operation manifested in special cases
- extended `.TEST` syntax (**6502** code for condition) to any number of expressions joined by `.OR` or `.AND` (no possibility to change valuation priority using parentheses), e.g.:

```
.test .byte k>#10+1 .or .word j>#100 .and .word j<#105 .or .byte k<=#5
...
...
.endt
```

- extended `.WHILE` syntax (**6502** code for loop) to any number of expressions joined by `.OR` or `.AND` (no possibility to change valuation priority using parentheses), e.g.:

```
.while .byte k>#4 .and .byte k<#39
...
...
.endw
```

## 1.7.6 - 1.7.7 <a name="1.7.6_1.7.7"></a>

- added new `-B:ADDRESS` switch allowing assembly from a given address
- added new `OPT F+-` option allowing to create continuous memory blocks (useful for carts)
- added support for `.LONG` / `.DWORD` type parameters passed to `.VAR` type `.PROC` procedures (previously only `.BYTE` / `.WORD` were accepted parameter types)
- added new `.FL` directive implementing storage of `REAL` numbers in **FP Atari** format, e.g.:

```
pi .fl 3.1415926535897932384626433832795  ; 40 03 14 15 92 65
tb .fl 0.5 12.34 -2.30 0.00002
tb .fl 0.5, 12.34, -2.30, 0.00002
```

- enabled storage of types other than just `.BYTE` in the `.ARRAY` block
- added support for multiple types for `.STRUCT`; previously such types were accepted but memory was not properly reserved for them, e.g.:

```
.struct test
  x :200 .byte
  y :999 .long
.ends

buf dta test [0]
```
- fixed bugs regarding relocatable code generation noticed by **Laoo**, e.g.:

```
    .reloc
    lda temp

temp .long $aabbcc
```

- **Address relocation overload** error will now occur only when the expression involves more than one relocatable label; previously every expression involving a relocatable label caused this error message to be displayed
- public symbol update block extended to allow passing constants of different types: B-YTE, W-ORD, L-ONG, D-WORD; previously the only passed type was W-ORD
- changed `.VAR` directive operation in `.LOCAL` blocks located in a `.PROC` block; such variables are always placed at the end of the block before the `.ENDP` directive; in other cases, at the end of the `.LOCAL` block before the `.ENDL` directive
- enabled relocatability of code generated by `.WHILE` / `.TEST` directives
- improved testing of `.WORD` type values in code generated by `.WHILE` / `.TEST` directives
- added new `.ADR` directive returning the label address before the assembly address change
- added new `.LEN` directive returning the length of blocks defined by `.PROC` / `.ARRAY`
- fixed operation of division, multiplication, and modulo operations; previously priority for these operations was misinterpreted
- comments at the end of a line not preceded by a comment character will cause an **Unexpected end of line** error
- added ability to assign structure-defined fields to a variable, e.g.:

```
@point .struct
       x .byte
       y .byte
       .ends

a @point
b @point
c @point
```

- extended `.STRUCT` syntax to allow adding new fields without defining a field name, e.g.:

```
.struct @id
 id .word
.ends
.struct @mem
 @id
 adr .word
.ends
```

- extended `MWA` macro command syntax to allow use of zero page indirect post-indexed by `Y` addressing, e.g.:

```
mwa ($80),y $a000,x
mwa $bc40,y ($f0),y
mwa ($80),y ($82),y
```

- extended `.EXTRN` directive syntax; it is now possible to announce more labels of different types in one line; announcing a `.PROC` procedure in such a line must be at its end, e.g.:

```
.extrn a,b,c,d .byte  x y z .word  line .proc(.byte x,y) .reg
```

- extended `.VAR` directive syntax; it is now possible to declare more labels of different types in one line and assign them an address from which they will be placed in memory, e.g.:

```
.var x y z .byte bit :2 .dword = $80
```

- extended syntax for procedure parameters passed via `.VAR` variables; it is possible to provide an offset, e.g.:

```
move .proc (.word src+1,dst+1) .var

src lda $ffff
dst sta $ffff

     .endp
```

- added new `.NOWARN` directive disabling warning display for the currently assembled line, e.g.:

```
.nowarn PROCNAME
```

- added new `PHR` / `PLR` macro commands implementing pushing and pulling register values using the hardware stack, e.g.:

```
PHR -> PHA         PLR -> PLA
       TXA                TAY
       PHA                PLA
       TYA                TAX
       PHA                PLA
```

- added new `ADB`, `SBB` macro commands implementing addition and subtraction of `.BYTE` type values, e.g.:

```
ADB $80 #12 $b000  ->  lda $80
                       clc
                       adc #12
                       sta $b000
SBB #200 $a000     ->  lda #200
                       sec
                       sbc $a000
                       sta $a000
```

- added ability to use C syntax for hexadecimal numbers, e.g.:

```
lda 0x2000
ldx #0x12

temp = 0x8000
```

## 1.7.5 <a name="1.7.5"></a>

- the `.DS` directive in **SDX** `RELOC` and **MADS** `RELOC` relocatable blocks now declares an empty block
- added new `-F` switch, which enables placing CPU commands and pseudo commands from the first column in a line
- rewritten procedures for reading `.MACRO` / `.REPT` blocks and the procedure implementing line splitting using the `\` character
- added new `ADW`, `SBW` pseudo commands implementing addition and subtraction of `WORD` type values for **CPU6502**, e.g.:

```
adw hlp #40        ; hlp=hlp+40
adw hlp #20 pom    ; pom=hlp+20
```

- extended `.DEF` directive operation to allow defining a label, e.g.: `.DEF label`
- increased number of passes for label declarations via `EQU` for certain special cases

## 1.7.4 <a name="1.7.4"></a>

- fixed `.PRINT` directive operation; until now it might not have displayed label values starting with letters `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `L`, `T`, `V`
- blocked `.DS` directive operation in **SDX** `.RELOC` blocks and fixed its operation with the `.IF` / `IFT` conditional instruction
- improved search for access paths `-i:path` (subdirectories contained there can be referenced)
- in case of errors during assembly, all of them are displayed instead of only the first error
- fixed observed bugs, including use of a macro in a `.RELOC` file which could cause incorrect information about relocated addresses to be saved in certain situations
- simplified method of ending procedures using the **MADS** program stack; there is no need to use the `.EXIT` directive, and the `.ENDP` directive no longer causes additional actions on the program stack
- added new `.SYMBOL` directive as an equivalent to the update block `BLK UPDATE NEW SYMBOL 'SYMBOL'`; the `.SYMBOL` directive can be used anywhere in the program
- added automatic calling of `ADDRESS`, `EXTERNAL`, `PUBLIC`, `SYMBOL` update blocks for `.RELOC` and **SDX**
- added new `.BY`, `.WO`, `.HE`, `.EN`, `.SB` directives (borrowed from **MAE**)
- added new `OPT ?-` switch (default): labels with a question mark (`?labels`) are treated as temporary labels; `OPT ?+`: labels with a question mark (`?labels`) are treated as local and temporary; the name of the local area is the last used label without a question mark
- added `.LEND`, `.PEND`, `.AEND`, `.WEND`, `.TEND`, `.SEND` directives as equivalents to `.ENDL`, `.ENDP`, `.ENDW`, `ENDW`, `.ENDT`, `.ENDS`
- added new `.GLOBAL`, `.GLOBL` directives as an equivalent (replacement) for the `.PUBLIC` directive
- added optimization of conditional jumps `JEQ`, `JNE`, `JPL`, `JMI`, `JCC`, `JCS`, `JVC`, `JVS`; if possible, a short jump type `BEQ`, `BNE`, `BPL`, `BMI`, `BCC`, `BCS`, `BVC`, `BVS` is chosen
- added a new default space separator for parameters passed to `.PROC` / `.MACRO`; until now it was only the comma character
- improvements regarding passing parameters to macros and procedures, e.g. a macro parameter can be a directive returning an expression value or the loop counter symbol `#`:

```
:12 macro #
```

- added ability to use a space character as a separator for `.VAR` / `.EXTRN`, e.g.:

```
.EXTRN a b c d .word
.VAR i = 1  j = 2 .byte
.VAR a b c d .byte
```

- extended `.VAR` syntax allowing initializing variables with a constant, e.g.:

```
.var i = 10  j = 12 .byte
.var a , b = 2 .byte
```

- added new `.WHILE` / `.ENDW` directives allowing automatic generation of code for a `WHILE` loop, e.g.:

```
        ldx #$ff
.while .word adr < #$bc40+40*24
        stx $bc40
   adr: equ *-2
        inw adr
.endw
```

- added new `.TEST` / `.ENDT` directives allowing automatic generation of code for a condition, e.g.:

```
.test .byte (@>=#'a')
  .test .byte (@<=#'z')

  .endt
.endt
```

## 1.7.3 <a name="1.7.3"></a>

- added ability to change the assembly address of `.PROC` or `.LOCAL` without changing the load address
- removed code optimization for `MWA` macro commands etc., which could cause **MADS** to loop in special cases
- added `.REG`, `.VAR` directives allowing to specify the method of passing parameters to procedures (`.REG` via **CPU** registers, `.VAR` via variables)
- added `.VAR` directive allowing declaration of variables in `.PROC` / `.LOCAL` blocks; declared variables are physically placed at the end of such a block
- extended `.EXTRN` directive syntax, e.g. `EXTRN label1,label2,label3... TYPE`
- if no label declaration for the **MADS** program stack exists, default values are assumed: `@PROC_VARS_ADR=$0500`, `@STACK_ADDRESS=$0600`, `@STACK_POINTER=$FE`
- added `repeat_counter #`, which can be used interchangeably with the `.R` directive
- `^ not relocatable` error will occur when trying to relocate the `lda ^label` command
- added support for public symbols for `CONSTANT` constants in `PUBLIC` blocks
- fixed relocatability for `.ARRAY` arrays, data created by `.STRUCT`, parameters passed to procedures via constant `#`

## 1.7.2 <a name="1.7.2"></a>

- rewritten handling of `REQ`, `RNE`, `RPL`, `RMI`, `RCC`, `RCS`, `RVC`, `RVS`, `SEQ`, `SNE`, `SPL`, `SMI`, `SCC`, `SCS`, `SVC`, `SVS` pseudo commands
- fixed `.LINK` directive operation for fixed-address blocks
- improved reserved words testing (reserved names for **WDC 65816** can be used when using only **6502**)
- changes in the listing; displays bank number information only when bank > 0
- added support for `MWA`, `MWX`, `MWY`, `MVA`, `MVX`, `MVY`, `ADD`, `SUB`, `INW`, `DEW` macro commands (macros are no longer needed to handle them)

## 1.7.1 <a name="1.7.1"></a>

- added ability to use **WDC 65816** mnemonic names in **6502** mode; in **WDC 65816** mode a **Reserved word** error will occur
- fixed operation of `SCC`, `RNE`, etc. jump pseudo commands in macros
- improved execution of multiple macros separated by the colon `:` character

## 1.7.0 <a name="1.7.0"></a>

- fixed a bug that caused too few assembly passes
- added support for `JEQ`, `JNE`, `JPL`, `JMI`, `JCC`, `JCS`, `JVC`, `JVS` pseudo commands (macros are no longer needed to handle them)

## 1.6.9 <a name="1.6.9"></a>

- extended syntax for `.ARRAY`, `.PUT`
- added `EXT` pseudo command allowing declaration of an external label
- added `JEQ`, `JNE`, `JPL`, `JMI`, `JCC`, `JCS` macros
- added `.PAGES`, `.ENDPG` directives
- added `.END` directive replacing other `.END?` directives
- `-H` switch has been replaced by `-HC` (generates header file for **CC65**)
- added new `-HM` switch generating a header file for **MADS** with sorting into labels of type `CONSTANTS`, `VARIABLES`, `PROCEDURES`
- added new `.RELOC` directive generating relocatable code in **MADS** format

## 1.6.8 <a name="1.6.8"></a>

- added new `.PUT` directive and extended syntax for the `.GET` directive (../EXAMPLES/MSX/MPT_PLAYER/MPT_RELOCATOR.MAC , ../EXAMPLES/MSX/TMC_PLAYER/TMC_RELOCATOR.MAC)
- added support for **XASM** pseudo commands `REQ`, `RNE`, `RPL`, `RMI`, `RCC`, `RCS`, `RVC`, `RVS`, `SEQ`, `SNE`, `SPL`, `SMI`, `SCC`, `SCS`, `SVC`, `SVS`
- added ability to join any number of known **MADS** mnemonics using the `:` character (**XASM** style), e.g.:

```
lda:cmp:req 20
ldx:ldy:lda:iny label
```

## 1.6.6 - 1.6.7 <a name="1.6.6_1.6.7"></a>

- **MADS** source compatible with **Free Pascal Compiler**; after compilation it can be used on other operating platforms, such as **Linux**, **Mac OS**, **OS/2**, etc.
- from now on **MADS** itself chooses the appropriate number of assembly passes; the `/3` switch is no longer needed
- improved and expanded mechanism for passing parameters to **MADS** (section *Assembler switches*)
- fixed macro call in a line split with the `\` character and improved recognition and execution of lines split with `\` characters
- fixed a bug in which **MADS** confused the `.ENDM` directive with the `IFT` pseudo command
- fixed operation of `.ELSEIF`, `.ELSE` conditional instructions
- fixed correctness testing of conditional instructions in macros
- `.PROC` procedure support has been expanded with new macros and mechanisms, making its operation and ease of use similar to procedures from higher-level languages
- for `.PROC` procedures with declared parameters, an additional `@PROC_VARS_ADR` declaration is now needed
- no limit on the number of parameters passed to procedures; the only limit is available memory
- added new `/d:label=value` switch allowing definition of a new **MADS** label from the command line
- added new `/x` switch (**Exclude unreferenced procedures**) allowing to skip procedures declared with the `.PROC` directive not used in the program during assembly
- new `OPT T+` option (track sep, rep) tracking `A`, `X`, `Y` register size changes made by `SEP`, `REP` **WDC 65816** commands
- new libraries in the `..\EXAMPLES\LIBRARIES` directory
- in the `.LOCAL` area declaration, providing an area name is not required
- new `-=`, `+=`, `++`, `--` operators allowing to decrease/increase the value of a temporary label, e.g.:

```
?label --      ->   ?label=?label-1
?lab ++        ->   ?lab=?lab+1
?temp += 3     ->   ?temp=?temp+3
?ofset -= 5    ->   ?ofset=?ofset-5
```

- extended syntax for procedure parameter declaration with the comma character, e.g.:

```
.proc name (.byte a,b,c .word d,e)
.endp
```
