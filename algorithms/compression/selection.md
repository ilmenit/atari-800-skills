# Selection

## 12.5 Low-RAM Compression Model Choice

On Atari XL/XE the best compressor is data-dependent. Pick the model by the
data and by the depacker budget, not by ratio alone.

| Data shape | Good model | Why |
|---|---|---|
| Screen clears, masks, repeated bytes | RLE | Tiny, byte-aligned, very fast |
| Code, fonts, maps, mixed assets | LZ77/LZ4/Exomizer | Reuses repeated substrings already output |
| Many frequent symbols with uneven probability | Huffman/static codes | Shorter codes for common symbols |
| Arbitrary already-packed data | Store raw or skip | Repacking often expands and costs loader time |

LZ77-style depackers are attractive on 6502 because the output buffer is also
the history buffer. A match only needs distance and length; the copy source is
`dst - distance`. This avoids maintaining a separate dictionary during
decompression.

Avoid LZ78-style dictionary-building depackers for small Atari loaders unless
there is a strong reason: the decoder must allocate and update a dictionary,
which costs RAM and cycles. DEFLATE can be worthwhile for tool-side packed data,
but dynamic Huffman tables and the sliding window make it a much heavier runtime
contract than RLE or LZ4.

When designing a custom packer:

- Model only the data you actually ship: charsets, tile maps, display lists,
  music, and executable code have different redundancy.
- Keep the decompressor byte-oriented if load speed matters more than ratio.
- Reserve bit-oriented coding for larger assets where the saved disk/load bytes
  repay the slower depacker.
- Test expansion cases. Some RLE formats expand short two-byte repeats or data
  with few runs.

Source note: this section condenses the portable parts of Pasi Ojala's
Compression Basics / C= Hacking compression articles into Atari loader rules.

---

## 12.6 Upkr, ZX0, and ZX2 Trade-Offs

Use Upkr when packed size is the priority and slow unpacking is acceptable:
title screens, one-time level loads, disk/menu assets, and demo parts that can
hide decompression behind a transition. Prefer ZX0 or ZX2 when the same asset
must unpack during gameplay, between animation beats, or inside a tight loader.

`pfusik/upkr6502` provides an Atari-friendly 6502 unpacker for the Upkr format.
Runtime contract:

| Area | Size / rule |
|---|---|
| Code | `unupkr`, 218 bytes, not self-modified; may live in ROM |
| Probability state | `unupkr_probs`, 319 bytes uninitialized RAM; page-align for best size/speed |
| Zero page | `unupkr_zp`, 15 bytes |
| Input/output | Source and destination must both fit in memory |
| Overlap | Allowed after already-read compressed bytes; source is read sequentially once |

Basic call pattern:

```asm
        lda #<packed_data
        sta unupkr_zp
        lda #>packed_data
        sta unupkr_zp+1
        lda #<unpacked_data
        sta unupkr_zp+2
        lda #>unpacked_data
        sta unupkr_zp+3
        jsr unupkr
```

The unpacker needs 8x8 multiplication. Leave `unupkr_mul = 0` for the smallest,
portable, slow path. If speed matters and 2 KB of temporary page-aligned RAM is
available, set `unupkr_mul` to that page; code grows to about 296 bytes, becomes
self-modifying, and can run about 50% faster. The generated multiply tables can
be reused after unpacking if the program also needs fast multiplication.

Pack with the matching Upkr options:

```sh
upkr -9 --big-endian-bitstream --invert-new-offset-bit --invert-continue-value-bit --simplified-prob-update INPUT_FILE OUTPUT_FILE
```

Choice guide:

| Format | Choose when | Avoid when |
|---|---|---|
| Upkr | Best ratio matters more than unpack time | In-frame/gameplay depack; no 319 B state RAM |
| ZX0 | Balanced ratio with much faster 6502 depackers | Need absolute smallest possible file |
| ZX2 / ZX02-style | 6502 depacker speed/size matters more than last ratio percent | Asset is so large that Upkr's ratio clearly wins |

For generated Atari code, state the compression contract next to the asset:
format, packed source address, output address/range, whether overlap is used,
workspace bytes/pages, and whether the depacker is self-modifying.
