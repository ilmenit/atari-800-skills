# Vbi Dli

## §6  NVBLNV — Deferred VBI via SETVBV/XITVBV

From scrolling.md. The VBI entry point `XITVBV` is set up by `SETVBV` before the VBI fires for the first time, and every subsequent VBI must return via `XITVBV` rather than `RTI` so the OS restores the VIM accumulator and completes the OS-IRQ chain.

```asm
        ; Register deferred VBI (do this ONCE at startup)
        ldx #>vbi_deferred
        ldy #<vbi_deferred
        lda #$07               ; 7 + NMIEN_VBI = deferred vertical blank
        jsr SETVBV             ; $E45C XL/OS vector — installs vector in VIM

vbi_deferred
        pha
        txa
        pha
        tya
        pha

        ; ... VBI work ...

        jmp XITVBV             ; $E462 — restores A/X/Y; exits deferred VBI through OS
```

**Why NVBLNV matters for DLI-heavy demos:** `RTI` from a VBI restores the I flag (which was clear) → IRQ mask off. `XITVBV` does the same via the OS path — but additionally re-arms the NMI enabler, so the next VBI / DLI chain continues uninterrupted. Forgetting to call `XITVBV` on the last instruction of a VBI with a looping DLI → the DLI tree stops on the next vertical blank.

---
