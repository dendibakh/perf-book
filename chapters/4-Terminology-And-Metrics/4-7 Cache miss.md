## Cache Miss

As discussed in [@sec:MemHierar], any memory request missing in a particular level of cache must be serviced by higher-level caches or DRAM. This implies a significant increase in the latency of such memory access. The typical latency of memory subsystem components is shown in Table {@tbl:mem_latency}. Performance greatly suffers when a memory request misses in the Last Level Cache (LLC) and goes all the way down to the main memory.[^3]

-------------------------------------------------
Memory Hierarchy Component   Latency (cycle/time)

--------------------------   --------------------
L1 Cache                     4 cycles (~1 ns)

L2 Cache                     10-25 cycles (5-10 ns)

L3 Cache                     ~40 cycles (20 ns)

Main                         200+ cycles (100 ns)
Memory

-------------------------------------------------

Table: Typical latency of a memory subsystem in x86-based platforms. {#tbl:mem_latency}

Both instruction and data fetches can miss in the cache. According to Top-down Microarchitecture Analysis (see [@sec:TMA]), an instruction cache (I-cache) miss is characterized as a Frontend stall, while a data cache (D-cache) miss is characterized as a Backend stall. Instruction cache misses happen very early in the CPU pipeline during instruction fetch. Data cache misses happen much later during the instruction execution phase.

Linux `perf` users can collect the number of L1 cache misses by running:

```bash
$ perf stat -e mem_load_retired.fb_hit,mem_load_retired.l1_miss,
  mem_load_retired.l1_hit,mem_inst_retired.all_loads -- a.exe
   29580  mem_load_retired.fb_hit
   19036  mem_load_retired.l1_miss
  497204  mem_load_retired.l1_hit
  546230  mem_inst_retired.all_loads
```

Above is the breakdown of all loads for the L1 data cache and fill buffers. A load might either hit the already allocated fill buffer (`fb_hit`), hit the L1 cache (`l1_hit`), or miss both (`l1_miss`), thus `all_loads = fb_hit + l1_hit + l1_miss`.[^2] We can see that only 3.5% of all loads miss in the L1 cache, thus the *L1 hit rate* is 96.5%.

We can further break down L1 data misses and analyze L2 cache behavior by running:

```bash
$ perf stat -e mem_load_retired.l1_miss,
  mem_load_retired.l2_hit,mem_load_retired.l2_miss -- a.exe
  19521  mem_load_retired.l1_miss
  12360  mem_load_retired.l2_hit
   7188  mem_load_retired.l2_miss
```

From this example, we can see that 37% of loads that missed in the L1 D-cache also missed in the L2 cache, thus the *L2 hit rate* is 63%. A breakdown for the L3 cache can be made similarly.

[^2]: Careful readers may notice a discrepancy in the numbers: `fb_hit + l1_hit + l1_miss = 545,820`, which doesn't exactly match `all_loads`. Most likely it's due to slight inaccuracy in hardware event collection, but we did not investigate this since the numbers are very close.
[^3]: There is also an interactive view that visualizes the latency of different operations in modern systems - [https://colin-scott.github.io/personal_website/research/interactive_latency.html](https://colin-scott.github.io/personal_website/research/interactive_latency.html)
