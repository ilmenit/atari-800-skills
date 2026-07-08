# FujiNet Programming Reference for Atari 8-bit

> **Type:** Topic guide and code reference
> **Purpose:** Detailed SIO/CIO specifications, registers, JSON parsing protocols, virtual R: modem extensions, and ready-to-use MADS assembly examples for FujiNet networking.

FujiNet is a multi-peripheral emulator and network adapter for vintage systems. On the Atari 8-bit, it allows programs to offload TCP/IP, UDP, HTTP, FTP, SSH, and JSON parsing to an onboard ESP32 coprocessor.

---

## 1. FujiNet Architecture

### Device IDs and Addresses
- **$70 (FujiNet Control Device):** Used for configuration, WiFi scanning, SSID setups, TNFS host and disk mounting, directory browser, app-key storage, Base64/Hash/QR utility operations.
- **$71–$78 (FujiNet Network Devices - `N1:` to `N8:`):** Allocated for network socket and stream operations. Standard `N:` defaults to unit 1 (`N1:`, ID `$71`).
- **$50–$53 (FujiNet R: Devices - `R1:` to `R4:`):** Serial/Modem emulation interface.
- **$45 (Clock / APETime Device):** Emulates the APETime clock, providing date and time in various formats.

### Communication Vectors
1. **CIO (Central Input/Output):** Recommended for most programs. Accessed using the OS `CIOV` vector (`$E456`) and the `N:` device handler.
2. **SIO (Serial Input/Output):** Directly bypasses the CIO handler using the `SIOV` vector (`$E459`). Essential if the resident DOS or application overwrites the `N:` handler memory space or when reaching the Control `$70` or Clock `$45` devices which are SIO-only.

---

## 2. CIO Programming (`N:` Device)

Standard network operations are mapped to the Atari's Input/Output Control Blocks (IOCBs, `$0340` to `$03BF`, 16 bytes per block).

### IOCB Register Mappings
- `ICCOM` (`$0342`): CIO Command.
- `ICBAL`/`ICBAH` (`$0344` / `$0345`): Buffer Address (pointer to URI/data).
- `ICBLL`/`ICBLH` (`$0348` / `$0349`): Buffer Length (for read/write operations).
- `ICAX1` (`$034A`): Open Mode.
- `ICAX2` (`$034B`): Auxiliary 2 (Translation Mode).

### Connection Modes (`ICAX1`)
When executing an `OPEN` command (`$03`), set `ICAX1` according to the required network mode:
- **`$04` (Read):** Read-only client connection (HTTP GET, socket read).
- **`$06` (Directory Read):** Used to read file/directory lists.
- **`$08` (Write):** Write-only client connection (HTTP PUT, socket write).
- **`$09` (Append):** Append to existing file.
- **`$0C` (Update / Read+Write):** Bidirectional client socket (standard TCP/UDP/HTTP), also used for TCP Listen Server.
- **`$0D` (HTTP POST):** Open connection for posting payloads.
- **`$05` (HTTP DELETE):** Request resource deletion.

### Line Translation Options (`ICAX2`)
FujiNet translates carriage returns and line feeds dynamically to match Atari's EOL character (`$9B`):
- **`$00` (Raw/Binary Mode):** No translation (essential for binary transfers, raw TCP, UDP datagrams).
- **`$01` (CR Mode):** Carriage Return (`$0D`) translated to EOL (`$9B`).
- **`$02` (LF Mode):** Line Feed (`$0A`) translated to EOL (`$9B`).
- **`$03` (CR/LF Mode):** CR/LF sequence (`$0D$0A`) translated to EOL (`$9B`).

### Protocol URIs
The filename passed to the `OPEN` command determines the protocol and endpoint:
- **TCP Client:** `N:TCP://<host>:<port>/`
- **TCP Server:** `N:TCP://:<port>/` (No host specifies a listening server socket)
- **UDP Client:** `N:UDP://<host>:<port>/`
- **HTTP/HTTPS:** `N:HTTP://<host>[:port]/<path>` or `N:HTTPS://...`

### CIO / XIO Special Commands
For operations beyond reading and writing, CIO special commands are sent via `XIO cmd,#ch,aux1,aux2,"Nx:..."`. 
*Note: The XIO command number is identical to the SIO command byte.*

| XIO Cmd | SIO Cmd (Hex) | Char | Description |
|:---:|:---:|:---:|---|
| **15** | — | — | Flush NDEV transmit buffer immediately (handled locally by NDEV) |
| **32** | `$20` | ` ` | Rename file. Filespec format: `"Nx:from_name,to_name"` |
| **33** | `$21` | `!` | Delete file |
| **35** | `$23` | `#` | Lock file (make read-only) |
| **36** | `$24` | `$` | Unlock file |
| **42** | `$2A` | `*` | Make directory |
| **43** | `$2B` | `+` | Remove directory |
| **44** | `$2C` | `,` | Change directory (sets active path prefix for the channel) |
| **48** | `$30` | `0` | Get current directory (reads active path prefix back) |
| **65** | `$41` | `A` | TCP: Accept waiting client on listening channel |
| **68** | `$44` | `D` | UDP: Set destination `"host:port"` for outgoing packets |
| **80** | `$50` | `P` | JSON: Parse JSON document just read |
| **81** | `$51` | `Q` | JSON: Query path (value becomes readable via standard inputs) |
| **84** | `$54` | `T` | Set translation mode (aux2 = 0/1/2/3) |
| **90** | `$5A` | `Z` | Set interrupt/status poll rate (aux1 = rate low, aux2 = rate high) |
| **99** | `$63` | `c` | TCP: Close current client, keep listening |
| **251** | `$FB` | — | Set JSON parameter (aux1 selects parameter index) |
| **252** | `$FC` | — | Set channel mode (aux2: 0 = protocol, 1 = JSON) |
| **253** | `$FD` | — | Set username (for FTP, SMB) before opening connection |
| **254** | `$FE` | — | Set password (for FTP, SMB) before opening connection |

