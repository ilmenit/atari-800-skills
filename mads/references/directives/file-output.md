# File Output

### .PRINT [.ECHO]
Causes the value of the expression or the character string provided as a parameter (enclosed in single `' '` or double `" "` quotes) to be printed on the screen, e.g.:

```
 .print "End: ",*,'..',$8000-*
 .echo "End: ",*,'..',$8000-*
```

<a name="error"></a>

### .ERROR [ERT] 'string'["string"] | .ERROR [ERT] expression

The `.ERROR` directive and the `ERT` pseudo-instruction have the same meaning. They stop program assembly and display the message provided as a parameter, enclosed in single `' '` or double `" "` quotes. If the parameter is a logical expression, assembly will be stopped when the value of the logical expression is true (displaying the message *User error*), e.g.:

```
 ert "halt"            ; ERROR: halt
 .error "halt"

 ert *>$7fff           ; ERROR: User error
 .error *>$7fff
```

<a name="sizeof"></a>

### .LEN label ['filename'], .SIZEOF label, .FILESIZE 'filename'
The `.LEN` directive returns the length (expressed in bytes) of a `.PROC`, `.ARRAY`, `.LOCAL`, or `.STRUCT` block, or the length of a file named `'filename'`. The `LABEL` is the name of the `.PROC`, `.ARRAY`, `.LOCAL`, or `.STRUCT` block (it is possible to place the `LABEL` name between round or square brackets), e.g.:

```
label .array [255] .dword
      .enda

      dta a(.len label)   ; = $400

.proc wait
 lda:cmp:req 20
 rts
.endp

 dta .sizeof wait    ; = 7
```

The `.SIZEOF` and `.FILESIZE` directives are alternative names for `.LEN`; they can be used interchangeably depending on the programmer's preference.


<a name="fileexists"></a>

### .FILEEXISTS 'filename'
The `.FILEEXISTS` directive returns `'1'` when the file `'filename'` exists; otherwise, it returns `'0'`, e.g.:

```
 ift .fileexists 'filename'
   .print 'true'
  els
   .print 'false'
  eif
```

<a name="define"></a>

### .GET [index] 'filename'... [.BYTE, .WORD, .LONG, .DWORD]

### .WGET [index] | .LGET [index] | .DGET [index]

`.GET` is the equivalent of the `INS` pseudo-instruction (similar syntax), with the difference that the file is not appended to the assembled file but instead loaded into **MADS** memory. This directive allows loading a specified file into **MADS** memory and referencing the bytes of this file like a one-dimensional array.

```
 .get 'file'                    ; loading a file into the MADS array
 .get [5] 'file'                ; loading a file into the MADS array starting from index = 5

 .get 'file',0,3                ; loading 3 values into the MADS array

 lda #.get[7]                   ; reading the 7th byte from the MADS array
 adres = .get[2]+.get[3]<<8     ; the 2nd and 3rd bytes in the DOS file header contain information about the load address

 adres = .wget[2]              ; word
 tmp = .lget[5]                ; long
 ?x = .dget[11]                ; dword
```

Using the `.GET` and `.PUT` directives, one can read, for example, a **Theta Music Composer** (*TMC*) module and perform its relocation. This is implemented by the macro included with **MADS** in the directory `../EXAMPLES/MSX/TMC_PLAYER/tmc_relocator.mac`.

The permitted range of values for `INDEX` is <0..65535>. Values read by `.GET` are of type `BYTE`. Values read by `.WGET` are of type `WORD`. Values read by `.LGET` are of type `LONG`. Values read by `.DGET` are of type `DWORD`.


<a name="put"></a>

### .PUT [index] = value
The `.PUT` directive allows referencing the one-dimensional array in **MADS** memory and writing a `BYTE` type value into it. This is the same array where the `.GET` directive saves the file.
The permitted range of values for INDEX = <0..65535>.

```
 .put [5] = 12       ; writing the value 12 into the MADS array at position 5
```

<a name="sav"></a>

### .SAV [index] ['filename',] length
The `.SAV` directive allows saving the buffer used by the `.GET` and `.PUT` directives to an external file or appending it to the currently assembled one.

```
 .sav ?length            ; appending the contents of the buffer [0..?length-1] to the assembled file
 .sav [200] 256          ; appending the contents of the buffer [200..200+256-1] to the assembled file
 .sav [6] 'filename',32  ; saving the contents of the buffer [6..6+32-1] to the file FILENAME
```

The permitted range of values for INDEX = <0..65535>.


<a name="or_and"></a>
