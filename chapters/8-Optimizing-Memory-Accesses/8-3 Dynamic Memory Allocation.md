## Dynamic Memory Allocation.

Developers should realize that dynamic memory allocation has many associated costs. Allocating an object on the stack is done instantly, regardless of the size of the object: you just need to move the stack pointer. However, dynamic memory allocation is a more complex operation. It involves calling a standard library function like `malloc`, which potentially may delegate the allocation to the operating system. Avoiding unnecessary dynamic memory allocation is a first step to avoiding these costs. The easy target in this process are temporary allocations, i.e., allocations that are directly followed by their deallocation. In [@sec:HeaptrackCaseStudy] we showed how you can use `heaptrack` to find sources of dynamic memory allocations.

You can amortize the cost of many small allocations by allocating one large block. This is the core idea behind [arena allocators](https://en.wikipedia.org/wiki/Region-based_memory_management)[^16] and memory pools. It gives more flexibility for manual memory management. You can take a memory region allocated by the OS and design your own allocation strategy on top of that region. One simple strategy could be to divide that region into two parts: one for the hot data and one for the cold data. And provide two allocation methods that will tap into their own arenas. Keeping hot data together creates opportunities for better cache utilization. It also likely to improve TLB utilization since hot data will be more compact an will occupy fewer memory pages. 

Another cost of dynamic memory allocation appears when an application is using multiple threads. When two threads are trying to allocate memory at the same time, the OS has to synchronize them. In a highly concurrent application, threads may spend a significant amount of time waiting for a common lock to allocate memory. This sometimes happens at an application startup, when many threads are created and they race with each other trying to allocate memory at the same time. The same applies to memory deallocation. Again, custom allocators can help to avoid this problem, for example, by employing a separate arena for each thread.

There are many drop-in replacements for the standard dynamic memory allocation routines (`malloc` and `free`), which are faster, more scalable, and address fragmentation problems better. One of the most popular memory allocation libraries are [jemalloc](http://jemalloc.net/)[^17] and [tcmalloc](https://github.com/google/tcmalloc)[^18]. Some projects adopted `jemalloc` and `tcmalloc` as their default memory allocator, and they have seen significant performance improvements. 

Finally, some costs of dynamic memory allocation are hidden[^20] and cannot be easily measured. In all major operating systems, the pointer returned by `malloc` is just a promise – the OS commits that when pages are touched it will provide required memory, but the actual physical pages are not allocated until the virtual addresses are accessed. This is called *demand paging*, which incurrs a cost of minor page fault for every newly allocated page. We discuss how to mitigate this cost in [@sec:AvoidPageFaults]. Also, for security reasons, all modern operating systems erase the contents (write zeros) of a page before giving it to the next process. The OS maintains a pool of zeroed pages to have them ready for allocation. But when this pool runs out of available zeroed pages, the OS has to zero a page on demand. This process isn't super expensive, but it isn't free either and may increase latency of a memory allocation call.

## Tune the Code for Memory Hierarchy.

[TODO]: Elaborate more

The performance of some applications depends on the size of the cache on a particular level. The most famous example here is improving matrix multiplication with [loop blocking](https://en.wikipedia.org/wiki/Loop_nest_optimization) (tiling). The idea is to break the working size of the matrix into smaller pieces (tiles) such that each tile will fit in the L2 cache.[^9] Most of the architectures provide `CPUID`-like instruction,[^11] which allows us to query the size of caches. Alternatively, one can use [cache-oblivious algorithms](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)[^19] whose goal is to work reasonably well for any size of the cache.

Intel CPUs have a Data Linear Address HW feature (see [@sec:sec_PEBS_DLA]) that supports cache blocking as described on an easyperf [blog post](https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy)[^10].

[TODO]: Trim footnotes

[^16]: Region-based memory management - [https://en.wikipedia.org/wiki/Region-based_memory_management](https://en.wikipedia.org/wiki/Region-based_memory_management)
[^17]: jemalloc - [http://jemalloc.net/](http://jemalloc.net/).
[^18]: tcmalloc - [https://github.com/google/tcmalloc](https://github.com/google/tcmalloc)
[^20]: Bruce Dawson: Hidden Costs of Memory Allocation - [https://randomascii.wordpress.com/2014/12/10/hidden-costs-of-memory-allocation/](https://randomascii.wordpress.com/2014/12/10/hidden-costs-of-memory-allocation/).

[^9]: Usually, people tune for the size of the L2 cache since it is not shared between the cores.
[^10]: Blog article "Detecting false sharing" - [https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy](https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy).
[^11]: In Intel processors `CPUID` instruction is described in [@IntelOptimizationManual, Volume 2]
[^19]: Cache-oblivious algorithm - [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm).
