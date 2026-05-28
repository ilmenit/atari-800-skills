## Arrays

### Array declaration

The following directives apply to arrays:

```
label .ARRAY [elements0][elements1][...] [.type] [= init_value]
      .ARRAY label [elements0][elements1][...] [.type] [= init_value]
      .ENDA [.AEND] [.END]
```

Available data types are `.BYTE`, `.WORD`, `.LONG`, `.DWORD`. If no type is specified, `.BYTE` is assumed by default. The array definition locates it in-place (at the point of definition).
`ELEMENTS` specifies the number of array elements, which will be indexed from `<0..ELEMENTS-1>`. The `ELEMENTS` value can be a constant or an expression, and should be in the range `<0..65535>`. If the number of elements is not specified, it will be determined based on the number of data entries provided.

In the area delimited by `.ARRAY` and `.ENDA` directives, it is not possible to use *CPU* mnemonics. If used, or if other disallowed characters are used, an error with the message _**Improper syntax**_ will occur.

It is possible to specify the starting index from which values will be entered for subsequent array fields. A new index value is specified by placing the `[expression]` in square brackets at the beginning of a new line. Multiple indices can be specified by separating them with a colon `:`. Then, the values for the array fields are entered after the equals sign `=`, e.g.:

```JavaScript
.array tab .word      ; TAB array with an unspecified number of .WORD fields
 1,3                  ; [0]=1, [1]=3
 5                    ; [2]=5
 [12] = 1             ; [12]=1
 [3]:[7]:[11] = 9,11  ; [3]=9, [4]=11, [7]=9, [8]=11, [11]=9, [12]=11
.enda

.array scr [24][40]   ; two-dimensional .BYTE array SCR
  [11][15] = "ATARI"
.enda
Example of an array translating a key press code to an INTERNAL code.

.array TAB [255] .byte = $ff   ; allocating 256 bytes [0..255] with an initial value of $FF

 [63]:[127] = "A"              ; assigning a new value TAB[63]="A", TAB[127]="A"
 [21]:[85]  = "B"
 [18]:[82]  = "C"
 [58]:[122] = "D"
 [42]:[106] = "E"
 [56]:[120] = "F"
 [61]:[125] = "G"
 [57]:[121] = "H"
 [13]:[77]  = "I"
 [1] :[65]  = "J"
 [5] :[69]  = "K"
 [0] :[64]  = "L"
 [37]:[101] = "M"
 [35]:[99]  = "N"
 [8] :[72]  = "O"
 [10]:[74]  = "P"
 [47]:[111] = "Q"
 [40]:[104] = "R"
 [62]:[126] = "S"
 [45]:[109] = "T"
 [11]:[75]  = "U"
 [16]:[80]  = "V"
 [46]:[110] = "W"
 [22]:[86]  = "X"
 [43]:[107] = "Y"
 [23]:[87]  = "Z"
 [33]:[97]  = " "

 [52]:[180] = $7e
 [12]:[76]  = $9b

.enda
```

In the above example, we created an array `TAB` of size 256 bytes `[0..255]`, data type `.BYTE`, and filled the fields with value `$FF`. Additionally, we stored INTERNAL character codes at positions (array indices) equal to the key press code (without SHIFT and with SHIFT, i.e., uppercase and lowercase letters).

The colon `:` separates individual array indices.

Example of a joystick movement detection procedure, e.g.:

```JavaScript
.local HERO

  .pages

  lda $d300
  and #$0f
  tay
  lda joy,y
  sta _jmp

  jmp null
_jmp equ *-2

left
right
up
down

null

  rts

  .endpg

  _none     = 15
  _up       = 14
  _down     = 13
  _left     = 11
  _left_up  = 10
  _left_dw  = 9
  _right    = 7
  _right_up = 6
  _right_dw = 5

.array joy [16] .byte = .lo(null)

	[_left]     = .lo(left)
	[_left_up]  = .lo(left)
	[_left_dw]  = .lo(left)

	[_right     = .lo(right)
	[_right_up] = .lo(right)
	[_right_dw] = .lo(right)

	[_up]       = .lo(up)
	[_dw]       = .lo(down)
.enda

.endl
```

Another example could be placing a centered string, e.g.:

```JavaScript
 org $bc40

.array txt 39 .byte
 [17] = "ATARI"
.enda
The created array is referenced as follows:
 lda tab,y
 lda tab[23],x
 ldx tab[200]
```

If an index value exceeding the declared size of the array is provided in square brackets, an error message _**Constant expression violates subrange bounds**_ will be generated.
