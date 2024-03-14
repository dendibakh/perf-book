---
typora-root-url: ..\..\img
---

# Optimizing Memory Accesses {#sec:MemBound}

[TODO]: maybe add example of using `perf mem`.

Modern computers are still being built based on the classical Von Neumann architecture which decouples CPU, memory and input/output units. Nowadays, operations with memory (loads and stores) account for the largest portion of performance bottlenecks and power consumption. It is no surprise that we start with this category first.

The statement that memory hierarchy performance is critical can be exacerbated by Figure @fig:CpuMemGap. It shows the growth of the gap in performance between memory and processors. The vertical axis is on a logarithmic scale and shows the growth of the CPU-DRAM performance gap. The memory baseline is the latency of memory access of 64 KB DRAM chips from 1980. Typical DRAM performance improvement is 7% per year, while CPUs enjoy 20-50% improvement per year. According to this picture, processor performance has plateaued, but even then, the gap in performance remains. [@Hennessy]

![The gap in performance between memory and processors. *© Image from [@Hennessy].*](../../img/memory-access-opts/ProcessorMemoryGap.png){#fig:CpuMemGap width=90%}

Indeed, a variable can be fetched from the smallest L1 cache in just a few clock cycles, but it can take more than three hundred clock cycles to fetch the variable from DRAM if it is not in the CPU cache. From a CPU perspective, a last-level cache miss feels like a *very* long time, especially if the processor is not doing any useful work during that time. Execution threads may also be starved when the system is highly loaded with threads accessing memory at a very high rate and there is no available memory bandwidth to satisfy all loads and stores promptly.

When an application executes a large number of memory accesses and spends significant time waiting for them to finish, such an application is characterized as being bounded by memory. It means that to further improve its performance, we likely need to improve how we access memory, reduce the number of such accesses or upgrade the memory subsystem itself.

In the TMA methodology, the `Memory Bound` metric estimates a fraction of slots where a CPU pipeline is likely stalled due to demand for load or store instructions. The first step to solving such a performance problem is to locate the memory accesses that contribute to the high `Memory Bound` metric (see [@sec:secTMA_Intel]). Once guilty memory access is identified, several optimization strategies could be applied. In this chapter, we will discuss techniques to improve memory access patterns.
