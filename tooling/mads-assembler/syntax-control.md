# Syntax Control

## 13.2 Syntax and Operands

Numbers: `#$NN` hex, `%NNNNNNNN` binary, `#NN` decimal. String literals in `.BYTE`, `.CBM`, `.SB` are ASCII ATASCII.

String expansion: immediate value can be two chars: `lda #'AB'`, `mwa #'XY' $80`.

**Expression operators:** `+ - * / MOD AND OR XOR SHL SHR NOT < <= = >= > <> ==`

Expressions use 64-bit signed arithmetic internally; results truncated to 32-bit unsigned for memory addresses.

**Addressing modes:**
```
lda #$01             ; immediate
lda $80              ; zero page
lda $0200            ; absolute
lda ($80,x)          ; indexed indirect (zp,X)
lda ($80),y          ; indirect indexed (zp),Y
lda $0200,x          ; absolute indexed X
lda $0200,y          ; absolute indexed Y
lda ($0200),y        ; (abs),Y indirect indexed
```

---

## 13.3 Directives and Control Flow

| Directive | Purpose |
|-----------|---------|
| `.ORG addr[, *]` | Set assembly origin; `*` = load origin |
| `.A8 / .A16` | Set 65816 accumulator width (8/16 bits) |
| `.I8 / .I16` | Set 65816 index register width (8/16 bits) |
| `.ALIGN N[,fill]` | Align to N-byte boundary; optional fill byte |
| `.NOWARN` | Suppress warning for the current line |
| `.PRINT / .ECHO` | Compile-time text output |
| `.ERROR / ERT` | Compile-time error halt |
| `.RND` | Random value 0..255 at assembly time |
| `.PAGES N / .ENDPG` | Page boundary markers (listing) |
| `.FILEEXISTS('fn')` | Returns 1 if file exists, 0 otherwise |
| `.LEN('fn')` | Returns file length |

### Conditional assembly

```asm
.IFDEF    label           ; true if label is defined
.IFNDEF   label           ; true if undefined
.IF       expr            ; assembly if expr ≠ 0
.ELSE                    ; alternative branch
.ENDIF                   ; end conditional block
.ELIF expr              ; shorthand for .ELSE .IF
```

### Repeat loops

```
.REPT N [, #,...          ; repeat N times, optional param # = counter
.rept 10,#*2             ; * counter × 2 = address offset
.label:1                 ; counter replacement: LABEL0, LABEL1...
.ENDR                    ; end repeat
```

Multi-dimensional loop:
```
.REPT 10
  lda  table,x
  inx
.ENDR
```

### Multi-pass zero-page auto-selection

MADS automatically selects free ZP addresses across multiple assembly passes when no explicit address is given — useful for procedure-local scratch variables.

---
