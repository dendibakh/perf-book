## Architecture-Specific Optimizations {.unlisted .unnumbered}

Performance considerations on x86, ARM
- page size
- More complex instruction set that allows for powerful single instructions. Includes many addressing modes and instruction formats,
- CISC vs RISC code density. ARM requires to load the mem location first, then perform the operation. x86 can do both in one instruction. 
- As of 2024, latest ARM ISA has 32 general purpose registers, while x86 has 16 registers. Say about APX extension. RISC-V and ARM have no FLAGS register, this eliminates unnecessary dependency chains on FLAGS register.

### ISA Extensions {.unlisted .unnumbered}

Describe major differences between ISAs

It's not possible to learn about all specific instructions. But we suggest you to familiarize yourself with major ISA extensions and their capabilities. For example, if you are developing an AI application that uses `fp16` data types, and you target one of the modern ARM processors, make sure that your program's machine code contains corresponding `fp16` ISA extensions. If you're developing encyption/decryption software, check if it utilizes crypto extensions of your target ISA.
Provide a list of these extensions?
(e.g. AES, VNNI, AVX512FP16 and AVX512BF16, AMX, ARM fp16, DOT, SVE, SME)

### Instruction latencies and throughput {.unlisted .unnumbered}
How to reason about instruction latencies and throughput?

### Microarchitecture-specific issues {.unlisted .unnumbered}
#### Memory ordering {.unlisted .unnumbered}
example with histogram
#### when FMA contraction hurts performance
example with nanobench
#### Memory alignment {.unlisted .unnumbered}
example with split loads in matmul
#### 4K aliasing {.unlisted .unnumbered}
just describe
#### Cache trashing {.unlisted .unnumbered}
just describe
#### Non-temporal stores {.unlisted .unnumbered}
remove?