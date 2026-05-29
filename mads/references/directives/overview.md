# Overview

## Directives


 [.A8, .A16, .AI8, .AI16](#a8)<br>
 [.I8, .I16, .IA8, .IA16](#i8)<br>

 [.ASIZE](#asize)<br>
 [.ISIZE](#isize)<br>

 [.ALIGN N[,fill]](symbols-vars.md#align)

 [.ARRAY label [elements0][elements1][...] .type [= init_value]](../arrays.md#arrays)<br>
 [.ENDA, [.AEND]](../arrays.md#arrays)<br>

 [.DEF label [= expression]](symbols-vars.md#def)

 [.DEFINE macro_name expression](file-output.md#define)<br>
 [.UNDEF macro_name](symbols-vars.md#undef)<br>

 [.ENUM label](../data-types.md#enumerations)<br>
 [.ENDE, [.EEND]](../data-types.md#enumerations)<br>

 [.ERROR [ERT] 'string'["string"] or .ERROR [ERT] expression](file-output.md#error)

 [.EXTRN label [,label2,...] type](../relocatable-code/external-symbols.md#external-symbols)

 [.IF [IFT] expression](expression-helpers.md#if_else)<br>
 [.ELSE [ELS]](expression-helpers.md#if_else)<br>
 [.ELSEIF [ELI] expression](expression-helpers.md#if_else)<br>
 [.ENDIF [EIF]](expression-helpers.md#if_else)<br>

 [.IFDEF label](symbols-vars.md#ifdef)<br>
 [.IFNDEF label](conditionals-repeat.md#ifndef)<br>

 [.LOCAL label](../local-areas.md#local-area)<br>
 [.ENDL, [.LEND]](../local-areas.md#local-area)<br>

 [.LONGA ON|OFF](../relocatable-code/65816-width-directives.md#directives-longa-and-longi)<br>
 [.LONGI ON|OFF](../relocatable-code/65816-width-directives.md#directives-longa-and-longi)<br>

 [.LINK 'filename']](../relocatable-code/linking.md#linking-link)

 [.MACRO label](../macros/overview.md#macros)<br>
 [.ENDM, [.MEND]](../macros/overview.md#macros)<br>
 [:[%%]parameter](../macros/overview.md#macros)<br>
 [.EXITM [.EXIT]](../macros/overview.md#macros)<br>

 [.NOWARN](#nowarn)

 [.PRINT [.ECHO] 'string1','string2'...,value1,value2,...](symbols-vars.md#print)

 [.PAGES [expression]](conditionals-repeat.md#pages)<br>
 [.ENDPG, [.PGEND]](conditionals-repeat.md#pages)<br>

 [.PUBLIC, [.GLOBAL], [.GLOBL] label [,label2,...]](../relocatable-code/public-symbols.md#public-symbols)

 [.PROC label](../procedures/declaration.md#procedure-declaration)<br>
 [.ENDP, [.PEND]](../procedures/declaration.md#procedure-declaration)<br>
 [.REG, .VAR](../procedures/declaration.md#procedure-declaration)<br>

 [.REPT expression [,parameter1, parameter2, ...]](segments.md#rept)<br>
 [.ENDR, [.REND]](segments.md#rept)<br>
 [.R](segments.md#rept)<br>

 [.RELOC [.BYTE|.WORD]](../relocatable-code/reloc-block.md#relocatable-block-reloc)

 [.STRUCT label](../data-types.md#structures)<br>
 [.ENDS, [.SEND]](../data-types.md#structures)<br>

 [.SYMBOL label](#symbol)

 [.SEGDEF label address length [bank]](segments.md#seg)<br>
 [.SEGMENT label](segments.md#seg)<br>
 [.ENDSEG](segments.md#seg)<br>

 [.USING, [.USE] proc_name, local_name](misc.md#using)

 [.VAR var1[=value],var2[=value]... (.BYTE|.WORD|.LONG|.DWORD)](data-storage.md#var)<br>
 [.ZPVAR var1, var2... (.BYTE|.WORD|.LONG|.DWORD)](symbols-vars.md#zpvar)<br>

 [.END](#end)

 [.EN](#en)

 [.BYTE](#byte)<br>
 [.WORD](#byte)<br>
 [.LONG](#byte)<br>
 [.DWORD](#byte)<br>

 [.OR](file-output.md#or_and)<br>
 [.AND](file-output.md#or_and)<br>
 [.XOR](file-output.md#or_and)<br>
 [.NOT](file-output.md#or_and)<br>

 [.LO (expression)](expression-helpers.md#lohi)<br>
 [.HI (expression)](expression-helpers.md#lohi)<br>

 [.DBYTE words](data-storage.md#dbyte)<br>
 [.DS expression](data-storage.md#_ds)<br>

 [.BY [+byte] bytes and/or ASCII](data-storage.md#_by)<br>
 [.WO words](data-storage.md#_wo)<br>
 [.HE hex bytes](data-storage.md#_he)<br>
 [.SB [+byte] bytes and/or ASCII](data-storage.md#_sb)<br>
 [.CB [+byte] bytes and/or ASCII](data-storage.md#_cb)<br>
 [.FL floating point numbers](data-storage.md#_fl)<br>

 [.ADR label](data-storage.md#adr)

 [.LEN label ['filename']](file-output.md#sizeof)<br>
 [.SIZEOF label](file-output.md#sizeof)<br>
 [.FILESIZE 'filename'](file-output.md#sizeof)<br>

 [.FILEEXISTS 'filename'](file-output.md#fileexists)<br>

 [.GET [index] 'filename'["filename"][*][+-value][,+-ofset[,length]]](symbols-vars.md#get)<br>
 [.WGET [index]](symbols-vars.md#get)<br>
 [.LGET [index]](symbols-vars.md#get)<br>
 [.DGET [index]](symbols-vars.md#get)<br>
 [.PUT [index] = value](file-output.md#put)<br>
 [.SAV [index] ['filename',] length](file-output.md#sav)<br>


<a name="symbol"></a>


## Legacy Index Anchors

<a name="a8"></a>
<a name="i8"></a>
<a name="asize"></a>
<a name="isize"></a>
<a name="nowarn"></a>
<a name="symbol"></a>
<a name="end"></a>
<a name="en"></a>
<a name="byte"></a>
