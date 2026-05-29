# Data Storage

### .END
The `.END` directive can be used interchangeably with the directives `.ENDP`, `.ENDM`, `.ENDS`, `.ENDA`, `.ENDL`, `.ENDR`, `.ENDPG`, `.ENDW`, and `.ENDT`.


<a name="var"></a>

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
