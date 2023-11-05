---
typora-root-url: ..\..\img
---

# Optimizing Memory Accesses {#sec:MemBound}

Modern computers are still being built based on the classical Von Neumann architecture with decouples CPU, memory and input/output units. Operations with memory (loads and stores) account for the largest portion of performance bottlenecks and power consumption. It is no surprise that we start with this category first.

The statement that the memory hierarchy performance is very important is backed by Figure @fig:CpuMemGap. It shows the growth of the gap in performance between memory and processors. The vertical axis is on a logarithmic scale and shows the growth of the CPU-DRAM performance gap. The memory baseline is the latency of memory access of 64 KB DRAM chips from 1980. Typical DRAM performance improvement is 7% per year, while CPUs enjoy 20-50% improvement per year.[@Hennessy]

![The gap in performance between memory and processors. *© Image from [@Hennessy].*](../../img/memory-access-opts/ProcessorMemoryGap.png){#fig:CpuMemGap width=90%}

Indeed, a variable can be fetched from the smallest L1 cache in just a few clock cycles, but it can take more than three hundred clock cycles to fetch the variable from DRAM if it is not in the CPU cache. From a CPU perspective, a last level cache miss feels like a *very* long time, especially if the processor is not doing any useful work during that time. Execution threads may also be starved when the system is highly loaded with threads accessing memory at a very high rate and there is no available memory bandwidth to satisfy all loads and stores in a timely manner.

When an application executes a large number of memory accesses and spends significant time waiting for them to finish, such an application is characterized as being bounded by memory. It means that to further improve its performance, we likely need to improve how we access memory, reduce the number of such accesses or upgrade the memory subsystem itself.

In the TMA methodology, `Memory Bound` estimates a fraction of slots where the CPU pipeline is likely stalled due to demand for load or store instructions. The first step to solving such a performance problem is to locate the memory accesses that contribute to the high `Memory Bound` metric (see [@sec:secTMA_locate]). Once guilty memory access is identified, several optimization strategies could be applied. Below we will discuss a few typical cases.
