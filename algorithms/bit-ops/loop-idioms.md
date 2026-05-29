# Loop Idioms

## 11.4 Negative-Index Loop

Using negative-style X-indexing to descend through a table or array in page 0:

```asm
        ldx   #$3F
@loop   lda   table,x
        dex
        bpl   @loop             ; BPL = until X goes negative; covers #$3F..0

; OR descending past $00 via BCC (carry propagated from carry=set at start)
        sec
@loop   lda   table,x
        dex
        bcc   @loop             ; $80 iterations before C wraps
```

---