---

## 3. JSON Parsing API (CIO / XIO)

FujiNet offloads JSON parsing to the ESP32. The Atari fetches the JSON, tells FujiNet to parse it, and queries specific paths using standard `XIO` (CIO Special) commands.

### JSON Lifecycle Steps
1. **Open Stream:** Open a channel to the API URL (`ICAX1` = `$0C`, `ICAX2` = `$00`).
2. **Enable JSON Mode:** Run `XIO 252` on the channel with `ICAX2` = `1`.
3. **Parse JSON:** Run `XIO 80` (`XIO ASC("P")`) on the channel. This triggers parsing on the ESP32.
4. **Query Path:** Run `XIO 81` (`XIO ASC("Q")`) with the target JSON path in the filename buffer (e.g., `N:/weather/temp`).
5. **Read Result:** Read the queried value using CIO Read (`GET BYTE` or `GET RECORD`).

---

## 4. Direct SIO Protocol Reference

For custom handlers or bare-metal execution, use standard SIO command blocks via `SIOV` (`$E459`).

### SIO Device Control Block (DCB) Structure
| Address | Name | Description |
|---|---|---|
| `$0300` | `DDEVID` | SIO Device ID (`$71`–`$78` for `N1:`–`N8:`, `$70` for Control, `$45` for Clock) |
| `$0301` | `DUNIT`  | Device Unit (typically `$01`) |
| `$0302` | `DCOMND` | SIO Command byte |
| `$0303` | `DSTATS` | Before call: Data Direction (`$40` = Read, `$80` = Write, `$00` = No data). After call: Result code. |
| `$0304` | `DBUFLO` | Data Buffer Address (Low) |
| `$0305` | `DBUFHI` | Data Buffer Address (High) |
| `$0306` | `DTIMLO` | Timeout (seconds, e.g., `$1F` = 31 seconds is recommended) |
| `$0308` | `DBYTLO` | Bytes to Transfer (Low) |
| `$0309` | `DBYTHI` | Bytes to Transfer (High) |
| `$030A` | `DAUX1`  | Auxiliary Byte 1 (parameters specific to command) |
| `$030B` | `DAUX2`  | Auxiliary Byte 2 (parameters specific to command) |

### SIO Commands for Device ID $70 (FujiNet Control)
Device `$70` handles configuration, WiFi settings, local time, and TNFS slot mounting.

