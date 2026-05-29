# Linking

## Linking .LINK

    .LINK 'filename'

The `.LINK` directive requires the name of the file to be relocated as a parameter. Only **Atari DOS** files are accepted; **SDX** files are not.

If the file's loading address is other than `$0000`, it means the file does not contain relocatable code; however, it may contain update blocks for external and public symbols. The `.LINK` directive accepts files with any loading address, but only those with a loading address of `$0000` are subjected to relocation. More details on the structure of such files can be found in the Relocatable Block `.RELOC` chapter.

The `.LINK` directive allows for combining relocatable and non-relocatable code. Based on the update blocks, **MADS** automatically relocates such files. All three types of update blocks—`ADDRESS`, `EXTERNAL`, and `PUBLIC`—are taken into account. There are no restrictions on the address where the relocatable file is placed.

If the relocatable block requires the **MADS** software stack to function, the labels `@STACK_POINTER`, `@STACK_ADDRESS`, and `@PROC_VARS_ADR` will be automatically updated based on the `.RELOC` block header. It is required that the `.RELOC` blocks and the main program operate on the same software stack if one is necessary.
