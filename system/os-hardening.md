---
name: atari8bit-system
description: >-
  Atari 8-bit OS-ROM disable, trampoline handler, VCOUNT/WSYNC, RESET survival, SpartaDOS X DOSVEC/SDLSTL integration.
---

# 09 - System Hardening

> **Source note:** This file is self-contained.
> **Scope:** OS-ROM disable, trampoline handler, VCOUNT, WSYNC, RESET survival, SpartaDOS X
> **Key items:** PORTB $D301; NMIEN $D40E; NMIST $D40F; VCOUNT $D40B; WSYNC $D40A; SDLSTL $0230

## Quick-lookup

| Need | See § |
|---|---|
| OS-ROM disable / re-enable | §9.1 |
| OS NMI bridge and mapping contract | §9.1 |
| VCOUNT units and frame synchronization | §9.2 |
| RESET survival 400/800 vs XL/XE | §9.3 |
| DOS command-table protocol and SDX API boundaries | §9.4 |
| SDX binary block types | [SpartaDOS X formats](storage/spartadosx.md) |

## 9.1 OS ROM Ownership and an NMI Bridge

On XL/XE, PORTB bit 0 selects OS ROM: 1 = enabled, 0 = RAM visible.
Disabling ROM does not stop hardware keyboard scanning, IRQs, or ANTIC NMIs.
It removes the OS code and exposes RAM interrupt vectors at `$FFFA–$FFFF`.
Before switching, mask IRQs with SEI, disable ANTIC NMIs, install valid RAM
vectors and handlers, and keep executing code outside the switched regions.
SEI alone cannot mask an NMI. Decide who owns IRQ, NMI, and RESET separately.

For a program that needs OS VBI/DLI dispatch while normally keeping ROM off,
use [os-nmi-bridge.asm](../examples/routines/os-nmi-bridge.asm). This is an
include-only routine, not a complete machine-takeover program. It saves A/X/Y
and PORTB on the stack, enables only the OS bit, builds a synthetic RTI frame,
and copies the original stacked status into that frame before jumping through
the now-visible OS NMI vector. Preserving its I bit matters: XL OS stage 2 and
deferred VBI are skipped when the interrupted status has I set. The OS returns to the bridge,
which restores PORTB, registers, and the original hardware interrupt frame.

Requirements:

- Install the bridge address in the RAM NMI vector while ROM is off; initialize
  the other RAM vectors before allowing their interrupts.
- Keep the bridge, stack, display data, and any called RAM handlers accessible
  under both mappings. Account for self-test at `$5000–$57FF` when enabling OS.
- OS-dispatched DLI handlers end in RTI; deferred VBI handlers use XITVBV.
  Do not call either as an ordinary RTS-returning subroutine.
- Leave enough stack space for both interrupt frames, the OS register saves,
  and any nested DLI. The bridge does not provide an IRQ or RESET solution.

The CPU test uses a bank-switching memory model and an OS-shaped dispatcher
stub. It verifies preservation, not compatibility with every ROM revision or
cycle-exact ANTIC timing. [os-off-vbi.asm](../examples/os-off-vbi.asm) is a complete
short-lived demonstration with hardware IRQ sources disabled. It tests both
interrupted I states and also runs in the optional
full-machine smoke suite. Test the complete program on its target ROM/emulator.

## 9.2 VCOUNT and Frame Synchronization

`VCOUNT ($D40B)` exposes bits 1–8 of ANTIC's vertical position counter. It
advances every two scanlines, not every scanline. The manual gives ranges
0–131 (NTSC) and 0–156 (PAL), including terminal readings around frame wrap.
VBI begins at scanline 248 on both standards; the remaining blank interval
is longer on PAL. VCOUNT is a beam-position reference, not an OS frame clock.

```asm
; Partial routine: wait for entry to the bottom-of-frame interval on XL/XE.
; In: none. Out: A >=124. Clobbers A/N/Z/C; OS not required.
; Return once per observed frame transition, not repeatedly within the interval.
wait_frame
@leave  lda VCOUNT
        cmp #124               ; scanline 248 / 2
        bcs @leave
@enter  lda VCOUNT
        cmp #124
        bcc @enter
        rts
```

A delayed caller may skip a frame; this routine is synchronization, not elapsed
frame accounting. When OS VBI runs, use changes to `RTCLOK+2 ($14)` instead.
For an exact line, convert the target line to VCOUNT units and allow for its
2-line resolution. WSYNC provides horizontal synchronization, releasing the
CPU near the end of a scanline (cycle 105); it does not wait an entire frame.

