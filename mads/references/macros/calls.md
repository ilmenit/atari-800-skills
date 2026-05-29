# Calls

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
