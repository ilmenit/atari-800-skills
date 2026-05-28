## Directives


 [.A8, .A16, .AI8, .AI16](#a8)<br>
 [.I8, .I16, .IA8, .IA16](#i8)<br>

 [.ASIZE](#asize)<br>
 [.ISIZE](#isize)<br>

 [.ALIGN N[,fill]](#align)

 [.ARRAY label [elements0][elements1][...] .type [= init_value]](arrays.md#arrays)<br>
 [.ENDA, [.AEND]](arrays.md#arrays)<br>

 [.DEF label [= expression]](#def)

 [.DEFINE macro_name expression](#define)<br>
 [.UNDEF macro_name](#undef)<br>

 [.ENUM label](data-types.md#enumerations)<br>
 [.ENDE, [.EEND]](data-types.md#enumerations)<br>

 [.ERROR [ERT] 'string'["string"] or .ERROR [ERT] expression](#error)

 [.EXTRN label [,label2,...] type](relocatable-code.md#external-symbols)

 [.IF [IFT] expression](#if_else)<br>
 [.ELSE [ELS]](#if_else)<br>
 [.ELSEIF [ELI] expression](#if_else)<br>
 [.ENDIF [EIF]](#if_else)<br>

 [.IFDEF label](#ifdef)<br>
 [.IFNDEF label](#ifndef)<br>

 [.LOCAL label](local-areas.md#local-area)<br>
 [.ENDL, [.LEND]](local-areas.md#local-area)<br>

 [.LONGA ON|OFF](relocatable-code.md#directives-longa-and-longi)<br>
 [.LONGI ON|OFF](relocatable-code.md#directives-longa-and-longi)<br>

 [.LINK 'filename']](../relocatable-code/#linking-link)

 [.MACRO label](macros.md#macros)<br>
 [.ENDM, [.MEND]](macros.md#macros)<br>
 [:[%%]parameter](macros.md#macros)<br>
 [.EXITM [.EXIT]](macros.md#macros)<br>

 [.NOWARN](#nowarn)

 [.PRINT [.ECHO] 'string1','string2'...,value1,value2,...](#print)

 [.PAGES [expression]](#pages)<br>
 [.ENDPG, [.PGEND]](#pages)<br>

 [.PUBLIC, [.GLOBAL], [.GLOBL] label [,label2,...]](relocatable-code.md#public-symbols)

 [.PROC label](procedures.md#procedure-declaration)<br>
 [.ENDP, [.PEND]](procedures.md#procedure-declaration)<br>
 [.REG, .VAR](procedures.md#procedure-declaration)<br>

 [.REPT expression [,parameter1, parameter2, ...]](#rept)<br>
 [.ENDR, [.REND]](#rept)<br>
 [.R](#rept)<br>

 [.RELOC [.BYTE|.WORD]](relocatable-code.md#relocatable-block-reloc)

 [.STRUCT label](data-types.md#structures)<br>
 [.ENDS, [.SEND]](data-types.md#structures)<br>

 [.SYMBOL label](#symbol)

 [.SEGDEF label address length [bank]](#seg)<br>
 [.SEGMENT label](#seg)<br>
 [.ENDSEG](#seg)<br>

 [.USING, [.USE] proc_name, local_name](#using)

 [.VAR var1[=value],var2[=value]... (.BYTE|.WORD|.LONG|.DWORD)](#var)<br>
 [.ZPVAR var1, var2... (.BYTE|.WORD|.LONG|.DWORD)](#zpvar)<br>

 [.END](#end)

 [.EN](#en)

 [.BYTE](#byte)<br>
 [.WORD](#byte)<br>
 [.LONG](#byte)<br>
 [.DWORD](#byte)<br>

 [.OR](#or_and)<br>
 [.AND](#or_and)<br>
 [.XOR](#or_and)<br>
 [.NOT](#or_and)<br>

 [.LO (expression)](#lohi)<br>
 [.HI (expression)](#lohi)<br>

 [.DBYTE words](#dbyte)<br>
 [.DS expression](#_ds)<br>

 [.BY [+byte] bytes and/or ASCII](#_by)<br>
 [.WO words](#_wo)<br>
 [.HE hex bytes](#_he)<br>
 [.SB [+byte] bytes and/or ASCII](#_sb)<br>
 [.CB [+byte] bytes and/or ASCII](#_cb)<br>
 [.FL floating point numbers](#_fl)<br>

 [.ADR label](#adr)

 [.LEN label ['filename']](#sizeof)<br>
 [.SIZEOF label](#sizeof)<br>
 [.FILESIZE 'filename'](#sizeof)<br>

 [.FILEEXISTS 'filename'](#fileexists)<br>

 [.GET [index] 'filename'["filename"][*][+-value][,+-ofset[,length]]](#get)<br>
 [.WGET [index]](#get)<br>
 [.LGET [index]](#get)<br>
 [.DGET [index]](#get)<br>
 [.PUT [index] = value](#put)<br>
 [.SAV [index] ['filename',] length](#sav)<br>


<a name="symbol"></a>
### .SYMBOL label
The `.SYMBOL` directive is the equivalent of the `SMB` pseudo-instruction, with the difference that you do not need to provide a symbol; the symbol is the `label`. The `.SYMBOL` directive can be placed anywhere within an **SDX** relocatable block (`BLK RELOC`), unlike `SMB`.

If the `.SYMBOL` directive occurs, a corresponding update block will be generated:

```
BLK UPDATE NEW LABEL 'LABEL'
```

More about SDX symbol declarations in the [Defining SMB symbols](#smb) chapter.


<a name="align"></a>
### .ALIGN N [,fill]
The `.ALIGN` directive allows aligning the assembly address to a specified value `N`, and potentially filling memory with a specified `FILL` value. It is possible to align the assembly address for relocatable code provided a memory fill value `FILL` is given.

Default values are: `N=$0100`, `FILL=0`.

```
 .align

 .align $400

 .align $100,$ff
```

<a name="rept"></a>
### .REPT expression [,parameter1, parameter2, ...]
The `.REPT` directive is an extension of `:repeat`, with the difference that it repeats a designated program block instead of a single line. The beginning of the block is defined by the `.REPT` directive, followed by a value or arithmetic expression specifying the number of repetitions in the range <0..2147483647>. After the number of repetitions, parameters may optionally occur. Unlike macros, parameters for `.REPT` are always evaluated first, and only then is their result substituted (this property can be used to define new labels). Parameters in a `.REPT` block are used similarly to parameters in a `.MACRO` block. The end of a `.REPT` block is defined by the `.ENDR` directive, before which no label should be placed.

Additionally, within the block marked by `.REPT` and `.ENDR`, you can use the hash character `#` (or the `.R` directive), which returns the current value of the `.REPT` loop counter (similar to `:repeat`).

```
 .rept 12, #*2, #*3        ; we can combine .REPT blocks with :rept
 :+4 dta :1                ; :+4 to distinguish the repetition counter from the parameter :4
 :+4 dta :2
 .endr

 .rept 9, #                ; we define 9 labels label0..label8
label:1 mva #0 $d012+#
 .endr
```

<a name="pages"></a>
### .PAGES [expression]
The `.PAGES` directive allows specifying the number of memory pages that our code snippet, bounded by `<.PAGES .. .ENDPG>`, should fit into (default is 1). If the program code exceeds the declared number of memory pages, a *Page error at ????* error message will be generated.

These directives can help us when we want a program fragment to fit within a single memory page, or when writing a program that fits into an additional memory bank (64 memory pages), e.g.:

```
 org $4000

 .pages $40
  ...
  ...
 .endpg
```

<a name="seg"></a>
### .SEGDEF label address length [attrib] [bank]
### .SEGMENT label
### .ENDSEG

The `.SEGDEF` directive defines a new segment `LABEL` with starting address `ADDRESS` and length `LENGTH`. Additionally, it is possible to specify an attribute for the segment (R-read, W-rite, RW-ReadWrite - default) and assign a virtual bank number `BANK` (default `BANK=0`).

The `.SEGMENT` directive activates writing the output code for segment `LABEL`. If the specified segment length is exceeded, a *Segment LABEL error at ADDRESS* error message will be generated.

The `.ENDSEG` directive ends writing to the current segment and restores writing to the main program block.

```
	.segdef sdata adr0 $100
	.segdef test  adr1 $40

	org $2000

	nop

	.cb 'ALA'

	.segment sdata

	nop

	.endseg

	lda #0

	.segment test
	ldx #0
	clc

	dta c'ATARI'

	.endseg

adr0	.ds $100
adr1	.ds $40
```

### .END
The `.END` directive can be used interchangeably with the directives `.ENDP`, `.ENDM`, `.ENDS`, `.ENDA`, `.ENDL`, `.ENDR`, `.ENDPG`, `.ENDW`, and `.ENDT`.


<a name="var"></a>
### .VAR var1[=value1],var2[=value2]... (.BYTE|.WORD|.LONG|.DWORD) [=address]
The `.VAR` directive is used to declare and initialize variables in the main program block and in `.PROC` and `.LOCAL` blocks. **MADS** does not use information about such variables in further operations involving pseudo and macro instructions. Permitted variable types are `.BYTE`, `.WORD`, `.LONG`, `.DWORD` and their multiples, as well as types declared by `.STRUCT` and `.ENUM`, e.g.:

```
 .var a,b , c,d   .word          ; 4 variables of type .WORD
 .var a,b,f  :256 .byte          ; 3 variables, each 256 bytes in size
 .var c=5,d=2,f=$123344 .dword   ; 3 .DWORD variables with values 5, 2, $123344

 .var .byte i=1, j=3             ; 2 variables of type .BYTE with values 1, 3

 .var a,b,c,d .byte = $a000      ; 4 variables of type .BYTE with addresses $A000, $A001, $A002, $A003 respectively

 .var .byte a,b,c,d = $a0        ; 4 byte-type variables, the last variable 'D' with value $A0
                                 ; !!! for this notation, it is not possible to specify the allocation address for variables

  .proc name
  .var .word p1,p2,p3            ; declaration of three .WORD type variables
  .endp

 .local
  .var a,b,c .byte
  lda a
  ldx b
  ldy c
 .endl

 .struct Point                   ; new structural data type POINT
 x .byte
 y .byte
 .ends

  .var a,b Point                 ; declaration of structural variables
  .var Point c,d                 ; equivalent to the syntax 'label DTA POINT'
```

Variables declared this way will be physically allocated only at the end of the block in which they were declared, after the `.ENDP`, `.ENDL` (`.END`) directive. An exception is the `.PROC` block, where variables declared via `.VAR` are always allocated before the `.ENDP` directive, regardless of whether any additional `.LOCAL` blocks with variables declared via `.VAR` occurred within the procedure block.


<a name="zpvar"></a>
### .ZPVAR var1, var2... (.BYTE|.WORD|.LONG|.DWORD) [=address]
The `.ZPVAR` directive is used to declare zero page variables in the main program block and in `.PROC` and `.LOCAL` blocks. Attempting to assign a value (initialize) such a variable will generate an *Uninitialized variable* warning message. **MADS** does not use information about such variables in further operations involving pseudo and macro instructions. Permitted variable types are `.BYTE`, `.WORD`, `.LONG`, `.DWORD` and their multiples, as well as types declared by `.STRUCT` and `.ENUM`, e.g.:

```
 .zpvar a b c d  .word = $80    ; 4 variables of type .WORD with starting address $0080
 .zpvar i j .byte               ; two subsequent variables from address $0080+8

 .zpvar .word a,b               ; 2 variables of type .WORD
                                ; !!! for this syntax, it is not possible to specify the address for variables

 .struct Point                  ; new structural data type POINT
 x .byte
 y .byte
 .ends

  .zpvar a,b Point              ; declaration of structural variables
  .zpvar Point c,d              ; equivalent to the syntax 'label DTA POINT'
```

Zero page variables declared this way will be assigned addresses only at the end of the block in which they were declared, after the `.ENDP`, `.ENDL` (`.END`) directive. An exception is the `.PROC` block, where addresses for variables declared via `.ZPVAR` are assigned before the `.ENDP` directive, regardless of whether any additional `.LOCAL` blocks with variables declared via `.ZPVAR` occurred within the procedure block.

Upon the first use of the `.ZPVAR` directive, you must initialize the address that will be assigned to subsequent variables (the default address is $0080).

```
 .zpvar = $40
```

With each subsequent variable, this address is automatically increased by **MADS**. If variable addresses overlap, an *Access violations at address $xxxx* warning message will be generated. If the zero page range is exceeded, a *Value out of range* error message is generated.


<a name="print"></a>
### .PRINT [.ECHO]
Causes the value of the expression or the character string provided as a parameter (enclosed in single `' '` or double `" "` quotes) to be printed on the screen, e.g.:

```
 .print "End: ",*,'..',$8000-*
 .echo "End: ",*,'..',$8000-*
```

<a name="error"></a>
### .ERROR [ERT] 'string'["string"] | .ERROR [ERT] expression

The `.ERROR` directive and the `ERT` pseudo-instruction have the same meaning. They stop program assembly and display the message provided as a parameter, enclosed in single `' '` or double `" "` quotes. If the parameter is a logical expression, assembly will be stopped when the value of the logical expression is true (displaying the message *User error*), e.g.:

```
 ert "halt"            ; ERROR: halt
 .error "halt"

 ert *>$7fff           ; ERROR: User error
 .error *>$7fff
```

<a name="byte"></a>
### .BYTE, .WORD, .LONG, .DWORD
The above directives are used to denote the allowed parameter types in procedure parameter declarations (`.BYTE`, `.WORD`, `.LONG`, `.DWORD`). They can also be used to define data, as a substitute for the `DTA` pseudo-instruction.

```
.proc test (.word tmp,a,b .byte value)

 .byte "atari",5,22
 .word 12,$FFFF
 .long $34518F
 .dword $11223344
```

<a name="dbyte"></a>
### .DBYTE
Definition of `WORD` type data in reverse order, i.e., the high byte first, followed by the low byte.

```
.DBYTE $1234,-1,1     ; 12 34 FF FF 00 01
```

<a name="_ds"></a>
### [label] .DS expression | label .DS [elements0][elements1][...] .type

This directive is borrowed from **MAC'65** and allows reserving memory without prior initialization. It is the equivalent of the `ORG *+expression` pseudo-instruction. Like `ORG`, the `.DS` directive cannot be used in relocatable code. Using square brackets in the expression enables reserving memory as an array, similar to `.ARRAY`; providing a label is required in this case. Using the `.DS` directive in a **Sparta DOS X** relocatable block will force the creation of an empty block (`blk empty`).

purpose: reserves space for data without initializing then space to any particular value(s).

```
usage: [label] .DS expression
       label .DS [elements0][elements1][...] .TYPE
```

Using `.DS expression` is exactly equivalent of using `ORG *+expression`. That is, the label (if it is given) is set equal to the current value of the location counter. Then then value of the expression is added to then location counter.

```
         BUFFERLEN .DS 1     ;reserve a single byte
         BUFFER   .DS [256]  ;reserve 256 bytes as array [0..255]
```

<a name="_by"></a>
### .BY [+byte] bytes and/or ASCII
Store byte values in memory. *ASCII* strings can be specified by enclosing the string in either single or double quotes.

If the first character of the operand field is a `+`, then the following byte will be used as a constant and added to all remaining bytes of the instruction.

```
      .BY +$80 1 10 $10 'Hello' $9B

will generate:
        81 8A 90 C8 E5 EC EC EF 1B
```

Values in `.BY` statements may also be separated with commas for compatibility with other assemblers. Spaces are allowed since they are easier to type.


<a name="_wo"></a>
### .WO words
Stores words in memory. Multiple words can be entered.

Values in `.WO` statements may also be separated with commas for compatibility with other assemblers. Spaces are allowed since they are easier to type.


<a name="_he"></a>
### .HE hex bytes
Store hex bytes in memory. This is a convenient method to enter strings of hex bytes, since it does not require the use of the '$' character. The bytes are still separated by spaces however, which I feel makes a much more readable layout than the 'all run together' form of hex statement that some other assemblers use.

```
   .HE 0 55 AA FF
```

Values in `.HE` statements may also be separated with commas for compatibility with other assemblers. Spaces are allowed since they are easier to type.


<a name="_sb"></a>
### .SB [+byte] bytes and/or ASCII
This is in the same format as the .BY pseudo-op, except that it will convert all bytes into *ATASCII* screen codes before storing them. The *ATASCII* conversion is done before any constant is added with the '+' modifier.

Values in `.SB` statements may also be separated with commas for compatibility with other assemblers. Spaces are allowed since they are easier to type.


<a name="_cb"></a>
### .CB [+byte] bytes and/or ASCII
This is in the same format as the `.BY` pseudo-op, except that the last character on the line will be EOR'ed with $80.

Values in `.CB` statements may also be separated with commas for compatibility with other assemblers. Spaces are allowed since they are easier to type.


<a name="_fl"></a>
### .FL floating point numbers
Stores 6-byte *BCD* floating point numbers for use with the *OS FP ROM* routines.

Values in `.FL` statements may also be separated with commas for compatibility with other assemblers. Spaces are allowed since they are easier to type.


### .EN
The `.EN` directive is the equivalent of the `END` pseudo-instruction, marking the end of the assembled program block.

This is an optional pseudo-op to mark the end of assembly. It can be placed before the end of your source file to prevent a portion of it from being assembled.


<a name="adr"></a>
### .ADR label
The `.ADR` directive returns the value of the `LABEL` label before the change of the assembly address (it is possible to place the `LABEL` name between round or square brackets), e.g.:

```
 org $2000

.proc tb,$1000
tmp lda #0
.endp

 lda .adr tb.tmp  ; = $2000
 lda tb.tmp       ; = $1000
```

<a name="sizeof"></a>
### .LEN label ['filename'], .SIZEOF label, .FILESIZE 'filename'
The `.LEN` directive returns the length (expressed in bytes) of a `.PROC`, `.ARRAY`, `.LOCAL`, or `.STRUCT` block, or the length of a file named `'filename'`. The `LABEL` is the name of the `.PROC`, `.ARRAY`, `.LOCAL`, or `.STRUCT` block (it is possible to place the `LABEL` name between round or square brackets), e.g.:

```
label .array [255] .dword
      .enda

      dta a(.len label)   ; = $400

.proc wait
 lda:cmp:req 20
 rts
.endp

 dta .sizeof wait    ; = 7
```

The `.SIZEOF` and `.FILESIZE` directives are alternative names for `.LEN`; they can be used interchangeably depending on the programmer's preference.


<a name="fileexists"></a>
### .FILEEXISTS 'filename'
The `.FILEEXISTS` directive returns `'1'` when the file `'filename'` exists; otherwise, it returns `'0'`, e.g.:

```
 ift .fileexists 'filename'
   .print 'true'
  els
   .print 'false'
  eif
```

<a name="define"></a>
### .DEFINE macro_name expression
The `.DEFINE` directive allows defining a one-line macro `MACRO_NAME`. Nine parameters are permitted, `%%1..%%9` (`:1..:9`), represented in the same way as for `.MACRO` macros, via the `%%` characters or the `:` character. Literal parameter names are not accepted, and there is no possibility to use the line break character `\`.

```
 .define poke mva #%%2 %%1

 poke(712, 100)
```

A one-line `.DEFINE` macro can be defined multiple times during a single assembly pass.

```
 .define pisz %%1+%%2

 .print pisz(712, 100)

 .define pisz %%1-%%2

 .print pisz(712, 100)
```

<a name="undef"></a>
### .UNDEF macro_name
The `.UNDEF` directive removes the definition of the one-line macro `MACRO_NAME`.

```
 .define poke mva #%%2 %%1

 .undef poke
```

<a name="def"></a>
### .DEF label [= expression]
The `.DEF` directive allows checking for the presence of a label definition `LABEL` or defining it. If the label is defined, it returns the value `1` (TRUE); otherwise, it returns `0` (FALSE). It is possible to place the `LABEL` name between round or square brackets, e.g.:

```
 ift .not(.def label)
 .def label
 eif
```

Defined labels are within the scope of the current local area. If you want to define global labels, place the `:` character before the label, e.g.:

```
.local test
 :10 .def :label%%1
.endl
```

This unary operator tests whether the following label has been defined yet, returning TRUE or FALSE as appropriate.

> _CAUTION:_
> _Defining a label AFTER the use of a .DEF which references it can be dangerous, particularly if the .DEF is used in a .IF directive._


<a name="ifdef"></a>
### .IFDEF label
The `.IFDEF` directive is a shorter equivalent of the `.IF .DEF LABEL` condition.

```
.ifdef label
       jsr proc1
.else
       jsr proc2
.endif
```

<a name="ifndef"></a>
### .IFNDEF label
The `.IFNDEF` directive is a shorter equivalent of the `.IF .NOT .DEF LABEL` condition.

```
.ifndef label
      clc
.else
      sec
.endif
```

For the example below, assembly of the `.IFNDEF` (`.IF`) block will occur only in the first pass. If we place any program code within such a block, it will certainly not be generated into the file. Label definitions will be carried out only in the first pass; if any errors occurred related to their definition, we will only find out when attempting to reference such labels, resulting in the *Undeclared label LABEL_NAME* error message.

```
 .ifndef label
 .def label
 lda #0               ; this instruction will not be assembled; only the last assembly pass generates code
 temp = 100           ; the label TEMP will be defined only in the 1st assembly pass
 .endif
```

<a name="nowarn"></a>
### .NOWARN
The `.NOWARN` directive disables the warning message for the currently assembled program line.

```
.nowarn .proc temp       ; the warning 'Unreferenced procedure TEMP' will not be generated
        .endp
```

<a name="using"></a>
### .USING, [.USE]
The `.USING` (`.USE`) directive allows specifying an additional search path for label names. The effect of `.USING` (`.USE`) applies in the current namespace as well as subsequent namespaces contained within it.

```
.local move

tmp    lda #0
hlp    sta $a000

.local move2

tmp2   ldx #0
hlp2   stx $b000

.endl

.endl

.local main

.use move.move2

       lda tmp2

.use move

       lda tmp

.endl
```

<a name="get"></a>
### .GET [index] 'filename'... [.BYTE, .WORD, .LONG, .DWORD]
### .WGET [index] | .LGET [index] | .DGET [index]

`.GET` is the equivalent of the `INS` pseudo-instruction (similar syntax), with the difference that the file is not appended to the assembled file but instead loaded into **MADS** memory. This directive allows loading a specified file into **MADS** memory and referencing the bytes of this file like a one-dimensional array.

```
 .get 'file'                    ; loading a file into the MADS array
 .get [5] 'file'                ; loading a file into the MADS array starting from index = 5

 .get 'file',0,3                ; loading 3 values into the MADS array

 lda #.get[7]                   ; reading the 7th byte from the MADS array
 adres = .get[2]+.get[3]<<8     ; the 2nd and 3rd bytes in the DOS file header contain information about the load address

 adres = .wget[2]              ; word
 tmp = .lget[5]                ; long
 ?x = .dget[11]                ; dword
```

Using the `.GET` and `.PUT` directives, one can read, for example, a **Theta Music Composer** (*TMC*) module and perform its relocation. This is implemented by the macro included with **MADS** in the directory `../EXAMPLES/MSX/TMC_PLAYER/tmc_relocator.mac`.

The permitted range of values for `INDEX` is <0..65535>. Values read by `.GET` are of type `BYTE`. Values read by `.WGET` are of type `WORD`. Values read by `.LGET` are of type `LONG`. Values read by `.DGET` are of type `DWORD`.


<a name="put"></a>
### .PUT [index] = value
The `.PUT` directive allows referencing the one-dimensional array in **MADS** memory and writing a `BYTE` type value into it. This is the same array where the `.GET` directive saves the file.
The permitted range of values for INDEX = <0..65535>.

```
 .put [5] = 12       ; writing the value 12 into the MADS array at position 5
```

<a name="sav"></a>
### .SAV [index] ['filename',] length
The `.SAV` directive allows saving the buffer used by the `.GET` and `.PUT` directives to an external file or appending it to the currently assembled one.

```
 .sav ?length            ; appending the contents of the buffer [0..?length-1] to the assembled file
 .sav [200] 256          ; appending the contents of the buffer [200..200+256-1] to the assembled file
 .sav [6] 'filename',32  ; saving the contents of the buffer [6..6+32-1] to the file FILENAME
```

The permitted range of values for INDEX = <0..65535>.


<a name="or_and"></a>
### .OR, .AND, .XOR, .NOT
The above directives are equivalents of the logical operators `||` (`.OR`), `&&` (`.AND`), `^` (`.XOR`), and `!` (`.NOT`).


<a name="lohi"></a>
### .LO (expression), .HI (expression)
The above directives are equivalents of the operators `<` (low byte) and `>` (high byte) respectively.

<a name="if_else"></a>
### .IF, .ELSE, .ELSEIF, .ENDIF

```
 .IF     [IFT] expression
 .ELSE   [ELS]
 .ELSEIF [ELI] expression
 .ENDIF  [EIF]
```

The above directives and pseudo-instructions affect the assembly process (they can be used interchangeably), e.g.:

```
 .IF .NOT .DEF label_name
   label_name = 1
 .ENDIF

 .IF [.NOT .DEF label_name] .AND [.NOT .DEF label_name2]
   label_name = 1
   label_name2 = 2
 .ENDIF
```

In the above example, parentheses (square or round) are a necessity; their absence would mean that for the first `.DEF` directive, the parameter would be the label name `label_name.AND.NOT.DEFlabel_name2` (spaces are ignored, and the dot character is accepted in label names).