NMIST reads do not clear status. A write to `NMIRES ($D40F)` clears the status
bits; ANTIC also changes DLI/VBI status as events occur. NMI is edge-triggered,
so clearing status is distinct from acknowledging a level-triggered IRQ.

Sources: [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf),
§§2.6, 4.8–4.10 and ANTIC register reference; [Atari XL OS Rev.2](https://github.com/ilmenit/A800-OS-XL-Rev2), NMI and DVNM.

---

## 9.3 System Reset and Power-On

System Reset is not the same as removing power. On 400/800 it triggers ANTIC
RNMI, synchronized to vertical blank, and the fixed OS handles warm start.
On XL/XE it asserts the hardware reset path; OS ROM is normally re-enabled
by the reset PIA state. DRAM contents generally survive a button reset, while
power-on contents must be treated as undefined.

Do not patch VDSLST as a reset hook: it is the DLI vector. Do not infer a cold
boot solely from an arbitrary RAM byte being zero. A resident program needs
a documented OS/DOS re-entry hook, a validated signature and state layout,
and an explicit decision about what startup code may overwrite. If survival
is not required, use the normal OS restart behavior.

Sources: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf),
§2.4 and System Reset NMI; [Atari XL OS Rev.2](https://github.com/ilmenit/A800-OS-XL-Rev2), warm/cold-start paths.

---

## 9.4 SpartaDOS X Integration

### SDX detection via the DOSVEC protocol

DOSVEC at `$000A` points at the DOS entry. Some DOS families expose a
command table with a JMP at offset +3. This recognizes that protocol shape,
not SpartaDOS X uniquely; do not use it as an SDX-specific API guarantee.

```asm
boot_?  = $09
dosvec  = $0a

detect_sdx
        lda boot_?
        lsr
        bcc _no_dos
        lda dosvec+1
        cmp #$c0
        bcs _no_dos
        ldy #$03
        lda (dosvec),y
        cmp #$4c              ; JMP opcode?
        bne _no_dos
        clc                   ; DOS command-table shape found (not proof of SDX)
        rts
_no_dos sec
        rts
```

SDX extends the standard DOS XL protocol with its own richer parameter-parsing library (available from DOSVEC+3), including automatic string-to-integer conversion, repeated option reads, and environment-variable substitution -- see the SDX Programmer's Guide section on parameter parsing.

### SDX autoboot and runtime types

| Startup path | Action |
|---|---|
| `AUTOEXEC.BAT` | Executed automatically at SDX boot |
| `RUN.BAT` | Executed after `AUTOEXEC.BAT` |
| Program `sa` loader | Calls SDX library `UPDATE NEW`, `UPDATE SYMBOL`, `BLK UPDATE EXTRN` for resolver |
### DOS memory ownership

A process cannot treat an arbitrary `$7000–$7FFF` range or a fixed `$6E00`
pointer as a shared-memory API. Use the allocator and documented interfaces
of the target DOS version. RAM data is not persistent across power cycles;
explicitly save/load a file if persistence is required.

See [SpartaDOS X relocatable formats](storage/spartadosx.md) for loader blocks.
Do not confuse assembler SAVE directives, DOS commands, and runtime APIs.

## 9.5 BREAK-Key Abort in Long Operations

Atari OS records BREAK-key activity through `BRKKEY ($0011)`. In ordinary OS
operation this byte is normally `$FF`; when BREAK is pressed, the OS clears it.
Long-running routines that do not call CIO often need to poll it explicitly.

Use this pattern in code that should be abortable without waiting for disk or
console I/O:

```asm
BRKKEY = $11

check_break
        lda BRKKEY
        beq ?break
        rts
?break  dec BRKKEY            ; restore to $FF after detecting BREAK
        lda #$80               ; BREAK KEY ABORT-style error code
        ; jump to caller's error path or SDX U_FAIL equivalent
        rts
```

If running under SpartaDOS X and using its structured error handlers, install
the failure handler before entering the protected routine and remove it after
the routine finishes. Keep the handler nesting shallow; SDX has a finite
internal handler stack. If no custom handler is installed, an abort should
fall through to the previous handler or system error path.

Reset `BRKKEY` after detecting BREAK. Console routines can also check this
byte and may raise an unexpected BREAK error later if stale state is left
behind.