| Command | Hex | Direction | Parameters & Payload Details |
|:---:|:---:|:---:|---|
| `Test` | `$00` | `$00` | Check if FujiNet is online |
| `Scan Networks` | `$FD` | `$40` | Kick off scan. Reads 1 byte (count of APs found). |
| `Get Scan Result` | `$FC` | `$40` | `DAUX1` = AP index (0-based). Reads 33 bytes (32-byte SSID + 1-byte signed RSSI). |
| `Set SSID` | `$FB` | `$80` | `DAUX1` = 1 (save to config). Payload: SSID (32 bytes) + Password (64 bytes). |
| `Get SSID` | `$FE` | `$40` | Reads 96 bytes (SSID + Password) of stored network. |
| `Get WiFi Status` | `$FA` | `$40` | Reads 1 byte: `3` = connected, `6` = not connected. |
| `Get Adapter Config` | `$E8` | `$40` | Reads 139 bytes of layout: SSID (32), hostname (64), local IP (4), gateway (4), netmask (4), DNS (4), MAC (6), BSSID (6), firmware version string (15). |
| `Read Host Slots` | `$F4` | `$40` | Reads 256 bytes (8 × 32-byte host slot names). |
| `Write Host Slots`| `$F3` | `$80` | Sends 256 bytes (8 × 32-byte host slot names) to configure slots. |
| `Read Device Slots`| `$F2` | `$40` | Reads 304 bytes (8 × 38-byte slot array). Record is: host slot (1), mode (1: 1=RO, 2=RW), filename (36). |
| `Write Device Slots`| `$F1`| `$80` | Sends 304 bytes (8 × 38-byte slot array). |
| `Mount Host` | `$F9` | `$00` | `DAUX1` = host slot to mount. |
| `Unmount Host` | `$E6` | `$00` | `DAUX1` = host slot to unmount. |
| `Mount Image` | `$F8` | `$00` | `DAUX1` = disk slot, `DAUX2` = mode (1 = RO, 2 = RW). |
| `Unmount Image` | `$E9` | `$00` | `DAUX1` = disk slot. |
| `Mount All` | `$D7` | `$00` | Mounts all configured slots. |
| `Set Dev Filename`| `$E2` | `$80` | `DAUX1` = slot, `DAUX2` = `(host << 4) \| mode`. Payload = filename. |
| `Get Dev Filename`| `$A0–$A7`| `$40` | `$A0 + slot` (0 to 7) queries and reads the path back. |
| `New Blank Disk` | `$E7` | `$80` | Payload (262 bytes): sector count (2), sector size (2: 128/256/512), host slot (1), disk slot (1), filename (256). |
| `Open Directory` | `$F7` | `$80` | `DAUX1` = host slot. Payload: path + NUL + optional filter. |
| `Read Dir Entry` | `$F6` | `$40` | `DAUX1` = max len, `DAUX2` = flags (`$80` appends packed date/size/flags). Reads one entry (first byte `$7F` is EOF). |
| `Close Directory`| `$F5` | `$00` | Closes active directory browser session. |
| `Get Position` | `$E5` | `$40` | Reads current directory position (2 bytes) for paging. |
| `Set Position` | `$E4` | `$00` | `DAUX1`/`DAUX2` = position to seek to. |
| `Open App Key` | `$DC` | `$80` | Payload (5 bytes): creator id (2, low first), app id (1), key id (1), mode (1: 0=Read, 1=Write). |
| `Write App Key` | `$DE` | `$80` | `DAUX1`/`DAUX2` = length (up to 64 bytes). Payload: data bytes. |
| `Read App Key` | `$DD` | `$40` | Reads 2-byte length followed by data bytes. |
| `Close App Key` | `$DB` | `$00` | Closes active key. |
| `Get Time` | `$D2` | `$40` | Reads 7-byte binary date/time: century (1), year (1), month (1), day (1), hour (1), minute (1), second (1). |
| `Random Number` | `$D3` | `$40` | Reads 4 hardware-generated random bytes. |
| `GUID Gen` | `$BB` | `$40` | Reads 36-character GUID string. |
| `Disable CONFIG Boot`| `$D9`| `$00` | `DAUX1` = 0/1 to disable/enable CONFIG boot. |
| `Set Boot Mode` | `$D6` | `$00` | `DAUX1` = boot mode. |
| `Enable Device` | `$D5` | `$00` | `DAUX1` = SIO device ID to enable. |
| `Disable Device` | `$D4` | `$00` | `DAUX1` = SIO device ID to disable. |
| `Device Status` | `$D1` | `$40` | Reads 1 byte showing enabled status. |
| `Copy File` | `$D8` | `$80` | Copies file between hosts. Payload = source and destination slots + specs. |
| `Set Baud Rate` | `$EB` | `$00` | `DAUX1` = index (0 = 19200 ... 6 = 921600). |
| `Set HSIO Index` | `$E3` | `$00` | `DAUX1` = HSIO rate index, `DAUX2` = 1 to save. |
| `Reset FujiNet` | `$FF` | `$00` | Performs hardware reboot of the ESP32. |

#### App Key / Hash / Base64 / QR Code Families
- **Hash commands:** `$C8` input, `$C7` compute, `$C6` length, `$C5` output, `$C2` clear. Hash algorithm is passed in the byte after `$C7` (0 = MD5, 1 = SHA-1, 2 = SHA-256, 3 = SHA-512).
- **Base64 encode:** `$D0` input, `$CF` compute, `$CE` length, `$CD` output.
- **Base64 decode:** `$CC` input, `$CB` compute, `$CA` length, `$C9` output.
- **QR Code:** `$BC` input, `$BD` encode, `$BE` length, `$BF` output (reads raw QR bitmap bytes).

### SIO Commands for Device IDs $71 to $78 (Network/N: Devices)
Used to directly control individual sockets and network streams.

| Command | Char | Hex | Direction | Description |
|:---:|:---:|:---:|:---:|---|
| `Open` | `'O'` | `$4F` | `$80` | Open network connection. `DAUX1` = mode, `DAUX2` = trans. Payload: 256-byte padded URI. |
| `Close` | `'C'` | `$43` | `$00` | Close network connection. |
| `Read` | `'R'` | `$52` | `$40` | Read bytes. `DAUX1/2` = 16-bit count (low/high). `DBYT` = count. *Must check STATUS first.* |
| `Write` | `'W'` | `$57` | `$80` | Write bytes. `DAUX1/2` = 16-bit count. `DBYT` = count. |
| `Status` | `'S'` | `$53` | `$40` | Channel status. Reads 4 bytes: `0-1` bytes waiting, `2` connection up (1/0), `3` error code. |
| `Get Error` | `'E'` | `$45` | `$40` | Returns detailed error string. |
| `Parse JSON` | `'P'` | `$50` | `$00` | Instructs ESP32 to parse downloaded JSON data. |
| `Query JSON` | `'Q'` | `$51` | `$80` | Queries path in parsed JSON. Payload: JSONPath query string. `DAUX2` = trans. |
| `Set Translation` | `'T'` | `$54` | `$00` | Changes translation mode via `DAUX2` (0/1/2/3). |
| `Set Channel Mode` | | `$FC` | `$00` | Configure channel mode (`DAUX2`: 0 = protocol, 1 = JSON). |
| `Set Interrupt Rate`| `'Z'` | `$5A` | `$00` | Set status poll interrupt rate in ms via `DAUX1` (low) / `DAUX2` (high). |
| `Username` | | `$FD` | `$80` | Set username credential payload before `OPEN`. |
| `Password` | | `$FE` | `$80` | Set password credential payload before `OPEN`. |
| `Rename File` | | `$20` | `$80` | Network filesystems: rename file (Payload: `"from,to"`). |
| `Delete File` | | `$21` | `$80` | Network filesystems: delete file (Payload: spec). |
| `Lock File` | `'#'` | `$23` | `$80` | Network filesystems: lock file (read-only). |
| `Unlock File` | `'$'` | `$24` | `$80` | Network filesystems: unlock file. |
| `Make Directory` | `'*'` | `$2A` | `$80` | Network filesystems: make directory. |
| `Remove Directory`| `'+'` | `$2B` | `$80` | Network filesystems: remove directory. |
| `Change Directory` | `','` | `$2C` | `$80` | Network filesystems: change active directory (Payload: new path). |
| `Get Current Dir` | `'0'` | `$30` | `$40` | Network filesystems: read current active path prefix into `DBUF`. |
| `Inquire Direction`| | `$FF` | `$40`/`$80`| Ask what direction a command uses. `DAUX1` = command. Returns 1 byte. |

