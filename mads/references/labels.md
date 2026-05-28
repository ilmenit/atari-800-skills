## Labels

 Labels defined in a program can have local or global scope, depending on where they were defined. Additionally, temporary labels can be defined, which can also have local or global scope.

* global scope of a label means it is visible from anywhere in the program, regardless of whether it is a `.MACRO`, a `.PROC` procedure, or a `.LOCAL` area.

* local scope of a label means it is visible only within a specifically defined area, e.g., defined by directives: `.MACRO`, `.PROC`, `.LOCAL`.

* labels must start with the character `'A'..'Z','a'..'z','_','?','@'`
* other allowed label characters are `'A'..'Z','a'..'z','0'..'9','_','?','@'`
* labels always occur at the beginning of a line
* labels preceded by "white space" should end with a `:` character to avoid misinterpretation of such a label as a macro
* in addressing, a label can be preceded by a `:` character; this informs the assembler that we are referring to a label in the main block of the program (we are referring to a global label)

Example of label definitions:

```
?nazwa   EQU  $A000    ; definition of a temporary global label
nazwa     =   *        ; definition of a global label
nazwa2=12              ; definition of a global label
@?nazwa  EQU  'a'+32   ; definition of a global label
  name: equ 12         ; definition of a global label not starting from the first character of the line
         nazwa: = 'v'  ; definition of a global label not starting from the first character of the line
```

Compared to **QA/XASM**, the possibility of using the question mark `?` and `@` in label names has been added.
Using a period `.` in a label name is allowed, but not recommended. The period character is reserved for marking mnemonic extensions, for designating assembler directives, and in addressing new **MADS** structures.

A period `.` at the beginning of a label name suggests it is an assembler directive, while a question mark `?` at the beginning of a label means a **temporary label**, one whose value can change multiple times during assembly.

### Anonymous

To ensure code clarity, the use of anonymous labels is limited only to conditional jumps and up to 10 occurrences forward/backward.

The `@` character has been reserved for anonymous labels; this character must be followed by a character specifying a jump forward `+` or backward `-`. Additionally, the occurrence number of the anonymous label in the range `[0..9]` can be specified; no occurrence number means `0` by default.

```
 @+[0..9]     ; forward
 @-[0..9]     ; backward

 @+           ; @+0
 @-           ; @-0

@ dex   ---- -------
  bne @+   |  --   |
  stx $80  |   |   |
@ lda #0   |  --   |
  bne @- ---       |
  bne @-1  ---------

  ldx #6
@ lda:cmp:req 20
@ dex
  bne @-1
```

### Local

Every label definition within a `.MACRO`, a `.PROC` procedure, or a `.LOCAL` area is local scope by default, in other words, it is local. The user does not need to additionally mark such labels.

Local labels are defined using the following equivalent pseudo-commands:

```
 EQU
  =
```

To access global scope labels (i.e., defined outside a `.MACRO`, `.PROC` procedure, or `.LOCAL` area) with the same names as local ones, use the `:` operator, e.g.:

```
lp   ldx #0         ; global label definition LP

     test
     test

test .macro

      lda :lp       ; the ':' character before the label will read the value of the global label LP

      sta lp+1      ; reference to the local label LP in the macro area
lp    lda #0        ; local label definition LP in the macro area

     .endm
```

In the example above, there are definitions of labels with the same names (LP), but each has a different value and different scope.

### Global

Every label definition made in the main program block outside a `.MACRO`, a `.PROC` procedure, or a `.LOCAL` area has global scope, in other words, it is global.

Global labels are defined using the following equivalent pseudo-commands:

```
 EQU
  =
```

or the `.DEF` directive with the syntax:

```
    .DEF :label [= expression]
```

The `.DEF` directive allows defining a label in the current local area, the `:` character at the beginning of the label signals a global label. Using the directive with the syntax `.DEF :label` allows defining a global label bypassing the current locality level.

The colon `:` character at the beginning of a label has a special meaning; it informs that we are referring to a global label, i.e., a label from the main program block bypassing all locality levels.

More information on using the `.DEF` directive in the chapter [.DEF Directive](#def)

Example of global label definitions:

```
lab equ *
   lab2 equ $4000

    ?tmp = 0
    ?tmp += 40

.proc name

      .def :?nazwa   = $A000
           .def :nazwa=20

      .local lok1
        .def :@?nazw   = 'a'+32
      .endl

.endp
```

An example of using a global temporary label definition is, among others, the `@CALL` macro, an example in the file `..\EXAMPLES\MACROS\@CALL.MAC`, which contains a definition of the temporary label `?@STACK_OFFSET`. It is later used by other macros called from within the `@CALL` macro, and it serves to optimize the program that puts parameters on the program stack.

```
@CALL .macro

  .def ?@stack_offset = 0    ; definition of a global temporary label ?@stack_offset

  ...
  ...


@CALL_@ .macro

  sta @stack_address+?@stack_offset,x
  .def ?@stack_offset = ?@stack_offset + 1    ; modification of the ?@stack_offset label

 .endm
```

### Temporary

A temporary label definition has the property that its value can change multiple times even during a single assembly pass. Normally, an attempt to redefine a label ends with the message _**Label declared twice**_. There will be no such message if it is a temporary label.

The scope of temporary labels depends on the area in which the label was defined. Temporary labels can have local scope ([Local labels](#local)) or global scope ([Global labels](#global)).

#### ?label

A temporary label is defined by the user by placing a question mark `?` at the beginning of the label name, e.g.:

    ?label

Temporary labels should not be used for names of `.PROC` procedures, `.MACRO` macros, `.LOCAL` areas, `.STRUCT` structures, or `.ARRAY` arrays.

Temporary labels are defined using the following equivalent pseudo-commands:

```
 EQU
  =
```

Additionally, they can be modified using operators known from **C**:

```
    -= expression
    += expression
    --
    ++
```

The above modifying operators apply only to temporary labels; attempting to use them for another type of label will end with an error message _**Improper syntax**_.

Example of using temporary labels:

```
?loc = $567
?loc2 = ?loc+$2000

     lda ?loc
     sta ?loc2

?loc = $123

     lda ?loc
```

#### label SET value

The [SET](#set) pseudo-command allows redefining a `LABEL`, it works with regular labels, i.e., those that do not have the `?` character as the first character in the name. Labels defined by `SET` cannot later be defined other than by `SET`.

```
 tmp set 1

 tmp = 2
```

For the above example, an **Infinite loop** will occur; it should correctly be:

```
 tmp set 1

 tmp set 2
```


### Self-modification

A label placed after a mnemonic and ending with a `:` character defines a code self-modification address.

```
  lda label:#$00

  add plus:#$00

  lda src:$ff00,y
  sta dst:$ff00,y
```

The above examples are equivalent to the code:

```
  lda #$00
label equ *-1

  add #$00
plus equ *-1

  lda $ff00,y
src equ *-2

  sta $ff00,y
dst equ *-2
```


### MAE-style Local

The `OPT ?+` option informs **MADS** to interpret labels starting with the `?` character as local labels, as **MAE** does. By default, labels starting with the `?` character are treated by **MADS** as temporary labels.

Example of using **MAE**-style local labels:

```
       opt ?+
       org $2000

local1 ldx #7
?lop   sta $a000,x
       dex
       bpl ?lop

local2 ldx #7
?lop   sta $b000,x
       dex
       bpl ?lop
