# Trig Tables

## 10.6 8-bit Sine/Cosine Tables

For animation and rotation, use one 256-byte signed sine table or one 128-byte
positive half-wave table plus quadrant folding. MADS can generate the table at
assembly time:

```asm
        .align $100
sine    dta b(sin(0,255,256,0,127))   ; 0..127 amplitude over 256 steps
cosine  equ sine+64                    ; 90-degree phase offset
```

If negative values are needed, fold by quadrant: `0..63` positive rising,
`64..127` positive falling, `128..191` negative falling, `192..255` negative
rising. Keep tables page-aligned for `LDA table,X`.

---
