## Procedures

**MADS** introduces new capabilities for handling procedures with parameters. These new features make the mechanism similar to those known from high-level languages and are just as easy for the programmer to use.

The macro declarations currently included with **MADS** (`@CALL.MAC`, `@PULL.MAC`, `@EXIT.MAC`) enable support for a software stack of 256 bytes—the same size as the hardware stack. They provide a mechanism for pulling parameters from and pushing parameters to the software stack as required during procedure calls and exits. **MADS** accounts for the possibility of recursion for such procedures.

The programmer is not involved in this mechanism and can focus on their program. They only need to remember to define the appropriate labels and include the relevant macros during program assembly.

Additionally, it is possible to bypass the **MADS** software stack 'mechanism' and use the classic method of passing parameters via *CPU* registers (using the `.REG` directive) or through variables (using the `.VAR` directive).

Another property of `.PROC` procedures is the ability to omit them during assembly if no reference to them has occurred—i.e., they are defined but not used. In such cases, an *Unreferenced procedure ????* warning message will appear. Omitting such a procedure during assembly is possible by passing the `-x 'Exclude unreferenced procedures'` parameter to **MADS** on the command line.

Any labels defined within the `.PROC` procedure scope are local. They can also be considered globally defined local labels with free access, as they can be referenced from outside—which is not typical in other programming languages.

Within the .PROC procedure area, it is possible to define labels with global scope (see the [Global labels](labels.md#global) chapter).

If you want to access labels defined within a procedure from outside the procedure scope, you address them using the dot character `.`, e.g.:

```
 lda test.pole

.proc test

pole nop

.endp
```

If a label sought by the assembler does not occur within the `.PROC` procedure scope, **MADS** will search for it in lower scopes until it reaches the global scope. To immediately read the value of a global label from within a `.PROC` procedure (or any other local area), precede the label name with a colon `:`.

**MADS** requires for procedures using the software stack, three global label definitions with specific names (stack address, stack pointer, procedure parameters address):

 - @PROC_VARS_ADR
 - @STACK_ADDRESS
 - @STACK_POINTER

Failure to define the above labels while attempting to use a `.PROC` block that utilizes the software stack will cause **MADS** to assume its default values for these labels: `@PROC_VARS_ADR = $0500`, `@STACK_ADDRESS = $0600`, `@STACK_POINTER = $FE`

For procedures using the software stack, **MADS** also requires macro declarations with specific names. The declarations for these macros included with **MADS** can be found in the following files:

 - @CALL    ..\EXAMPLES\MACROS\@CALL.MAC
 - @PUSH    ..\EXAMPLES\MACROS\@CALL.MAC
 - @PULL    ..\EXAMPLES\MACROS\@PULL.MAC
 - @EXIT    ..\EXAMPLES\MACROS\@EXIT.MAC

The aforementioned macros handle passing and pushing parameters onto the software stack, as well as pulling and pushing parameters for procedures using the software stack that are called from within other procedures also using the software stack.


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


### Procedure Call

A procedure is called by its name (just like a macro), followed by parameters separated by a comma `,` or a space `' '` (no other separators can be declared).

If the parameter type does not match the type declared in the procedure declaration, an *Incompatible types* error message will occur.

If the number of passed parameters differs from the number of parameters declared in the procedure declaration, an *Improper number of actual parameters* error message will occur. An exception is a procedure where parameters are passed via *CPU* registers (`.REG`) or variables (`.VAR`); in such cases, parameters can be omitted, as they are assumed to be already loaded into the appropriate registers or variables.

Three ways of passing a parameter are possible:

- '#' by value
- ' ' by value from an address (without a preceding character)
- '@' via the accumulator (for `.BYTE` type parameters)
- "string" via a character string, e.g., "label,x"

Example of a procedure call:

```
 name @ , #$166 , $A400  ; for the software stack
 name , @ , #$3f         ; for .REG or .VAR
 name "(hlp),y" "tab,y"	 ; for .VAR or for the software stack (the software stack uses regX)
```

Upon encountering a call to a procedure that uses the software stack, **MADS** forces the execution of the `@CALL` macro. However, if the procedure does not use the software stack, a standard `JSR PROCEDURE` instruction will be generated instead of the `@CALL` macro.

**MADS** passes parameters to the `@CALL` macro calculated based on the procedure declaration (it breaks each parameter down into three components: addressing mode, parameter type, and parameter value).

```
@CALL_INIT 3\ @PUSH_INIT 3\ @CALL '@','B',0\ @CALL '#','W',358\ @CALL ' ',W,"$A400"\ @CALL_END PROC_NAME
```

The `@CALL` macro will push the accumulator's contents onto the stack, followed by the value `$166` (358 decimal), and then the value from address `$A400`. For more information on passing parameters to macros (and the meaning of single `' '` and double `" "` quotes), see the [Macro call](macros.md#macro-call) chapter.

A parameter passed via the accumulator `@` should always be the first parameter passed to the procedure; if it appears elsewhere, the accumulator's contents will be modified (the default `@CALL` macro imposes this limitation). Of course, the user can change this by writing their own version of the `@CALL` macro. In the case of `.REG` or `.VAR` procedures, the order of the `@` parameter does not matter.

Exit from a `.PROC` procedure occurs via the `RTS` instruction. Upon returning from the procedure, **MADS** calls the `@EXIT` macro, which contains code to modify the `@STACK_POINTER` stack pointer; this is essential for the software stack to function correctly. The number of bytes passed to the procedure is subtracted from the stack pointer; this byte count is passed to the macro as a parameter.

Adding an `RTS` instruction within the procedure body at every exit path is the programmer's responsibility, not the assembler's.


### Procedure Parameters

Referencing procedure parameters from within the procedure does not require additional actions from the programmer, e.g.:

```
@stack_address equ $400
@stack_pointer equ $ff
@proc_vars_adr equ $80

name .PROC (.WORD par1,par2)

 lda par1
 clc
 adc par2
 sta par1

 lda par1+1
 adc par2+1
 sta par1+1

.endp

 icl '@call.mac'
 icl '@pull.mac'
 icl '@exit.mac'
```

Upon encountering a `.PROC` declaration with parameters, **MADS** automatically defines these parameters, assigning them values based on `@PROC_VARS_ADR`. In the example above, **MADS** will automatically define parameters `PAR1 = @PROC_VARS_ADR` and `PAR2 = @PROC_VARS_ADR + 2`.

The programmer references these parameters by the name given in the procedure declaration, similar to high-level languages. In **MADS**, it is possible to access procedure parameters from outside the procedure, which is not typical in high-level languages. From the example above, we can read the contents of `PAR1`, e.g.:

```
 lda name.par1
 sta $a000
 lda name.par1+1
 sta $a000+1
```

The value of `PAR1` has been copied to address `$A000`, and the value of `PAR1+1` to address `$A000+1`. Of course, this can only be done immediately after that specific procedure finishes. Keep in mind that parameters for such procedures are stored at the common address `@PROC_VARS_ADR`, so with each new call to a procedure utilizing the software stack, the contents of the area `<@PROC_VARS_ADR .. @PROC_VARS_ADR + $FF>` change.

If a procedure has parameters declared as type `.REG`, the programmer should ensure they are saved or properly utilized before being modified by the procedure code. For parameters of type `.VAR`, there is no cause for concern, as parameters are saved to specific memory cells from which they can always be read.
