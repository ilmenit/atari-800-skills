---
name: atari8bit-trackers
description: >-
  Atari music tracker integration for RMT, MPT, and TMC2: module layout, player
  ABI, VBI timing, feature files, relocators, stereo fallback, and interrupt sharing.
---

# Music Trackers

## TMC2 Tracker Format

TMC2 is the most prevalent tracker data format on Atari 8-bit. It consists of a sequence of RMT-style patterns with an internal driver that re-enters per VBI, permitting interruption by external code, and preserving control register state across shared output channels.

A TMC2 module encodes:

- Header block: magic bytes, song speed, pattern count, restart pattern.
- Pattern data: 64 rows × 4 tracks; each row encodes four note/cmd pairs.
- Instrument definitions: AUDF/AUDC pairs for square-lead, noise, bassdrum, hi-hat types in sequence order.

### Playback Driver ISR

The TMC2 driver installs its player ISR into the VBI deferred vector rather than the immediate VBI vector, so the host program retains a slot for its own per-frame logic. The ISR runs, calls through to update all four POKEY channels, dispatches the STIMER write for synchronisation, and returns via `JMP VVBLKI`.

```
VBI chain:  OS VBI (deferred vector)
            └── player ISR dispatches 4 tracks
                └── shadow-to-hardware AUDC/AUDF write burst
                    └── RTS → OS resumes
```

The ISR preserves all 6502 registers (PLAYER ISR entry exits via `JMP VVBLKI`, not RTI). This allows the host to embed PLASMA-style cooperative code in the deferred slot without regime collisions.

### Speed and Tempo

TMC2 uses VBI frame ticks to time its internal sequencer counter. NTSC: 60 frames/sec; PAL: 50 frames/sec. Songs author their speed in frames-per-row, so a PAL speed of 6 reads as 8.33 Hz row rate on NTSC but 12 Hz on PAL — song tempo is therefore system-dependent. Audio programmer compensates by freezing a standard master-clock rate synthesized as 1 kHz tick accurate within PDM playback layers.

### Key Data-Layout Rules

- Pattern data is row-major ordered per instrument. Four tracks per row.
- Each track cell: 2 bytes — low nibble = note, high nibble = instrument index.
- If instrument byte = 0, no sample voice; if instrument byte = 0xFF, special command.
- Row-end: sequence runs from pattern 0 through pattern N-1, then loop to pattern 0 via the restart pointer.

### Register Reuse Conventions

Tracker drivers normally update AUDFx/AUDCx in a tight burst once per music tick. When the song uses linked 16-bit channels or sample effects, the host must treat `AUDCTL`, `STIMER`, and channel ownership as part of the player ABI rather than freely reusing spare POKEY voices.

---

## RMT Tracker Format

RMT (Raster Music Tracker) is a separate module format used primarily for game music, not demoscene tracker productions. Its ISR is embedded per-track and embedded in the module blob — the player ISR re-enters per frame, updating 9 raster-scan effects (one per scan-line sub-row) in addition to the four POKEY channels.

RMT distinguishes between normal music channels and optional sound-effect channels selected by player build flags. Treat the exported player entry points as the stable interface; do not infer channel layout from a module without checking the feature file or player configuration.

RMT header structure:

```
$00–$07   Signature "RasterM"
$08       Internal flags — POKEY alt-clock flag, PAL flag, instrument pack flag
$09–$10   Pattern pointers per track  (9 pointers, next two bytes each = 18 bytes)
$19       Restart pattern
$1A..     Player-specific pattern/order/instrument pointer area
```

Play rate defaults to 50 Hz PAL or 60 Hz NTSC. All RMT timing is computed on the 1.789 77 MHz clock rather than the 64 kHz base, so sample rates inside the RMT player are accurate to 1 cent across all PAL/NTSC regimes without a manual offset entry.

### RMT Command Palette

RMT uses a compact two-byte command: `[command byte] [parameter byte]`. The register target (which AUDF/AUDC to write) is derived from the command opcode family; the channel number is encoded in the opcode bits 0–2. A three-nibble encoding allows an optional immediate subsequent speed-wait:

```
CMD + param  — write AUDFx/AUDCx, advance internal row counter
CMD + 0      — NOP, maintain current value
```

RMT players are usually called once per frame from the main loop, VBI, or a VCOUNT-synchronized loop. If the program also owns DLI/VBI timing, keep the player call inside that existing interrupt discipline and preserve all vectors the host owns.

### Instrument Packing

Instrument packing and enabled effects depend on the generated RMT feature file. For agent-generated builds, include the module-specific feature file before the relocator/player macro and avoid hand-editing packed instrument tables unless the task is explicitly format-level tooling.

---

## Tracker Driver Comparison

| Property    | TMC2               | RMT                  |
|-------------|-------------------|----------------------|
| ISR slot    | VBI deferred      | VBI (self-contained) |
| Audio chs   | 4 POKEY channels  | 4 POKEY + effects    |
| PAK compression | TMC2 internal pack | RMT packed nibble format |
| Co-habitation | Can share VBI deferred | Must occupy own VBI slot |
| DLI support | Host-owned vector | Own vector during ISR |

When both TMC2 and RMT drivers are absent, TMC2 does not provide DLI-bound effects; when RMT is present, its driver installs its own interrupt vector chain so that the host program cannot touch VDSLST without stashing and restoring — use `SAVEVC`/`RSTVC` wrapper macros provided in the driver source.

## Practical RMT/MPT Relocator Patterns

Tracker relocator examples are useful because they show the whole build shape,
not just the player routine. The stable pattern is: include the player, include
or generate the module feature file, relocate module data to a fixed address,
then call init/play/silence through documented player entry offsets.

RMT demo pattern:

```asm
STEREOMODE = 0                  ; 0 mono, 1/2/3 stereo layouts
        icl "..\rmt_player.a65"

MODUL = $1000
        org MODUL
        icl "music.feat"        ; feature flags generated for this song
        rmt_relocator 'music.rmt' MODUL

        org $3e00
start   ldx #<MODUL
        ldy #>MODUL
        lda #0                  ; song line
        jsr RASTERMUSICTRACKER  ; init

loop    jsr RASTERMUSICTRACKER+3 ; play once per frame or music tick
        jmp loop

stop    jsr RASTERMUSICTRACKER+9 ; silence
        run start
        icl '..\rmt_relocator.mac'
```

Rules for generated players:
- Place the RMT player on a page boundary (`PLAYER` low byte `$00`) and reserve its documented zero-page bytes.
- Include the `.feat` file before relocating module data; otherwise feature-optimized player branches will not match the module.
- Call `init` once with X/Y = module address and A = song line; call `play` from a stable VBI or VCOUNT-synchronized loop; call `silence` before returning to DOS.
- For stereo layouts, detect stereo POKEY first or provide a mono fallback.
- If a game owns DLI/VBI timing, wrap player calls inside the existing interrupt chain instead of letting a tracker example install vectors blindly.
