# FujiNet Programming Reference for Atari 8-bit

> **Type:** Topic guide and code reference
> **Purpose:** Detailed SIO/CIO specifications, registers, JSON parsing protocols, virtual R: modem extensions, and ready-to-use MADS assembly examples for FujiNet networking.

FujiNet is a multi-peripheral emulator and network adapter for vintage systems. On the Atari 8-bit, it allows programs to offload TCP/IP, UDP, HTTP, FTP, SSH, and JSON parsing to an onboard ESP32 coprocessor.

---

## 1. FujiNet Architecture

### Device IDs and Addresses
- **$70 (FujiNet Control Device):** Used for configuration, WiFi scanning, SSID setups, and TNFS disk mounting.
- **$71–$78 (FujiNet Network Devices - `N1:` to `N8:`):** Allocated for network socket and stream operations. Standard `N:` defaults to unit 1 (`N1:`, ID `$71`).
- **$50–$53 (FujiNet R: Devices - `R1:` to `R4:`):** Serial/Modem emulation interface.

### Communication Vectors
1. **CIO (Central Input/Output):** Recommended for most programs. Accessed using the OS `CIOV` vector (`$E456`) and the `N:` device handler.
2. **SIO (Serial Input/Output):** Directly bypasses the CIO handler using the `SIOV` vector (`$E459`). Essential if the resident DOS or application overwrites the `N:` handler memory space.

---

## 2. CIO Programming (`N:` Device)

Standard network operations are mapped to the Atari's Input/Output Control Blocks (IOCBs, `$0340` to `$03BF`, 16 bytes per block).

### IOCB Register Mappings
- `ICCOM` (`$0342`): CIO Command.
- `ICBAL`/`ICBAH` (`$0344` / `$0345`): Buffer Address (pointer to URI/data).
- `ICBLL`/`ICBLH` (`$0348` / `$0349`): Buffer Length (for read/write operations).
- `ICAX1` (`$034A`): Open Mode.
- `ICAX2` (`$034B`): Auxiliary 2 (Translation / Protocol Flags).

### Connection Modes (`ICAX1`)
When executing an `OPEN` command (`$03`), set `ICAX1` according to the required network mode:
- **`$04` (Read):** Read-only client connection.
- **`$08` (Write):** Write-only client connection.
- **`$0C` (Update / Read+Write):** Bidirectional client socket (standard TCP/UDP/HTTP).
- **`$09` (Listen):** Server mode. Listens for incoming connections on the specified port.

### Line Translation Options (`ICAX2`)
FujiNet can translate carriage returns and line feeds on the fly to match Atari ATASCII EOL (`$9B`):
- **`$00` (Raw Mode):** No translation (essential for binary data, TCP raw streams, UDP packets).
- **`$01` (LF Mode):** LF translated to EOL (`$9B`).
- **`$02` (CR Mode):** CR translated to EOL.
- **`$03` (CR/LF Mode):** CR/LF sequence translated to EOL.

### Protocol URIs
The filename passed to the `OPEN` command determines the protocol and endpoint:
- **TCP Client:** `N:TCP://<host>:<port>/`
- **TCP Server:** `N:TCP://:<port>/`
- **UDP Client:** `N:UDP://<host>:<port>/`
- **HTTP/HTTPS:** `N:HTTP://<host>[:port]/<path>` or `N:HTTPS://...`

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
| `$0300` | `DDEVID` | SIO Device ID (`$71`–`$78` for `N1:`–`N8:`, `$70` for Control) |
| `$0301` | `DUNIT`  | Device Unit (typically `$01`) |
| `$0302` | `DCOMND` | SIO Command byte |
| `$0303` | `DSTATS` | Status/Direction (`$40` = Read, `$80` = Write, `$00` = No data) |
| `$0304` | `DBUFLO` | Data Buffer Address (Low) |
| `$0305` | `DBUFHI` | Data Buffer Address (High) |
| `$0306` | `DTIMLO` | Timeout (seconds, e.g., `$0F`) |
| `$0308` | `DBYTLO` | Bytes to Transfer (Low) |
| `$0309` | `DBYTHI` | Bytes to Transfer (High) |
| `$030A` | `DAUX1`  | Auxiliary Byte 1 (parameters specific to command) |
| `$030B` | `DAUX2`  | Auxiliary Byte 2 (parameters specific to command) |

