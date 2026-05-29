# Calls

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

The `@CALL` macro will push the accumulator's contents onto the stack, followed by the value `$166` (358 decimal), and then the value from address `$A400`. For more information on passing parameters to macros (and the meaning of single `' '` and double `" "` quotes), see the [Macro call](../macros/calls.md#macro-call) chapter.

A parameter passed via the accumulator `@` should always be the first parameter passed to the procedure; if it appears elsewhere, the accumulator's contents will be modified (the default `@CALL` macro imposes this limitation). Of course, the user can change this by writing their own version of the `@CALL` macro. In the case of `.REG` or `.VAR` procedures, the order of the `@` parameter does not matter.

Exit from a `.PROC` procedure occurs via the `RTS` instruction. Upon returning from the procedure, **MADS** calls the `@EXIT` macro, which contains code to modify the `@STACK_POINTER` stack pointer; this is essential for the software stack to function correctly. The number of bytes passed to the procedure is subtracted from the stack pointer; this byte count is passed to the macro as a parameter.

Adding an `RTS` instruction within the procedure body at every exit path is the programmer's responsibility, not the assembler's.
