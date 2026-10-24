# CIO File Access

The authoritative [IOCB layout](../os-vectors-handlers.md#3-cio-and-iocb-lifecycle)
uses X = channel * 16, ICHID at offset 0, ICCOM at +2, and ICSTA at +3.
A closed IOCB has **ICHID = $FF**; this is not a status-byte test.

Use [find-free-iocb.asm](../../examples/routines/find-free-iocb.asm): it searches
IOCBs 1–7, returns C clear and X equal to the slot offset, or C set if all are
in use. It does not alter the IOCBs. IOCB0 normally belongs to the screen editor.

For file access:

1. Find a free slot; supply a NUL-terminated name such as `D1:DATA.BIN`.
2. Set ICCOM=3 (OPEN), ICBAL/H=name, ICAX1=4 (read), ICAX2=0.
3. Call CIOV and check Y/negative status before reading data.
4. For byte reads, use ICCOM=7, a buffer pointer, and a positive ICBLL/H length.
5. Close with ICCOM=12 even when a later read fails. Preserve the earlier error
   if the caller needs to report it after CLOSE.

The handler/DOS determines directory format, EOF behavior, and supported XIO
commands. Do not assume CIO carry reports success, or that each channel is
hardwired to a particular device. See the complete [text I/O example](../../examples/text-io.asm)
for OPEN, buffered GET, output, and CLOSE with status checking.

Source: [cc65 Atari OS equates](https://github.com/cc65/cc65/blob/8d86ca7e7ed15300cc4bfaba61a40a3d00f3114d/asminc/atari.inc), IOCB fields and commands.
