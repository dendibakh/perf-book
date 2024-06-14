### Microarchitecture-Specific Performance Issues

#### Memory ordering {.unlisted .unnumbered}

example with histogram
Once memory operations are in their respective queues, the load/store unit has to make sure memory ordering is preserved.
When load is executing it has to be checked against all older stores for potential store forwarding. But some stores might still have their address unknown. The LSU has to apply memory disambiguation prediction to decide if load can proceed ahead of unknown stores or not. And clearly load cannot forward from a store which address is still unknown.

4.6.10 Memory Dependence  (https://developer.apple.com/documentation/apple-silicon/cpu-optimization-guide)

#### Memory alignment {.unlisted .unnumbered}

The cores support unaligned accesses to normal, cacheable memory for all available
data sizes. When executed sporadically, unaligned accesses generally complete without
any observable performance impact to overall execution. Some accesses will suffer
delays, however, and the impact is often greater for stores than loads

example with split loads in matmul

#### 4K aliasing {.unlisted .unnumbered}

just describe
https://richardstartin.github.io/posts/4k-aliasing
While unlikely to be a significant
problem, L1I Cache misses may result from set conflicts. Apple silicon uses 16KB
memory pages that may make this even more likely to occur, since independent
libraries tend to be aligned to page boundaries when they are loaded.

#### Cache trashing {.unlisted .unnumbered}

just describe
Avoid Cache Thrashing: Minimize cache conflicts by ensuring data structures do not excessively map to the same cache lines.
https://github.com/ibogosavljevic/hardware-efficiency/blob/main/cache-conflicts/cache_conflicts.c

#### Non-Temporal Loads and Stores {.unlisted .unnumbered}

Caches naturally store data close to the processor under the assumption that the data in
the cache line will be used again in the near term. Data that benefits from caching is said
to have temporal locality. However, some algorithms stream (read and/or write) through
large quantities of data with little temporal reuse. In these cases, storing the data in the
cache is counterproductive because it floods (or "pollutes") the cache with unneeded
data, forcing out potentially useful data.
When using Non-Temporal Loads and Stores, the processor will optimize cache allocation
policies for particular cache lines to minimize pollution.
These special assembly instructions usually have "NT" suffix.

https://www.agner.org/optimize/optimizing_cpp.pdf#page=108&zoom=100,116,716

#### Store-to-Load Forwarding Delays {.unlisted .unnumbered}

#### Minimize Moves Between Integer and Floating-Point Registers {.unlisted .unnumbered}

DUP(general), FMOV(general), INS(general), MOV(from general), SCVTF(scalar), UCVTF(scalar)
Movement of data between integer and vector registers requires several cycles. Load
directly into vector registers
In most of the cases it is compiler's job to ensure, but in case you're writing compiler intrinsics or inline assembly routines, this advice may become handy.
When you need to load a `uint32_t` value from memory and then convert it to `float`, do not load the value in a general-purpose register (e.g. `EAX`) and then convert it to `XMM0`; load straight into `XMM0`.

Also, avoid mixing single and double precision values. For example:
```cpp
float circleLength(float r) {
    //return 2.0 * 3.14 * r; // 
    return 2.0f * 3.14f * r;
}
```

#### Slow Floating-Point Arithmetic {.unlisted .unnumbered}

#### AVX-SSE Transitions {.unlisted .unnumbered}

remove?
https://www.agner.org/optimize/microarchitecture.pdf#page=167&zoom=100,116,904