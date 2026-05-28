# SpartaDOS X

## File Structure

Reprint from **Serious Magazine**, author: **Qcyk/Dial**.

A file in itself is just a collection of bytes of little value. A lot of numbers that can mean everything and at the same time nothing if you don't know how to interpret them. For this reason, most files are equipped with various headers that store information about what the file contains or how it should be treated during reading. This also includes executable files, binary files, or simply those intended to be loaded from **DOS**, since **DOS** is also a program and, like any other, has the right to expect data with a specific, known structure.

Traditional binary files, recognized by all **DOSes** for **Atari XL/XE** computers, have a block structure where each block has its own header. There are two types of headers:

1. `dta a($ffff),a(str_adr),a(end_adr)`

2. `dta a(str_adr),a(end_adr)`

`str_adr` - address where the first byte of data will be loaded

`end_adr` - address where the last byte will be loaded

The first block in the file must have a `$ffff` type header; other blocks can have either. Naturally, the header should be followed by data in the amount of:

    (end_adr-str_adr)+1

So much for a reminder. The creators of the **Sparta DOS X** system maintained the above standard while adding several new header types. Thus, we are still dealing with a file divided into blocks, but there are now many more block types. Here they are:

### Non-relocatable Block

    dta a($fffa),a(str_adr),a(end_adr)

Non-relocatable block (loaded to a fixed address in memory). This is the same as the `$ffff` block—it doesn't matter which one is used. However, `$fffa` will clearly indicate that the program is intended for SDX—other DOSes will not read such a file.

### Relocatable Block

    dta a($fffe),b(blk_num),b(blk_id)
    dta a(blk_off),a(blk_len)

Relocatable block (loaded at MEMLO into the specified memory type).

#### `blk_num`

The block number in the file. Each relocatable block should have its own number. Since the loading addresses of blocks are unknown, blocks are identified precisely by their numbers. They can take values in the range `0-7`, although in practice, numbering usually starts from 1 upwards.

#### `blk_id`

Bits `1-5` represent the memory index where the block is to be loaded. I have encountered two values:

    $00 - main memory
    $02 - extended memory

Additionally setting bit `7` indicates the absence of a data block. In this case, **SDX** loads nothing but reserves memory.

#### `blk_off`

The so-called address offset in the block, which is simply the address where the code was assembled. This is necessary for updating addresses that refer to the block's content.

#### `blk_len`

Block length. This much data should follow the header, unless it's a memory-reserving block, in which case there is no data.

When writing relocatable code, one must keep in mind several limitations imposed by the idea of *moveable* code. All addresses referring to the area of such a program must be updated during loading; therefore, sequences such as the following cannot be used:

    lda coś
    ...
    coś equ *
    ...

Instead, options like this remain:

    lda _coś
    ldx _coś+1
    ...
    _coś dta a(coś)
    ...
    coś equ *

### Update Block (Relocation)

    dta a($fffd),b(blk_num),a(blk_len)

Update block for addresses referring to a relocatable block.


#### `blk_num`

The number of the block to which the updated addresses refer.

#### `blk_len`

The length of the update block (excluding the header). It is ignored.

Addresses are updated by adding the difference between the address where the specified relocatable block was loaded and the `blk_off` (assembly address) of that block to the existing address. This can be represented by the formula:

    ADR=ADR+(blk_adr-blk_off)

The *body* of the update block consists of pointers to the addresses being corrected and special instructions. A pointer is a number in the range `$00-$fb` and represents the offset relative to the location of the previous update. This location is remembered by the loader as a direct address, let's call it the update counter. This counter can be initialized using special functions, which are numbers greater than `$fb`:

* `$fc` indicates the end of the update block,

* `$fd,a(ADDR)`—the address pointed directly by `ADDR` is updated. Thus, the `ADDR` value is written to the update counter, and subsequent offsets will be calculated from it,

* `$fe,b(blk_num)`—the address of the block pointed by `blk_num` is inserted into the update counter, meaning subsequent updates will refer to the code contained in that block,

* `$ff`—the update counter is increased by `$fa` (without updating an address).

### Update Block (Symbols)

    dta a($fffb),c'SMB_NAME',a(blk_len)

Update block for addresses of procedures defined by symbols.

#### `SMB_NAME`

Symbolic name of the procedure (or array, system register, etc.). Eight characters in ATASCII code.

#### `blk_len`

As in the `$fffd` block.

