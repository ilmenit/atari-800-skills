# Storage Sources

- [Atari XL OS Rev.2 source](https://github.com/ilmenit/A800-OS-XL-Rev2):
  DIO/DSKINV, SIO, CIO, device handlers, and their register/status contracts.
- [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf):
  chapters 9–10 for SIO/peripheral timing and drive behavior.
- [cc65 Atari equates](https://github.com/cc65/cc65/blob/8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d/asminc/atari.inc):
  IOCB/DCB offsets, OS vectors, commands, and returned error codes.
- [MADS upstream](https://github.com/tebe6502/Mad-Assembler): executable examples
  and assembler output formats; use its SDX documentation for relocation blocks.
- [XXL's xBIOS distribution](https://xxl.atari.pl/): use the installed release's
  API, relocation settings, and examples rather than substituting OS DCB calls.

DOS/XIO extensions and peripheral commands are version-dependent. State the
handler/release for a portable-code claim. File-format heuristics should be
checked against representative images, not assumed from a single file size.
