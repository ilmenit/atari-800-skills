# Build, Run, and Debug

Use this workflow when starting or validating an Atari program. Start from the
project's target and toolchain; these examples use MADS and the NMOS 6502.

## Starter Programs

These are complete XEX sources with equates, data, and RUNAD, assembled by
`scripts/validate.py`. They require a normal OS launch with BASIC disabled.
The bitmap example installs DLI/deferred-VBI handlers. The OS-off example
installs temporary RAM vectors and a bridge; the other programs leave OS ROM on.

| Source | Demonstrates | Ownership / exit |
|---|---|---|
| [text-io.asm](../examples/text-io.asm) | E: output, K: OPEN/GET/CLOSE, error cleanup | IOCB0 output plus one free channel; returns after a key |
| [joystick.asm](../examples/joystick.asm) | Frame-paced joystick/trigger shadows | Two screen cells; START returns |
| [pokey-tone.asm](../examples/pokey-tone.asm) | Pure-tone POKEY setup | Shared POKEY configuration; stops after 50/60 frames |
| [pmg.asm](../examples/pmg.asm) | Aligned single-line P0 DMA | `$4000–$47FF`; requires initially unused PMG; START disables it and returns |
| [bitmap-dli-vbi.asm](../examples/bitmap-dli-vbi.asm) | 160×192 bitmap, LMS boundaries, DLI, deferred VBI | `$4000–$4EFF` and `$5000–$5EFF`, display/NMI ownership; START restores saved OS state |
| [disk-read.asm](../examples/disk-read.asm) | Complete SIO DCB, status capture | Reads D1: sector 1 into private buffer; never writes disk |
| [os-off-vbi.asm](../examples/os-off-vbi.asm) | OS-off RAM vectors and ROM-enabling NMI bridge | Immediate VBI with I set, then deferred VBI with I clear; disables IRQ sources and restores state |

The graphics examples assume 64K XL/XE with standard OS display/VBI and no
resident graphics engine. They do not promise coexistence with arbitrary DOS
extensions, custom DLIs, or already allocated screen/PMG memory. Code/data begin
at `$2000`; check all load segments against the selected DOS before launch.

## Build and Run

From the repository root, with MADS on PATH:

```sh
mkdir -p /tmp/atari-skills-build
mads examples/bitmap-dli-vbi.asm -o:/tmp/atari-skills-build/bitmap.xex -t:/tmp/atari-skills-build/bitmap.lab -l:/tmp/atari-skills-build/bitmap.lst
atari800 -xl -xl-rev altirra -nobasic -pal -run /tmp/atari-skills-build/bitmap.xex
atari800 -xl -xl-rev altirra -nobasic -ntsc -run /tmp/atari-skills-build/bitmap.xex
```

Atari800 builds that include the replacement Altirra OS can use `-xl-rev altirra`
without a proprietary ROM. To validate a specific Atari ROM, select that ROM
explicitly instead. Never silently treat a replacement OS test as an original
OS compatibility test. Keep assembler/emulator versions with the test results.

## Debugging

Generate `.lab` and `.lst` files so a debugger can resolve labels and you can
inspect emitted bytes. In Atari800, `-monitor` enters the monitor and
`-bpc <hex-address>` breaks on a program counter. Its monitor accepts:

- `BPC address`, `CONT`, `SHOW`, `STACK`: execution and register inspection.
- `M address`, `D address`, `DLIST address`: RAM, machine code, display-list decoding.
- `ANTIC`, `GTIA`, `PIA`, `POKEY`: chip state.

The monitor's HELP output is paginated. When automating it, use a PTY, consume
prompts, send QUIT explicitly, and enforce a timeout/forced process cleanup.
Do not leave it reading EOF in a loop. Check `atari800 -help` for the installed
version's command-line options.

Useful breakpoints include program entry, the first VBI/DLI, and cleanup.
Compare SP at the same handler entry over successive frames. Watch writes to
NMIEN, PORTB, display-list pointers, and saved vectors when tracking crashes.
In Altirra, import the generated symbols and use register-write breakpoints and
the history/raster tools; consult that version's debugger help for syntax.

## Memory Ownership

Before choosing load addresses, list each allocation and who can write it:

| Allocation | Constraint |
|---|---|
| Zero page | OS, DOS, language, and ISR ownership; no private ZP is used by these starters |
| CPU stack | Main calls plus hardware frames, OS saves, bridge frames, and nested interrupts |
| Display list | Fetches wrap within 1K; keep address operands within that block |
| Bitmap/playfield | Fetches wrap within 4K; use LMS to restart before crossing |
| Font | 1K aligned in ANTIC 2–5; 512 bytes/alignment in 6–7 |
| PMG | 2K alignment for single-line DMA; 1K for double-line |
| DOS/program buffers | Consult MEMLO/MEMTOP and actual load segments; preserve resident allocations |
| Extended RAM | Identify CPU/ANTIC bank enables and DOS reservations before probing |

A runtime overlap check cannot undo damage that happened while loading an
XEX segment. Choose a compatible layout before loading. Returning to DOS also
requires restoring the state actually claimed: vectors, display/font/color
shadows, DMA, and any device/channel state. Write-only hardware registers need
a caller-provided initial-state contract or a software shadow.

## Frame Scheduling and Rendering

With the OS active, detect changes to RTCLOK+2 or use a minimal VBI counter.
Do input/update/render work in the main loop; keep interrupt work bounded.
For OS-off beam synchronization use the [VCOUNT contract](../system/os-hardening.md#92-vcount-and-frame-synchronization).
Do not put blocking CIO/SIO calls inside a time-critical VBI or DLI.

PAL and NTSC have different frame rates and CPU clocks. Express movement and
animation timing per second, then accumulate fractional steps per frame. A
50 Hz logic update can add 50 to a tick accumulator each frame and consume a
tick whenever it reaches the configured frame rate (50 or 60). This avoids
running the same per-frame displacement 20% faster on NTSC. Account for the
small difference between nominal and actual frame rates when precision matters.
Tracker speed and POKEY pitch are separate timing problems.

For double buffering, restore/draw the hidden buffer, finish the frame, then
publish its pointer during a controlled VBI interval. Main code must not modify
a pointer while an ISR reads its two bytes. Track sprite overlap and clipping;
restoring stale backgrounds can erase another sprite or newer playfield data.

## Validation Matrix

Run the [automated checks](validation.md) first. Then test the actual program on
each required machine/ROM, PAL/NTSC, RAM layout, and OS/DOS configuration.
Check input, output, errors, repeated frames, and return/cleanup behavior.
For raster/audio code, inspect the rendered output or recording and test the
target hardware when hardware timing is part of the requirement. CPU-only
emulation cannot establish pixel timing, sound quality, or universal compatibility.

Sources: [MADS upstream](https://github.com/tebe6502/Mad-Assembler),
[Atari800 upstream](https://github.com/atari800/atari800), and the
[Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf).
