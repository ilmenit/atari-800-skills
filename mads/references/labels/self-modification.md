# Self Modification

### Self-modification

A label placed after a mnemonic and ending with a `:` character defines a code self-modification address.

```
  lda label:#$00

  add plus:#$00

  lda src:$ff00,y
  sta dst:$ff00,y
```

The above examples are equivalent to the code:

```
  lda #$00
label equ *-1

  add #$00
plus equ *-1

  lda $ff00,y
src equ *-2

  sta $ff00,y
dst equ *-2
```
