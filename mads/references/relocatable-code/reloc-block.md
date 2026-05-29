# Reloc Block

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