#### Protocol-Specific Extensions
- **TCP Accept (`'A'` / `$41`):** Accept incoming server client on listening socket.
- **TCP Close Client (`'c'` / `$63`):** Terminates client connection while keeping the server socket listening.
- **UDP Destination (`'D'` / `$44`):** Sets target IP/port for outgoing UDP packets.
- **UDP Get Remote (`'r'` / `$72`):** Reads the address of the last datagram's sender into `DBUF`. (SIO only).

---

### SIO Commands for Device ID $45 (Clock / APETime Device)
FujiNet emulates the APETime clock at SIO bus ID `$45`. It offers the current NTP time pre-formatted in various formats depending on the command byte.

| Command | Hex | Direction | Description |
|:---:|:---:|:---:|---|
| `Get APETime Binary` | `$93` | `$40` | Reads 6 bytes: `Day Month Year Hour Minute Second` (binary). |
| `Get Atari Binary` | `$41` (`'A'`) | `$40` | Reads Atari OS-native binary time format. |
| `Get ISO Local` | `$49` (`'I'`) | `$40` | Reads ISO-8601 local time string. |
| `Get ISO UTC` | `$5A` (`'Z'`) | `$40` | Reads ISO-8601 UTC time string. |
| `Get ProDOS Time` | `$50` (`'P'`) | `$40` | Reads ProDOS format date/time. |
| `Set Time Zone` | `$99` | `$80` | Sends timezone definition string. |

---

## 5. Virtual R: Modem Extensions (Device $50–$53)

FujiNet emulates an Atari 850 interface / R: device, enabling legacy BBS software and terminal clients to work over TCP/IP seamlessly.

### Additional R: Commands (SIO Level)
- **`'L'` (`$4C`) - Listen:** Binds and listens on a specified TCP port for incoming BBS callers.
- **`'M'` (`$4D`) - Unlisten:** Closes the listening TCP port.
- **`'N'` (`$4E`) - Toggle Baud Rate Lock:** Locks/unlocks the virtual baud rate, preventing subsequent `CONFIGURE` calls from resetting the connection speed.

---

## 6. HTTP/HTTPS Protocol & BASIC Integration

When programming HTTP clients using the `N:` handler, the ESP32 manages TLS/SSL handshakes, redirection, and packet fragmentation.

### HTTP Open Modes
Using `OPEN #iocb, mode, aux2, "N:HTTP://..."`:
- **Mode 4 (`ICAX1` = `$04`):** Standard HTTP GET (read-only).
- **Mode 12 (`ICAX1` = `$0C`):** Standard HTTP GET / read-write socket.
- **Mode 13 (`ICAX1` = `$0D`):** HTTP GET/POST with raw header management. Setting headers requires using `PUT` commands to send headers before fetching payload.
- **Mode 5 (`ICAX1` = `$05`):** HTTP DELETE.
- **Aux2 (`ICAX2`):** Sets EOL translations (typically `2` for LF to EOL or `3` for CR/LF to EOL).

### Using HTTP/HTTPS from BASIC
```basic
10 REM Download raw file
20 OPEN #1,4,0,"N:HTTPS://fujinet.online/test.txt"
30 TRAP 60
40 GET #1,C:PUT #16,C:GOTO 40
50 CLOSE #1:END
60 CLOSE #1:? "EOF OR ERROR":END
```

---

## 7. MADS Assembly Examples

### Example 1: HTTP GET Request (CIO-based)
Downloads raw content from a URL via the `N:` device using CIO.

