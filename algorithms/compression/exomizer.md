# Exomizer

## 12.3 Exomizer — Adaptive Dictionary Compression

Exomizer uses an adaptive dictionary: long repeated substrings are replaced by reference pairs (offset-, length-bits). On Atari 8-bit the decompressor requires ~512 B of RAM and ~1–2 KB of code. The depacker loop unpacks variable-length sequences bit-by-bit from the input byte-stream;

```asm
; Exomizer-style adaptive depacker skeleton
; In:  src = packed data pointer, dst = output pointer
; RAM: 512 B bit-buffer window
exo_unpack
        lda    (src),y         ; read next packed byte
        sta    bitbuf
        ldx    #$08
@bits   asl    bitbuf           ; shift next bit into carry
        rol    dst_offset       ; build offset in dst_offset (2 bytes)
        bcc    @match           ; bit=0 -> match reference
        ; literal byte
        lda    (src),y
        sta    (dst),y
        iny
        bne    @next
        inc    src+1            ; cross-page source
        inc    dst+1            ; cross-page dest
        jmp    @bits
@match  ; match: offset bits already in dst_offset; length in next N bits
        lda    (src),y
        sta    length
        ; copy from already-unpacked output: dst - offset
        lda    dst
        sec
        sbc    dst_offset
        sta    copy_src
        lda    dst+1
        sbc    dst_offset+1
        sta    copy_src+1
@copy   lda    (copy_src),y
        sta    (dst),y
        iny
        dec    length
        bne    @copy
        ; advance pointers and resume bit stream
        iny
        bne    @bits
@next   iny
        jmp    @bits
```

This skeleton implements the core bit-driven adaptive loop — adapt bit-order, length encoding, and offset size to match the specific Exomizer profile variant.

---
