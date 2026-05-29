# Dli Boilerplate

## §1  Mandatory DLI Boilerplate

The shortest correct DLI that changes one hardware register:

```asm
my_dli
        pha                 ; save A
        txa
        pha                 ; save X
        tya
        pha                 ; save Y

        sta WSYNC           ; wait for end of current scan line
        lda #$0C
        sta COLPF0          ; $D016 — hardware, not $02C4

        pla
        tay
        pla
        tax
        pla
        rti                 ; pops P register from stack
```

**The RTI path:** the OS handler at $FFFA passes control to the handler at address loaded into `VDSLST ($200/$201)`. On entry, the CPU has already pushed the P register; RTI pops it off the stack — that is the `I`-flag restore that re-enables / disables IRQ.

**Do not skip PYA/Y/PLA/PLY in the prologue/epilogue.** Relying on the DLI being in a band that preserves X/Y, or that the OS has stored A, is a fragile assumption — the behaviour differs between OS-A/XL/XE and bare-metal.

---

## §3  JVB DLI Storm — Stack Depth Limit

`$41` (JVB) is re-executed once per scan line in the range scan-line 8–248. Every scan line an NMI fires, pushes the stack, and DLI handler runs. **Maximum ≈25 concurrent DLIs before the 6502 256-byte stack overflows** (runaway cascades if the DLI cascade writes more than it pops per frame).

**Mitigation:**

```asm
; DLI storm guard — only run on every Nth scan line
storm_counter = $90
storm_threshold = $05       ; execute 1/5 of JVB DLIs

jvb_dli
        pha
        txa
        pha
        tya
        pha

        inc storm_counter
        lda storm_counter
        cmp #storm_threshold
        bne ?skip            ; skip all but every 5th DLI
        ; -- critical DLI work here --
        lda #$00
        sta COLPF0
?skip
        pla
        tay
        pla
        tax
        pla
        rti
```

Alternatively, use `NMIEN bit 7` gating: disable DLI output on the last DLI of the JVB frame before the VBI fires. On next VBI, re-enable. DLI storm is a tool (used by the `unity` demo for the 3-mode scan-line split), not a bug — just guard the stack.

---
