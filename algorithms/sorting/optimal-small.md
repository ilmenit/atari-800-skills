# Optimal Small

## 18.1 Optimal Sort — 8-bit Elements

Indexed merge variant using a ZP scratch pad and a ZP-indexed lookup to identify the
minimum directly. The build phase maintains two link fields (nxt/prv array); the
walk phase simply chains through the linked list.

```asm
; A = key array address; X = N elements (< 128); Y = output pointer

OptimalSort8
        sta    key_ptr
        stx    n_elems

        ; Phase 1: initialise linked lists
        ldx    #$00
@init   lda    #$FF
        sta    nxt,x
        sta    prv,x
        inx
        cpx    n_elems
        bne    @init

        ; Phase 2: build key order (nxt/prv doubly-linked list)
        ldx    #$00
@outer  txa
        tay
@inner  iny
        cpy    n_elems
        beq    @next_outer
        lda    key_ptr,y
        cmp    key_ptr,x
        bcc    @inner           ; key[y] < key[x] -> skip x
        ; Insert x before y
        lda    prv,y
        sta    nxt,x
        lda    nxt,x
        sta    prv,y
        lda    x
        sta    prv,x
        lda    y
        sta    nxt,x
        jmp    @inner
@next_outer
        inx
        cpx    n_elems
        bne    @outer

        ; Phase 3: find head (prv = $FF) and walk linked list
        ldx    #$00
@head   lda    prv,x
        bne    @head
        txa
        sta    head_idx

        ldx    head_idx
        ldy    #$00
@walk   lda    key_ptr,x
        sta    output,y
@filled
        lda    nxt,x
        cmp    #$FF
        beq    @done
        tax
        iny
        cpy    #$FF
        bne    @walk
@done   rts
```

| | |
|---|---|
| Workspace | OPTIMAL_W 128 B (nxt + prv arrays) |
| Key size | 8-bit unsigned, N < 128 |
| Time | ~6N + fixed build overhead |
| Stable | yes (insertion preserves key order) |
| ZP-only | yes; no absolute hot-path access |

---

## 18.2 Optimal Sort — 16-bit Elements

Same structure, 16-bit compare uses high-byte first then low-byte.

```asm
; 16-bit swap (in-place, ZP temp)
        lda    key_ptr,x
        ldy    key_ptr+1,x
        lda    key_ptr,y
        sta    ZP_TEMP
        sty    ZP_TEMP+1
        lda    key_ptr,y
        sta    key_ptr,x
        sty    key_ptr+1,x
        lda    ZP_TEMP
        sta    key_ptr,y
        lda    ZP_TEMP+1
        sta    key_ptr+1,y
```

The PLA stack swap technique (used by §18.4 Quicksort): pop two bytes from the stack
as virtual X indices, perform the 16-bit swap, then push.

---
