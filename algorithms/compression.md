---
name: atari8bit-compression
description: >-
  Atari 8-bit decompression for RLE, LZ4, Exomizer, and DEFLATE.
---

# 12 — Compression & Decompression

> reference articles: LZ4, Exomizer, DEFLATE summaries (content fully embedded below)> **Scope:** RLE, LZ4, Exomizer, DEFLATE compression/decompression for Atari 8-bit demos and data-load
> **Key items:** RLE POST byte; LZ4 token stream; Exomizer adaptive dict 512B; DEFLATE Huffman tier table
> **Scope:** RLE, LZ4, Exomizer, DEFLATE compression/decompression for Atari 8-bit demos and data-load

## Quick-lookup

| Need | See § |
|---|---|
| RLE format (POST literal/repeat) | §12.1 |
| RLE depacker skeleton (getByte/flag dispatch) | §12.1 |
| LZ4 decompression (~17 KB/s, <256 B workspace) | §12.2 |
| Exomizer ratio + workspace (~512 B) | §12.3 |
| DEFLATE/zlib \u2014 decoder ~2-4 KB + tables + window | §12.4 |
| Format trade-off table (code/size/speed/ratio) | §12.4 |

## 12.1 RLE — Run-Length Encoding

Tebe/MadTeam format (Konop/Probe/TeBe/Seban):
- Packed byte is POST'ed (least-significant-bit = `1`) for **literal** runs; LSB=`0` for **repeat** runs.
- The run-length decoder reads flag bytes and branches:
  - Flag LSB=1 → read literal bytes (count = flag >> 1 + 1)
  - Flag LSB=0 → read one target byte and repeat (count = flag >> 1 + 2)

**RLE depacker skeleton:**

```asm
        ; ZP: src_ptr = input pointer, dst_ptr = output pointer
        ; dfw_flag = current flag byte
rle_unpack
        jsr    getByte          ; reads from src_ptr
        sta    dfw_flag

        lsr                    ; test flag LSB
        bcs    @literal         ; LSB=1 → literal run
        ; --- repeat run ---
        jsr    getByte          ; read byte to repeat
        lsr    dfw_flag         ; shift flag right (÷2)
        beq    @end_flag        ; flag was 0 → repeat byte once, done
@rptlp  sta    (dst_ptr),y      ; output byte existing, counts 2
        dey
        bpl    @rptlp
        jmp    rle_unpack

@literal lsr    dfw_flag
        beq    rle_unpack
@litlp  jsr    getByte
        sta    (dst_ptr),y
        dey
        bpl    @litlp
        jmp    rle_unpack
```

### 12.1.2 Pascal cross-check (Tebe, rle.pas, Free Pascal)

Reads the input, reads each byte:
- If byte is odd (`b and 1=1`): reads one data byte, copies to output
- If byte is even (`b and 1=0`): reads one repeat byte, writes it `(b >> 1) + 1` times
- End-of-stream: zero byte

```pascal
procedure encode(output, input)
  b: byte;
  i: integer;
  ... for b=output 0 early: output seq of (odd/even) bytes
  ...protected for ZP: memory-buffer routines
```

---

## 12.2 LZ4 — LZ4-family Decompression

Reference: LZ4-family decompressor reference (~17 KB/s unpacked), second-to-none for low-memory access

Format overview:
- LZ4 is a variation of LZ77 — token stream of `literal_len | match_len` pairs.
- Match offset is encoded as a backward 2-byte distance (relative to current output position).
- Encodes literals directly, then uses backward match offsets for repeated data.
- LZ4 is the lightest with respect to workspace and code size: the decompressor requires <256 B on Atari

No extra allocatable workspace needed; memory footprint is < 256 bytes during decompression.
Stream decompression from external device supported.

On Atari, the LZ4 decompressor (~17 KB/s) consumes <256 bytes of extra workspace.

The MADS LZ4 example usually named `unlz4.asm` is a compact pattern worth reusing:

```asm
        mwa #packed inputPointer
        mwa #output outputPointer
        jsr unlz4

unlz4   jsr get_byte              ; token: high nibble literal len, low nibble match len
        sta token
        :4 lsr
        jsr getLength             ; handles $0f extension bytes
        ; copy literals to outputPointer
        ; read little-endian negative match offset
        ; source = outputPointer - offset
        ; copy match length + 4 bytes
```

The important idioms are self-modifying absolute operands for `inputPointer`, `outputPointer`, and `source`, plus `INW` for 16-bit pointer increments. This is faster than `(zp),Y` for long streams, but it requires the depacker code to live in writable RAM.

---

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
