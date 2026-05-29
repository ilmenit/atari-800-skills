# Origin Include Data

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

The `INS` pseudo-command allows including an additional binary file. The included file does not have to be in the same directory as the main assembly file. It is enough to have specified the search paths for **MADS** using the `/i` switch (see [Assembler Switches](../usage.md#assembler-options)).

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

The `ICL` pseudo-command allows including an additional source file and assembling it. The included file does not have to be in the same directory as the main assembly file. It is enough to have specified the search paths for **MADS** using the `/i` switch (see [Assembler Switches](../usage.md#assembler-options)).

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
