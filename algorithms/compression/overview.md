# Overview

## Quick-lookup

| Need | See § |
|---|---|
| RLE format (POST literal/repeat) | §12.1 |
| RLE depacker skeleton (getByte/flag dispatch) | §12.1 |
| LZ4 decompression (~17 KB/s, <256 B workspace) | §12.2 |
| Exomizer ratio + workspace (~512 B) | §12.3 |
| DEFLATE/zlib \u2014 decoder ~2-4 KB + tables + window | §12.4 |
| Format trade-off table (code/size/speed/ratio) | §12.4 |
| Choosing a low-RAM compression model | §12.5 |
| Upkr ratio-first unpacking; ZX0/ZX2 faster alternatives | §12.6 |
