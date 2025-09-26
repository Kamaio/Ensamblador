RISC‑V Assembler in Python (SLY)

Overview
- Small assembler for RISC‑V written in Python using SLY (lex/yacc style).
- Expands common pseudo‑instructions to base RV32I forms.
- Assembles R, I, S, B, J, and U instruction formats into 32‑bit machine code.
- Supports .text and a subset of .data directives (.word, .dword, .half, .byte, .ascii, .asciz, .space).
- Outputs: binary and hex encodings for .text; collects .data bytes into a list.

Prerequisites
- Python 3.8+
- pip install sly
- JSON tables in project root:
  - BType.json, IType.json, JType.json, RType.json, SType.json, UType.json
  - REGnames.json (ABI alias to register number mapping)

Input format
- input.asm may contain optional .data (must appear before any .text content) and .text sections.
- Labels: lines ending with “label:”.
- Registers as xN or ABI names (a0..a7, s0..s11, t0..t6, ra, sp, etc.).
- Immediates: decimal or 0x‑hex.
- Lines starting with “#” are treated as comments and skipped.

Outputs
- output.bin: each line contains a 32‑bit binary string and the PC value (e.g., “xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx + PC”).
- output.hex: each line contains the instruction word in hex (e.g., “0xXXXXXXXX”).
- infoGuardada: in‑memory list of 8‑bit strings from .data (one element per byte).
- variables: dict mapping each .data symbol to its base data offset (PCv).

Assembly pipeline
1) First pass (labels):
   - Scan file and assign each label the current PC.
   - For every non‑empty, non‑label line, PC += 4 (assuming 32‑bit fixed instruction size).

2) Second pass:
   - .text:
     - Expand pseudo‑instructions to canonical forms.
     - Lex and parse using SLY into structured tuples by format.
     - Pack fields and write to output.bin (binary) and output.hex (hex).
   - .data:
     - Handle directives and push bytes into infoGuardada.
     - Track symbol offsets in variables and advance PCv accordingly.

Supported instruction formats
- R‑type: packs funct7 | rs2 | rs1 | funct3 | rd | opcode
- I‑type: packs imm[11:0] | rs1 | funct3 | rd | opcode
- S‑type: packs imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode
- B‑type: packs imm | imm[10:5] | rs2 | rs1 | funct3 | imm[4:1] | imm | opcode
- J‑type (UJ): packs imm | imm[10:1] | imm | imm[19:12] | rd | opcode
- U‑type: packs imm[31:12] | rd | opcode

Pseudo‑instructions implemented
- nop, mv, not, neg
- seqz, snez, sltz, sgtz
- beqz, bnez, blez, bgez, bltz, bgtz
- bgt, ble, bgtu, bleu
- j, jal (when label is known), jr, jalr (short form), ret

Immediate validation
- slli/srli/srai shift amount in
- I/S immediates in [-2048, 2047]
- U‑type immediate in  (20‑bit unsigned)
- Labels must exist for B/J references

.data directives
- .word n
  - 4 bytes, stored into infoGuardada as four 8‑bit strings (little‑endian order).
- .dword n
  - 8 bytes, stored as 8 bytes (little‑endian).
- .half n
  - 2 bytes.
- .byte c or n
  - 1 byte; if c is a quoted single character (e.g., "A"), it is converted via ord().
- .ascii "text"
  - Emits one byte per character; no trailing NUL.
- .asciz "text"
  - Emits one byte per character plus a trailing 0x00 byte.
- .space N
  - Emits N zero bytes.

Endianness
- .data bytes are stored in little‑endian order for multi‑byte quantities (.word/.dword/.half).

Known caveats and suggestions
- Branch/jump offsets are computed as labels[target] − PC; strict RISC‑V semantics often use base PC + 4. If that’s required, change to labels[target] − (PC + 4).
- String literals currently do not process escape sequences like \n, \t, or escaped quotes. Add a proper string literal parser if needed.
- The extra startswith/endswith validation after slicing quotes in .asciz/.string can be removed (redundant).
- Consider adding .align, .float, .double, and more informative error messages including line numbers.

Example
input.asm:
  .data
  msg: .asciz "Hello\n"
  .text
  addi x1, x0, 4

Run:
  python assembler.py

Check:
- output.bin/output.hex for code emission
- Printed variables and infoGuardada for .data bytes and symbol addresses

Testing tips
- Write short unit tests per instruction format and directive.
- Print intermediate immediates for S/B/J when debugging.
- Verify label math on forward/backward branches with small toy programs.