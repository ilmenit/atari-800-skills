## Macros

Macros make it easier for us to perform repetitive tasks by automating them. They exist only in the assembler's memory and are assembled only at the time of invocation. With their help, **MADS** can push and pull parameters for procedures declared with the `.PROC` directive onto/from the software stack, and switch extended memory banks in *BANK SENSITIVE* mode (`OPT B+`).

> _Macros are read only in the first assembly pass; for the example below, macros located in a file included via `ICL` will not be recognized_:

```
 .macro test
   icl 'additional_macros.mac'
 .endm
```

### Macro Declaration
The following pseudo-instructions and directives apply to macros:

```
name .MACRO [arg1, arg2 ...] ['separator'] ["separator"]
     .MACRO name [(arg1, arg2 ...)] ['separator'] ["separator"]
     .EXITM [.EXIT]
     .ENDM [.MEND]
     :[%%]parameter
     :[%%]label
```

#### name .MACRO [(arg1, arg2 ...)] ['separator'] ["separator"]

Declaration of a macro named `name` using the `.MACRO` directive. The macro name is required and mandatory; its absence will generate an error. Names of mnemonics and pseudo-instructions cannot be used as macro names (error _**Reserved word**_).

A list of labels for the names of arguments to be passed to the macro is allowed; such a list can additionally be enclosed in parentheses `( )`. Presenting arguments as label names is intended to improve the clarity of the macro code. Within the macro body itself, argument label names or their numerical equivalents can be used interchangeably.

```
.macro SetColor val,reg
 lda :val
 sta :reg
.endm
```

At the end of the macro declaration, a separator declaration and simultaneously the mode for passing parameters to the macro can occur (single quote for no change, double quote for splitting parameters into addressing mode and argument).
The default separator for parameters passed to the macro is the comma `,` and space `' '`.

```
name .MACRO 'separator'
```

Between single quotes `' '`, we can place a separator character that will be used to separate parameters when calling the macro (single quotes can only serve this purpose).

```
name .MACRO "separator"
```

Between double quotes `" "`, we can also place a separator character that will be used to separate parameters when calling the macro. Additionally, the use of double quotes signals **MADS** to split the passed parameters into two elements: addressing mode and argument, e.g.:

```
 test #12 200 <30

test .macro " "
.endm
```

The `TEST` macro has a space separator declared using the `"` quote, meaning that after calling the macro, the parameters will be split into two elements: addressing mode and argument.

```
 #12   ->  addressing mode '#' argument 12
 200   ->  addressing mode ' ' argument 200
 <30   ->  addressing mode '#' argument 0   (calculated value of the expression "<30")

 test '#' 12 ' ' 200 '#' 0
```

NOTE #1: Parameters with the operator sign `<`, `>` are calculated and only then is their result passed to the macro (substituted for the parameter).

NOTE #2: If the macro parameter is the loop counter `#`, `.R` (!!! single character `#` or directive `.R`, not an expression involving this character or directive !!!), then the value of the loop counter is passed to the macro (substituted for the parameter).

This property can be used to create "self-writing" code when we need to create new labels like "label0", "label1", "label2", "label3" ... etc., e.g.:

```
 :32 find #

find .macro
      ift .def label:1
      dta a(label:1)
      eif
     .endm
```

The above example saves the label address provided that such a label exists (has been defined).


#### .EXITM [.EXIT]
Termination of macro execution. Causes absolute termination of macro execution.

#### .ENDM [.MEND]
Using the `.ENDM` or `.MEND` directive, we end the current macro declaration. It is not possible to use the `.END` directive as is the case for other areas declared by the directives `.LOCAL`, `.PROC`, `.ARRAY`, `.STRUCT`, `.REPT`.

#### :[%%]parameter

A parameter is a positive decimal number (`>=0`), preceded by a colon `:` or two percent signs `%%`. If in a macro we want the `:` character to specify the number of repetitions and not the parameter number, it is sufficient that the character following the colon is not in the range `'0'..'9'`, but for example:

```
 :$2 nop
 :+2 nop
 :%10 nop
```

The parameter `:0` (`%%0`) has a special meaning; it contains the number of passed parameters. With its help, we can check if the required number of parameters has been passed to the macro, e.g.:

```
  .IF :0<2 || :0>5
    .ERROR "Wrong number of arguments"
  .ENDIF

  IFT %%0<2 .or :0>5
    ERT "Wrong number of arguments"
  EIF
```

Macro example:

