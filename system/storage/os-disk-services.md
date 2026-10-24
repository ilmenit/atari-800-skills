# OS Disk and Device Services

## §7.10 SIO Peripheral-Side Protocol

A custom SIO peripheral sees a command phase followed by an optional data
phase. A command frame has:

| Byte | Meaning |
|---|---|
| 0 | Device ID and unit |
| 1 | Command byte |
| 2 | `DAUX1` |
| 3 | `DAUX2` |
| 4 | Checksum |

For a write-style command:

1. Wait for SIO COMMAND asserted.
2. Receive the 4-byte command plus checksum.
3. Wait for COMMAND deasserted.
4. If device ID, command, and checksum match, send ACK (`'A'`); otherwise send NAK (`'N'`).
5. Receive the data frame plus checksum.
6. ACK or NAK the data frame.
7. Perform the operation.
8. Send COMPLETE (`'C'`) or ERROR (`'E'`).

Common timing in simple microcontroller implementations is about 1000 us
before ACK/NAK and about 250 us before COMPLETE/ERROR. Treat these as
conservative software delays, not proof that all devices can collapse timing.

## §7.11 DSKINV Disk-Driver Entry

`DSKINV` is the OS disk-driver entry at `$E453`. It fills standard DCB fields
for basic disk operations and then uses `SIOV ($E459)`. Status is returned in
`DSTATS ($0303)` and in `Y`; negative status (`N=1`) means error.

The disk driver uses:

| Variable | Address | Purpose |
|---|---|---|
| `DSKTIM` | `$0246` | Long timeout, mainly formatting |
| `DSCTLN` | `$02D5/$02D6` | Sector size |
| `DCOMND` | `$0302` | Requested disk command |

Supported direct commands:

| Command | Meaning |
|---|---|
| `$21` / `'!'` | format disk |
| `$50` / `'P'` | put sector without verification |
| `$52` / `'R'` | read sector |
| `$53` / `'S'` | read status |
| `$57` / `'W'` | write sector with verification |

Any other command is effectively treated as a read-sector setup by the disk
driver; use a manually prepared DCB and `SIOV` for nonstandard drive commands.

Read/write sector setup:

```asm
        lda #1
        sta DUNIT
        lda #'R'        ; or 'P' / 'W'
        sta DCOMND
        ldx #<buffer
        ldy #>buffer
        stx DBUF
        sty DBUF+1
        ldx #<sector
        ldy #>sector
        stx DAUX1
        sty DAUX2
        jsr DSKINV
        bmi error
```

Read status sets `DSTATS` for read, `DBYT` to 4, `DBUF` to `DVSTAT ($02EA)`,
and timeout to about seven seconds. Formatting uses `DSKTIM`; after a format,
the buffer receives a list of bad sector numbers ending with `$FFFF`, and
`DBYT` returns the list length excluding the terminator.

## §7.12 DOS and SpartaDOS X Command Lines

Several DOSes expose command-line parameter retrieval through the OSS/DOS XL
protocol. Detect it by checking that DOS is loaded, `DOSVEC ($000A)` points
below ROM, and `(DOSVEC)+3` contains opcode `$4C` (`JMP`). The callable
parameter reader is at `(DOSVEC)+3`.

The parameter reader places the next parameter in `COMFNAM` at `(DOSVEC)+33`.
The returned string starts with a device name and ends with EOL `$9B`. The
routine does not by itself report end-of-line; compare the buffer offset
before and after the call to detect that no more parameters were consumed.

SpartaDOS X also provides a richer parsing library:

- `U_SLASH` parses a group of adjacent slash switches as a set, not as a
  sequence of separate ordered tokens.
- `/X /A 23 /Q`, `/XA 23 /Q`, and `/AX 23 /Q` can be equivalent to
  `U_SLASH` for switch detection.
- If a switch such as `/A` requires the following numeric parameter, check
  which switch occurred last before calling `U_GETNUM`.
- In SDX 4.47 and later, `U_SLASH` returns the ATASCII code of the last
  switch in `A`.
- SDX command lines are limited to 64 characters. For persistent option
  sets, parse an environment variable first, then restore and parse the real
  command line.

Environment-variable parse pattern:

1. Save `LBUF` and `BUFOFF`.
2. Call `GETENV` for the variable name.
3. Copy the returned text from the floating-point buffer area to `LBUF`.
4. Set `BUFOFF` to zero and run the same parser used for command-line text.
5. Restore the saved `LBUF` and `BUFOFF`.
6. Parse the actual command-line arguments.

The environment-variable text is constrained by the same 64-character command
buffer limit.

## §7.13 CIO Special Commands by Device

CIO special commands are device-handler specific. Do not assume a command
number has the same meaning across `D:`, `E:`, `P:`, and `S:`.

Common `D:` special commands:

| CMD | Meaning on common DOS handlers |
|---|---|
| `$20` / 32 | rename file |
| `$21` / 33 | delete file |
| `$22` / 34 | DOS-dependent: unerase, lock disk, make directory, or unsupported |
| `$23` / 35 | lock file or directory |
| `$24` / 36 | unlock file or directory |
| `$25` / 37 | POINT / seek |
| `$26` / 38 | NOTE / tell |
| `$27` / 39 | DOS-dependent: get file length or binary load |
| `$28` / 40 | binary load on many DOSes |
| `$29` / 41 | DOS-dependent: binary save, set current directory, or pick directory |
| `$2A` / 42 | make directory |
| `$2B` / 43 | remove directory |
| `$2C` / 44 | change directory |
| `$2D` / 45 | set boot file |
| `$2F` / 47 | get disk info |
| `$30` / 48 | get current directory |
| `$31` / 49 | set attributes on SpartaDOS X-style handlers |
| `$FD-$FF` / 253-255 | formatting variants on some DOSes |

`E:` and `P:` normally have no standard special commands, but XEP80 handlers
add device-specific commands. Typical XEP80 `E:` commands include:

| CMD | Meaning |
|---|---|
| `$14` / 20 | send command |
| `$15` / 21 | set normal or burst transmit mode |
| `$16` / 22 | send input command |
| `$18` / 24 | enable 80-column mode, with optional clear-screen |
| `$19` / 25 | disable 80-column mode |

The graphics-screen `S:` handler implements:

| CMD | Meaning |
|---|---|
| `$11` / 17 | `DRAWTO` using `CRSCOL`, `CRSROW`, and `ATACHR` |
| `$12` / 18 | `FILLTO`, like `DRAWTO` plus horizontal fill using `FILDAT` |

When writing portable DOS code, gate special commands by DOS/handler
detection. If the command is not supported, expect a device error rather than
quiet no-op behavior.
