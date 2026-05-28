## Pseudo-commands

 [IFT _.IF_ expression](#ift)<br>
 [ELS _.ELSE_](#ift)<br>
 [ELI _.ELSEIF_ expression](#ift)<br>
 [EIF _.ENDIF_](#eif)<br>

<a name="ert"></a>
 [ERT _ERT 'string'_ | ERT expression](#ert)

 [label SET expression](#set)<br>
 [label EXT type](#ext)<br>
 [label EQU expression](#equ)<br>
 [label  =  expression](#equ2)<br>

 [OPT [bcfhlmorst][+-]](#opt)<br>
 [ORG [[expression]]address[,address2]](#org)<br>
 [INS 'filename'["filename"][*][+-value][,+-ofset[,length]]](#ins)<br>
 [ICL 'filename'["filename"]](#icl)<br>

 [DTA [abfghltvmer](value1,value2...)[(value1,value2...)]](#dta)<br>
 [DTA [cd]'string'["string"]](#dta_s)<br>

 [RUN expression](#run)<br>
 [INI expression](#ini)<br>
 [END _.EN_](#end)<br>

 [SIN (centre,amp,size[,first,last])](#sin)<br>
 [COS (centre,amp,size[,first,last])](#cos)<br>
 [RND (min,max,length)](#rnd)

 [:repeat](#rep)

 [BLK N`one` X](#blk_n)<br>
 [BLK D`os` X](#blk_d)<br>
 [BLK S`parta` X](#blk_s)<br>
 [BLK R`eloc` M`ain`|E`xtended`](#blk_r)<br>
 [BLK E`mpty` X M`ain`|E`xtended`](#blk_e)<br>
 [BLK U`pdate` S`ymbols`](#blk_us)<br>
 [BLK U`pdate` E`xternal`](#blk_ue)<br>
 [BLK U`pdate` A`dress`](#blk_ua)<br>
 [BLK U`pdate` N`ew` X 'string'](#blk_un)<br>

 [label SMB 'string'](#smb)

 [NMB](#nmb)<br>
 [RMB](#rmb)<br>
 [LMB #expression](#lmb)<br>

Mostly the same as before, although a few changes have occurred. Both single ' ' and double " " quotes can be used. Both types are treated equally except for addressing (single quotes ' ' calculate the `ATASCII` value of the character, while double quotes " " calculate the `INTERNAL` value of the character).


### BLK

```
 BLK N[one] X                    - block without headers, program counter set to X

 BLK D[os] X                     - DOS block with $FFFF header or without header if the
                                   previous one is the same, program counter set to X

 BLK S[parta] X                  - block with fixed loading addresses and $FFFA header,
                                   program counter set to X

 BLK R[eloc] M[ain]|E[xtended]   - relocatable block placed in MAIN or EXTENDED memory

 BLK E[mpty] X M[ain]|E[xtended] - relocatable block reserving X bytes in MAIN or EXTENDED memory
                                   NOTE: the program counter is immediately increased by X bytes

 BLK U[pdate] S[ymbols]          - block updating SDX symbol addresses in previous SPARTA or
                                   RELOC blocks

 BLK U[pdate] E[xternal]         - block updating external label addresses ($FFEE header)
                                   NOTE: does not apply to Sparta DOS X, this is a MADS extension

 BLK U[pdate] A[dress]           - block for updating addresses in RELOC blocks

 BLK U[pdate] N[ew] X 'string'   - block declaring a new symbol 'string' in a RELOC block
                                   at address X. If the symbol name is preceded by the @ sign
                                   and the address is from main memory, such a symbol can be
                                   called from command.com
```

More information about blocks in **Sparta DOS X** files in the [Sparta DOS X File Structure](spartadosx.md#file-structure) and [Sparta DOS X Programming](spartadosx.md#programming) chapters.

<a name="set"></a>
### label SET expression

The `SET` pseudo-command allows redefining a label; it works similarly to temporary labels starting with the `?` sign, e.g.:

```
temp set 12

     lda #temp

temp set 23

     lda #temp
```

<a name="smb"></a>
### label SMB 'string'

Label declaration as an **SDX** symbol. The symbol can have a maximum length of 8 characters. As a result, after using `BLK UPDATE SYMBOLS`, the assembler will generate the correct symbol update block. E.g.:

```
       pf  smb 'PRINTF'
           jsr pf
           ...
```

will make the **SDX** system insert the symbol's address after the `JSR` instruction.

> **NOTE:**
> _This declaration is not transitive, meaning the following example will cause compilation errors:_

```
       cm  smb 'COMTAB'
       wp  equ cm-1       (error!)

           sta wp
```

Instead, use:

```
       cm  smb 'COMTAB'

           sta cm-1       (ok!)
```

> **NOTE:**
> _All symbol declarations must be used before label declarations and the main program!_


<a name="rep"></a>
### :repeat

```
           :4 asl @
           :2 dta a(*)
           :256 dta #/8

ladr :4 dta l(line:1)
hadr :4 dta h(line:1)
```

The `:` sign specifies the number of line repetitions (in the case of macros, it specifies the parameter number, provided the numerical value is written in decimal). The number of repetitions should be in the range `<0..2147483647>`. In the repeated line `:repeat`, it is possible to use the loop counter - the hash sign `#` or the parameter `:1`.
If we use the `:` sign in a macro as the line repetition count, e.g.:

```
.macro test
 :2 lsr @
.endm
```

Then, for the above example, the `:` sign will be interpreted as the second macro parameter. To prevent this interpretation by **MADS**, place a character that does nothing after the colon `:`, such as a plus sign '+'.

```
.macro test
 :+2 lsr @
.endm
```

Now the colon sign `:` will be correctly interpreted as `:repeat`

### OPT

The `OPT` pseudo-command allows enabling/disabling additional options during assembly.

```
 b+  bank sensitive on
 b-  bank sensitive off                                               (default)
 c+  enables support for CPU 65816 (16-bit)
 c-  enables support for CPU 6502 (8-bit)                             (default)
 f+  output file as a single block (useful for carts)
 f-  output file in block format                                      (default)
 h+  saves the file header for DOS                                   (default)
 h-  does not save the file header for DOS
 l+  saves the listing to a file (LST)
 l-  does not save the listing (LST)                                  (default)
 m+  saves entire macros in the listing
 m-  saves only the part of the macro that is executed in the listing (default)
 o+  saves the assembly result to an output file (OBX)                (default)
 o-  does not save the assembly result to an output file (OBX)
 r+  code length optimization for MVA, MVX, MVY, MWA, MWX, MWY
 r-  no code length optimization for MVA, MVX, MVY, MWA, MWX, MWY     (default)
 s+  prints the listing on the screen
 s-  does not print the listing on the screen                         (default)
 t+  track SEP REP on (CPU 65816)
 t-  track SEP REP off (CPU 65816)                                    (default)
 ?+  labels starting with '?' are local (MAE style)
 ?-  labels starting with '?' are temporary                           (default)
```

```
 OPT c+ c  - l  + s +
 OPT h-
 OPT o +
```

All `OPT` options can be used anywhere in the listing; for example, we can enable listing recording at line 12 and disable it at line 20, etc. Then the listing file will only contain lines 12..20.

If we want to use *65816* addressing modes, we must inform the assembler via `OPT C+`.

If using **CodeGenie** or **Notepad++**, you can use `OPT S+` so you don't have to switch to the listing file, as the listing will be printed in the bottom window (Output Bar).


### ORG

The `ORG` pseudo-command sets a new assembly address, and thus the location of the assembled data in *RAM*.

```
 adr                 assemble from address ADR, set the file header address to ADR
 adr,adr2            assemble from address ADR, set the file header address to ADR2
 [b($ff,$fe)]        change header to $FFFE (2 bytes will be generated)
 [$ff,$fe],adr       change header to $FFFE, set the file header address to ADR
 [$d0,$fe],adr,adr2  change header to $D0FE, assemble from address ADR, set the file header address to ADR2
 [a($FFFA)],adr      SpartaDOS header $FAFF, set the file header address to ADR
```

```
 opt h-
 ORG [a($ffff),d'atari',c'ble',20,30,40],adr,adr2
```

Square brackets `[ ]` are used to specify a new header, which can be of any length. The remaining values after the closing square bracket `]`, separated by commas `,`, represent respectively: the assembly address and the address in the file header.

Example of a header for a single-block file assembled from address $2000, with the block's start and end addresses provided in the header.

```
 opt h-f+
 ORG [a(start), a(over-1)],$2000

start
 nop
 .ds 128
 nop
over
```

<a name="ins"></a>
### INS 'filename'["filename"][*][+-value][,+-ofset[,length]]

The `INS` pseudo-command allows including an additional binary file. The included file does not have to be in the same directory as the main assembly file. It is enough to have specified the search paths for **MADS** using the `/i` switch (see [Assembler Switches](usage.md#assembler-options)).

Additionally, the following operations can be performed on the included binary file:

```
*          invert the bytes of the binary file
+-VALUE    increase/decrease the byte values of the binary file by the value of the VALUE expression

+OFSET     skip OFFSET bytes from the beginning of the binary file (SEEK OFFSET)
-OFSET     read the binary file from its end (SEEK FileLength-OFFSET)

LENGTH     read LENGTH bytes of the binary file
```

If the `LENGTH` value is not specified, the binary file will be read until the end by default.

<a name="icl"></a>
### ICL 'filename'["filename"]

The `ICL` pseudo-command allows including an additional source file and assembling it. The included file does not have to be in the same directory as the main assembly file. It is enough to have specified the search paths for **MADS** using the `/i` switch (see [Assembler Switches](usage.md#assembler-options)).


### DTA

The `DTA` pseudo-command is used to define data of a specific type. If no type is specified, the `BYTE` (b) type is set by default.

```JavaScript
   b   BYTE value
   a   WORD value
   v   WORD value, relocatable
   l   low byte of the value (BYTE)
   h   high byte of the value (BYTE)
   m   highest byte of a LONG value (24-bit)
   g   highest byte of a DWORD value (32-bit)
   t   LONG value (24-bit)
   e   LONG value (24-bit)
   f   DWORD value (32-bit)
   r   DWORD value in reversed order (32-bit)
   c   ATASCII character string delimited by single '' or double "" quotes; a * character
       at the end will invert the string values, e.g., dta c'alphabet'*
   d   INTERNAL character string delimited by single '' or double "" quotes; a * character
       at the end will invert the string values, e.g., dta d'alphabet'*
```

```JavaScript
  dta 1 , 2, 4
  dta a ($2320 ,$4444)
  dta d'sasasa', 4,a ( 200 ), h($4000)
  dta  c  'file' , $9b
  dta c'invers'*
```

<a name="sin"></a>
### SIN (centre,amp,size[,first,last])

```
centre     is a number which is added to every sine value
amp        is the sine amplitude
size       is the sine period
first,last define range of values in the table. They are optional.
           Default are 0,size-1.
```

```
   dta a(sin(0,1000,256,0,63))
```
defines table of 64 words representing a quarter of sine with amplitude of 1000.


<a name="cos"></a>
### COS (centre,amp,size[,first,last])

```
centre     is a number which is added to every cosine value
amp        is the cosine amplitude
size       is the cosine period
first,last define range of values in the table. They are optional.
           Default are 0,size-1.
```

```
   dta a(cos(0,1000,256,0,63))
```
defines table of 64 words representing a quarter of cosine with amplitude of 1000.


<a name="rnd"></a>
### RND (min,max,length)
This pseudo-command allows generating LENGTH random values within the range <MIN..MAX>.

```
   dta b(rnd(0,33,256))
```

<a name="ift"></a>
<a name="els"></a>
<a name="eli"></a>
<a name="eif"></a>
### IFT, ELS, ELI, EIF

```
 IFT .IF expression
 ELS .ELSE
 ELI .ELSEIF expression
 EIF .ENDIF
```

The above pseudo-commands and directives affect the assembly process (they can be used interchangeably).