Following the header is a sequence of pointers defining the locations of addresses to be updated—identical to the `$fffd` block. Addresses are changed by adding the address of the procedure defined by the symbol to the existing address. This allows for using procedures in programs whose addresses we don't know, e.g., procedures added by other programs running in the SDX environment. System procedures should also be used in this way, since they can have different addresses in different versions of **Sparta**.

### Definition Block

    dta a($fffc),b(blk_num),a(smb_off)
    dta c'SMB_NAME'

Block for defining new symbols.

#### `blk_num`

The number of the block where the procedure being defined is located. This implies that the procedure must be loaded as a relocatable block.

#### `smb_off`

The address offset of the procedure in the block, i.e., the offset of the procedure relative to the start of the block (the first byte is numbered 0) increased by the `blk_off` of that block. In other words, it is the address where the procedure was assembled. `SMB_NAME` is the symbolic name of the procedure being defined.

Blocks of types `$fffb`, `$fffc`, and `$fffd` are not permanently retained in memory. The system uses them only during program loading.

## Programming

The syntax for **Sparta DOS X** support was taken from **FastAssembler** by **Marek Goderski**; below is a quote from the manual included with **FA**. `*.FAS` source files can currently be assembled using **MADS** without major issues. Relocatable instructions always have a 2-byte argument; it is not possible to relocate 3-byte arguments (*65816*).

The most important innovation in **SDX** for the programmer is the ability to easily write relocatable programs. Since the *MOS 6502* processor lacks relative addressing (except for short conditional jumps), programmers from **ICD** applied special mechanisms for loading program blocks. The entire process consists of loading a block, followed by a special address update block. All addresses in the program block are calculated from zero. Thus, adding the `memlo` value to them is sufficient to obtain the proper address. Which addresses to increase, and which to leave alone? That is precisely what the special update block is for, which contains pointers (specially encoded) to those addresses. Therefore, after a `RELOC` block or blocks, it is mandatory to perform `UPDATE ADDRESS` for the program to function correctly. Also, after `SPARTA` blocks where instructions (or vectors) refer to `RELOC` or `EMPTY` blocks, performing `UPDATE ADDRESS` is mandatory.

Another innovation is the introduction of symbols. Well, some **SDX** service procedures have been defined using names! These names always have 8 letters (similar to filenames). Instead of using vector or jump tables (as in the **OS**), we use symbols defined by **SMB**. After loading a program block or blocks, **SDX** loads a symbol update block and replaces addresses in the program in a similar way to relocatable blocks. Symbols can be used for `RELOC` and `SPARTA` blocks.

A programmer can define their own symbols to replace **SDX** ones or completely new ones for use by other programs. This is done via the `UPDATE NEW` block. However, it should be noted that a new symbol must be contained within a `RELOC` block.

The number of `RELOC` and `EMPTY` blocks is limited to 7 by **SDX**.

Such blocks can be chained together, e.g.:

```
blk sparta $600
...

blk reloc main
...

blk empty $100 main
...

blk reloc extended
...

blk empty $200 extended
```

This means that instructions in these blocks can refer to all blocks in the chain.

Such a chain is not broken by address or symbol updates, but it is destroyed by the definition of a new symbol or other blocks, e.g., `dos`.

**NOTES**:

* Such a chain only makes sense if all its blocks are loaded into the same memory, or if the program switches memory during the appropriate references.

* Instructions and vectors in `RELOC` and `EMPTY` blocks should not refer to `SPARTA` blocks! This can cause an error if a user loads a program with the `LOAD` command and uses it after a long time. While `RELOC` and `EMPTY` blocks are safe, you never know what is in memory where the `SPARTA` block was last located! It is equally dangerous for `SPARTA` blocks to use references to `RELOC` and `EMPTY` blocks (for the same reason); however, during the installation of `*.sys` overlays using `INSTALL`, it is sometimes necessary and thus permissible. A `SPARTA` block can also be initialized via `$2E2`—it will then always be running and later redundant.

* An address collision may occur between `SPARTA` and `RELOC` or `EMPTY` blocks! **FA** recognizes references to other blocks via addresses, assuming a `PC` for `RELOC` and `EMPTY` starting from `$1000`. Thus, when mixing these blocks, you must ensure that `SPARTA` lies below `$1000` (e.g., `$600`) or above the last relocatable block—typically `$4000` is sufficient. Such an error is not detected by the compiler!
