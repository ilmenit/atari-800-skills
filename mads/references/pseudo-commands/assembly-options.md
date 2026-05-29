# Assembly Options

### BLK

```
 BLK N[one] X                    - block without headers, program counter set to X

 BLK D[os] X                     - DOS block with $FFFF header or without header if the
                                   previous one is the same, program counter set to X

 BLK S[parta] X                  - block with fixed loading addresses and $FFFA header,
                                   program counter set to X

 BLK R[eloc] M[ain]|E[xtended]   - relocatable block placed in MAIN or EXTENDED memory

 BLK E[mpty] X M[ain]|E[xtended] - relocatable block reserving X bytes in MAIN or EXTENDED memory
                                   NOTE: the program counter is immediately increased by X bytes

 BLK U[pdate] S[ymbols]          - block updating SDX symbol addresses in previous SPARTA or
                                   RELOC blocks

 BLK U[pdate] E[xternal]         - block updating external label addresses ($FFEE header)
                                   NOTE: does not apply to Sparta DOS X, this is a MADS extension

 BLK U[pdate] A[dress]           - block for updating addresses in RELOC blocks

 BLK U[pdate] N[ew] X 'string'   - block declaring a new symbol 'string' in a RELOC block
                                   at address X. If the symbol name is preceded by the @ sign
                                   and the address is from main memory, such a symbol can be
                                   called from command.com
```

More information about blocks in **Sparta DOS X** files in the [Sparta DOS X File Structure](../spartadosx.md#file-structure) and [Sparta DOS X Programming](../spartadosx.md#programming) chapters.

<a name="set"></a>

### OPT

The `OPT` pseudo-command allows enabling/disabling additional options during assembly.

```
 b+  bank sensitive on
 b-  bank sensitive off                                               (default)
 c+  enables support for CPU 65816 (16-bit)
 c-  enables support for CPU 6502 (8-bit)                             (default)
 f+  output file as a single block (useful for carts)
 f-  output file in block format                                      (default)
 h+  saves the file header for DOS                                   (default)
 h-  does not save the file header for DOS
 l+  saves the listing to a file (LST)
 l-  does not save the listing (LST)                                  (default)
 m+  saves entire macros in the listing
 m-  saves only the part of the macro that is executed in the listing (default)
 o+  saves the assembly result to an output file (OBX)                (default)
 o-  does not save the assembly result to an output file (OBX)
 r+  code length optimization for MVA, MVX, MVY, MWA, MWX, MWY
 r-  no code length optimization for MVA, MVX, MVY, MWA, MWX, MWY     (default)
 s+  prints the listing on the screen
 s-  does not print the listing on the screen                         (default)
 t+  track SEP REP on (CPU 65816)
 t-  track SEP REP off (CPU 65816)                                    (default)
 ?+  labels starting with '?' are local (MAE style)
 ?-  labels starting with '?' are temporary                           (default)
```

```
 OPT c+ c  - l  + s +
 OPT h-
 OPT o +
```

All `OPT` options can be used anywhere in the listing; for example, we can enable listing recording at line 12 and disable it at line 20, etc. Then the listing file will only contain lines 12..20.

If we want to use *65816* addressing modes, we must inform the assembler via `OPT C+`.

If using **CodeGenie** or **Notepad++**, you can use `OPT S+` so you don't have to switch to the listing file, as the listing will be printed in the bottom window (Output Bar).
