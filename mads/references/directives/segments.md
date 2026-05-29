# Segments

### .ALIGN N [,fill]
The `.ALIGN` directive allows aligning the assembly address to a specified value `N`, and potentially filling memory with a specified `FILL` value. It is possible to align the assembly address for relocatable code provided a memory fill value `FILL` is given.

Default values are: `N=$0100`, `FILL=0`.

```
 .align

 .align $400

 .align $100,$ff
```

<a name="rept"></a>

### .PAGES [expression]
The `.PAGES` directive allows specifying the number of memory pages that our code snippet, bounded by `<.PAGES .. .ENDPG>`, should fit into (default is 1). If the program code exceeds the declared number of memory pages, a *Page error at ????* error message will be generated.

These directives can help us when we want a program fragment to fit within a single memory page, or when writing a program that fits into an additional memory bank (64 memory pages), e.g.:

```
 org $4000

 .pages $40
  ...
  ...
 .endpg
```

<a name="seg"></a>

### .SEGDEF label address length [attrib] [bank]

### .SEGMENT label

### .ENDSEG

The `.SEGDEF` directive defines a new segment `LABEL` with starting address `ADDRESS` and length `LENGTH`. Additionally, it is possible to specify an attribute for the segment (R-read, W-rite, RW-ReadWrite - default) and assign a virtual bank number `BANK` (default `BANK=0`).

The `.SEGMENT` directive activates writing the output code for segment `LABEL`. If the specified segment length is exceeded, a *Segment LABEL error at ADDRESS* error message will be generated.

The `.ENDSEG` directive ends writing to the current segment and restores writing to the main program block.

```
	.segdef sdata adr0 $100
	.segdef test  adr1 $40

	org $2000

	nop

	.cb 'ALA'

	.segment sdata

	nop

	.endseg

	lda #0

	.segment test
	ldx #0
	clc

	dta c'ATARI'

	.endseg

adr0	.ds $100
adr1	.ds $40
```
