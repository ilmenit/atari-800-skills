# Declaration

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
