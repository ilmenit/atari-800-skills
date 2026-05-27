---
name: atari8bit-cartridges-pbi
description: >-
  Atari 8-bit cartridge windows, cartridge banking, PBI expansion devices,
  internal devices, and reverse-engineering notes.
---

# Cartridges, PBI, and Internal Devices

> **When to load:** The task involves ROM carts, banked carts, PBI devices, IDE/SIDE-like hardware, internal clocks, or device-space reversing.
> **Primary sources:** Altirra hardware chapters on cartridges/PBI/SIO, Atari reference articles on VBXE/APE-Time, and Jindroush hardware notes linked from Gury's reference-card index.

## Cartridge Basics

Atari 8-bit cartridges map ROM into fixed CPU address windows. Reverse them as banked memory devices, not as ordinary XEX files.

Common windows:

| Window | Signal / use |
|---|---|
| `$8000-$9FFF` | Lower 8K cartridge window, selected by `S4`; presence signaled by `RD4` |
| `$A000-$BFFF` | Upper 8K cartridge window, selected by `S5`; presence signaled by `RD5` |
| `$BFFA-$BFFF` | cartridge vectors/signature area in many formats |
| `$D500-$D5FF` | `CCTL` cartridge control area, commonly used for bank switching or cart hardware registers |

Reversing workflow:

1. Identify ROM size and visible initial bank.
2. Locate cartridge vectors/signature bytes.
3. Watch writes to `$D5xx` and any documented control range.
4. Build a bank-switch table before linear disassembly.
5. Treat code reached after a bank write as a different address-space state.

## Banked Cartridge Rules

- A CPU address is not enough to identify code; record `(bank, address)`.
- Bank registers can be write-only; infer current bank from the last write.
- Interrupt handlers must live in always-visible ROM/RAM or restore the expected bank before executing.
- Self-modifying code cannot modify ROM, but can copy routines to RAM and patch the RAM copy.
- Reads or writes to `$D5xx` may have side effects even if the value is ignored; log the address low nibble and address bits, not only the data bus value.
- Some carts turn themselves off by clearing `RD4`/`RD5`; after an off command, code may continue from RAM or OS vectors.

Common cartridge families useful for reversing:

| Family | Bank-control rule |
|---|---|
| OSS 16K | 4K banks: fixed bank in `$B000-$BFFF`, selectable bank in `$A000-$AFFF`; control often depends on address bits A0/A3. |
| SpartaDOS X / Diamond / Express | 8 x 8K banks in `$A000-$BFFF`; base ranges differ, `base+0..7` selects bank and `base+8..F` turns cart off. |
| XEGS | Last 8K bank fixed at `$A000-$BFFF`; banks 0..N-1 switch into `$8000-$9FFF` by writing bank number to `$D500-$D5FF`. |
| R-Time 8 | Pass-through cartridge with RTC hardware; reads are often enough for clock access. |

## PBI Overview

The Parallel Bus Interface exposes expansion hardware on XL-class systems. PBI devices can add ROM handlers, disk interfaces, memory, clocks, or other peripherals.

Key hardware behavior:

| Signal | Meaning for software/reversing |
|---|---|
| `EXTENB` | External decoder enable; high when address is in a PBI-allowed device range. |
| `EXTSEL` | Selected device pulls low when it owns the addressed range. |
| `MPD` | Math-pack disable; lets a device provide handler ROM in `$D800-$DFFF`. |
| `RDY` | A slow device can extend a CPU bus cycle by pulling it low. |
| `IRQ` | PBI devices can interrupt the CPU; preserve/identify IRQ vectors when tracing. |
| `AUDIO IN` | Expansion audio can mix into the computer audio path. |

600XL and 800XL both expose PBI, but 600XL has +5V lines used by the 1064 memory expansion. Most XE systems expose the reduced ECI connector plus the cartridge connector instead of a full PBI; ECI carries selected PBI signals such as `EXTSEL`, `IRQ`, `HALT`, `D1XX`, `MPD`, `REF`, and audio in.

Agent rules:

- If code scans device IDs or handler tables, treat it as expansion discovery.
- If code patches CIO/SIO behavior after reset, check for PBI-resident handlers.
- If a program depends on PBI hardware, document fallback behavior or requirement.

## Internal Devices and Clocks

Internal or pseudo-internal devices can appear through OS vectors, PBI, or SIO commands.

Examples in this corpus:

| Device | Skill location |
|---|---|
| APE-Time RTC | `exotics/sophia-rapidus.md` |
| VBXE | `exotics/vbxe.md` |
| Sophia | `exotics/sophia-rapidus.md` |
| XEP80 and accessories | `system/input.md` plus Altirra chapter 7 |

## Reverse-Engineering Notes

- Hardware control ranges often decode incompletely and mirror across address ranges.
- Some devices require timing gaps after commands; do not collapse polling loops unless the hardware docs say it is safe.
- For emulation-targeted code, note whether Altirra supports the device and whether real hardware timing has been tested.
