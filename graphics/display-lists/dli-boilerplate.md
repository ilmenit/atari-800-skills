# DLI Handler Contract

The OS DLI path jumps through VDSLST after the CPU has saved PC/P. Preserve
only the A/X/Y registers the handler actually changes, then RTI. For a DLI that
changes a color using only A, this partial routine is sufficient:

```asm
my_dli
        pha
        lda #$0c
        sta WSYNC
        sta COLPF0
        pla
        rti
```

The complete [bitmap/DLI/VBI program](../../examples/bitmap-dli-vbi.asm) includes
installation, a display-list DLI flag, and cleanup. Its DLI uses the same stack
contract and is exercised by the CPU validation suite.

`$41` is ordinary JVB and does not request a DLI. `$C1` sets the DLI bit and
can trigger repeatedly while JVB is replayed. Avoid it in ordinary display
lists. If deliberately used, ensure each handler completes before the next
edge or explicitly gate NMIEN with a maintained mask. A counter inside the
handler cannot prevent the hardware from entering it; it can only reduce the
work after entry. See [instruction encoding](../../hardware/antic/display-list-instructions.md).

Source: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §§4.6 and 4.8.
