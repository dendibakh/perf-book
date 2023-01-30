---
typora-root-url: ..\..\img
---

# Optimizing Memory Accesses {#sec:MemBound}

TODO: fix the beginning

## CPU Back-End Optimizations

CPU Back-End (BE) component is discussed in [@sec:uarchBE]. Most of the time, inefficiencies in CPU BE can be described as a situation when FE has fetched and decoded instructions, but BE is overloaded and can't handle new instructions. Technically speaking, it is a situation when FE cannot deliver uops due to a lack of required resources for accepting new uops in the Backend. An example of it may be a stall due to data-cache miss or a stall due to the divider unit being overloaded.

I want to emphasize to the reader that it's recommended to start looking into optimizing code for CPU BE only when TMA points to a high "Back-End Bound" metric. TMA further divides the `Backend Bound` metric into two main categories: `Memory Bound` and `Core Bound`, which we will discuss next.

## Memory Bound

When an application executes a large number of memory accesses and spends significant time waiting for them to finish, such an application is characterized as being bounded by memory. It means that to further improve its performance, we likely need to improve how we access memory, reduce the number of such accesses or upgrade the memory subsystem itself. 

The statement that memory hierarchy performance is very important is backed by Figure @fig:CpuMemGap. It shows the growth of the gap in performance between memory and processors. The vertical axis is on a logarithmic scale and shows the growth of the CPU-DRAM performance gap. The memory baseline is the latency of memory access of 64 KB DRAM chips from 1980. Typical DRAM performance improvement is 7% per year, while CPUs enjoy 20-50% improvement per year.[@Hennessy]

![The gap in performance between memory and processors. *© Image from [@Hennessy].*](../../img/memory-access-opts/ProcessorMemoryGap.png){#fig:CpuMemGap width=90%}

In TMA, `Memory Bound` estimates a fraction of slots where the CPU pipeline is likely stalled due to demand for load or store instructions. The first step to solving such a performance problem is to locate the memory accesses that contribute to the high `Memory Bound` metric (see [@sec:secTMA_locate]). Once guilty memory access is identified, several optimization strategies could be applied. Below we will discuss a few typical cases.
