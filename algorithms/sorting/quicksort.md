# Quicksort

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
