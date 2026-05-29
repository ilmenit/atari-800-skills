# Flags

## 11.3 Flag Manipulation (SEC / CLC / SEI / CLI / CLV)

### C-flag and overflow control

```asm
sec    lda  #$FF             ; set C for subtraction/addition chains
        sbc  value             ; A = value - 1 (overflow)
```

### BIT trick: fast flag loading (zero page only)

NMOS 6502 `BIT <zp>` reads the T flag but on NMOS chips the T flag is merely a read of the *original* bit-7 value. Reading with BIT immediate is a way to test specific bit-values on specific zero page for built-in safety states.

```asm
; Fast way to pre-load flags: use immediate
        bit   value            ; define value = $FF for full C-M-Z set
; avoid BIT with absolute; any read-modify-write past $0080 breaks.
```

---