```mads
; Atari OS Equates
ICHID   = $0340
ICCOM   = $0342
ICSRN   = $0343
ICBAL   = $0344
ICBAH   = $0345
ICBLL   = $0348
ICBLH   = $0349
ICAX1   = $034A
ICAX2   = $034B

CIOV    = $E456

; CIO Command Constants
CMD_OPEN  = $03
CMD_CLOSE = $0C
CMD_GETBYT = $07

        org $2000

main
        ldx #$10            ; Use IOCB #1 (Index = $10)

        ; 1. Close IOCB #1 just in case
        lda #CMD_CLOSE
        sta ICCOM,x
        jsr CIOV

        ; 2. Open Network Stream
        lda #CMD_OPEN
        sta ICCOM,x
        lda #<url_str
        sta ICBAL,x
        lda #>url_str
        sta ICBAH,x
        lda #$0C            ; ICAX1: Read/Write (Update)
        sta ICAX1,x
        lda #$00            ; ICAX2: Raw mode (no translation)
        sta ICAX2,x
        jsr CIOV
        bmi io_error        ; Status in Y, negative indicates error

read_loop
        ; 3. Read bytes one by one
        lda #CMD_GETBYT
        sta ICCOM,x
        jsr CIOV
        bmi check_eof

        ; Process byte in accumulator (A)
        ; E.g., print to screen (CIO write to E:)
        jsr print_char
        jmp read_loop

check_eof
        cpy #136            ; Status 136 = EOF
        beq close_conn

io_error
        ; Handle IO errors here (status in Y)
        rts

close_conn
        lda #CMD_CLOSE
        sta ICCOM,x
        jsr CIOV
        rts

; Print character in Accumulator to E:
print_char
        ldy #$00            ; Use IOCB #0 for screen/editor
        sta $0342,y         ; Put byte command (actually use CMD_PUTBYT = $0B)
        lda #$0B
        sta $0342,y
        lda #0
        sta $0348,y         ; Buffer len = 0 for single byte
        sta $0349,y
        lda $2000           ; dummy read or restore character
        lda #0              ; print character from A (needs setup depending on E: state)
        ; For simplicity, write directly to screen memory or call OS routine:
        jsr $F2B0           ; OS print character routine (put byte to screen)
        rts

url_str .byte 'N:HTTP://fujinet.online/test.txt',$9B
```

### Example 2: Parsing JSON API Response (SIO-based)
Fetches JSON from the Coinbase API via raw SIO bus commands (bypassing the resident `N:` driver handler), parses it on the ESP32 coprocessor, and queries the BTC price.

