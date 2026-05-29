# Declaration

### Procedure Declaration

The following directives apply to procedures:

```
 name .PROC [(.TYPE PAR1 .TYPE PAR2 ...)] [.REG] [.VAR]
 .PROC name [,address] [(.TYPE PAR1 .TYPE PAR2 ...)] [.REG] [.VAR]
 .ENDP [.PEND] [.END]
```

#### name .PROC [(.TYPE Par1,Par2 .TYPE Par3 ...)] [.REG] [.VAR]

Declaration of procedure `name` using the `.PROC` directive. The procedure name is required and mandatory; its absence will generate an error. Names of mnemonics and pseudo-instructions cannot be used as procedure names. If a name is reserved, an error with the message *Reserved word* will occur.

If we want to use one of the **MADS** mechanisms for passing parameters to procedures, we must declare them beforehand. The declaration of procedure parameters is enclosed in parentheses `( )`. Four parameter types are available:

 - .BYTE  (8-bit)  relocatable
 - .WORD  (16-bit) relocatable
 - .LONG  (24-bit) non-relocatable
 - .DWORD (32-bit) non-relocatable

> _In the current version of **MADS**, it is not possible to pass parameters using `.STRUCT` structures._

Immediately following the type declaration, separated by at least one space, is the parameter name. If declaring multiple parameters of the same type, their names can be separated by a comma `,`.

Example of a procedure declaration using the software stack:

```
name .PROC ( .WORD par1 .BYTE par2 )
name .PROC ( .BYTE par1,par2 .LONG par3 )
name .PROC ( .DWORD p1,p2,p3,p4,p5,p6,p7,p8 )
```

Additionally, by using the `.REG` or `.VAR` directives, we can specify the way and method of passing parameters to **MADS** procedures: via *CPU* registers (`.REG`) or via variables (`.VAR`). Directives specifying the parameter passing method are placed at the end of our `.PROC` procedure declaration.

Example of a procedure declaration using *CPU* registers:

```
name .PROC ( .BYTE x,y,a ) .REG
name .PROC ( .WORD xa .BYTE y ) .REG
name .PROC ( .LONG axy ) .REG
```

The `.REG` directive requires parameter names to consist of the letters `A`, `X`, `Y`, or combinations thereof. These letters correspond to the *CPU* registers and determine the order in which registers are used. The number of parameters that can be passed is limited by the number of *CPU* registers, meaning a total of at most 3 bytes can be passed to the procedure. The advantage of this method, however, is speed and low *RAM* usage.

Example of a procedure declaration using variables:

```
name .PROC ( .BYTE x1,x2,y1,y2 ) .VAR
name .PROC ( .WORD inputPointer, outputPointer ) .VAR
name .PROC ( .WORD src+1, dst+1 ) .VAR
```

For `.VAR`, the parameter names indicate the names of variables into which the passed parameters will be loaded. This method is slower than `.REG` but still faster than the software stack method.

You exit a procedure in the standard way, i.e., using the `RTS` instruction. Adding an `RTS` instruction within the procedure body at every exit path is the programmer's responsibility, not the assembler's.

As with a `.LOCAL` block, we can specify a new assembly address for a `.PROC` block, e.g.:

```
.PROC label,$8000
.ENDP

.PROC label2,$a000 (.word ax) .reg
.ENDP
```

For procedures utilizing the software stack, after the procedure ends with `.ENDP`, **MADS** calls the `@EXIT` macro, which is responsible for modifying the `@STACK_POINTER` software stack pointer. This is necessary for the software stack to function correctly. The user can design their own `@EXIT` macro or use the one included with **MADS** (file `..\EXAMPLES\MACROS\@EXIT.MAC`), which currently takes the following form:

```
.macro @EXIT

 ift :1<>0

  ift :1=1
   dec @stack_pointer

  eli :1=2
   dec @stack_pointer
   dec @stack_pointer

  els
   pha
   lda @stack_pointer
   sub #:1
   sta @stack_pointer
   pla

  eif

 eif

.endm
```

The `@EXIT` macro should not change the contents of *CPU* registers if we wish to retain the ability to return the result of the `.PROC` procedure via *CPU* registers.

#### .ENDP

The `.ENDP` directive ends the procedure block declaration.
