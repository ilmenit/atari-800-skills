# Temporary

### Temporary

A temporary label definition has the property that its value can change multiple times even during a single assembly pass. Normally, an attempt to redefine a label ends with the message _**Label declared twice**_. There will be no such message if it is a temporary label.

The scope of temporary labels depends on the area in which the label was defined. Temporary labels can have local scope ([Local labels](local.md#local)) or global scope ([Global labels](global.md#global)).

#### ?label

A temporary label is defined by the user by placing a question mark `?` at the beginning of the label name, e.g.:

    ?label

Temporary labels should not be used for names of `.PROC` procedures, `.MACRO` macros, `.LOCAL` areas, `.STRUCT` structures, or `.ARRAY` arrays.

Temporary labels are defined using the following equivalent pseudo-commands:

```
 EQU
  =
```

Additionally, they can be modified using operators known from **C**:

```
    -= expression
    += expression
    --
    ++
```

The above modifying operators apply only to temporary labels; attempting to use them for another type of label will end with an error message _**Improper syntax**_.

Example of using temporary labels:

```
?loc = $567
?loc2 = ?loc+$2000

     lda ?loc
     sta ?loc2

?loc = $123

     lda ?loc
```

#### label SET value

The [SET](../pseudo-commands/symbols-repeat.md#set) pseudo-command allows redefining a `LABEL`, it works with regular labels, i.e., those that do not have the `?` character as the first character in the name. Labels defined by `SET` cannot later be defined other than by `SET`.

```
 tmp set 1

 tmp = 2
```

For the above example, an **Infinite loop** will occur; it should correctly be:

```
 tmp set 1

 tmp set 2
```
