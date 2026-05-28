---
name: mads
description: >-
  Use for MADS/Mad-Assembler work: Atari 8-bit 6502/65C02/65816 assembly
  syntax, command-line usage, directives, pseudo-commands, labels, macros,
  procedures, structures, arrays, memory banks, relocatable code, and
  SpartaDOS X output.
---

# MADS Assembler

MADS, also called Mad-Assembler, is a cross-assembler commonly used for Atari
8-bit development. Its syntax is close to XASM/QA/FA, with additions for local
and temporary labels, macros, procedures, typed data, virtual and hardware
memory banks, relocatable output, SpartaDOS X files, and WDC 65816 code.

Use this skill when writing, reviewing, porting, or debugging MADS assembly.
Prefer the smallest reference file that answers the question.

## Quick Start

- For command-line assembly, output files, listings, and exit codes, read
  [references/usage.md](references/usage.md).
- For comments, line joining, mnemonic chaining, numbers, strings, expressions,
  and operator precedence, read [references/syntax.md](references/syntax.md).
- For ordinary assembler directives such as `.ORG`, `.BYTE`, `.WORD`, `.DS`,
  `.VAR`, `.ZPVAR`, `.IFDEF`, `.REPT`, `.PRINT`, `.ERROR`, `.LEN`, `.SIZEOF`,
  `.DEFINE`, and `.UNDEF`, read [references/directives.md](references/directives.md).
- For XASM-style pseudo-commands such as `OPT`, `ORG`, `INS`, `ICL`, `DTA`,
  `SIN`, `COS`, `RND`, `IFT`, `ELS`, `ELI`, and `EIF`, read
  [references/pseudo-commands.md](references/pseudo-commands.md).

## Reference Map

### Orientation

- [references/introduction.md](references/introduction.md): what MADS is, how it
  relates to XASM, compilation notes, and MADS vs XASM differences.
- [references/changelog.md](references/changelog.md): full version history from
  the original docs. Load only when a task depends on feature availability by
  MADS version.
- [references/mnemonics.md](references/mnemonics.md): supported 6502, illegal
  6502, 65816, and mnemonic-extension notes.
- [references/cpu-detection.md](references/cpu-detection.md): compile-time CPU
  detection symbols.

### Assembly Control and Syntax

- [references/control.md](references/control.md): high-level assembly control,
  conditional assembly pointers, and zero-page assembly behavior.
- [references/code-generation-directives.md](references/code-generation-directives.md):
  `#IF`, `#WHILE`, and `#CYCLE` code-generation directives.
- [references/directives.md](references/directives.md): dot directives.
- [references/pseudo-commands.md](references/pseudo-commands.md): legacy-style
  pseudo-commands.
- [references/macro-commands.md](references/macro-commands.md): built-in macro
  commands such as `MVA`, `MWA`, `ADW`, `SBW`, branches, increments, moves, and
  compares.

### Names and Scope

- [references/labels.md](references/labels.md): anonymous, local, global,
  temporary, self-modifying, and MAE-style labels.
- [references/local-areas.md](references/local-areas.md): `.LOCAL` / `.ENDL`
  scoped areas.

### Abstractions and Data

- [references/macros.md](references/macros.md): `.MACRO` declarations, parameter
  syntax, generated labels, and calls.
- [references/procedures.md](references/procedures.md): `.PROC` declarations,
  calls, `.REG`/`.VAR`, and typed parameters.
- [references/data-types.md](references/data-types.md): `.STRUCT` and `.ENUM`.
- [references/arrays.md](references/arrays.md): `.ARRAY` declarations and access.
- [references/memory-banks.md](references/memory-banks.md): virtual memory banks
  with `OPT B-` and hardware memory banks with `OPT B+`.

### Linking and Output Formats

- [references/relocatable-code.md](references/relocatable-code.md):
  `.RELOC`, external and public symbols, `.LONGA`, `.LONGI`, and `.LINK`.
- [references/spartadosx.md](references/spartadosx.md): SpartaDOS X executable
  file blocks, relocation/update/definition blocks, and SDX programming notes.

## Authoring Guidance

- Use MADS-native constructs when they clarify Atari 8-bit code: named local
  areas, `.PROC`, `.STRUCT`, `.ARRAY`, and macro commands are expected in MADS
  projects.
- Preserve source compatibility when porting from XASM: check
  [references/introduction.md](references/introduction.md) before changing
  syntax that XASM and MADS treat differently.
- For examples involving 65816 accumulator or index width, verify the relevant
  mode directives in [references/relocatable-code.md](references/relocatable-code.md)
  and mnemonic support in [references/mnemonics.md](references/mnemonics.md).
- When diagnosing assembly output, inspect both the command-line options in
  [references/usage.md](references/usage.md) and the output-affecting `OPT` /
  `ORG` / `INS` / `ICL` / `DTA` behavior in
  [references/pseudo-commands.md](references/pseudo-commands.md).

## Source Transfer Notes

The reference files are copied directly or nearly directly from
`mad-assembler-mkdocs-master/docs/en/docs`. `examples.md` and `projects.md`
were not transferred because they only contain TODO placeholders. The original
`index.md` was transferred as `references/changelog.md` because its useful
content is the MADS change log.