```mads
; SIO DCB Registers
DDEVIC  = $0300  ; Device ID
DUNIT   = $0301  ; Unit number
DCOMND  = $0302  ; Command byte
DSTATS  = $0303  ; Data direction / status
DBUFLO  = $0304  ; Buffer pointer (Low)
DBUFHI  = $0305  ; Buffer pointer (High)
DTIMLO  = $0306  ; Timeout (seconds)
DBYTLO  = $0308  ; Buffer length (Low)
DBYTHI  = $0309  ; Buffer length (High)
DAUX1   = $030A  ; Auxiliary 1
DAUX2   = $030B  ; Auxiliary 2

SIOV    = $E459  ; SIO Vector
DVSTAT  = $02EA  ; OS SIO Status Buffer (4 bytes, populated by SIO Status CMD $53)

        org $2000

get_price
        ; 1. Close connection just in case
        jsr close_sio_conn

        ; 2. Open HTTP connection to JSON source
        lda #$4F            ; 'O' (Open)
        sta DCOMND
        lda #$80            ; DSTATS: Write (Atari -> FujiNet)
        sta DSTATS
        lda #<api_url
        sta DBUFLO
        lda #>api_url
        sta DBUFHI
        lda #0              ; Buffer size must be exactly 256 bytes
        sta DBYTLO
        lda #1
        sta DBYTHI
        lda #$0C            ; DAUX1: Read/Write (Update)
        sta DAUX1
        lda #$00            ; DAUX2: Raw mode
        sta DAUX2
        jsr do_sio
        cpy #$01
        bne err             ; If Y is not $01, it's an error

        ; 3. Enable JSON parser on the channel (Set Channel Mode $FC)
        lda #$FC            ; $FC = NETCMD_CHANNEL_MODE
        sta DCOMND
        lda #$00            ; DSTATS: No data transfer
        sta DSTATS
        sta DBUFLO
        sta DBUFHI
        sta DBYTLO
        sta DBYTHI
        lda #$0C            ; DAUX1: 12
        sta DAUX1
        lda #$01            ; DAUX2: 1 = JSON mode
        sta DAUX2
        jsr do_sio
        cpy #$01
        bne err

        ; 3.5. Enable ATASCII translation ('T' / $54)
        lda #$54            ; 'T' (Translation)
        sta DCOMND
        lda #$00            ; DSTATS: No data transfer
        sta DSTATS
        sta DBUFLO
        sta DBUFHI
        sta DBYTLO
        sta DBYTHI
        lda #$0C            ; DAUX1: 12
        sta DAUX1
        lda #$01            ; DAUX2: 1 = ATASCII
        sta DAUX2
        jsr do_sio
        cpy #$01
        bne err

        ; 4. Instruct FujiNet to parse the HTTP content ('P' / $50)
        lda #$50            ; $50 = NETCMD_PARSE
        sta DCOMND
        lda #$00            ; DSTATS: No data transfer
        sta DSTATS
        sta DBUFLO
        sta DBUFHI
        sta DBYTLO
        sta DBYTHI
        lda #$0C            ; DAUX1: 12
        sta DAUX1
        lda #$00            ; DAUX2: 0
        sta DAUX2
        jsr do_sio
        cpy #$01
        bne err

        ; 5. Query the JSON path ('Q' / $51)
        lda #$51            ; 'Q' (Query JSON)
        sta DCOMND
        lda #$80            ; DSTATS: Write (Atari -> FujiNet)
        sta DSTATS
        lda #<json_path
        sta DBUFLO
        lda #>json_path
        sta DBUFHI
        lda #0              ; Buffer size must be exactly 256 bytes
        sta DBYTLO
        lda #1
        sta DBYTHI
        lda #$0C            ; DAUX1: 12
        sta DAUX1
        lda #$00            ; DAUX2: 0
        sta DAUX2
        jsr do_sio
        cpy #$01
        bne err

        ; 6. Get status to determine length of the queried value ('S' / $53)
        lda #$53            ; 'S' (Status)
        sta DCOMND
        lda #$40            ; DSTATS: Read (FujiNet -> Atari)
        sta DSTATS
        lda #<DVSTAT        ; CRITICAL: Must point DBUFLO/HI to DVSTAT!
        sta DBUFLO
        lda #>DVSTAT
        sta DBUFHI
        lda #4              ; Status always returns 4 bytes
        sta DBYTLO
        lda #0
        sta DBYTHI
        lda #$0C            ; DAUX1: 12
        sta DAUX1
        lda #$00            ; DAUX2: 0
        sta DAUX2
        jsr do_sio
        cpy #$01
        bne err

        ; Ensure there are bytes waiting (stored automatically by SIO in DVSTAT)
        lda DVSTAT          ; Bytes waiting Low
        ora DVSTAT+1        ; Bytes waiting High
        beq err             ; Zero bytes indicates no data or error

        ; 7. Read the parsed string response ('R' / $52) with dynamic size
        lda #$52            ; 'R' (Read)
        sta DCOMND
        lda #$40            ; DSTATS: Read (FujiNet -> Atari)
        sta DSTATS
        lda #<buffer
        sta DBUFLO
        lda #>buffer
        sta DBUFHI
        lda DVSTAT          ; Dynamic size from DVSTAT!
        sta DBYTLO
        sta DAUX1           ; CRITICAL: FujiNet MUST know how many bytes to send
        lda DVSTAT+1
        sta DBYTHI
        sta DAUX2           ; CRITICAL: FujiNet MUST know how many bytes to send
        jsr do_sio
        cpy #$01
        bne err

        ; Success: buffer contains the target value string
        jsr close_sio_conn
        rts

err
        jsr close_sio_conn
        rts

; SIO invocation helper
do_sio
        lda #$71            ; DDEVIC: FujiNet Network Device 1 ($71)
        sta DDEVIC
        lda #$01            ; DUNIT: Unit 1
        sta DUNIT
        lda #$0F            ; DTIMLO: 15 seconds
        sta DTIMLO
        jsr SIOV
        rts

; Close connection SIO command
close_sio_conn
        lda #$43            ; 'C' (Close)
        sta DCOMND
        lda #$00            ; DSTATS: No data transfer
        sta DSTATS
        sta DBUFLO
        sta DBUFHI
        sta DBYTLO
        sta DBYTHI
        lda #$0C
        sta DAUX1
        lda #$00
        sta DAUX2
        jsr do_sio
        rts

api_url       .byte 'N:HTTPS://api.coinbase.com/v2/prices/spot',$9B
              .ds 256 - (* - api_url)

json_path     .byte 'N:/data/amount',$9B
              .ds 256 - (* - json_path)

buffer        .ds 256
```

### Example 3: Non-blocking TCP Sockets (Status Check)
Checks if bytes are available to read using `STATUS` before executing a blocking read.

```mads
; Equates
ICCOM   = $0342
ICSRN   = $0343
ICBAL   = $0344
ICBAH   = $0345
CIOV    = $E456

CMD_STATUS = $0D
DVSTAT     = $02EA  ; OS Device Status Buffer (4 bytes)

IOCB_IDX   = $20    ; IOCB #2

check_tcp_data
        ldx #IOCB_IDX

        ; Call STATUS CIO command
        lda #CMD_STATUS
        sta ICCOM,x
        jsr CIOV
        bmi conn_error

        ; FujiNet populates DVSTAT status buffer:
        ; DVSTAT+0: Network connection status (1 = connected, 0 = disconnected)
        ; DVSTAT+1: Bytes available to read (Low)
        ; DVSTAT+2: Bytes available to read (High)
        ; DVSTAT+3: Last error code
        
        lda DVSTAT
        beq disconnected

        lda DVSTAT+2        ; Check bytes high byte
        bne data_available
        lda DVSTAT+1        ; Check bytes low byte
        bne data_available

no_data
        sec                 ; Set carry = no data
        rts

data_available
        clc                 ; Clear carry = data is waiting
        rts

disconnected
        ; Handle disconnect
        rts

conn_error
        rts
```

---

## 8. Simple NetCat Program Logic

