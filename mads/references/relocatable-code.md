# Relocatable Code

## Introduction

Relocatable code is code that does not have a predefined loading address in computer memory; such code must function correctly regardless of the address it's loaded into. In **Atari XE/XL**, relocatable code is provided by the **Sparta DOS X** (**SDX**) system; more on this can be found in the *Sparta DOS X - Programming* chapter.

Relocatable code for **SDX** has a basic limitation: only `WORD` type addresses can be relocated, and there is no support for *CPU 65816* instructions. **MADS** provides the ability to generate relocatable code in both the **SDX** format and its own format, which is incompatible with **SDX** but removes the aforementioned limitations.

The file format for **MADS** relocatable code is similar to the one known from **SDX**, also featuring a main block and additional blocks containing information about the addresses to be relocated. MADS uses a simpler record for update blocks, without the *compression* used by **SDX**.

Advantages of **MADS** relocatable code:

* takes into account argument sizes for *CPU 6502* and *65816*
* all *CPU* instructions can be used without limitations
* allows relocation of both low and high bytes of an address

Limitations of **MADS** relocatable code:

* label declarations via `EQU` must be made before the `.RELOC` block
* if you want to define a new label within the `.RELOC` block, its name must be preceded by a space or tab (global label)
* pseudo-commands `ORG`, `RMB`, `LMB`, `NMB`, and the `.DS` directive cannot be used
* the highest byte of a 24-bit word cannot be relocated, e.g., `lda ^$121416`

An example of how easily relocatable code can be created is the `..\EXAMPLES\TETRIS_RELOC.ASM` file, which, in terms of the *CPU* instructions and data-defining pseudo-commands used, is no different from the non-relocatable version `..\EXAMPLES\TETRIS.ASM`.

## Relocatable Block .RELOC

A **MADS** relocatable block will be generated after using the directive:

    .RELOC [.BYTE|.WORD]

The update block for a **MADS** relocatable block is called using the `BLK` pseudo-command:

    BLK UPDATE ADDRESS

After the `.RELOC` directive, it is possible to specify the relocatable block type as `.BYTE` or `.WORD`; the default is `.WORD`. The `.BYTE` type applies to a block intended to be placed exclusively on the zero page (it will contain zero-page instructions), and **MADS** will assemble such a block starting from address `$0000`. The `.WORD` type means **MADS** will assemble the relocatable block starting from address `$0100`, and it is intended to be placed in any memory area (it will not contain zero-page instructions).

The header of the `.RELOC` block resembles the one known from **DOS**, but it has been extended by 10 new bytes, totaling 16 bytes, e.g.:

```
HEADER            .WORD = $FFFF
START_ADDRESS     .WORD = $0000
END_ADDRESS       .WORD = FILE_LENGTH-1
MADS_RELOC_HEADER .WORD = $524D
UNUSED            .BYTE = $00
CONFIG            .BYTE (bit0)
@STACK_POINTER    .WORD
@STACK_ADDRESS    .WORD
@PROC_VARS_ADR    .WORD
```

* `MADS_RELOC_HEADER`

Always with the value `$524D`, which corresponds to the characters `MR` (M-ADS R-ELOC).

* `FILE_LENGTH`

The length of the relocatable block without the 16-byte header.

* `CONFIG`

Currently only `bit0` of this byte is used; `bit0=0` means the relocatable block is assembled from address `$0000`, and `bit0=1` means it is assembled from address `$0100`.

---

The last 6 bytes contain information about the label values required for the software stack's operation: `@STACK_POINTER`, `@STACK_ADDRESS`, and `@PROC_VARS_ADR`, if they were used during the assembly of relocatable blocks. If individual `.RELOC` blocks were assembled with different values for these labels and they are linked, an **Incompatible stack parameters** warning will occur. If the software stack was not used, the values of these labels will be zero.

The `.RELOC` pseudo-command switches **MADS** to relocatable code generation mode, taking into account the argument sizes for *CPU 6502* and *65816*. Within such code, it is impossible to use pseudo-commands `ORG`, `LMB`, `NMB`, `RMB`, and the `.DS` directive. It is impossible to return **MADS** to non-relocatable code generation mode; however, more than one `.RELOC` block can be generated.

