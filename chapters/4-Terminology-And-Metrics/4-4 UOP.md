---
typora-root-url: ..\..\img
---

## UOPs (micro-ops) {#sec:sec_UOP}

Microprocessors with the x86 architecture translate complex CISC-like instructions into simple RISC-like microoperations, abbreviated as µops or uops. We will use the "uop" notation as it is easier to write. A simple addition instruction such as `ADD rax, rbx` generates only one µop, while more complex instruction like `ADD rax, [mem]` may generate two: one for reading from `mem` memory location into a temporary (un-named) register, and one for adding it to the `rax` register. The instruction `ADD [mem], rax` generates three uops: one for reading from memory, one for adding, and one for writing the result back to memory.

The main advantage of splitting instructions into micro operations is that uops can be executed:

* **Out of order**. Consider `PUSH rbx` instruction, that decrements the stack pointer by 8 bytes and then stores the source operand on the top of the stack. Suppose that `PUSH rbx` is "cracked" into two dependent micro operations after decode:
  ```
  SUB rsp, 8
  STORE [rsp], rbx
  ```
  Often, function prologue saves multiple registers using `PUSH` instructions. In our case, the next `PUSH` instruction can start executing after the `SUB` uop of the previous `PUSH` instruction finishes, and doesn't have to wait for the `STORE` uop, which can now go asynchronously.

* **In parallel**. Consider `HADDPD xmm1, xmm2` instruction, that will sum up (reduce) two double precision floating point values in both `xmm1` and `xmm2` and store two results in `xmm1` as follows: 
  ```
  xmm1[63:0] = xmm2[127:64] + xmm2[63:0]
  xmm1[127:64] = xmm1[127:64] + xmm1[63:0]
  ```
  One way to microcode this instruction would be to do the following: 1) reduce `xmm1`, 2) reduce `xmm2`, 3) merge the two results. Three uops in total. Notice that steps 1) and 2) are independent and thus can be done in parallel.

Sometimes, uops can also be fused. There are two types of fusion in modern CPUs:

* **Microfusion** - fuse uops from the same machine instruction. Microfusion can only be applied to two types of combinations: memory write operations and read-modify operations. For example:

  ```bash
  # Read the memory location [ESI] and add it to EAX
  # Two uops are fused into one at the decoding step.
  add    eax, [esi]
  ```
  
* **Macrofusion** - fuse uops from different machine instructions. The decoders can fuse arithmetic or logic instruction with a subsequent conditional jump instruction into a single compute-and-branch µop in certain cases. For example:

  ```bash
  # Two uops from DEC and JNZ instructions are fused into one
  .loop:
    dec rdi
    jnz .loop
  ```

Both Micro- and Macrofusion save bandwidth in all stages of the pipeline from decoding to retirement. The fused operations share a single entry in the reorder buffer (ROB). The capacity of the ROB is increased when a fused uop uses only one entry. This single ROB entry represents two operations that have to be done by two different execution units. The fused ROB entry is dispatched to two different execution ports but is retired again as a single unit. Readers can learn more about uop fusion in [@fogMicroarchitecture].

To collect the number of issued, executed, and retired uops for an application, you can use Linux `perf` as follows[^1]:

```bash
$ perf stat -e uops_issued.any,uops_executed.thread,uops_retired.all -- a.exe
  2856278  uops_issued.any             
  2720241  uops_executed.thread
  2557884  uops_retired.all
```

The way instructions are split into micro operations may vary across CPU generations. Usually, the lower number of uops used for an instruction means that HW has a better support for it and is likely to have lower latency and higher throughput. For the latest Intel and AMD CPUs, the vast majority of instructions generate exactly one uop. Latency, throughput, port usage, and the number of uops for x86 instructions on recent microarchitectures can be found at [uops.info](https://uops.info/table.html)[^2] website.

[^1]: `UOPS_RETIRED.ALL` event is not available since Skylake. Use `UOPS_RETIRED.RETIRE_SLOTS`.
[^2]: Instruction latency and Throughput - [https://uops.info/table.html](https://uops.info/table.html)