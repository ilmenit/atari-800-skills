# Symbols Vars

### .SYMBOL label
The `.SYMBOL` directive is the equivalent of the `SMB` pseudo-instruction, with the difference that you do not need to provide a symbol; the symbol is the `label`. The `.SYMBOL` directive can be placed anywhere within an **SDX** relocatable block (`BLK RELOC`), unlike `SMB`.

If the `.SYMBOL` directive occurs, a corresponding update block will be generated:

```
BLK UPDATE NEW LABEL 'LABEL'
```

More about SDX symbol declarations in the [Defining SMB symbols](../pseudo-commands/symbols-repeat.md#smb) chapter.


<a name="align"></a>

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
