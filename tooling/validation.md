# Validation and Sources

## Run the Checks

```sh
python3 -m venv /tmp/atari-skills-venv
/tmp/atari-skills-venv/bin/pip install -r tests/requirements.txt
/tmp/atari-skills-venv/bin/python scripts/validate.py
```

MADS must be on PATH, or set MADS to its executable path. The local suite uses
temporary build files, requires no network or ROM, and does not alter the skill
files. It assembles every top-level `examples/*.asm` program and each maintained
include-only routine. `examples/atari.inc` supplies constants, not allocations.

## What Is Checked

- All 65,536 unsigned byte pairs for quarter-square multiplication, including
  sums above 255, zero, and `$FF*$FF`.
- All byte pairs for table-free multiplication, all 16-bit inputs for multiply
  by 3/10, all byte inputs for multiply by 96, and a boundary matrix plus 512
  seeded 16x16 products.
- Every occupancy combination for IOCBs 1–7, including full allocation and
  a free IOCB0 that must be skipped. No OS workspace writes are permitted.
- NMI bridge execution through a ROM overlay and an OS-shaped dispatcher;
  exact preservation of A/X/Y/P/SP/PORTB for DLI and VBI paths, original I-state
  gating of deferred VBI, decimal-mode entry, and stack-page wrap cases.
- Actual assembled DLI/deferred-VBI handlers through the same stack convention.
- PMG initialization with all 2K of DMA memory prefilled with nonzero bytes.
- CIO OPEN/GET/PUT/CLOSE request fields, error cleanup, and SIO read DCB/status.
- Bitmap display-list decoding, 192 fetched rows, JVB target, DLI count, and
  prevention of 1K display-list / 4K playfield crossings.
- Example equates and all 64 keyboard matrix positions against a pinned
  reference fixture, plus local Markdown file links.

These are assembly, CPU, and API-contract checks. Stubbed CIO/SIO and the NMI
fixture do not emulate the complete OS or devices. Atari800/Altirra machine
tests and visible/audio inspection remain separate validation stages; see
[workflow.md](workflow.md#validation-matrix).

## Optional Full-Machine Smoke Test

With Atari800 installed and its replacement Altirra OS available:

```sh
/tmp/atari-skills-venv/bin/pip install -r tests/emulator-requirements.txt
/tmp/atari-skills-venv/bin/python scripts/emulator_smoke.py
```

This runs all seven starters under PAL and NTSC, in a temporary 64K XL/XE
configuration. It checks repeated VBI stack/counter behavior, actual DLI color
writes, display/vector restoration, PMG DMA and cleanup, joystick screen output
and exit, POKEY register setup/duration/silencing, and real CIO keyboard
translation/close. Keyboard input uses an injected OS pending scan code;
console exits use GTIA's console-mask write to exercise the normal exit path.

The OS-off example verifies that deferred VBI is skipped while I is set and
runs after I is cleared, with hardware IRQ sources disabled. Disk access is
checked both with no drive (timeout) and with a temporary ATR (success and exact
128-byte sector contents). The tests do not write disk sectors.

Executed locally with MADS 2.1.8, py65 1.2.0, and Atari800 6.0.0 using its
replacement OS and a locally assembled Atari XL OS Rev.2 image (CRC32
`1F9CD270`). Each configuration has seven program cases plus the second disk
case: **32 execution cases** across PAL/NTSC and both OS images. The suite uses
headless video and muted audio; it makes no claim about screenshot appearance
or sound. To test a local original ROM, pass
`--rom /absolute/path/to/xl-os.rom`; no ROM is downloaded or bundled.

## Evidence for the Corrections

| Topic | Evidence / maintained source |
|---|---|
| IOCB offsets, commands, callable OS vector addresses | cc65 equates; [OS vectors](../system/os-vectors-handlers.md) |
| VBI stack balance | Atari XL OS `NMI` saves A/X/Y; `DVNM` restores Y/X/A and RTI; [VBI contract](../system/os-vectors-handlers.md#11-deferred-vbi-via-setvbv--xitvbv) |
| NMI bridge | [Canonical source](../examples/routines/os-nmi-bridge.asm) and ROM-overlay CPU test |
| VCOUNT, NMIST/NMIRES, JVB | Altirra manual §§4.6, 4.8–4.10 and ANTIC reference |
| 65816 arithmetic | WDC datasheet block diagram/instruction table: no intrinsic multiplier or `$4202` registers |
| Quarter-square overflow | Previous 200×100 produced 63520; corrected source passes all byte pairs |
| Duplicate memory/storage chapters | Parent files now route to maintained leaves instead of duplicating their contents |

## Source Provenance

- [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf):
  checked against the **2026-01-02 edition**; cite the chapter/register when
  changing hardware facts. The download URL may later serve a newer edition.
- [cc65 Atari equates](https://github.com/cc65/cc65/blob/8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d/asminc/atari.inc):
  fixture revision `8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d`, including its
  `atari_antic.inc`, `atari_gtia.inc`, and `atari_pokey.inc` register definitions.
  `tests/fixtures/atari-equates.json` records that URL and the numeric values used
  for regression checks. Updates should compare against the new upstream revision.
- [Atari XL OS Rev.2 source](https://github.com/ilmenit/A800-OS-XL-Rev2/tree/fededcbdde9c540fa961213eafd768419b9ac4a7):
  `NMI`, `DVNM`, `IVNM`, and the OS vector/equate tables establish the stack/API
  contract. Do not infer an RTS contract from an interrupt entry's address.
- [WDC W65C816S datasheet](https://www.westerndesigncenter.com/wdc/documentation/w65c816s.pdf):
  **2024-03-13 edition**; distinguish CPU features from host-system peripherals.

## Adding Examples

Provide the input/output/register/flag contract, scratch bytes, table sizes,
decimal-mode requirement, reentrancy, machine requirements, and cleanup behavior.
Keep the assembly in one maintained source and link to it from references.
Mark illustrative fragments as partial; do not call them verified solely because
they assembled. For timing claims, record the measured path, addressing modes,
page crossings, and whether ANTIC DMA/interrupts were included.

The repository also contains legacy catalog/reference snippets outside this
maintained example set. They have not all been assembled or behaviorally checked;
the automated suite does not certify the entire reference collection.
