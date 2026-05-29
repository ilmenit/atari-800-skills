# Anonymous

### Anonymous

To ensure code clarity, the use of anonymous labels is limited only to conditional jumps and up to 10 occurrences forward/backward.

The `@` character has been reserved for anonymous labels; this character must be followed by a character specifying a jump forward `+` or backward `-`. Additionally, the occurrence number of the anonymous label in the range `[0..9]` can be specified; no occurrence number means `0` by default.

```
 @+[0..9]     ; forward
 @-[0..9]     ; backward

 @+           ; @+0
 @-           ; @-0

@ dex   ---- -------
  bne @+   |  --   |
  stx $80  |   |   |
@ lda #0   |  --   |
  bne @- ---       |
  bne @-1  ---------

  ldx #6
@ lda:cmp:req 20
@ dex
  bne @-1
```
