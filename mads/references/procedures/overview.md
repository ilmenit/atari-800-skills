# Overview

## Procedures

**MADS** introduces new capabilities for handling procedures with parameters. These new features make the mechanism similar to those known from high-level languages and are just as easy for the programmer to use.

The macro declarations currently included with **MADS** (`@CALL.MAC`, `@PULL.MAC`, `@EXIT.MAC`) enable support for a software stack of 256 bytes—the same size as the hardware stack. They provide a mechanism for pulling parameters from and pushing parameters to the software stack as required during procedure calls and exits. **MADS** accounts for the possibility of recursion for such procedures.

The programmer is not involved in this mechanism and can focus on their program. They only need to remember to define the appropriate labels and include the relevant macros during program assembly.

Additionally, it is possible to bypass the **MADS** software stack 'mechanism' and use the classic method of passing parameters via *CPU* registers (using the `.REG` directive) or through variables (using the `.VAR` directive).

Another property of `.PROC` procedures is the ability to omit them during assembly if no reference to them has occurred—i.e., they are defined but not used. In such cases, an *Unreferenced procedure ????* warning message will appear. Omitting such a procedure during assembly is possible by passing the `-x 'Exclude unreferenced procedures'` parameter to **MADS** on the command line.

Any labels defined within the `.PROC` procedure scope are local. They can also be considered globally defined local labels with free access, as they can be referenced from outside—which is not typical in other programming languages.

Within the .PROC procedure area, it is possible to define labels with global scope (see the [Global labels](../labels/global.md#global) chapter).

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
