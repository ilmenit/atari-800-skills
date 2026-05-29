# Interrupts

## 1.5  Interrupts — IRQ / NMI / BRK

### IRQ (maskable)

- **Level triggered** — IRQ line must remain asserted; the 6502 responds when I-flag is clear.
- The IRQ must be **cleared at the device** before `CLI`, else IRQ handler re-enters immediately.
- **Branch delay:** a taken non-page-crossing branch delays IRQ acknowledge by 1 cycle. Cross-page branch = 4 cycles, no extra delay.
- **Overlapping IRQ + NMI:** IRQ acknowledged at cycle 4–8 can be hijacked by NMI; NMI executes with B flag set on stack if overlapping a BRK.

### NMI (edge‑triggered, non‑maskable)

On the 400/800: `RNMI` asserted only once on leading edge of VBLANK → OS warm-start handler (`$FED6`). On XL/XE: RESET button asserts `RESET` line directly (not RNMI); NMIST bit 5 stays latched until NMIRES write.

**NMIST (`$D40F`) bit layout**:  
- bit 7 = DLI occurred  
- bit 6 = VBI occurred  
- bit 5 = RNMI / SYSTEM RESET (400/800 only)  
- bit 4–0 = unused / reserved

DLI and VBI bits are mutually exclusive; DLI bit is cleared at scan line 248; VBI bit cleared whenever a DLI fires. NMIRES write does NOT suppress the pending interrupt — it only resets the status bit.

**Critical: never set NMIEN bit 7 before `VDSLST` is valid:**

```asm
        lda #<my_dli        ; set vector FIRST
        sta VDSLST
        lda #>my_dli
        sta VDSLST+1
        lda #$C0            ; NMIEN: $40=VBI, $80=DLI
        sta NMIEN           ; NOW enable
```

### BRK edge case

BRK = 7-cycle interrupt sequence, B-flag set on stack. If an NMI fires during cycles 4–8 of the BRK sequence, the NMI vector executes **with B-flag set**. Therefore a robust NMI/IRQ handler must check BRK first, then fall through to VBI in both:

```asm
dli_handler
        pha                  ; save A
        txa
        pha
        tya
        pha
        lda NMIST
        bpl ?vbi             ; B clear → IRQ/BRK
        ; BRK path: check RTI return
        bne ?dli             ; don't care about BRK here, VBI applies or DLI
?dli    lda NMIST
        and #$80
        beq ?end             ; no DLI
        ; ... DLI handler body ...
?end    pla
        tay
        pla
        tax
        pla
        rti
```

---

## 1.6  DLI Interrupt Hierarchy (Summary)

| Event | Effect on In-Progress DLI | Notes |
|---|---|---|
| **DLI while another DLI running** | First DLI saved; second executes; first resumes several lines later → artifacts if too slow | DLI stack: max 25 DLI frames before VBI |
| **WSYNC + interrupt gotcha** | Interrupt processing + ANTIC font cycles consume the first WSYNC → extra scan line of old color | Don't put WSYNC at top of DLI if already behind |
| **VBI while DLI running** | DLI resumes on first scan line of the *next frame* after VBI completes | VBI is highest priority |
| **DLI while VBI running** | VBI resumes; DLI fires on scan line 24 of *following* frame | Delayed delivery |
| **JVB `$C1` + DLI** | DLI on *every* scan line 224–248; up to 24 DLIs stack; unwind after VBI | DLI must be extremely short (~12-20 cycles) |

---
