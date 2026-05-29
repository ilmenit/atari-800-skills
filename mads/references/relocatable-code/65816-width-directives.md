# 65816 Width Directives

## Directives `.LONGA` and `.LONGI`

```
.LONGA ON|OFF
.LONGI ON|OFF
```

* The `.LONGA` directive informs the assembler about the accumulator register size: 16-bit when ON, 8-bit when OFF.

* The `.LONGI` directive informs the assembler about the index register (`XY`) size: 16-bit when ON, 8-bit when OFF.

* These directives affect the argument size in absolute addressing for *CPU 65816*.
