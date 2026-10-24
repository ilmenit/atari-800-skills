# Timing Validation

Cycle-level kernels depend on ANTIC mode, DMA width, scrolling, PMG, CPU
instruction phase, and interrupt path. Validate the emitted code and actual
raster output on the intended emulator version and hardware configuration.
Do not convert a rough cycle budget into a universal instruction deadline.

- Initialize VDSLST before enabling DLI and preserve the registers a handler uses.
- Use ordinary JVB `$41` unless repeated DLI behavior from `$C1` is intentional.
- VCOUNT uses two-line units; WSYNC provides horizontal alignment.
- Shadow writes are delayed until OS VBI; DLI effects need hardware writes.
- Keep display-list fetches inside a 1K block and playfield fetches inside each
  4K block, using jumps/LMS to cross boundaries deliberately.

The [runnable bitmap example](../../examples/bitmap-dli-vbi.asm) and
[validation workflow](../../tooling/workflow.md) provide a baseline. Historical
emulator bugs should be cited to a specific release/change, rather than given
as unsupported dates or rankings.
