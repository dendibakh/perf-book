---
typora-root-url: ..\..\img
---

## Explicit Memory Prefetching {#sec:memPrefetch}

By now, you should know that memory accesses that are not resolved from caches are often very expensive. Modern CPUs try very hard to lower the penalty of cache misses if the prefetch request is issued sufficiently ahead of time. If the requested memory location is not in the cache, we will suffer the cache miss anyway as we have to go to the DRAM and fetch the data anyway. But if manage to bring that memory location in caches by the time the data is demanded by the program, then we effectively make the penalty of a cache miss to be zero.

Modern CPUs have two mechanism for prefetching data: hardware prefetching and OOO execution, which we discussed in [@sec:uarch]. HW prefetchers help to hide the memory access latency by initiating prefetching requests on repetitive memory access patterns. While OOO engine looks N instructions into the future and issues loads early to allow smooth execution of future instructions that will demand this data.

HW prefetchers fail when data accesses patterns are too complicated to predict. And there is nothing SW developers can do about it as we cannot control the behavior of this unit. On the other hand, OOO engine does not try to predict memory locations that will be needed in the future as HW prefetching does. So, the only measure of success for it is how much latency it was able to hide by scheduling the load in advance.

Consider a small snippet of code in [@lst:MemPrefetch1], where `arr` is an array of one million integers. The index `idx`, which is assigned to a random value, is immediately used to access a location in `arr`, which almost certainly misses in caches as it is random. It is impossible for a HW prefetcher to predict as every time the load goes to a completely new place in memory. The interval from the time the address of a memory location is known (returned from the function `random_distribution`) until the value of that memory location is demanded (call to `doSomeExtensiveComputation`) is called *prefetching window*. In this example, the OOO engine doesn't have the opportunity to issue the load early since the prefetching window is very small. This leads to the latency of the memory access `arr[idx]` to stand on a critical path while executing the loop as shown in figure @fig:SWmemprefetch1. It's visible that the program waits for the value to come back (hatched fill rectangle) without making forward progress.

Listing: Random number feeds a subsequent load.

~~~~ {#lst:MemPrefetch1 .cpp}
for (int i = 0; i < N; ++i) {
  size_t idx = random_distribution(generator);
  int x = arr[idx]; // cache miss
  doSomeExtensiveComputation(x);
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Execution timeline that shows the load latency standing on a critical path.](../../img/memory-access-opts/SWmemprefetch1.png){#fig:SWmemprefetch1 width=90%}

There is another important observation here. When a CPU gets close to finish running the first iteration, it speculatively starts executing instruction from the second iteration. It creates a positive overlap in the execution between iterations. However, even in modern processors, there are not enough OOO capabilities to fully overlap the latency of a cache miss with executing `doSomeExtensiveComputation` from the iteration1. In other words, in our case a CPU cannot look that far ahead of current execution to issue the load early enough.

Luckily, it's not a dead end as there is a way to speed up this code. To hide the latency of a cache miss, we need to overlap it with execution of `doSomeExtensiveComputation`. We can achieve it if we pipeline generation of random numbers and start prefetching the memory location for the next iteration as shown in [@lst:MemPrefetch2]. Notice the usage of [`__builtin_prefetch`](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)[^4], a special hint that developers can use to explicitly request a CPU to prefetch a certain memory location. Graphical illustration of this transformation is illustrated in figure @fig:SWmemprefetch2.

Listing: Utilizing Exlicit Software Memory Prefetching hints.

~~~~ {#lst:MemPrefetch2 .cpp}
size_t idx = random_distribution(generator);
for (int i = 0; i < N; ++i) {
  int x = arr[idx]; 
  idx = random_distribution(generator);
  // prefetch the element for the next iteration
  __builtin_prefetch(&arr[idx]);
  doSomeExtensiveComputation(x);
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Hiding the cache miss latency by overlapping it with other execution.](../../img/memory-access-opts/SWmemprefetch2.png){#fig:SWmemprefetch2 width=90%}

TODO: prefetch is a fake load.
TODO: hint will be compiled down to machine instruction
TODO: one can also use compiler intrinsic
TODO: It is not always possible. example: pointer chaising
TODO: add example of look ahead for 4,8,16 iterations.

I STOPPED HERE

For prefetch hints to take effect, be sure to insert it well ahead of time so that by the time the loaded value will be used in other calculations, it will be already in the cache. Also, do not insert it too early since it may pollute the cache with the data that is not used for some time. In order to estimate the prefetch window, use the method described in [@sec:timed_lbr]. [^5]

The most common scenario where engineers use explicit memory prefetching is to get the data required for the next iteration of the loop. However, linear function prefetching can also be very helpful, e.g., when you know the address of the data ahead of time but request the data with some delay (prefetch window).

Explicit memory prefetching is not portable, meaning that if it gives performance gains on one platform, it doesn't guarantee similar speedups on another platform. Even worse, when used badly, it can worsen the performance of caches. When using the wrong size of a memory block or requesting prefetches too often, it can force other useful data to be evicted from the caches.

While software prefetching gives programmer control and flexibility, it's not always easy to get it right. Consider a situation when we want to insert a prefetch instruction into the piece of code that has average IPC=2, and every DRAM access takes 100 cycles. To have the best effect, we would need to insert prefetching instruction 200 instructions before the load. It is not always possible, especially if the load address is computed right before the load itself. The pointer chasing problem can be a good example when explicit prefetching is helpless. [@PrefetchSlides]

Finally, an explicit prefetch instruction increases code size and adds pressure on the CPU Front-End. The prefetch instruction is just like any other instruction: it consumes CPU resources, and when using it wrong, it can pessimize the performance of a program.

[^3]: For this example, we define "big enough" to be more than this size of L3 cache inside a typical desktop CPU, which, at the time of writing, varies from 5 to 20 MB.
[^4]: GCC builtins - [https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html).
[^5]: Readers can also find an example of estimating the prefetch window in the article: [https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf#application-estimating-prefetch-window](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf#application-estimating-prefetch-window).
