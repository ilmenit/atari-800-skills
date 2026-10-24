# IRQ, NMI, and BRK

## CPU stack contract

On an NMOS 6502 interrupt entry the CPU pushes return PC and P, sets I, and
fetches the appropriate vector. It does not save A/X/Y. RTI restores P and PC;
RTS consumes a subroutine return address with a different convention.

- IRQ is level-triggered and maskable with I. Clear the peripheral source before
  returning with IRQs enabled or it can be serviced again immediately.
- NMI is edge-triggered and is not masked by SEI. A later edge can nest an NMI
  even while I is set. Stack depth depends on the actual interrupted code,
  handler saves, and subroutine calls; there is no fixed safe DLI nesting count.
- BRK uses the IRQ vector but marks its pushed status with B. The 6502 has no
  persistent B register bit corresponding to that stack marker. NMI/BRK/IRQ
  overlap has additional CPU-specific behavior; consult the hardware reference
  for cycle-level handling rather than guessing from NMIST.
- NMOS 6502 does not clear decimal mode on interrupt entry. A handler that uses
  binary ADC/SBC must establish D=0; RTI restores the interrupted status.

## Atari OS dispatch

The OS NMI dispatcher tests NMIST and jumps through VDSLST for DLI. That path
does not save A/X/Y; a DLI preserves the registers it changes and ends in RTI.
The VBI path saves A/X/Y before entering the OS VBI chain. A deferred VBI exits
through XITVBV, which restores those saves and executes RTI. See the
[OS vector contracts](../../system/os-vectors-handlers.md).

Install vectors before enabling their source. If an existing DLI is enabled,
disable it while updating the two-byte VDSLST pointer; SEI is insufficient.
Keep a write-only NMIEN shadow when the previous mask must be restored.

## ANTIC status

| NMIST bit | Source |
|---|---|
| 7 | Display-list interrupt |
| 6 | Vertical-blank interrupt |
| 5 | System Reset / RNMI on 400/800 |

Reading NMIST does not clear it. Writing NMIRES (`$D40F`) resets status bits.
The DLI bit clears when VBI status is set at scanline 248; ANTIC updates status
as new events occur. A status clear is not the same operation as clearing a
level-triggered IRQ line. On 400/800, System Reset RNMI is synchronized to
vertical blank and the OS gives it priority. XL/XE System Reset uses hardware
RESET instead, and its unused RNMI status can be stale after power-on.

Sources: [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf),
§§3.4 and 4.8; [Atari XL OS Rev.2 NMI/DVNM](https://github.com/ilmenit/A800-OS-XL-Rev2).
