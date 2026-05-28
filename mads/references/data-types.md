**MADS** provides the ability to declare two data types: structural `.STRUCT` and enumeration `.ENUM`.

## STRUCTURES

If you have programmed in **C**, you have probably encountered structures before. Generally, in **MADS**, a structure defines a virtual, one-dimensional array with fields of various types: `.BYTE`, `.WORD`, `.LONG`, `.DWORD`, and their multiples. It is virtual because it currently exists only in the assembler's memory.

The fields of such a structure contain information about the offset from the beginning of the structure.

### `.STRUCT` Declaration

The following directives apply to structures:

```
name .STRUCT
     .STRUCT name
     .ENDS [.SEND] [.END]
```

* `name .STRUCT`

Declaration of a structure `name` using the `.STRUCT` directive. The structure name is mandatory; its absence will trigger an error. CPU mnemonics and pseudo-commands cannot be used as structure names. If a name is reserved, an error with the message **Reserved word** will occur.

---

Example of a structure declaration:

```
.STRUCT name

  x .word      ; lda #name.x = 0
  y .word      ; lda #name.y = 2
  z .long      ; lda #name.z = 4
  v .dword     ; lda #name.v = 7

  q :3 .byte   ; lda #name.q = 11

.ENDS          ; lda #name   = 14 (length)
```

Structure fields are defined by providing a name and a field type: `.BYTE`, `.WORD`, `.LONG`, `.DWORD`. The field name can be preceded by whitespace. In the area delimited by `.STRUCT` and `.ENDS` directives, it is not possible to use *CPU* mnemonics. If used, or if other disallowed characters are used, an error with the message **Improper syntax** or **Illegal instruction** will occur.

In summary, the `name` label contains information about the total length of the structure (in bytes). The other labels describing the fields contain information about the offset from the beginning of the structure.
Structure declarations cannot be nested, but previously declared structures can be nested (the order of occurrence in the program does not matter), e.g.:

```
.STRUCT temp

x .word
y .word
v .byte
z .word

.ENDS


.STRUCT test

tmp  temp

.ENDS

 lda #temp.v
 lda #test.tmp.x
 lda #test.tmp.z
```

What can a structure be useful for?

Suppose we have an array with fields of different types; we can read the fields of such an array using predefined offset values. However, if we add an extra field to the array or modify it in another way, we will be forced to correct the program code that used the predefined offset values. When we define such an array using a structure, we will be able to read its fields using the offsets stored in the structure declaration, meaning we will always read the correct field regardless of changes made to the array.

Another example of using structures is described in the *External Symbols* chapter, in the example of using external symbols and `.STRUCT` structures.

### Definition (References)

Defining structural data consists of assigning a specific structure to a new label using the `DTA` pseudo-command or without it. The result of such an assignment is reserved memory; it is no longer a virtual entity.

```
label DTA struct_name [count] (data1,data2,data3...) (data1,data2,data3...) ...

label struct_name
```

`COUNT` specifies a value in the range `0..COUNT`, which defines the maximum index value of a one-dimensional array, and thus the number of structural data items stored in memory.
Example of structure declaration and structural data definition:

```
;----------------------;
; structure declaration;
;----------------------;
.STRUCT temp

x .word
y .word
v .byte
z .word

.ENDS

;---------------------;
; data definition     ;
;---------------------;

data dta temp [12] (1,20,200,32000) (19,2,122,42700)

data2 dta temp [0]

data3 temp          // shorter equivalent of DATA2
```

The structure name must be followed by a value in square brackets in the range `0..2147483647`, which defines the maximum index value of a one-dimensional array and the number of structural data items stored in memory.

The square brackets can optionally be followed by a list of initial values (delimited by parentheses). If it is not present, the default field values of the structure are zero. If the list of initial values is smaller than the number of declared fields, the remaining fields are initialized with the last value provided, e.g.

    data dta temp [12] (1,20,200,32000)

Such a declaration will cause all fields to be initialized with the values `1, 20, 200, 32000`, not just the first `data[0]` field.

If the list of initial values is larger or smaller than the number of structure fields, an error with the message **Constant expression violates subrange bounds** will occur.

To reference the fields of newly created data, you must provide their name, followed by an index in square brackets and the field name after a dot, e.g.:

    lda data[4].y
    ldx #data[0].v

Missing square brackets with an index `label[index]` will result in the error message **Undeclared label**.

## ENUMERATIONS

The following directives apply to enumerations:

```
name .ENUM
     .ENDE [.EEND] [.END]

Example:

.enum portb
 rom_off = $fe
 rom_on = $ff
.ende

.enum test
 a             ; a=0
 b             ; b=1
 c = 5         ; c=5
 d             ; d=6
.ende
```

An enumeration is declared using the `.ENUM` and `.ENDE` directives. The enumeration name is mandatory; its absence will trigger an error. CPU mnemonics and pseudo-commands cannot be used as enumeration names. If a name is reserved, an error with the message **Reserved word** will occur.

The values of subsequent labels are automatically incremented by 1, starting from the default value of `0`. Label values can be defined manually or left to the automatic mechanism.

Enumeration labels are referenced using the following syntax:

    enum_name (field)

or directly, similar to references for `.LOCAL` and `.PROC` blocks, where field names follow the type name separated by a dot, e.g.:

```
lda #portb(rom_off)

dta portb.rom_on, portb.rom_off
```

Enumerations can be used to declare `.STRUCT` fields or to allocate variables with the `.VAR` directive, e.g.:

```
bank portb           // allocation of a 1-byte variable BANK
.var bank portb      // allocation of a 1-byte variable BANK

.struct test
 a portb
 b portb
.ends
```

The size of an enumeration variable depends on the maximum value of its labels, e.g.:

```
.enum EState
    DONE, DIRECTORY_SEARCH=$ff, INIT_LOADING, LOADING
.ende
```

In the above example, the allocation of an `EState` variable will be two bytes (`WORD`).

The size can be checked using the `.LEN` or `.SIZEOF` directive; the result will be a value from `1` to `4` (1 **BYTE**, 2 **WORD**, 3 **LONG**, 4 **DWORD**), e.g.:

    .print .len EState
