---
typora-root-url: ..\..\img
---

## Micro-ops {#sec:sec_UOP}

Microprocessors with the x86 architecture translate complex CISC-like instructions into simple RISC-like microoperations, abbreviated as $\mu$ops or $\mu$ops. A simple addition instruction such as `ADD rax, rbx` generates only one $\mu$op, while a more complex instruction like `ADD rax, [mem]` may generate two: one for reading from the `mem` memory location into a temporary (un-named) register, and one for adding it to the `rax` register. The instruction `ADD [mem], rax` generates three $\mu$ops: one for reading from memory, one for adding, and one for writing the result back to memory.

Decoding to $\mu$ops is done by the frontend. To reduce decode latency, lower the power consumption of the decoder and prevent that the frontend becomes the bottleneck, there is a cache for the $\mu$ops code. This cache is called the $\mu$op cache.

The main advantage of splitting instructions into micro operations is that $\mu$ops can be executed:

* **Out of order**: consider the `PUSH rbx` instruction, which decrements the stack pointer by 8 bytes and then stores the source operand on the top of the stack. Suppose that `PUSH rbx` is "cracked" into two dependent micro operations after decode:
  ```
  SUB rsp, 8
  STORE [rsp], rbx
  ```
  Often, a function prologue saves multiple registers by using multiple `PUSH` instructions. In our case, the next `PUSH` instruction can start executing after the `SUB` $\mu$op of the previous `PUSH` instruction finishes, and doesn't have to wait for the `STORE` $\mu$op, which can now execute asynchronously.

* **In parallel**: consider `HADDPD xmm1, xmm2` instruction, which will sum up (reduce) two double precision floating point values in both `xmm1` and `xmm2` and store two results in `xmm1` as follows: 
  ```
  xmm1[63:0] = xmm2[127:64] + xmm2[63:0]
  xmm1[127:64] = xmm1[127:64] + xmm1[63:0]
  ```
  One way to microcode this instruction would be to do the following: 1) reduce `xmm2` and store the result in `xmm_tmp1[63:0]`, 2) reduce `xmm1` and store the result in `xmm_tmp2[63:0]`, 3) merge `xmm_tmp1` and `xmm_tmp2` into `xmm1`. Three $\mu$ops in total. Notice that steps 1) and 2) are independent and thus can be done in parallel.

Even though we were just talking about how instructions are split into smaller pieces, sometimes, $\mu$ops can also be fused together. There are two types of fusion in modern CPUs:

* **Microfusion**: fuse $\mu$ops from the same machine instruction. Microfusion can only be applied to two types of combinations: memory write operations and read-modify operations. For example:

  ```bash
  add    eax, [mem]
  ```
  There are two $\mu$ops in this instruction: 1) read the memory location `mem`, and 2) add it to `eax`. With microfusion, two $\mu$ops are fused into one at the decoding step.
  
* **Macrofusion**: fuse $\mu$ops from different machine instructions. The decoders can fuse arithmetic or logic instruction with a subsequent conditional jump instruction into a single compute-and-branch $\mu$op in certain cases. For example:

  ```bash
  .loop:
    dec rdi
    jnz .loop
  ```
  With macrofusion, two $\mu$ops from the `DEC` and `JNZ` instructions are fused into one. The Zen4 microarchitecture also added support for DIV/IDIV and NOP macrofusion [@amd_zen4, sections 2.9.4 and 2.9.5].

Both micro- and macrofusion save bandwidth in all stages of the pipeline from decoding to retirement. The fused operations share a single entry in the reorder buffer (ROB). The capacity of the ROB is utilized better when a fused $\mu$op uses only one entry. Such a fused ROB entry is later dispatched to two different execution ports but is retired again as a single unit. Readers can learn more about $\mu$op fusion in [@fogMicroarchitecture].

To collect the number of issued, executed, and retired $\mu$ops for an application, you can use Linux `perf` as follows:

```bash
$ perf stat -e uops_issued.any,uops_executed.thread,uops_retired.slots -- ./a.exe
  2856278  uops_issued.any             
  2720241  uops_executed.thread
  2557884  uops_retired.slots
```

The way instructions are split into micro operations may vary across CPU generations. Usually, a lower number of $\mu$ops used for an instruction means that HW has better support for it and is likely to have lower latency and higher throughput. For the latest Intel and AMD CPUs, the vast majority of instructions generate exactly one $\mu$op. Latency, throughput, port usage, and the number of $\mu$ops for x86 instructions on recent microarchitectures can be found at the [uops.info](https://uops.info/table.html)[^1] website.

[^1]: Instruction latency and Throughput - [https://uops.info/table.html](https://uops.info/table.html)
