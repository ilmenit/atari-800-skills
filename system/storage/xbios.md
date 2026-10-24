# xBIOS API Boundary

xBIOS is XXL's relocatable file/directory library and loader. It can operate
without DOS and can use an I/O module that bypasses Atari OS ROM. It is not
the OS SIOV API with a zero-page DCB; writing `$00–$0B` and calling SIOV does
not perform an xBIOS file read.

For a project using xBIOS:

- Identify the installed release, relocation base, buffer, I/O module, and
  reserved memory from that release's package.
- Include its exported equates. Use xBIOS_OPEN_FILE, xBIOS_LOAD_DATA,
  xBIOS_GET_BYTE, or the documented sector entry as appropriate.
- Follow that entry's register/status convention and filename format. Do not
  substitute CIO/SIO error conventions or assume file creation/extension support.
- Keep OS-off interrupt ownership consistent with the selected I/O module.

For ordinary OS sector reads, use [SIO/DCB](sio-disk.md) and the complete
[disk-read example](../../examples/disk-read.asm) instead.

Primary sources: [XXL's xBIOS distribution](https://xxl.atari.pl/) and
[bocianu's xBIOS wrapper/API reference](https://bocianu.gitlab.io/blibs/xbios.html).
Version-specific assembly examples should accompany their matching library.
