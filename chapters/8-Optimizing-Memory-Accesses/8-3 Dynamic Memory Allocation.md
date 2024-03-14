## Dynamic Memory Allocation.

[TODO]: Elaborate. Add reference to heaptrack.

First of all, there are many drop-in replacements for `malloc`, which are faster, more scalable,[^15] and address [fragmentation](https://en.wikipedia.org/wiki/Fragmentation_(computing))[^20] problems better. You can have a few percent performance improvement just by using a non-standard memory allocator. A typical issue with dynamic memory allocation is when at startup threads race with each other trying to allocate their memory regions at the same time.[^5] One of the most popular memory allocation libraries are [jemalloc](http://jemalloc.net/)[^17] and [tcmalloc](https://github.com/google/tcmalloc)[^18].

Secondly, it is possible to speed up allocations using custom allocators, for example, [arena allocators](https://en.wikipedia.org/wiki/Region-based_memory_management)[^16]. One of the main advantages is their low overhead since such allocators don't execute system calls for every memory allocation. Another advantage is its high flexibility. Developers can implement their own allocation strategies based on the memory region provided by the OS. One simple strategy could be to maintain two different allocators with their own arenas (memory regions): one for the hot data and one for the cold data. Keeping hot data together creates opportunities for it to share cache lines, which improves memory bandwidth utilization and spatial locality. It also improves TLB utilization since hot data occupies less amount of memory pages. Also, custom memory allocators can use thread-local storage to implement per-thread allocation and get rid of any synchronization between threads. This becomes useful when an application is based on a thread pool and does not spawn a large number of threads.

## Tune the Code for Memory Hierarchy.

[TODO]: Elaborate more

The performance of some applications depends on the size of the cache on a particular level. The most famous example here is improving matrix multiplication with [loop blocking](https://en.wikipedia.org/wiki/Loop_nest_optimization) (tiling). The idea is to break the working size of the matrix into smaller pieces (tiles) such that each tile will fit in the L2 cache.[^9] Most of the architectures provide `CPUID`-like instruction,[^11] which allows us to query the size of caches. Alternatively, one can use [cache-oblivious algorithms](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)[^19] whose goal is to work reasonably well for any size of the cache.

Intel CPUs have a Data Linear Address HW feature (see [@sec:sec_PEBS_DLA]) that supports cache blocking as described on an easyperf [blog post](https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy)[^10].

[TODO]: Trim footnotes

[^9]: Usually, people tune for the size of the L2 cache since it is not shared between the cores.
[^10]: Blog article "Detecting false sharing" - [https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy](https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy).
[^11]: In Intel processors `CPUID` instruction is described in [@IntelOptimizationManual, Volume 2]
[^15]: Typical `malloc` implementation involves synchronization in case multiple threads would try to dynamically allocate the memory
[^16]: Region-based memory management - [https://en.wikipedia.org/wiki/Region-based_memory_management](https://en.wikipedia.org/wiki/Region-based_memory_management)
[^17]: jemalloc - [http://jemalloc.net/](http://jemalloc.net/).
[^18]: tcmalloc - [https://github.com/google/tcmalloc](https://github.com/google/tcmalloc)
[^19]: Cache-oblivious algorithm - [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm).
[^20]: Fragmentation - [https://en.wikipedia.org/wiki/Fragmentation_(computing)](https://en.wikipedia.org/wiki/Fragmentation_(computing)).