A standard "NetCat" pattern in Atari BASIC connects to a TCP endpoint and creates a non-blocking terminal bridge between the keyboard (`K:`) and the socket (`N1:`).

```basic
100 OPEN #1,12,3,"N1:TCP://BBS.FOZZTEXX.NET/":OPEN #2,4,0,"K:"
101 TRAP 140
110 IF PEEK(764)<>255 THEN GET #2,K:PUT #1,K:XIO 15,#1,12,3,"N:"
120 STATUS #1,A:BW=PEEK(747)*256+PEEK(746):IF BW=0 THEN 110
130 FOR M=1 TO BW:GET #1,C:PUT #16,C:NEXT M:GOTO 110
140 CLOSE #1:? "DISCONNECTED.":END
```
- **Line 110:** Checks keypress buffer. If a key is hit, reads from `K:`, writes to `N1:`, and calls `XIO 15` (Flush).
- **Line 120:** Queries socket status. Computes bytes waiting using `DVSTAT` low/high bytes (`PEEK(747)*256 + PEEK(746)`).
- **Line 130:** Reads exactly the number of waiting bytes and prints them to the editor screen (`#16`).

---

## 9. Optimization and Caveats

### Connection Timeouts
Network operations depend on external servers. Set appropriate SIO timeouts (default is usually 7 seconds). For long HTTP requests, ensure the timeout is extended by modifying `DTIMLO` (`$0306`) in raw SIO blocks, or use non-blocking status queries.

### NDEV 128-Byte Receive Cap
The resident `N:` handler (NDEV) receive and transmit buffers are 128 bytes each, and NDEV caps a single read at 127 bytes. While high-level programs using `INPUT` or `GET` inside loops do not notice this (the handler automatically loops to read incoming streams), it means NDEV cannot return a large block (e.g. 512 bytes) in a single CIO call. For high-speed bulk data transfers, direct SIO reads (`$52` on the low road) bypass this buffer limit and are significantly faster.

### Page boundaries and SIO Buffers
Like all Atari SIO transactions, direct SIO buffers passed to `DBUFLO/DBUFHI` should avoid crossing page boundaries if executing under systems with custom SIO software that requires strict timing alignment.

### DOS Compatibility
Under SpartaDOS X or RealDOS, memory allocations for the resident `N:` handler may conflict with program buffers. Always configure your loaders to reserve zero page addresses `$F0`–`$FF` and memory above the handler address limit (`$0C00` or `$2000` depending on the DOS footprint).

### CIO Register Overwriting Gotcha
In Atari OS, calling `CIOV` can overwrite zero page variables or registers in the target IOCB (`ICBLL/H`, `ICAX1/2`, `ICBAL/H` can be altered depending on the command executed and the device handler implementation). 
* **Rule:** Always explicitly re-initialize **all** required IOCB registers (`ICCOM`, `ICBAL/H`, `ICBLL/H`, `ICAX1`, `ICAX2`) immediately before *every* `CIOV` call. Relying on values surviving from previous calls will result in unstable execution and network failures.

