# Overview

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
