# MADS Directives

Router for MADS dot directives.

Load only the focused file that matches the task.

- [overview.md](directives/overview.md) - original overview and command index
- [symbols-vars.md](directives/symbols-vars.md) - .SYMBOL label, .VAR var1[=value1],var2[=value2]... (.BYTE|.WORD|.LONG|.DWORD) [=address], .ZPVAR var1, var2... (.BYTE|.WORD|.LONG|.DWORD) [=address]
- [data-storage.md](directives/data-storage.md) - .END, .BYTE, .WORD, .LONG, .DWORD, .DBYTE
- [conditionals-repeat.md](directives/conditionals-repeat.md) - .REPT expression [,parameter1, parameter2, ...], .IFDEF label, .IFNDEF label
- [file-output.md](directives/file-output.md) - .PRINT [.ECHO], .ERROR [ERT] 'string'["string"] | .ERROR [ERT] expression, .LEN label ['filename'], .SIZEOF label, .FILESIZE 'filename'
- [segments.md](directives/segments.md) - .ALIGN N [,fill], .PAGES [expression], .SEGDEF label address length [attrib] [bank]
- [expression-helpers.md](directives/expression-helpers.md) - .OR, .AND, .XOR, .NOT, .LO (expression), .HI (expression)
- [misc.md](directives/misc.md) - .NOWARN
