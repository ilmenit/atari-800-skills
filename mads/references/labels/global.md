# Global

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

More information on using the `.DEF` directive in the chapter [.DEF Directive](../directives/symbols-vars.md#def)

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
