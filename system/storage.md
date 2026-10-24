# Storage, Files, and Loaders

Use the maintained topic files below instead of copying register tables between
chapters. OS CIO and SIO are different APIs; a DOS file, a disk sector, and an
ATR file offset are different address spaces.

- [SIO and disks](storage/sio-disk.md): bus frames, DCB calls, checksums, drive geometry, status.
- [CIO file access](storage/cio-file-access.md): IOCB ownership, OPEN/GET/CLOSE, and free-slot search.
- [XEX and ATR formats](storage/xex-atr-formats.md): load segments, disk headers, and sector offsets.
- [SpartaDOS X](storage/spartadosx.md): relocatable block types.
- [xBIOS](storage/xbios.md): external mini-OS API boundary.
- [Loaders and depackers](storage/loaders-depackers.md): DSKINV boot loaders, relocation, and reversing.
- [OS disk/device services](storage/os-disk-services.md): DSKINV, peripheral-side protocol, and device-specific commands.
- [Sources](storage/notes.md): authoritative references and version boundaries.
- [Runnable disk-read example](../examples/disk-read.asm): read-only sector access with a complete DCB.