Using the `.RELOC` directive also increments the **MADS** virtual bank counter, making the area local and invisible to other blocks. More information about virtual banks can be found in the Virtual Memory Banks `OPT B-` chapter.

At the end of the `.RELOC` block, an update block must be generated; this is done using the `BLK` pseudo-command with the same syntax as for the **SDX** relocatable block (**BLK UPDATE ADDRESS**). However, the format of this update block is not identical to **SDX**; it has the following form:

```
HEADER       WORD ($FFEF)
TYPE         CHAR (B-YTE, W-ORD, L-ONG, D-WORD, <, >)
DATA_LENGTH  WORD
DATA         WORD [BYTE]
```

* `HEADER`

Always with the value `$FFEF`.

* `TYPE`

The data type is stored in bits `0..6` of this byte and specifies the type of modified addresses; the `<` sign means the low byte of the address, and the `>` sign means the high byte.

* `DATA_LENGTH`

The number of 2-byte data entries (addresses) to be modified.

* `DATA`

The actual sequence of data used to modify the main relocatable block. At the address specified here, the value of type `TYPE` must be read and then modified based on the new loading address.

---

An exception is the update block for high bytes of addresses (`>`); for such a block, an additional `BYTE` (the low byte of the modified address) is also stored in `DATA`. To update the high bytes, we must read the byte from the `WORD` address in `DATA`, add it to the current relocation address, and also add the low byte from `BYTE` in `DATA`. The newly calculated high byte is then placed at the `WORD` address from `DATA`.

## External Symbols

External symbols indicate that the variables and procedures they represent will be located somewhere outside the current program. We do not need to specify where. We only need to provide their names and types. Depending on the type of data the symbol represents, assembler instructions are translated into the appropriate machine code; the assembler must know the size of the data used.

> **NOTE:**
> _Currently, it is not possible to perform operations on external symbols of type `^` (highest byte)._

External symbols can be used in `.RELOC` relocatable blocks as well as in standard **DOS** blocks.

External symbols are declared using the `EXT` pseudo-command or the `.EXTRN` directive:

```
label EXT type
label .EXTRN type
.EXTRN label1,label2,label3... type
```

The update block for **external** symbols is called using the `BLK` pseudo-command:

    BLK UPDATE EXTERNAL

> **NOTE:**
> _Only symbols used in the program will be saved._

External symbols do not have a defined value, only a type: `.BYTE`, `.WORD`, `.LONG`, or `.DWORD`, e.g.:

```
name EXT .BYTE

label_name EXT .WORD

 .EXTRN label_name .WORD

wait EXT .PROC (.BYTE delay)
```

An external symbol with a `.PROC` procedure declaration defaults to type `.WORD`. Any attempt to reference such a label name will be treated by **MADS** as an attempt to call the procedure; more on `.PROC` procedure calls in the *Procedures* chapter.

During the assembly process, zeros are always substituted when an external symbol reference is encountered.

External symbols can be useful when we want to assemble a program separately, independent of the rest of the main program. Such a program typically contains references to procedures or variables defined elsewhere, externally, where we only know their type but not their value. This is where external symbols come in, allowing for the assembly of such a program even in the absence of the actual procedures or variables.

Another application for external symbols is for so-called *plugins*—external programs linked to the main program to perform additional tasks. These are essentially libraries that utilize the main program's procedures to extend its functionality. To create such a plugin, one would need to define which procedures the main program provides (their names, parameters, and types) and create a procedure to read a file with **external** symbols; this procedure would handle the inclusion of plugins into the main program.

Below is the header format in a file with **B**-YTE, **W**-ORD, **L**-ONG, and **D**-WORD external symbols after a `BLK UPDATE EXTERNAL` call:

```
HEADER        WORD ($FFEE)
TYPE          CHAR (B-YTE, W-ORD, L-ONG, D-WORD, <, >)
DATA_LENGTH   WORD
LABEL_LENGTH  WORD
LABEL_NAME    ATASCII
DATA          WORD .. .. ..
```

