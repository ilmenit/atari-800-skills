# Overview

## Macros

Macros make it easier for us to perform repetitive tasks by automating them. They exist only in the assembler's memory and are assembled only at the time of invocation. With their help, **MADS** can push and pull parameters for procedures declared with the `.PROC` directive onto/from the software stack, and switch extended memory banks in *BANK SENSITIVE* mode (`OPT B+`).

> _Macros are read only in the first assembly pass; for the example below, macros located in a file included via `ICL` will not be recognized_:

```
 .macro test
   icl 'additional_macros.mac'
 .endm
```
