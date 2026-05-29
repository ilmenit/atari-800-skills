# Local

### Local

Every label definition within a `.MACRO`, a `.PROC` procedure, or a `.LOCAL` area is local scope by default, in other words, it is local. The user does not need to additionally mark such labels.

Local labels are defined using the following equivalent pseudo-commands:

```
 EQU
  =
```

To access global scope labels (i.e., defined outside a `.MACRO`, `.PROC` procedure, or `.LOCAL` area) with the same names as local ones, use the `:` operator, e.g.:

```
lp   ldx #0         ; global label definition LP

     test
     test

test .macro

      lda :lp       ; the ':' character before the label will read the value of the global label LP

      sta lp+1      ; reference to the local label LP in the macro area
lp    lda #0        ; local label definition LP in the macro area

     .endm
```

In the example above, there are definitions of labels with the same names (LP), but each has a different value and different scope.

### MAE-style Local

The `OPT ?+` option informs **MADS** to interpret labels starting with the `?` character as local labels, as **MAE** does. By default, labels starting with the `?` character are treated by **MADS** as temporary labels.

Example of using **MAE**-style local labels:

```
       opt ?+
       org $2000

local1 ldx #7
?lop   sta $a000,x
       dex
       bpl ?lop

local2 ldx #7
?lop   sta $b000,x
       dex
       bpl ?lop
```
