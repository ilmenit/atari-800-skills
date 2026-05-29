# Shadow Registers

## §2  Shadow-vs-Hardware Register Gotcha

The OS maintains shadow registers in page 2 (e.g. `PCOLR0=$02C0`, `COLOR0=$02C4`, `GPRIOR=$022E`). Every VBI the OS copies every shadow register to its corresponding hardware register. Changes to shadow registers *during a DLI* are NOT reflected in hardware until the next VBI.

**Rule:** write to `$D0xx` hardware registers in DLI; write to `$02xx` shadow registers only in VBI or main code.

### POKEY Timer IRQ Scanline Split

The MADS examples usually named `irq_mcp.asm` and `irq_mcp_2.asm` show a useful alternative to very long DLI chains: use the DLI to land at a stable scanline, then arm a POKEY timer IRQ for an intra-line colour split.

```asm
dli_arm_irq
        pha
        txa
        pha

        lda #0
        sta SKCTL              ; stop keyboard scan while aligning timer
        sta WSYNC              ; stable scanline boundary
        ldx #20
?wait   dex
        bne ?wait
        sta STIMER             ; reset POKEY timers at known cycle
        lda #1
        sta SKCTL              ; restore keyboard scan
        lda #4
        sta IRQEN              ; enable selected POKEY timer IRQ

        pla
        tax
        pla
        rti
```

Use this for MCP/HIP/RIP-style colour timing where a normal DLI cannot hit the exact horizontal position cheaply. Always restore `SKCTL`, acknowledge/disable `IRQEN` in the IRQ stop path, and keep the custom IRQ vector resident outside any banked `$4000-$7FFF` window.

### Shadow → Hardware mapping

| Shadow ($02xx) | Hardware ($D0xx) | Notes |
|---|---|---|
| `PCOLR0 = $02C0` | `COLPM0 = $D012` | colour / |
| `PCOLR1 = $02C1` | `COLPM1 = $D013` | use hardware register in DLI |
| `PCOLR2 = $02C2` | `COLPM2 = $D014` | |
| `PCOLR3 = $02C3` | `COLPM3 = $D015` | |
| `COLOR0 = $02C4` | `COLPF0 = $D016` | PF0–3 + BAK |
| `COLOR1 = $02C5` | `COLPF1 = $D017` | |
| `COLOR2 = $02C6` | `COLPF2 = $D018` | |
| `COLOR3 = $02C7` | `COLPF3 = $D019` | |
| `COLOR4 = $02C8` | `COLBK = $D01A` | background / border |
| `GPRIOR = $022E` | `PRIOR = $D01B` | P/M priority bits |
| `CHACT = $02F1` | `CHACTL = $D401` | character mode control |
| `CHBAS = $02F4` | `CHBASE = $D409` | character set base |

---
