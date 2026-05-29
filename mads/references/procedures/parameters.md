# Parameters

### Procedure Parameters

Referencing procedure parameters from within the procedure does not require additional actions from the programmer, e.g.:

```
@stack_address equ $400
@stack_pointer equ $ff
@proc_vars_adr equ $80

name .PROC (.WORD par1,par2)

 lda par1
 clc
 adc par2
 sta par1

 lda par1+1
 adc par2+1
 sta par1+1

.endp

 icl '@call.mac'
 icl '@pull.mac'
 icl '@exit.mac'
```

Upon encountering a `.PROC` declaration with parameters, **MADS** automatically defines these parameters, assigning them values based on `@PROC_VARS_ADR`. In the example above, **MADS** will automatically define parameters `PAR1 = @PROC_VARS_ADR` and `PAR2 = @PROC_VARS_ADR + 2`.

The programmer references these parameters by the name given in the procedure declaration, similar to high-level languages. In **MADS**, it is possible to access procedure parameters from outside the procedure, which is not typical in high-level languages. From the example above, we can read the contents of `PAR1`, e.g.:

```
 lda name.par1
 sta $a000
 lda name.par1+1
 sta $a000+1
```

The value of `PAR1` has been copied to address `$A000`, and the value of `PAR1+1` to address `$A000+1`. Of course, this can only be done immediately after that specific procedure finishes. Keep in mind that parameters for such procedures are stored at the common address `@PROC_VARS_ADR`, so with each new call to a procedure utilizing the software stack, the contents of the area `<@PROC_VARS_ADR .. @PROC_VARS_ADR + $FF>` change.

If a procedure has parameters declared as type `.REG`, the programmer should ensure they are saved or properly utilized before being modified by the procedure code. For parameters of type `.VAR`, there is no cause for concern, as parameters are saved to specific memory cells from which they can always be read.
