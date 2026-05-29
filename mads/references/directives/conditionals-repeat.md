# Conditionals Repeat

### .REPT expression [,parameter1, parameter2, ...]
The `.REPT` directive is an extension of `:repeat`, with the difference that it repeats a designated program block instead of a single line. The beginning of the block is defined by the `.REPT` directive, followed by a value or arithmetic expression specifying the number of repetitions in the range <0..2147483647>. After the number of repetitions, parameters may optionally occur. Unlike macros, parameters for `.REPT` are always evaluated first, and only then is their result substituted (this property can be used to define new labels). Parameters in a `.REPT` block are used similarly to parameters in a `.MACRO` block. The end of a `.REPT` block is defined by the `.ENDR` directive, before which no label should be placed.

Additionally, within the block marked by `.REPT` and `.ENDR`, you can use the hash character `#` (or the `.R` directive), which returns the current value of the `.REPT` loop counter (similar to `:repeat`).

```
 .rept 12, #*2, #*3        ; we can combine .REPT blocks with :rept
 :+4 dta :1                ; :+4 to distinguish the repetition counter from the parameter :4
 :+4 dta :2
 .endr

 .rept 9, #                ; we define 9 labels label0..label8
label:1 mva #0 $d012+#
 .endr
```

<a name="pages"></a>

### .IFDEF label
The `.IFDEF` directive is a shorter equivalent of the `.IF .DEF LABEL` condition.

```
.ifdef label
       jsr proc1
.else
       jsr proc2
.endif
```

<a name="ifndef"></a>

### .IFNDEF label
The `.IFNDEF` directive is a shorter equivalent of the `.IF .NOT .DEF LABEL` condition.

```
.ifndef label
      clc
.else
      sec
.endif
```

For the example below, assembly of the `.IFNDEF` (`.IF`) block will occur only in the first pass. If we place any program code within such a block, it will certainly not be generated into the file. Label definitions will be carried out only in the first pass; if any errors occurred related to their definition, we will only find out when attempting to reference such labels, resulting in the *Undeclared label LABEL_NAME* error message.

```
 .ifndef label
 .def label
 lda #0               ; this instruction will not be assembled; only the last assembly pass generates code
 temp = 100           ; the label TEMP will be defined only in the 1st assembly pass
 .endif
```

<a name="if_else"></a>

<a name="if-else"></a>

### .IF, .ELSE, .ELSEIF, .ENDIF

```
 .IF     [IFT] expression
 .ELSE   [ELS]
 .ELSEIF [ELI] expression
 .ENDIF  [EIF]
```

The above directives and pseudo-instructions affect the assembly process (they can be used interchangeably), e.g.:

```
 .IF .NOT .DEF label_name
   label_name = 1
 .ENDIF

 .IF [.NOT .DEF label_name] .AND [.NOT .DEF label_name2]
   label_name = 1
   label_name2 = 2
 .ENDIF
```

In the above example, parentheses (square or round) are a necessity; their absence would mean that for the first `.DEF` directive, the parameter would be the label name `label_name.AND.NOT.DEFlabel_name2` (spaces are ignored, and the dot character is accepted in label names).
