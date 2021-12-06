---
typora-root-url: ..\..\img
---

## UOPs (micro-ops) {#sec:sec_UOP}

Microprocessors with the x86 architecture translate complex [CISC](https://en.wikipedia.org/wiki/Complex_instruction_set_computer)-like[^1] instructions into simple [RISC](https://en.wikipedia.org/wiki/Reduced_instruction_set_computer)-like[^5] microoperations - abbreviated µops or uops. The main advantage of this is that µops can be executed out of order [@fogMicroarchitecture, chapter 2.1]. A simple addition instruction such as `ADD EAX,EBX` generates only one µop, while more complex instruction like `ADD EAX,[MEM1]` may generate two: one for reading from memory into a temporary (un-named) register, and one for adding the contents of the temporary register to `EAX`. The instruction `ADD [MEM1],EAX` may generate three µops: one for reading from memory, one for adding, and one for writing the result back to memory.  The relationship between instructions and the way they are split into microoperations can vary across CPU generations[^6].

On the opposite of splitting complex CISC-like instructions into RISC-like microoperations (Uops), the latter can also be fused. There are two types of fusion in modern Intel CPUs:

* [Microfusion](https://easyperf.net/blog/2018/02/15/MicroFusion-in-Intel-CPUs)[^3] - fuse uops from the same machine instruction. Microfusion can only be applied to two types of combinations: memory write operations and read-modify operations. For example:

  ```bash
  # Read the memory location [ESI] and add it to EAX
  # Two uops are fused into one at the decoding step.
  add    eax, [esi]
  ```
  
* [Macrofusion](https://easyperf.net/blog/2018/02/23/MacroFusion-in-Intel-CPUs)[^4] - fuse uops from different machine instructions. The decoders can fuse arithmetic or logic instruction with a subsequent conditional jump instruction into a single compute-and-branch µop in certain cases. For example:
  ```bash
  # Two uops from DEC and JNZ instructions are fused into one
  .loop:
    dec rdi
    jnz .loop
  ```

Both Micro- and Macrofusion save bandwidth in all stages of the pipeline from decoding to retirement. The fused operations share a single entry in the reorder buffer (ROB). The capacity of the ROB is increased when a fused uop uses only one entry. This single ROB entry represents two operations that have to be done by two different execution units. The fused ROB entry is dispatched to two different execution ports but is retired again as a single unit. [@fogMicroarchitecture]

Linux `perf` users can collect the number of issued, executed, and retired uops for their workload by running[^2]:

```bash
$ perf stat -e uops_issued.any,uops_executed.thread,uops_retired.all -- a.exe
  2856278  uops_issued.any             
  2720241  uops_executed.thread
  2557884  uops_retired.all
```

Latency, throughput, port usage, and the number of uops for instructions on recent x86 microarchitectures can be found at [uops.info](https://uops.info/) website.

[^1]: CISC - [https://en.wikipedia.org/wiki/Complex_instruction_set_computer](https://en.wikipedia.org/wiki/Complex_instruction_set_computer).
[^2]: `UOPS_RETIRED.ALL` event is not available since Skylake. Use `UOPS_RETIRED.RETIRE_SLOTS`.
[^3]: UOP Microfusion - [https://easyperf.net/blog/2018/02/15/MicroFusion-in-Intel-CPUs](https://easyperf.net/blog/2018/02/15/MicroFusion-in-Intel-CPUs).
[^4]: UOP Macrofusion - [https://easyperf.net/blog/2018/02/23/MacroFusion-in-Intel-CPUs](https://easyperf.net/blog/2018/02/23/MacroFusion-in-Intel-CPUs).
[^5]: RISC - [https://en.wikipedia.org/wiki/Reduced_instruction_set_computer](https://en.wikipedia.org/wiki/Reduced_instruction_set_computer).
[^6]: However, for the latest Intel CPUs, the vast majority of instructions operating on registers generate exactly one uop.

