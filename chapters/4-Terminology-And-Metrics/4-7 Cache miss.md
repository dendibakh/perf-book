---
typora-root-url: ..\..\img
---

## Cache miss

As discussed in [@sec:MemHierar], any memory request missing in a particular level of cache must be serviced by higher-level caches or DRAM. This implies a significant increase in the latency of such memory access. The typical latency of memory subsystem components is shown in table {@tbl:mem_latency}.[^1] Performance greatly suffers, especially when a memory request misses in Last Level Cache (LLC) and goes all the way down to the main memory (DRAM). Intel® [Memory Latency Checker](https://www.intel.com/software/mlc)[^2] (MLC) is a tool used to measure memory latencies and bandwidth and how they change with increasing load on the system. MLC is useful for establishing a baseline for the system under test and for performance analysis.

-------------------------------------------------
Memory Hierarchy Component   Latency (cycle/time)

--------------------------   --------------------
L1 Cache                     4 cycles (~1 ns)

L2 Cache                     10-25 cycles (5-10 ns)

L3 Cache                     ~40 cycles (20 ns)

Main                         200+ cycles (100 ns)
Memory

-------------------------------------------------

Table: Typical latency of a memory subsystem. {#tbl:mem_latency}

A cache miss might happen both for instructions and data. According to Top-Down Microarchitecture Analysis (see [@sec:TMA]), an instruction (I-cache) cache miss is characterized as a Front-End stall, while a data cache (D-cache) miss is characterized as a Back-End stall. When an I-cache miss happens during instruction fetch, it is attributed as a Front-End issue. Consequently, when the data requested by this load is not found in the D-cache, this will be categorized as a Back-End issue.

Linux `perf` users can collect the number of L1-cache misses by running:

```bash
$ perf stat -e mem_load_retired.fb_hit,mem_load_retired.l1_miss,
  mem_load_retired.l1_hit,mem_inst_retired.all_loads -- a.exe
   29580  mem_load_retired.fb_hit
   19036  mem_load_retired.l1_miss
  497204  mem_load_retired.l1_hit
  546230  mem_inst_retired.all_loads
```

Above is the breakdown of all loads for the L1 data cache. We can see that only 3.5% of all loads miss in the L1 cache. We can further break down L1 data misses and analyze L2 cache behavior by running:

```bash
$ perf stat -e mem_load_retired.l1_miss,
  mem_load_retired.l2_hit,mem_load_retired.l2_miss -- a.exe
  19521  mem_load_retired.l1_miss
  12360  mem_load_retired.l2_hit
   7188  mem_load_retired.l2_miss
```

From this example, we can see that 37% of loads that missed in the L1 D-cache also missed in the L2 cache. In a similar way, a breakdown for the L3 cache can be made.

[^1]: There is also an interactive view that visualizes the cost of different operations in modern systems: [https://colin-scott.github.io/personal_website/research/interactive_latency.html](https://colin-scott.github.io/personal_website/research/interactive_latency.html).
[^2]: Memory Latency Checker - [https://www.intel.com/software/mlc](https://www.intel.com/software/mlc).