### SIO Commands for Device ID $70 (FujiNet Control)
Device `$70` handles configuration, WiFi settings, local time, and TNFS slot mounting.

| Command | Hex | Description |
|:---:|:---:|---|
| `Test` | `$00` | Check if FujiNet is online |
| `Get HSIO Index` | `$3F` | Reads current High-Speed SIO rate |
| `Get Time` | `$D2` | Fetches current date/time from NTP |
| `Random Number` | `$D3` | Generates hardware random bytes from ESP32 |
| `Disable/Enable Device` | `$D4`/`$D5` | Hardware peripheral slot activation |
| `Get Device Slot Filename`| `$DA` | Queries mounted disk filename |
| `Open/Close App Key` | `$DC`/`$DB` | Access local key-value config store |
| `Read/Write App Key` | `$DD`/`$DE` | Read/Write custom config parameters |
| `Unmount Device Image` | `$E9` | Ejects virtual disk slot |
| `Scan Networks` | `$FD` | Requests WiFi scan |
| `Get Scan Result` | `$FC` | Reads WiFi SSIDs list |
| `Set SSID and Connect` | `$FB` | Sets network and connects |
| `Get WiFi Status` | `$FA` | Queries connection status |
| `Mount Host` / `Unmount Host` | `$F9` / `$E6` | Mounts remote TNFS directory |
| `Mount Device Image` | `$F8` | Mounts remote ATR/XEX file |
| `Open/Read/Close Directory` | `$F7`/`$F6`/`$F5` | TNFS remote directory listing |
| `Reset FujiNet` | `$FF` | Performs cold reboot of ESP32 |

### SIO Commands for Device IDs $71 to $78 (Network/N: Devices)
Used to directly control individual sockets and network streams.

| Command | Char | Hex | Description |
|:---:|:---:|:---:|---|
| `Open` | `'O'` | `$4F` | Open network connection (URI payload) |
| `Close` | `'C'` | `$43` | Close network connection |
| `Read` | `'R'` | `$52` | Read bytes from socket |
| `Write` | `'W'` | `$57` | Write bytes to socket |
| `Status` | `'S'` | `$53` | Returns connection status & waiting bytes (4-byte packet) |
| `Get Error` | `'E'` | `$45` | Returns detailed error string |
| `Parse JSON` | `'P'` | `$50` | Instructs ESP32 to parse downloaded JSON data |
| `Query JSON` | `'Q'` | `$51` | Queries path in parsed JSON |
| `Set Translation` | `'T'` | `$54` | Changes line endings translation mode |
| `Rename File` | | `$20` | Network file system rename |
| `Delete File` | | `$21` | Network file system delete |
| `Change Directory` | | `$2C` | Change directory on host |
| `Get Current Directory`| | `$30` | Get current directory path |
| `Set Channel Mode` | | `$FC` | Configure protocol options / JSON parsing modes |
| `Query Special Cmd` | | `$FF` | Queries support for protocol-specific extensions |

#### Protocol-Specific Extensions
- **TCP Accept (`'A'` / `$41`):** Accept incoming server client.
- **TCP Close Client (`'c'` / `$63`):** Terminates client connection.
- **UDP Destination (`'D'` / `$44`):** Sets target IP/port for outgoing UDP packets.
- **HTTP Mode (`'M'` / `$4D`):** Sets HTTP specific flags (such as raw headers mode).

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
- **Mode 12 (`ICAX1` = `$0C`):** Standard HTTP GET.
- **Mode 13 (`ICAX1` = `$0D`):** HTTP GET/POST with raw header management. Setting headers requires using `PUT` commands to send headers before fetching payload.
- **Aux2 (`ICAX2`):** Sets EOL translations (typically `3` for CR/LF to EOL).

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
