# Comb Shell

## 18.5 CombSort + ShellSort

### CombSort (gap-based bubble)

Gap sequence: N, N/1.3, N/1.3^2, ... until gap < 1.
1.3 approximated as integer: multiply by 100 / 1329 (avoid FP).

ShellSort (Hibbard increments): 1, 3, 7, 15, 31, 63, 127, 255 = 2^k - 1.

```asm
; Hibbard gap table (N <= 128 uses 1,3,7,15,31,63,127)
hibbard_gaps
        .byte  127, 63, 31, 15, 7, 3, 1, 0   ; sentinel 0 ends loop

; ShellSort main loop
ShellSort
        ldx    #$00
@outer  lda    hibbard_gaps,x
        beq    @done
        tay                    ; Y = gap
        ldx    #$00
@inner  lda    key,y
        cmp    key,x
        bcc    @shift
        ; swap key[x] and key[x+gap]
        tax
        lda    key,x
        sta    ZP_TEMP
        lda    key,y
        sta    key,x
        ldy    ZP_TEMP
        sty    key,y
@shift  inx
        cpx    #$0F
        bne    @outer
@done   rts
```

| Algorithm | N | Cycles | Code | Stable? |
|---|---|---|---|---|
| Optimal Sort 8-bit | < 200 | ~6N | 180 B | yes |
| CombSort | any | ~N^1.2 | 100 B | no |
| ShellSort (Hibbard) | any | ~N^1.2 | 60 B | no |
| Quicksort 16-bit | any | O(NlogN) | 150 B | no |
| Bucket 8-way | 50-200 | O(N) | 80 B | no |

---
