## 6502 Code Generation Directives

 [#IF type expression [.OR type expression] [.AND type expression]](#d_if)<br>
 [#ELSE](#d_if)<br>
 [#END](#d_if)<br>

 [#WHILE type expression [.OR type expression] [.AND type expression]](#d_while)<br>
 [#END](#d_while)<br>

 [#CYCLE #N](#d_cycle)

<a name="d_if"></a>
### #IF type expression [.OR type expression] [.AND type expression]

The `#IF` directive is a modest equivalent of the `IF` statement found in high-level languages (**C**, **Pascal**).

The `#IF`, `#ELSE`, and `#END` directives allow for generating *CPU 6502* machine code for an `IF` conditional statement for a designated program block; nesting is possible.

All types `.BYTE`, `.WORD`, `.LONG`, and `.DWORD` are allowed. Multiple conditions can be combined using the `.OR` and `.AND` directives; however, it is not possible to specify evaluation order using parentheses.

Execution of the `#IF` directive begins with evaluating a simple expression, i.e., one consisting of two arguments and one operator (expressions can be combined using `.OR` or `.AND` directives).

If the expression evaluates to non-zero (`TRUE`), the program block following the `#IF` directive is executed. Such a program block is automatically terminated with a `JMP` instruction that jumps to the next instruction after the `#END` directive if an `#ELSE` block is present.

If the expression evaluates to zero (`FALSE`), the code following the `#ELSE` directive is executed. If the `#ELSE` directive is absent, control is passed to the next instruction after the `#END` directive, e.g.:

```JavaScript
#if .byte label>#10 .or .byte label<#5
#end

#if .byte label>#100

#else

 #if .byte label<#200
 #end

#end

#if .byte label>#100 .and .byte label<#200 .or .word lab=temp
#end

#if .byte @
#end
```

<a name="d_while"></a>
### #WHILE type expression [.OR type expression] [.AND type expression]

The `#WHILE` directive is the equivalent of the `WHILE` statement in high-level languages (**C**, **Pascal**).

The `#WHILE` and `#END` directives allow for generating *CPU 6502* machine code for a loop for a designated program block; nesting is possible.

All types `.BYTE`, `.WORD`, `.LONG`, and `.DWORD` are allowed. Multiple conditions can be combined using the `.OR` and `.AND` directives; however, it is not possible to specify evaluation order using parentheses.

The sequence of actions when executing the `#WHILE` directive is as follows:

1. Evaluate the expression and check if it is zero (`FALSE`).
	- if so, skip step 2;
	- if not (`TRUE`), go to step 2.
2. Execute the program block bounded by the `#WHILE` and `#END` directives, then return to step 1.

If the initial evaluation of the expression shows it is zero, the program block will never be executed, and control will pass to the next instruction after the `#END` directive.

```JavaScript
#while .byte label>#10 .or .byte label<#5
#end

#while .byte label>#100
 #while .byte label2<#200
 #end
#end

#while .byte label>#100 .and .byte label<#200 .or .word lab=temp
#end
```

Short version of the `#WHILE` loop, continues as long as `LABEL<>0`

```
#while .word label
#end
```

<a name="d_cycle"></a>
### #CYCLE #N

The `#CYCLE` directive allows for generating *6502* code with a specified number of cycles. The generated code does not modify any memory cell or CPU register, only flags at most.

```JavaScript
#cycle #17  ; pha      3 cycle
            ; pla      4 cycle
            ; pha      3 cycle
            ; pla      4 cycle
            ; cmp $00  3 cycle
                      ---------
                      17 cycle
```