### Cloudflare & Public API Blocks
Modern public APIs (e.g., CoinGecko) use strict Cloudflare, rate-limiting, or User-Agent validation rules. Since FujiNet's ESP32 network client doesn't emulate standard browser headers by default, requests to these endpoints will often return `403 Forbidden` or `1020 Access Denied` errors.
* **Solution:** Use developer-friendly, rate-limit-free endpoints with simple JSON structures (such as Coinbase's `api.coinbase.com`) for direct network calls, or deploy a custom proxy that appends standard browser headers.

### MADS String Conventions
When writing assembly code for MADS:
- **Single quotes (`'string'`)** compile to standard **ATASCII** codes. Use this for CIO/SIO device parameters, URLs, JSON paths, and anything passed to OS I/O vectors.
- **Double quotes (`"string"`)** compile to **Internal Screen Codes**. Use this only when writing text directly to screen memory in standard graphics/text modes.

---

## 10. References & External Wiki Links

For the latest specifications and protocol enhancements, refer to the official FujiNet firmware wiki articles:
- [SIO Commands for Device ID $70](https://github.com/FujiNetWiFi/fujinet-firmware/wiki/SIO-Commands-for-Device-ID-$70)
- [SIO Commands for Device IDs $71 to $78](https://github.com/FujiNetWiFi/fujinet-firmware/wiki/SIO-Commands-for-Device-IDs-$71-to-$78)
- [CIO Commands for N Device](https://github.com/FujiNetWiFi/fujinet-firmware/wiki/CIO-Commands-for-N-Device)
- [Additional Commands for R: Devices](https://github.com/FujiNetWIFI/fujinet-firmware/wiki/Additional-Commands-for-R%3A-Devices)
- [A Simple NetCat Program](https://github.com/FujiNetWIFI/fujinet-firmware/wiki/A-Simple-NetCat-Program)
- [HTTP Protocol Details](https://github.com/FujiNetWIFI/fujinet-firmware/wiki/HTTP-Protocol)
- [Using HTTP/HTTPS from BASIC](https://github.com/FujiNetWIFI/fujinet-firmware/wiki/Using-HTTP-S-from-BASIC)


---

## 11. Common SIO Pitfalls & Gotchas

When programming bare-metal SIO (`$E459`), it is easy to make assumptions that lead to NAKs (`$88` / 136) or Timeouts (`$8A` / 138). Be aware of the following FujiNet-specific constraints:

> [!WARNING]
> **Gotcha #1: SIO Status (`$53`) and the `DVSTAT` buffer**
> When querying FujiNet for the number of Bytes Waiting via the `Status` (`$53`) command, FujiNet replies with exactly 4 bytes (the `nstatus` structure). Even though the Atari OS is supposed to store this automatically into the system `DVSTAT` registers (`$02EA` - `$02ED`), you **must explicitly point your `DBUFLO` and `DBUFHI` pointers to `DVSTAT`**. If you leave `DBUFLO/HI` pointing to your previous payload (like a JSON path string), the OS SIOV will overwrite your payload with the 4 status bytes, and `DVSTAT` will remain completely un-updated (holding garbage from previous commands).

> [!WARNING]
> **Gotcha #2: `DAUX1` / `DAUX2` in SIO Read (`$52`) dictates payload size**
> Standard Atari SIO peripherals often ignore `DAUX1` / `DAUX2` during a read. However, FujiNet's `sioNetwork::sio_read()` implementation **combines `DAUX1` and `DAUX2` into a 16-bit integer to determine EXACTLY how many bytes to send over the SIO bus.** 
> If you set `DBYTLO`/`DBYTHI` to the number of bytes you want to read (e.g. from `DVSTAT`), you **must also copy that size into `DAUX1` and `DAUX2`**. If you hardcode `DAUX1` to 12 but `DBYTLO` expects 10, FujiNet will send 12 bytes. The Atari will read 10 data bytes and consume the 11th byte as the SIO Checksum. The checksum will fail, Atari will retry, and the connection will ultimately time out. Always keep `DAUX1/DAUX2` strictly synchronized with `DBYTLO/DBYTHI` for `NETCMD_READ`.

> [!TIP]
> **Gotcha #3: SIO `$00` Bytes and Atari "Hearts"**
> If you are using CIO's `PUT RECORD` (`CMD_PUTREC` = `$09`) to print diagnostic text to the screen (`E:`), strings must be terminated by the ATASCII EOL character (`$9B`). If you accidentally terminate strings with C-style NULL (`$00`), the `PUT RECORD` routine will not stop at the NULL. Instead, it prints `$00`, which translates to the internal display code `0` - the famous **Atari Heart (♥)** symbol! Always terminate display strings in Assembly with `$9B`.

---

## 12. FujiNet & SIO Error Codes Reference

### OS SIO Result Codes (in `DSTATS` / `$0303`)
After executing an SIO command via `SIOV` (`$E459`), `DSTATS` will contain the SIO result. A value with the high bit set ($\ge 128$) indicates an error.

| Code | Hex | Description |
|:---:|:---:|---|
| **1** | `$01` | **SUCCESS** - Command completed successfully |
| **138** | `$8A` | **TIMEOUT** - Device timed out (no response on the bus) |
| **139** | `$8B` | **NAK** - Device NAK (the frame was refused by the peripheral) |
| **143** | `$8F` | **BAD FRAME** - Checksum mismatch |
| **144** | `$90` | **DEVICE ERROR** - FujiNet signaled a device error. You must issue a Network `STATUS` (`$53`) command to read the extended error code. |

### FujiNet Extended Device-Status Error Codes
When `DSTATS` returns `144` (or `PEEK(749)` / `DVSTAT+3` under NDEV), query the channel status and read byte 3 of the status payload to get the exact error code:

| Code | Name | Description |
|:---:|---|---|
| **1** | `SUCCESS` | No error occurred. |
| **136** | `END OF FILE` | The resource has been fully read (Normal completion). |
| **144** | `GENERAL` | A fatal device error occurred on the ESP32. |
| **146** | `NOT IMPLEMENTED` | The command is unknown to the handler/peripheral. |
| **151** | `FILE EXISTS` | Directory creation or file creation failed because the item already exists. |
| **162** | `NO SPACE` | Storage space is full. |
| **165** | `INVALID DEVICESPEC` | The network device URI spec could not be parsed. |
| **167** | `ACCESS DENIED` | Permission refused by host or server. |
| **170** | `FILE NOT FOUND` | File or directory not found (equivalent to network 404). |
| **200** | `CONNECTION REFUSED` | The remote host refused the connection or is unreachable. |
| **201** | `NETWORK UNREACHABLE` | No routing path is available to the destination host. |
| **202** | `SOCKET TIMEOUT` | The TCP/UDP socket connection timed out. |
| **203** | `NETWORK DOWN` | The FujiNet WiFi link is disconnected or down. |
| **204** | `CONNECTION RESET` | The connection was reset/terminated by the remote host. |
| **207** | `NOT CONNECTED` | Attempted an I/O operation on a closed network channel. |
| **208** | `SERVER NOT RUNNING` | A listening server socket returned no data or client closed. |
| **212** | `BAD USER / PASSWORD` | Authentication credentials were rejected by host. |
| **213** | `CANNOT PARSE JSON` | The received document is not valid JSON. |
| **255** | `NO BUFFERS` | ESP32 memory exhaustion: no allocation buffers available. |
