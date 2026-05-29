# Lz4

## 12.2 LZ4 — LZ4-family Decompression

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