* `HEADER`

Always with the value `$FFEE`.

* `TYPE`

The data type is stored in bits `0..6` of this byte and specifies the type of modified addresses.

* `DATA_LENGTH`

The number of 2-byte data entries (addresses) to be modified.

* `LABEL_LENGTH`

The length of the symbol name in bytes.

* `LABEL_NAME`

The symbol name in **ATASCII** codes.

* `DATA`

The actual sequence of data used to modify the main relocatable block. At the address specified here, the value of type `TYPE` must be read and then modified based on the new symbol value.

---

An example of using **external** symbols and `.STRUCT` structures is the sample library of graphical primitives: `PLOT`, `LINE`, and `CIRCLE` in the `..\EXAMPLES\LIBRARIES\GRAPHICS\LIB` directory. Individual modules here use a considerable number of zero-page variables. If we wanted their addresses to be relocatable, we would have to declare each variable individually as an external symbol using `EXT` or `.EXTRN`. We can simplify this by using only one external symbol and a `.STRUCT` data structure. Using structures, we define a *map* of `ZP` variables, then a single external symbol `ZPAGE` of type `.BYTE` because we want the variables to be on the zero page. Now, when referencing a variable, we must write it in a way that forces relocatability, e.g., `ZPAGE+ZP.DX`, resulting in a completely relocatable module with the ability to change the variable addresses in zero-page space.

## Public Symbols

Public symbols expose the variables and procedures within a relocatable block to the rest of the assembled program. With public symbols, we can reference variables and procedures *embedded* in places like libraries.

Public symbols can be used in `.RELOC` relocatable blocks as well as in standard **DOS** blocks.

**MADS** automatically recognizes whether the label provided for publication is a variable, a constant, or a procedure declared via `.PROC`. No additional information is required, unlike with external symbols.

Public symbols are declared using the following directives:

```
.PUBLIC label [,label2,...]
.GLOBAL label [,label2,...]
.GLOBL label [,label2,...]
```

The `.GLOBAL` and `.GLOBL` directives were added for compatibility with other assemblers; their meaning is identical to the `.PUBLIC` directive.

The update block for public symbols is called using the `BLK` pseudo-command:

    BLK UPDATE PUBLIC

Below is the header format in a file with public symbols after a `BLK UPDATE PUBLIC` call:

```
HEADER        WORD ($FFED)
LENGTH        WORD
TYPE          BYTE (B-YTE, W-ORD, L-ONG, D-WORD)
LABEL_TYPE    CHAR (C-ONSTANT, V-ARIABLE, P-ROCEDURE, A-RRAY, S-TRUCT)
LABEL_LENGTH  WORD
LABEL_NAME    ATASCII
ADDRESS       WORD
```

**MADS** automatically selects the appropriate type for the published label:

* `C-ONSTANT`: a non-relocatable label
* `V-ARIABLE`: a relocatable label
* `P-ROCEDURE`: a procedure declared via .PROC; undergoes relocation
* `A-RRAY`: an array declared via .ARRAY; undergoes relocation
* `S-TRUCT`: a structure declared via .STRUCT; does not undergo relocation

If the symbol refers to a `.STRUCT` structure, additional information is saved (field type, field name, field repetition count):

```
STRUCT_LABEL_TYPE    CHAR (B-YTE, W-ORD, L-ONG, D-WORD)
STRUCT_LABEL_LENGTH  WORD
STRUCT_LABEL_NAME    ATASCII
STRUCT_LABEL_REPEAT  WORD
```

If the symbol refers to an `.ARRAY` array, additional information is saved (maximum declared array index, declared field type):

```
ARRAY_MAX_INDEX  WORD
ARRAY_TYPE       CHAR (B-YTE, W-ORD, L-ONG, D-WORD)
```

If the symbol refers to a `.PROC` procedure, additional information is saved regardless of whether parameters were declared:

```
PROC_CPU_REG  BYTE (bits 00 - regA, 01 - regX, 10 - regY)
PROC_TYPE     BYTE (D-EFAULT, R-EGISTRY, V-ARIABLE)
PARAM_COUNT   WORD
```

