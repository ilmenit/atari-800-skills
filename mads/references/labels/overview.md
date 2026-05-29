# Overview

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