```
.macro load_word

   lda <:1
   sta :2
   lda >:1
   sta :2+1
 .endm

 test ne
 test eq

.macro test
  b%%1 skip
.endm
```


### Macro Call

A macro is called by its name, followed by the macro parameters, separated by a separator which is by default a comma `,` or a space `' '`.

The number of parameters depends on the available memory of the *PC*. If the number of passed parameters is less than the number of parameters used in a given macro, the value `-1` (`$FFFFFFFF`) will be substituted for the missing parameters. This property can be used to check whether a parameter was passed or not, but it is easier to do this using the zero parameter `%%0`.

```
 macro_name [Par1, Par2, Par3, 'Par4', "string1", "string2" ...]
```

A parameter can be a value, an expression, or a character string enclosed in single quotes `' '` or double quotes `" "`.

* single quotes `' '` will be passed to the macro along with the characters between them
* double quotes `" "` denote a character string and only the character string between the quotes will be passed to the macro

Any label definitions within a macro have local scope.

If a label sought by the assembler does not occur within the macro area, it will be searched for in the local area (if the `.LOCAL` directive occurred), then in the procedure (if a procedure is currently being processed), and finally in the main program.

Example of a macro call:

```
 macro_name 'a',a,>$a000,cmp    ; for the default separator ','
 macro_name 'a'_a_>$a000_cmp    ; for a declared separator '_'
 macro_name 'a' a >$a000 cmp    ; for the default separator ' '
```

It is possible to call macros from within a macro, and to call macros recursively. In the latter case, caution is advised as it may lead to a **MADS** stack overflow. **MADS** protects against infinite macro recursion and stops assembly when the number of macro calls exceeds 4095 (error _**Infinite recursion**_).

Example of a macro that will cause a **MADS** stack overflow:

```
jump .macro

      jump

     .endm
```

Example of a program that passes parameters to pseudo-procedures `..\EXAMPLES\MACRO.ASM`:

```
 org $2000

 proc PutChar,'a'-64    ; calling the PROC macro as a parameter
 proc PutChar,'a'-64    ; name of the procedure that will be called via JSR
 proc PutChar,'r'-64    ; and one argument (INTERNAL character code)
 proc PutChar,'e'-64
 proc PutChar,'a'-64

 proc Kolor,$23         ; calling another small procedure that changes background color

;---

loop jmp loop           ; infinite loop to see the effect

;---

proc .macro             ; declaration of the PROC macro
 push =:1,:2,:3,:4      ; calling the PUSH macro which pushes arguments onto the stack
                        ; =:1 calculates the memory bank

 jsr :1                 ; jump to procedure (procedure name in the first parameter)

 lmb #0                 ; Load Memory Bank, sets the bank to value 0
 .endm                  ; end of PROC macro

;---

push .macro             ; declaration of the PUSH macro

  lmb #:1               ; sets the virtual memory bank

 .if :2<=$FFFF          ; if the passed argument is less than or equal to $FFFF then
  lda <:2               ; push it onto the stack
  sta stack
  lda >:2
  sta stack+1
 .endif

 .if :3<=$FFFF
  lda <:3
  sta stack+2
  lda >:3
  sta stack+3
 .endif

 .if :4<=$FFFF
  lda <:4
  sta stack+4
  lda >:4
  sta stack+5
 .endif

 .endm


* ------------ *            ; KOLOR procedure
*  PROC Kolor  *
* ------------ *
 lmb #1                     ; setting the virtual bank number to 1
                            ; all label definitions will now belong to this bank
stack org *+256             ; stack for the KOLOR procedure
color equ stack

Kolor                       ; KOLOR procedure code
 lda color
 sta 712
 rts


* -------------- *          ; PUTCHAR procedure
*  PROC PutChar  *
* -------------- *
 lmb #2                     ; setting the virtual bank number to 2
                            ; all label definitions will now belong to this bank
stack org *+256             ; stack for the PUTCHAR procedure
char  equ stack

PutChar                     ; PUTCHAR procedure code
 lda char
 sta $bc40
scr equ *-2

 inc scr
 rts
```

Of course, the stack in this example program is a software stack. In the case of *65816*, the hardware stack could be used. Because the defined variables are assigned to a specific bank number, a procedure or function call structure similar to those in high-level languages can be created.

However, it is simpler and more efficient to use the `.PROC` procedure declaration that **MADS** enables. More about procedure declarations and operations related to them in the [Procedures] chapter.