For symbols relating to `.REG` procedures, only the types of these parameters are currently saved, in the quantity of `PARAM_COUNT`:

```
PARAM_TYPE    CHAR (B-YTE, W-ORD, L-ONG, D-WORD)
...
...
```

For symbols relating to `.VAR` procedures, the parameter types and their names are saved. `PARAM_COUNT` specifies the total length of this data:

```
PARAM_TYPE    CHAR (B-YTE, W-ORD, L-ONG, D-WORD)
PARAM_LENGTH  WORD
PARAM_NAME    ATASCII
...
...
```

* `HEADER`

Always with the value `$FFED`.

* `LENGTH`

The number of symbols saved in the update block.

* `TYPE`

The type of symbolized data: **B**-YTE, **W**-ORD, **L**-ONG, or **D**-WORD.

* `LABEL_TYPE`
    * Symbol type: V-ARIABLE, C-ONSTANT, P-ROCEDURE, A-RRAY, S-TRUCT
    * For type P, additional information is saved: PROC_CPU_REG, PROC_TYPE, PARAM_COUNT, PARAM_TYPE
    * For type A, additional information is saved: ARRAY_MAX_INDEX, ARRAY_TYPE
    * For type S, additional information is saved: STRUCT_LABEL_TYPE, STRUCT_LABEL_LENGTH, STRUCT_LABEL_NAME, STRUCT_LABEL_REPEAT

* `LABEL_LENGTH`

The length of the public symbol label in bytes.

* `LABEL_NAME`

The public symbol label in **ATASCII** codes.

* `ADDRESS`

The address assigned to the symbol in the `.RELOC` relocatable block. This value undergoes relocation by adding the current assembly address to it.

* `PROC_CPU_REG`

Information about the order of *CPU* register usage for a `.REG` type procedure.

* `PROC_TYPE`
    * **D**-EFAULT: the default type using the **MADS** software stack for parameter passing.
    * **R**-EGISTRY: parameters are passed to the procedure via **CPU** registers (`.REG`).
    * **V**-ARIABLE: parameters are passed to the procedure via variables (`.VAR`).

* `PARAM_COUNT`

Information about the number of parameters for a `.REG` procedure or the total length of data containing parameter types and names for a `.VAR` procedure.

* `PARAM_TYPE`

Parameter types recorded using the characters `B`, `W`, `L`, and `D`.

* `PARAM_LENGTH`

The length of the parameter name in `.VAR`.

* `PARAM_NAME`

The parameter name in ATASCII codes in `.VAR`.

## Directives `.LONGA` and `.LONGI`

```
.LONGA ON|OFF
.LONGI ON|OFF
```

* The `.LONGA` directive informs the assembler about the accumulator register size: 16-bit when ON, 8-bit when OFF.

* The `.LONGI` directive informs the assembler about the index register (`XY`) size: 16-bit when ON, 8-bit when OFF.

* These directives affect the argument size in absolute addressing for *CPU 65816*.

## Linking .LINK

    .LINK 'filename'

The `.LINK` directive requires the name of the file to be relocated as a parameter. Only **Atari DOS** files are accepted; **SDX** files are not.

If the file's loading address is other than `$0000`, it means the file does not contain relocatable code; however, it may contain update blocks for external and public symbols. The `.LINK` directive accepts files with any loading address, but only those with a loading address of `$0000` are subjected to relocation. More details on the structure of such files can be found in the Relocatable Block `.RELOC` chapter.

The `.LINK` directive allows for combining relocatable and non-relocatable code. Based on the update blocks, **MADS** automatically relocates such files. All three types of update blocks—`ADDRESS`, `EXTERNAL`, and `PUBLIC`—are taken into account. There are no restrictions on the address where the relocatable file is placed.

If the relocatable block requires the **MADS** software stack to function, the labels `@STACK_POINTER`, `@STACK_ADDRESS`, and `@PROC_VARS_ADR` will be automatically updated based on the `.RELOC` block header. It is required that the `.RELOC` blocks and the main program operate on the same software stack if one is necessary.
