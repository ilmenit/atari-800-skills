## Introduction

Probably everyone who has dealt with the small **Atari** architecture associates the term *memory bank* with extended memory, divided into **16kb** banks, switched into the `$4000..$7FFF` area.

**MADS** can also understand it this way (`OPT B+` option, [Hardware memory banks](#hardware-memory-banks-opt-b)), but by default it understands it in a more virtual way (`OPT B-` option, [Virtual memory banks](#virtual-memory-banks-opt-b)).

The following pseudo-commands apply to banks:

```
LMB #value
NMB
RMB
```

* `LMB #` Load Memory Bank

We set the MADS bank counter to a specific value from the range <$00..$FF> (BANK = value), e.g.

```
lmb #0
lmb #bank
lmb #5 , $6500      ; only when OPT B+
```

* `NMB` Next Memory Bank

We increase the **MADS** bank counter by 1 (BANK = BANK + 1).

```
nmb
nmb  $6500          ; only when OPT B+
```

* `RMB` Reset Memory Bank

We zero the **MADS** bank counter (BANK = 0).

```
rmb
rmb $3500           ; only when OPT B+
rmb $8500           ; only when OPT B+
```

---

During assembly, **MADS** assigns the current bank counter value to each newly defined label. The programmer can influence the bank counter value using the above pseudo-commands.

* Labels with an assigned **MADS** bank counter `=0` have **global** scope.
* Labels with an assigned **MADS** bank counter `>0` have **local** scope.

## Virtual memory banks `OPT B-`

In **MADS**, the term *virtual memory bank* is understood as any area marked by a newly defined label with the current bank counter value assigned (by default, the bank counter is zeroed). So a virtual memory bank is not necessarily the `$4000..$7FFF` memory area, but any label representing some program code area to which a code (bank counter value) from the range `$00..$FF` has been assigned using appropriate pseudo-commands provided for the programmer's use: `NMB`, `RMB`, `LMB`.

An exception is `.RELOC` blocks in which you cannot manually change the bank counter; this is performed automatically by **MADS**, which increases the counter with each call to the `.RELOC` directive. In this case, the bank counter takes values from the range `$0001..$FFF7`.

The programmer can read the bank counter value assigned to a label using the `=` operator, e.g.:

```
label

 ldx #=label
```

In the above example, we stored the **MADS** memory bank counter value assigned to the `LABEL` label in the *CPU* register `X`.

Another useful operator can be the colon character `:` placed at the beginning of the label name. This will cause **MADS** to read the value of such a label bypassing the scope restrictions introduced by the **MADS** bank counter. Sometimes this can cause complications, e.g., if multiple labels with the same name occurred but in different local areas or in areas with different virtual bank counter values.

```


 lmb #5

label5
 nop

 lmb #6

label6
 nop

 lda :label5
```

In the above example, the absence of the `:` operator at the beginning of the label name in the `lda :label5` command would end with the error message **ERROR: Undeclared label LABEL5 (BANK=6)**.

Virtual memory banks can be used to index an array containing values for **PORTB**. This is also their use when the `OPT B+` option is selected.

## Hardware memory banks `OPT B+`

This **MADS** operating mode can be described as **BANK SENSITIVE**.

Hardware memory banks are an extension of virtual banks. They are understood by **MADS** as extended memory banks, switched into the `$4000..$7FFF` area. The operation of pseudo-commands `NMB`, `RMB`, `LMB` is extended by a call to the `@BANK_ADD` macro, which can be found in the `..\EXAMPLES\MACROS\` directory.

In this operating mode, **MADS** needs declarations of specific macros:

```
@BANK_ADD
@BANK_JMP
```

and needs label definitions with names:

```
@TAB_MEM_BANKS
@PROC_ADD_BANK
```

The `@TAB_MEM_BANKS` label defines the address of the table from which values will be copied to the **PORTB** register responsible for switching extended memory banks. We can make things easier and use the ready-made procedure for detecting extended memory banks included with **MADS**, file `..\EXAMPLES\PROCEDURES\@MEM_DETECT.ASM`.

The `@PROC_ADD_BANK` label is used by the `@BANK_ADD` macro and defines the address where the program code switching the extended memory bank will be located.

The programmer can read the bank counter value assigned to a label using the `=` operator, e.g.:

```
label

 ldy #=label
```

In the above example, we stored the **MADS** memory bank counter value assigned to the `LABEL` label in the `regY` register.

If the **MADS** bank counter `= 0` then:

* program code must be located outside the `$4000..$7FFF` area
* newly defined labels in this area are global
* all defined labels can be referenced without restriction, regardless of the bank number
* a jump to a bank area is possible using the `@BANK_JMP` macro, example in file `..\EXAMPLES\MACROS\@BANK_JMP.MAC`; the parameter for this macro does not need to be preceded by the `:` operator

If the **MADS** bank counter `> 0` then:

* program code must be located in the `$4000..$7FFF` area
* newly defined labels in this area are local
* only global labels and those defined in the current bank area can be referenced
* the `LMB`, `NMB` pseudo-command causes the execution of the `@BANK_ADD` macro, which switches on a new extended memory bank based on the MADS bank counter and sets a new assembly address (default to `$4000`)
* the `RMB` pseudo-command causes zeroing of the **MADS** memory bank counter and sets a new assembly address outside the bank (default to `$8000`)
* a jump to another bank area is possible using the `@BANK_JMP` macro, example in file `..\EXAMPLES\MACROS\@BANK_JMP`, the parameter for this macro must be preceded by the `:` operator

An example of using this **MADS** operating mode is the file `..\EXAMPLES\XMS_BANKS.ASM`. In this example, the program code is located in two different extended memory banks and executes as if it were a single whole.
