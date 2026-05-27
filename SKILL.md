---
name: atari8bit
description: >-
  Root router for Atari 8-bit XL/XE AI-agent skills. Load this file first,
  choose the smallest matching topic file, then open original corpus sources
  only when deeper verification is needed.
---

# Atari 8-bit Agentic Programming Skills

> **Type:** Root router and taxonomy
> **Purpose:** Route Atari XL/XE programming, reversing, and hardware questions to the smallest useful English skill file.

Use progressive disclosure:

1. Read this router.
2. Open exactly one or two topic files that match the task.
3. If the topic file cites original source paths, open those only for details not already summarized.

All files under `atari8bit/` are English skill material. Source files elsewhere in the repository may be English, Polish, code, PDFs, or original examples.

## 1. `hardware/` — Silicon Reference

- **`hardware/cpu.md`** — 6502/65C02/65C816 flags, timing, undocumented opcodes, IRQ/NMI/BRK, opcode quick reference.
- **`hardware/antic.md`** — ANTIC DMA, display-list instruction bytes, scrolling registers, DLI timing, WSYNC, NMIEN/NMIST.
- **`hardware/gtia.md`** — GTIA registers, color model, GTIA modes, player/missile graphics, priority and collisions.
- **`hardware/pokey.md`** — POKEY audio, timers, IRQs, random/noise polynomials, keyboard/serial/SIO clocking.

## 2. `system/` — OS, Memory, I/O, Compatibility

- **`system/memory-map.md`** — 64K memory map, zero page, PIA, PORTB banking, extended RAM detection.
- **`system/os-vectors-handlers.md`** — OS vectors, VBI/DLI/CIO/SIO entry points, IOCB lifecycle, handler tables, safe hook patterns.
- **`system/os-hardening.md`** — OS ROM disable, trampoline handlers, RESET survival, VCOUNT/VBLANK bare-metal sync.
- **`system/storage.md`** — SIO protocol, disk commands, XEX/ATR formats, CIO file access, SpartaDOS X, loader/depacker reversing.
- **`system/screen.md`** — ATASCII, screen codes, CIO GET/PUT/PRINT, keyboard codes, number display.
- **`system/input.md`** — Joysticks, paddles, mouse, light pen, console keys, trigger registers.
- **`system/compatibility.md`** — 400/800 vs XL/XE, PAL/NTSC, RAM expansions, CPU/chip/upgrades detection matrix.
- **`system/cartridges-pbi.md`** — Cartridge windows, banking, PBI devices, internal devices, reverse-engineering notes.

## 3. `graphics/` — Rendering Techniques

- **`graphics/display-lists.md`** — DLI routines, display-list instruction set, LMS/JVB, WSYNC, multi-zone DLI patterns.
- **`graphics/character-modes.md`** — ANTIC text modes, fonts, CHBASE/CHACTL, blink/inversion, character-mode plotting.
- **`graphics/bitmap-modes.md`** — Hires and multicolor bitmap modes, 240-line tricks, custom video modes.
- **`graphics/pm-graphics.md`** — Player/missile setup, multiplexing, collision detection, soft sprites, OR-overlap patterns.
- **`graphics/scrolling.md`** — Coarse/fine vertical and horizontal scroll, VSCROL/HSCROL, parallax, MWP buffering.
- **`graphics/advanced-fx.md`** — HIP, RIP, TIP, GTIA 9++, interlaced shade/color techniques.

## 4. `audio/` — Sound and Music

- **`audio/synthesis.md`** — POKEY synthesis, distortion tables, filters, linked 16-bit channels, double POKEY.
- **`audio/digital-audio.md`** — 4-bit PCM/PDM playback, volume-only mode, VCOUNT-sync sample playback.
- **`audio/trackers.md`** — RMT and TMC2 playback engines, interrupt coexistence, tracker data layout.

## 5. `algorithms/` — Code Patterns

- **`algorithms/math.md`** — 8/16/32-bit multiply/divide, modulo, LUT math, atan2, sqrt, distance.
- **`algorithms/bit-ops.md`** — Bit shifts/rotates, flag testing, zero-page idioms, INC/DEC hardware hazards.
- **`algorithms/optimization.md`** — 6502 size/speed patterns, jump tables, compare-free loops, flag-preserving tests.
- **`algorithms/compression.md`** — RLE, LZ4, Exomizer, DEFLATE decompression patterns.
- **`algorithms/3d-graphics.md`** — Matrix rotation, projection, shading, span buffers, culling.
- **`algorithms/sorting.md`** — 8/16-bit optimal sorts, bucket sort, CombSort, ShellSort, Quicksort.
- **`algorithms/macros.md`** — Reusable MADS macros for memory, arithmetic, shifting, interpolation.

## 6. `tooling/` — Build, Examples, Reversing

- **`tooling/mads-assembler.md`** — MADS syntax, directives, macros, procedures, banks, relocatables, 65816 addenda.
- **`tooling/code.md`** — Ready-to-read examples: sieve, Tetris, RLE, GTIA 9++, 40x40, demoscene catalog.
- **`tooling/reversing.md`** — XEX/ATR/source/listing triage, segment maps, depackers, Altirra tracing, hardware breakpoints.

## 7. `exotics/` — Upgrades and Peripherals

- **`exotics/vbxe.md`** — VBXE FX core, detection, XDL, blitter, VRAM, palette, MEMAC windows, examples.
- **`exotics/sophia-rapidus.md`** — Sophia video upgrades, Rapidus/65C816 notes, APE-Time RTC, LDW/CA-2001 device protocol.

## Source Corpus

Primary original sources live outside `atari8bit/`, especially:

- `Altirra-hardware/extracted_chapters/` — authoritative English hardware reference.
- `atari-documentation/` — memory maps, MADS, POKEY, ANTIC/GTIA, XEX, banking, code examples.
- Online hardware reference cards such as Gury/Jindroush are useful for connector pinouts and cartridge/PBI signal names; verify register-level behavior against Altirra or local documentation before generating final code.
- `Atariki/articles/` — Polish articles used selectively for English skill summaries.
- `articles/scrolling.md` and `articles/ironman.md` — major English tutorial sources.
- User-provided MADS assembler example corpus, if available — runnable examples for banked 130XE code, relocatable modules, SpartaDOS X/FAS binaries, tracker-player relocators, DLI/IRQ raster kernels, CIO/SIO loaders, and small syntax demonstrations. If the path is not obvious in the workspace, ask the user for it.
- `torus-project/`, `math/`, `other/` — working algorithm and demo-code references.

## Navigation Rules

- Hardware-register behavior belongs in `hardware/`; software rendering recipes belong in `graphics/`.
- OS/device/file/vector questions belong in `system/`; build examples and reverse workflows belong in `tooling/`.
- Use original Polish sources only as references for translation or verification; do not expose Polish text in final skill answers.
