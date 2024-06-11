## Architecture-Specific Optimizations {.unlisted .unnumbered}

Optimizing software for a specific CPU microarchitecture involves tailoring your code and compilation process to leverage the strengths and mitigate the weaknesses of that microarchitecture. Here's a step-by-step guide to using knowledge of a target CPU microarchitecture to optimize your software:

Progressive Enhancement:
Default to Generic: Write code to perform well on a baseline architecture.
Add Optimizations: Introduce specific optimizations progressively, ensuring there is a fallback for architectures that do not support them.

When developing cross-platform applications where the exact target CPU configuration is unknown, you can still apply microarchitecture-specific optimizations in a general and adaptable way.

There are many things 
Performance considerations on x86, ARM
- page size
- More complex instruction set that allows for powerful single instructions. Includes many addressing modes and instruction formats,
- CISC vs RISC code density. ARM requires to load the mem location first, then perform the operation. x86 can do both in one instruction. Debunking CISC vs RISC code density. https://www.bitsnbites.eu/cisc-vs-risc-code-density/

- As of 2024, latest ARM ISA has 32 general purpose registers, while x86 has 16 registers. Say about APX extension. RISC-V and ARM have no dedicated `FLAGS` register, this eliminates unnecessary dependency chains on FLAGS register.

Cache Hierarchy: Understand the levels of cache, their sizes, and their latencies.
Execution Units: Identify the types and numbers of execution units (e.g., ALUs, FPUs).
Instruction Set Extensions: Familiarize yourself with available SIMD, cryptographic, and other specialized instructions.
These aspects are often publicly accessible in the CPU's datasheet or technical reference manual.

Other details of a microarchitecture might not be public, such as sizes of branch prediction history buffers, branch misprediction penalty, instructions latencies and throughput. While this information is not disclosed by CPU vendors, people have reverse-engineered some of it, which can be found online.

### ISA Extensions {.unlisted .unnumbered}

Describe major differences between ISAs

It's not possible to learn about all specific instructions. But we suggest you to familiarize yourself with major ISA extensions and their capabilities. For example, if you are developing an AI application that uses `fp16` data types, and you target one of the modern ARM processors, make sure that your program's machine code contains corresponding `fp16` ISA extensions. If you're developing encyption/decryption software, check if it utilizes crypto extensions of your target ISA.
Provide a list of these extensions?
(e.g. AES, VNNI, AVX512FP16 and AVX512BF16, AMX, ARM fp16, DOT, SVE, SME)
Use compiler flags that generate code optimized for your target CPU. 
GCC/Clang: -march=native or -march=[architecture] (e.g., -march=skylake)
Intel Compiler: -xHost or -x[architecture] (e.g., -xCORE-AVX512)
MSVC: /arch:[architecture] (e.g., /arch:AVX2)

These advice are mostly about compute-bound loops

### CPU dispatch

Use compile-time or runtime checks to introduce platform-specific optimizations. This technique is called CPU dispatching. It allows you to write a single codebase that can be optimized for different microarchitectures. For example, you can write a generic implementation of a function and then provide microarchitecture-specific implementations that are used when the target CPU supports certain instructions. For example:

```cpp
if (__builtin_cpu_supports ("avx512f")) {
  avx512_impl();
} else {
  generic_impl();
}
```

https://johnnysswlab.com/cpu-dispatching-make-your-code-both-portable-and-fast/

### Instruction latencies and throughput {.unlisted .unnumbered}

How to reason about instruction latencies and throughput?

Be very careful about making conclusions just on the numbers. In many cases, instruction latencies are hidden by the out-of-order execution engine, and it may not matter if an instruction has latency of 4 or 8 cycles. If it doesn't block forward progress, this instruction will be handled "in the background" without harming performance. However, latency of an instuction becomes important when it stands on a critical dependency chain of instructions because it delays execution of dependant operations.

In contrast, if you have a loop that performs a lot of independent operations, you should focus on instruction throughput rather than latency. When operations are independent, they can be processed in parallel. In such scenario, the critical factor is how many operations of a certain type can be executed per cycle, or *execution throughput*. Even if an instruction has a high latency, the out-of-order execution engine can hide it. Keep in mind, there are also "in between" scenarios, where both instruction latency and throughput may affect performance.

You'll find a lot of stuff *has* to go to p5. So one of the challenges is to find ways of substituting things that aren't p5. If you're heavily bottlenecked enough of p5, then you may find that 2 ops on p0 are better than 1 op
on p5.

### Microarchitecture-specific issues {.unlisted .unnumbered}
#### Memory ordering {.unlisted .unnumbered}
example with histogram
Once memory operations are in their respective queues, the load/store unit has to make sure memory ordering is preserved.
When load is executing it has to be checked against all older stores for potential store forwarding. But some stores might still have their address unknown. The LSU has to apply memory disambiguation prediction to decide if load can proceed ahead of unknown stores or not. And clearly load cannot forward from a store which address is still unknown.
#### when FMA contraction hurts performance
example with nanobench
#### Memory alignment {.unlisted .unnumbered}
example with split loads in matmul
#### 4K aliasing {.unlisted .unnumbered}
just describe
https://richardstartin.github.io/posts/4k-aliasing
#### Cache trashing {.unlisted .unnumbered}
just describe
Avoid Cache Thrashing: Minimize cache conflicts by ensuring data structures do not excessively map to the same cache lines.
https://github.com/ibogosavljevic/hardware-efficiency/blob/main/cache-conflicts/cache_conflicts.c
#### AVX-SSE Transitions {.unlisted .unnumbered}
#### Non-temporal stores {.unlisted .unnumbered}
remove?