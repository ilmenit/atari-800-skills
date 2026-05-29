# Deflate

## 12.4 DEFLATE — zlib-compatible Bitstream

DEFLATE on Atari 8-bit:
- Uses Huffman coding (literal/length + distance codes stored in dynamic Huffman trees).
- Very high densification ratio (up to ~50 % of LZ4).
- Compressor is large; **decompressor is 2–4 KB** and requires several hundred bytes of workspace for bitstream, Huffman tables, and sliding window.

Full DEFLATE depacker (~2–4 KB code + Huffman tables + 32 KB sliding window) is too
large to embed in full. The core loop is:

```asm
; DEFLATE core loop skeleton (fixed-Huffman, no ISO block types)
; In:  bitstream reader (shift-bit-carry pattern); state: sym=literal or length
; Out: output byte at dst, dst advances

deflate_core
        jsr    read_huffman     ; A = next Huffman symbol
        cmp    #$100            ; literal code threshold
        bcc    @literal         ; < $100 -> literal byte
        ; length/distance pair (match)
        sec
        sbc    #$100            ; A = length code (0..255)
        tax
        lda    length_base,x    ; base_length[x]
        jsr    read_extra_bits   ; add extra length bits if applicable
        tax                     ; X = match length
        jsr    read_distance     ; A = distance code
        tay
        lda    dist_base,y      ; base_distance[y]
        jsr    read_extra_dist   ; add extra distance bits
        tay
        ; copy from window: dst - distance, X bytes
        lda    dst
        sec
        sbc    distance
        sta    copy_src
        lda    dst+1
        sbc    distance+1
        sta    copy_src+1
@copy   lda    (copy_src),y
        sta    (dst),y
        iny
        dex
        bne    @copy
        jmp    deflate_core

@literal sta    (dst),y
        iny
        jmp    deflate_core
```

---

*See also: RLE depacker skeleton §12.1; Pascal encoder pattern §12.1.2.*
demoscene subdirectories (code-examples/demoscene/) — compressed production binaries: Candle/scroll/slideshow, LAMERS_Group, Electron.vfs).

---
