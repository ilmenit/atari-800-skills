# Symbols Repeat

### label SET expression

The `SET` pseudo-command allows redefining a label; it works similarly to temporary labels starting with the `?` sign, e.g.:

```
temp set 12

     lda #temp

temp set 23

     lda #temp
```

<a name="smb"></a>

### label SMB 'string'

Label declaration as an **SDX** symbol. The symbol can have a maximum length of 8 characters. As a result, after using `BLK UPDATE SYMBOLS`, the assembler will generate the correct symbol update block. E.g.:

```
       pf  smb 'PRINTF'
           jsr pf
           ...
```

will make the **SDX** system insert the symbol's address after the `JSR` instruction.

> **NOTE:**
> _This declaration is not transitive, meaning the following example will cause compilation errors:_

```
       cm  smb 'COMTAB'
       wp  equ cm-1       (error!)

           sta wp
```

Instead, use:

```
       cm  smb 'COMTAB'

           sta cm-1       (ok!)
```

> **NOTE:**
> _All symbol declarations must be used before label declarations and the main program!_


<a name="rep"></a>

### :repeat

```
           :4 asl @
           :2 dta a(*)
           :256 dta #/8

ladr :4 dta l(line:1)
hadr :4 dta h(line:1)
```

The `:` sign specifies the number of line repetitions (in the case of macros, it specifies the parameter number, provided the numerical value is written in decimal). The number of repetitions should be in the range `<0..2147483647>`. In the repeated line `:repeat`, it is possible to use the loop counter - the hash sign `#` or the parameter `:1`.
If we use the `:` sign in a macro as the line repetition count, e.g.:

```
.macro test
 :2 lsr @
.endm
```

Then, for the above example, the `:` sign will be interpreted as the second macro parameter. To prevent this interpretation by **MADS**, place a character that does nothing after the colon `:`, such as a plus sign '+'.

```
.macro test
 :+2 lsr @
.endm
```

Now the colon sign `:` will be correctly interpreted as `:repeat`


<a name="set"></a>
