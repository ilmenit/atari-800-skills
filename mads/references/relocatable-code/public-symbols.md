# Public Symbols

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
