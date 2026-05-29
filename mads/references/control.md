## Assembly Control

### [Changing assembly options](pseudo-commands/assembly-options.md#opt)

### [Conditional assembly](directives/conditionals-repeat.md#if_else)

### [Interrupting assembly](directives/file-output.md#error)

### Zero Page Assembly

Unlike two-pass assemblers such as **QA** and **XASM**, **MADS** is multi-pass. What does this provide?

Let's take this example:

```
 org $00

 lda tmp+1

tmp lda #$00
```

A two-pass assembler, not knowing the value of the `TMP` label, will assume by default that its value is two bytes, i.e., type `WORD`, and will generate an `LDA W` instruction.

However, **MADS** will kindly generate a zero page instruction `LDA Z`. This is essentially the main and simplest property of having more passes to explain.

Now, one might say they prefer it when an instruction referencing the zero page takes the form `LDA W`. No problem, just extend the mnemonic:

```
 org $00

 lda.w tmp+1

tmp lda #$00
Three mnemonic extensions are permitted
 .b[.z]
 .w[.a][.q]
 .l[.t]
```

representing `BYTE`, `WORD`, and `LONG` respectively. The last one generates a 24-bit value and refers to the *65816* and continuous memory areas. More information about *CPU 6502* and *65816* mnemonics and their allowed extensions can be found in the [Mnemonics](mnemonics.md) chapter.
Another way to force a zero page instruction is to use curly braces `{ }`, e.g.:

```
 dta {lda $00},$80    ; lda $80
```

In **MADS**, we could do the same, but why bother? The last pass will handle it for us :) The problem now is placing such a code snippet in the computer's memory. We can try to load such a program directly onto the zero page, and if the target area is within the range `$80..$FF`, the **OS** will probably survive; below that area, it will be more difficult.
That is why **MADS** allows this:

```
 org $20,$3080

 lda tmp+1

tmp lda #$00
```

Meaning: assemble from address `$0020`, but load at address `$3080`. Of course, subsequently moving the code to the correct address (in our example `$0020`) is the programmer's task.

In summary:

```
 org address1,address2
```

Assemble from address `address1`, place in memory starting at address `address2`. Such an `ORG` will always cause a new block to be created in the file, meaning an additional four header bytes for the new block will be saved.

If we do not require a new memory location for the data, and the data should be placed at the current address, we can use the properties of `.LOCAL` and `.PROC` blocks; in this case, header bytes will not be saved, e.g.:

```none
     1
     2                                  org $2000
     3
     4 FFFF> 2000-200D> A9 00           lda #0
     5 2002 EA                          nop
     6
     7 0060                     .local  temp, $60
     8
     9 0060 BD FF FF                    lda $ffff,x
    10 0063 BE FF FF                    ldx $ffff,y
    11
    12                          .endl
    13
    14 2009 A5 60                       lda temp
    15 200B AD 03 20                    lda .adr temp
    16
```

In the above example, the `TEMP` program block will be assembled with the new address `= $60` and placed in memory at address `$2003`.

After the directive terminating the block (`.ENDL`, `.ENDP`, `.END`), the assembly address from before the block is restored, plus the length of the assembled block. In our example, the address from which assembly will continue after the `.LOCAL` block ends will be `$2009`.
Subsequently, using the `.ADR` and `.LEN` directives, such a block can be copied to the correct address, e.g.:

```
      ldy #0
copy  mva .adr(temp),y temp,y+
      cpy #.len temp
      bne copy
```

More information on the functioning of the [.ADR](directives/data-storage.md#adr) and [.LEN](directives/file-output.md#sizeof) directives.
