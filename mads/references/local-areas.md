## Local Area

The main task of a local area in **MADS** is to create a new namespace for labels.

Any labels defined in a `.LOCAL` area have local scope; they can also be described as locally defined global labels with free access, because they can be referenced, which is not normal in other programming languages.

Local areas are additive, meaning there can be many `.LOCAL` blocks with the same name, and no error message _**Label ... declared twice**_ will be generated.

The additivity of local areas occurs at the current namespace level; if we want to connect to a selected local area in another namespace, we precede the full name leading to such an area with a `+` character, e.g.:

```
  .local lvl

tmp = 3

  .endl



  .local temp

tmp = 7


    .local +lvl

      .print tmp

    .endl


  .endl

```

For the above example, the value of the `TMP` label from the `LVL` local area with the value `3` will be displayed. If the `+` character were missing in `.LOCAL +LVL`, then the `TMP` value displayed would be `7`.

In a `.LOCAL` area, it is possible to define labels with global scope (see chapter [Global labels](#global)).

If the label sought by the assembler did not occur in the `.LOCAL` area, then **MADS** will search for it in a lower area until it reaches the global area. To immediately read the value of a global label from a `.LOCAL` area (or another local area), precede the label name with a colon character `:`.

The following directives apply to local areas:

```
 [name] .LOCAL [,address]
 .LOCAL [name] [,address]
 .ENDL [.LEND] [.END]
```

### [name] .LOCAL [,address]

Declaration of a local area named `name` using the `.LOCAL` directive. The area name is not required and is not necessary. Mnemonic names and pseudo-command names cannot be used for local area names. If a name is reserved, an error with the message _**Reserved word**_ will occur.

After the local area name (or after the `.LOCAL` directive), we can provide a new assembly address for the local block. After completing such a block (`.ENDL`), the previous assembly address is restored, increased by the length of the local block.

```
label .local,$4000
.endl

.local label2,$8000
.endl

.local
.endl

.local label3
.endl
```

All label definitions in a `.LOCAL` area are of local type. To refer to a global label with the same name as a local label, precede it with a colon character `:`, e.g.:

```
lab equ 1

.local

lab equ 2

 lda #lab
 ldx #:lab

.endl
```

In the above example, the value `2` will be loaded into register `A`, while the value `1` will be loaded into register `X`.

If the label sought by the assembler did not occur in the `.LOCAL` area, then it will be searched for in the macro area (if currently being processed), then in the procedure (if the procedure is currently being processed), and finally in the main program.

In a declared local area, all label definitions are distinguished based on the local area name. To reach a defined label in a local area from outside the local area, we must know the name of the area and the label occurring in it, e.g.:

```
 lda #name.lab1
 ldx #name.lab2

.local name

lab1 = 1
lab2 = 2

.endl
```

When addressing such a `.LOCAL` structure, use the period character `.`.

Local areas can be nested, and they can be placed in the body of procedures declared by the `.PROC` directive. Local areas are additive, i.e., there can be many local areas with the same name; all symbols occurring in these areas will belong to a common namespace.

The length of the generated code in a `.LOCAL` block can be checked using the `.LEN` (`.SIZEOF`) directive.

### .ENDL
The `.ENDL` directive ends the local area declaration.

Example of a local area declaration:

```
 org $2000

tmp ldx #0   <-------------   label in the global area
                          |
 lda obszar.pole  <---    |   reference to the local area
                     |    |
.local obszar        |    |   local area declaration
                     |    |
 lda tmp   <---      |    |
              |      |    |
 lda :tmp     |      | <---   reference to the global area
              |      |
tmp nop    <---      |        definition in the local area
                     |
pole lda #0       <---   <--- definition in the local area
                            |
 lda pole  <----------------- reference in the local area

.endl                        end of local area declaration
