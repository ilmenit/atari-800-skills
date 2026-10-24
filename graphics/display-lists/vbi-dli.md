# Deferred VBI

The canonical [OS VBI contract](../../system/os-vectors-handlers.md#11-deferred-vbi-via-setvbv--xitvbv)
uses SETVBV with A=7, X=high address, Y=low address to install a deferred handler.
XITVBV is the OS exit vector, not an installed handler pointer.

The OS NMI dispatcher already saves A/X/Y on the VBI path. A deferred handler
may use them, then JMP XITVBV to restore that original frame. If the handler
pushes additional values, it must pop them before the jump. A raw RTI at that
point consumes saved register bytes as the CPU status/program counter.

See [bitmap-dli-vbi.asm](../../examples/bitmap-dli-vbi.asm) for the complete
installation and balanced handler. XITVBV restores registers and returns from
interrupt; it is not a mechanism for re-arming NMIEN.
