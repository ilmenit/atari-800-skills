# External Symbols

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
