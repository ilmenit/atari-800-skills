# Syntax

## Comments

Single-line comment characters should be preceded by the `;` or `*` sign. However, for marking single-line comments, it is safest to use the semicolon `;` because the `*` character has other meanings—it can represent a multiplication operation or the current address during assembly. The semicolon, on the other hand, is dedicated solely to marking comments.

It is also possible to use `//` for single-line comments and `/* */` for multi-line comments.

```
 * this is a comment
                 ; this is a comment
 lda #0      ; this is a comment
 dta  1 , 3     * INVALID COMMENT, WILL BE MISINTERPRETED

 org $2000 + 1      INVALID COMMENT, WILL BE MISINTERPRETED

 nop // this is a comment

 // this is a comment

 dta 1,2, /* comment */ 3,4

 lda /* comment */ #0

/*
  ...
  this is a multi-line comment
  ...
*/

/*************************************
  this is also a multi-line comment
**************************************/
```

Multi-line comment characters `/* */` and single-line comment characters `//` can be used without restrictions.

## Line Joining

Any number of listing lines can be combined (separated) into a single line using the `\` character, e.g.:

```
  lda 20\ cmp 20\ beq *-2

  lda 20   \ cmp  20   \   beq *-2

  lda #0  \lop  sta $a000,y  \ iny  \ bne lop     ; comment only at the end of such a line
```

If a space character is not placed after the `\` character, the mnemonic or other character string may be interpreted as a label. Remember that the `\` sign signifies the start of a new line.

**MADS** finishes processing such a line upon encountering a comment or the end of the character string; therefore, comments can only be placed at the end of such a multi-line.

> **NOTE:**
> _Placing the `\` character at the end of a line indicates to **MADS** the intention to continue the current line on the next line, e.g.:_

```
 lda\
 #\
 12
```

In the above example, we will get the `LDA #12` instruction.

## Mnemonic Chaining

The ability to chain two mnemonics using the colon `:` character is already known from **XASM**. In **MADS**, this capability has been extended to chaining any number of mnemonics known to **MADS**, e.g.:

```
 lda:cmp:req 20

 lda:iny:sta:iny $600,y
```

## Expressions

The term "expression" refers to a sequence of operators and operands (arguments) that defines operations, i.e., the type and order of calculations. A complex expression is one in which two or more operators occur. Operators that act on only one operand are called unary. Operators with two arguments are called binary.

The evaluation of an expression proceeds in the order defined by operator precedence and in the direction defined by operator associativity.

### Numbers

**MADS** accepts numbers in decimal, hexadecimal, and binary formats, as well as in **ATASCII** and **INTERNAL** codes.

#### decimal notation

```JavaScript
    -100
    -2437325
    1743
```

#### hexadecimal notation

```JavaScript
    $100
    $e430
    $000001

    0x12
    0xa000
    0xaabbccdd
```

#### binary notation

```JavaScript
    %0001001010
    %000000001
    %001000
```

#### ATASCII code notation:

```JavaScript
    'a'
    'fds'
    'W'*
```

#### INTERNAL code notation:

```JavaScript
    "B"
    "FDSFSD"
    "."*
```

Only the first character of an *ATASCII* or *INTERNAL* string is significant. A `*` character after the closing quote causes an `inverse` of the character.

---

Additionally, two operations, `+` and `-`, are possible for character strings, which increase or decrease the character codes delimited by quotes.

```JavaScript
    "FDttrteSFSD"-12
    'FDSFdsldksla'+2
```

### Operators

#### binary

    +   Addition
    -   Subtraction
    *   Multiplication
    /   Division
    %   Remainder
    &   Bitwise and
    |   Bitwise or
    ^   Bitwise xor
    <<  Arithmetic shift left
    >>  Arithmetic shift right
    =   Equal
    ==  Equal (same as =)
    <>  Not equal
    !=  Not equal (same as <>)
    <   Less than
    >   Greater than
    <=  Less or equal
    >=  Greater or equal
    &&  Logical and
    ||  Logical or


#### unary

    +  Plus (does nothing)
    -  Minus (changes sign)
    ~  Bitwise not (complements all bits)
    !  Logical not (changes true to false and vice versa)
    <  Low (extracts low byte)
    >  High (extracts high byte)
    ^  High 24bit (extracts high byte)
    =  Extracts memory bank
    :  Extracts global variable value


#### precedence order

    first []             (brackets)
    + - ~ < >            (unary)
    * / % & << >>        (binary)
    + - | ^              (binary)
    = == <> != < > <= >= (binary)
    !                    (unary)
    &&                   (binary)
    last  ||             (binary)
