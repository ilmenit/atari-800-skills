---
name: atari8bit-sorting
description: >-
  Atari 8-bit sorting algorithms — Optimal Sort 8/16-bit, bucket sort for 3D
  depth-order, Quicksort 16-bit, CombSort, ShellSort. Selection guide by data
  size and key width.
---

# 18 — Sorting Algorithms

> Rictor; Quicksort by Vladimir Lidovski/litwr); TORUS3D cull.asm 8-bucket
> sort — all patterns below with cycle costs.
> **Scope:** 6 sorting algorithms covering 8-bit and 16-bit keys: Optimal Sort,
> CombSort, ShellSort, Quicksort, and TORUS3D bucket sort.
> **Key items:** Optimal 8-bit ZP LUT ~6N cycles; 16-bit PLA swap; 8-way
> bucket depth sort; Quicksort via PLA stack; CombSort gap table; ShellSort
> Hibbard increments.

## Quick-lookup

| Need | See § |
|---|---|
| Optimal Sort 8-bit (Mats Rosengren, ZP LUT, ~6N cycles) | §18.1 |
| Optimal Sort 16-bit (PLA stack swap, same structure) | §18.2 |
| Bucket sort for 3D depth (TORUS3D 8-way, O(N), 96 verts) | §18.3 |
| Quicksort 16-bit (litwr / Vladimir Lidovski) | §18.4 |
| CombSort + ShellSort (gap comparison table, cycle cost) | §18.5 |
| Sort selection guide (N vs key-size vs stability) | §18.6 |

---

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

## 18.3 Bucket Sort — 3D Depth Order (TORUS3D preferred)

TORUS3D uses an 8-way bucket sort for its 50–96 visible quads. Depth keys are
0–255 unsigned bytes — index = depth >> 3 into 8 buckets. Zero comparisons.

```asm
SortVisible
        ldx    #$00
        lda    #$00
        sta    bkt_0..bkt_7

@fill   lda    BUF_DEPTH,x
        tay
        lsr                   ; depth >> 3
        lsr
        lsr
        tay
        lda    bkt_head,y     ; current tail
        sta    next,x
        lda    vis_quad,x
        sta    bkt_head,y     ; push into bucket
        inx
        cpx    vis_count
        bne    @fill

        ; Drain bucket 7 (far) to bucket 0 (near)
        ldy    #$07
@bucket lda    bkt_head,y
        beq    @next
        ; follow linked list into sorted output array
@next   dey
        bpl    @bucket
```

| | |
|---|---|
| Buckets | 8 (depth >> 3) |
| Bucket storage | BKT_HEAD[8] ZP |
| Link storage | NXT_PTR[96] |
| Cycles | ~500 (96 verts, single pass) |
| Comparisons | 0 |

---

## 18.4 Quicksort — 16-bit Keys (litwr / Vladimir Lidovski)

Recursive via PLA stack — no auxiliary stack allocation.

```asm
; quicksort16: sorts uint16 array [lo..hi]
; lo/hi indices arrive via PLA (popped return-address trick)

quicksort16
        cpy    lo_ptr
        bcs    @done           ; base case: lo >= hi
        tax                     ; T = hi
        sty    lo_ptr
        txa

        ; partition pass
        ; search left for key > pivot
        ; search right for key < pivot
        ; swap when both found

        ; after partition: recurse on left half, then right half
        ; via PLA-low+PLA-high for each range

        pla
        pla                    ; pop low byte of partition range
        cmp    lo_ptr
        bcs    @recurse_right
        jsr    quicksort16     ; left
        ; fall through to right
@recurse_right
        jsr    quicksort16
@done   rts
```

> Always add a median-of-3 pivot guard against O(N^2) worst case on sorted input.

---

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
| Bucket 8-way | 50–200 | O(N) | 80 B | no |

---

## 18.6 Selection Guide

```
N < 20          ->  Optimal Sort 8/16-bit   (low overhead, linked list)
N = 50-200      ->  Bucket sort 8-way        (TORUS3D pattern; zero comparisons)
N large/unsorted->  Quicksort 16-bit          (add median-of-3 pivot guard)
Nearly sorted   ->  CombSort                  (gap=1 only on last pass)
Tiny code       ->  ShellSort Hibbard         (60 B, no ZP workspace)
```

---

## See also

- `algorithms/math.md` — SMult8/UMult8 quarter-square multiply and distance helpers.
- `algorithms/3d-graphics.md` — object-space culling, backface tests, and depth-bucket usage.
