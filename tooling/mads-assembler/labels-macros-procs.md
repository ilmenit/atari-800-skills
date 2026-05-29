# Labels Macros Procs

## 13.4 Labels and Scope

```asm
global_label:             ; global by default
.local local_area
  local_label:            ; local to local_area
  ?temporary:             ; temporary (OPT ?- implicit); auto-cleared each pass
.endl

; Self-modifying label
        lda  label:#$40     ; assembles as LDA immediate $40,
                            ; but linker form keeps label as data in-situ*
        ; generally only writes T2 instruction reads
.UNDEF  macro_name         ; removes single-line macro definition
```

---

## 13.5 Macros (.MACRO/.ENDM)

Up to 9 positional parameters. Anonymous forwarded labels `@+[1..9]` / `@-[1..9]` for forward/backward branching within macros.

```asm
.macro  draw_bar  color,  xpos,  width
        lda   #:color
        sta   COLPM0
        ldy   #:xpos
        mva   #:width bar_len
@bar    sta   (ptr),y
        iny
        dec   bar_len
        bne   @+              ; loop (auto uses @+1 backward)
.endm

; Anonymous forward label
@      lda  bar_length,x
       bne  @-              ; @- loops back to nearest @

; Invocation:
; @BAR on forward (0-based relative to last @)
```

### Macro commands (built-in pseudo-ops)

| Macro command | Expansion semantics |
|---------------|-------------------|
| `MVA src, dst` | `LDA src / STA dst` — mov A-destination |
| `MWA src, dst` | `LDA src+1 / STA dst+1; LDA src / STA dst` — word move |
| `ADW ptr, val` | `CLC / LDA val / ADC ptr / STA ptr; LDA val+1 / ADC ptr+1 / STA ptr+1` |
| `SBW ptr, val` | `SEC / LDA ptr / SBC val / STA ptr` (high byte borrow cleared) |
| `INW / DEW` | 16-bit inc/dec on ZP word |
| `MVX / MVY` | Move X-register or Y-register directly |
| `ADW ptr,ptr2,result` | ptr+ptr2 → result |

---

## 13.6 Procedures (.PROC/.ENDP)

`.PROC` blocks localise scope; parameters pass via `.REG` or `.VAR`.

```asm
; .REG passes through CPU registers; .VAR allocates ZP scratch vars
draw_line .PROC (.BYTE x0, y0, x1, y1) .REG
    mva x0, current_x
    mva y0, current_y
    ; ...
    @EXIT           ; early exit from procedure
.endp

; call:
draw_line #10, #20, #100, #80
@CALL draw_line
```

Typed parameters: `.BYTE` /`.WORD` / `.LONG` / `.DWORD` can be declared. Multi-dimensional arrays pass via `.PROC`, optionally with `@PUSH`/`@PULL`.

```asm
.proc copy (.WORD src+1, dst+1) .var
src   lda   $ffff
dst   sta   $ffff
       iny
       bne   src
       rts
.endp

copy.ToDst #$a080, #$b000   ; explicit sub-proc call
copy      #$a360            ; default call
```

Nesting: `.PROC` blocks can be nested.
```
.proc outer
    .proc inner
    .endp
.endp
```

---
