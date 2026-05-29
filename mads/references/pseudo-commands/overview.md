# Overview

## Pseudo-commands

 [IFT _.IF_ expression](generated-data.md#ift)<br>
 [ELS _.ELSE_](generated-data.md#ift)<br>
 [ELI _.ELSEIF_ expression](generated-data.md#ift)<br>
 [EIF _.ENDIF_](generated-data.md#eif)<br>

<a name="ert"></a>
 [ERT _ERT 'string'_ | ERT expression](#ert)

 [label SET expression](assembly-options.md#set)<br>
 [label EXT type](#ext)<br>
 [label EQU expression](#equ)<br>
 [label  =  expression](#equ2)<br>

 [OPT [bcfhlmorst][+-]](#opt)<br>
 [ORG [[expression]]address[,address2]](#org)<br>
 [INS 'filename'["filename"][*][+-value][,+-ofset[,length]]](origin-include-data.md#ins)<br>
 [ICL 'filename'["filename"]](origin-include-data.md#icl)<br>

 [DTA [abfghltvmer](value1,value2...)[(value1,value2...)]](#dta)<br>
 [DTA [cd]'string'["string"]](#dta_s)<br>

 [RUN expression](#run)<br>
 [INI expression](#ini)<br>
 [END _.EN_](#end)<br>

 [SIN (centre,amp,size[,first,last])](origin-include-data.md#sin)<br>
 [COS (centre,amp,size[,first,last])](generated-data.md#cos)<br>
 [RND (min,max,length)](generated-data.md#rnd)

 [:repeat](symbols-repeat.md#rep)

 [BLK N`one` X](#blk_n)<br>
 [BLK D`os` X](#blk_d)<br>
 [BLK S`parta` X](#blk_s)<br>
 [BLK R`eloc` M`ain`|E`xtended`](#blk_r)<br>
 [BLK E`mpty` X M`ain`|E`xtended`](#blk_e)<br>
 [BLK U`pdate` S`ymbols`](#blk_us)<br>
 [BLK U`pdate` E`xternal`](#blk_ue)<br>
 [BLK U`pdate` A`dress`](#blk_ua)<br>
 [BLK U`pdate` N`ew` X 'string'](#blk_un)<br>

 [label SMB 'string'](symbols-repeat.md#smb)

 [NMB](#nmb)<br>
 [RMB](#rmb)<br>
 [LMB #expression](#lmb)<br>

Mostly the same as before, although a few changes have occurred. Both single ' ' and double " " quotes can be used. Both types are treated equally except for addressing (single quotes ' ' calculate the `ATASCII` value of the character, while double quotes " " calculate the `INTERNAL` value of the character).


## Legacy Index Anchors

<a name="ert"></a>
<a name="ext"></a>
<a name="equ"></a>
<a name="equ2"></a>
<a name="opt"></a>
<a name="org"></a>
<a name="dta"></a>
<a name="dta_s"></a>
<a name="run"></a>
<a name="ini"></a>
<a name="end"></a>
<a name="blk_n"></a>
<a name="blk_d"></a>
<a name="blk_s"></a>
<a name="blk_r"></a>
<a name="blk_e"></a>
<a name="blk_us"></a>
<a name="blk_ue"></a>
<a name="blk_ua"></a>
<a name="blk_un"></a>
<a name="nmb"></a>
<a name="rmb"></a>
<a name="lmb"></a>
