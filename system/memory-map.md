# Memory Map and System Architecture

Load the focused reference matching the task. These files are the maintained
sources; this router does not duplicate their register tables or routines.

- [Base map](memory-map/base-map.md): OS RAM, DCB/IOCBs, hardware/ROM regions, zero page, and PIA registers.
- [Reset](memory-map/reset.md): power-on versus System Reset and model differences.
- [Banking and extended RAM](memory-map/banking-extended-ram.md): PORTB, 130XE CPU/ANTIC windows, expansions, and detection caveats.
- [Zero page and stack](memory-map/zero-page-stack.md): allocation, multi-byte operations, and inline parameters.
- [Memory ownership workflow](../tooling/workflow.md#memory-ownership): program layout and OS/DOS coexistence.
