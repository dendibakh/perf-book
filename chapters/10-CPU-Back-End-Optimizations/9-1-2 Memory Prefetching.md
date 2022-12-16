---
typora-root-url: ..\..\img
---

### Explicit Memory Prefetching {#sec:memPrefetch}

Often, in general-purpose workloads, there are situations when data accesses have no clear pattern or are random, so hardware can't effectively prefetch the data ahead of time (see information about HW prefetchers in [@sec:HwPrefetch]). Those are cases when cache misses could not be eliminated by choosing a better data structure either. An example of code when such transformation might be profitable is shown on [@lst:MemPrefetch1]. Suppose `calcNextIndex` returns random values that significantly differ from each other. In this situation, we would have a subsequent load `arr[j]` go to a completely new place in memory and will frequently miss in caches. When the `arr` array is big enough[^3], the HW prefetcher won't be able to catch the pattern and fail to pull the required data ahead of time. In the example in [@lst:MemPrefetch1], there is some time window between when the index `j` is calculated, and when the element `arr[j]` is requested. Thanks to that, we can manually add explicit prefetching instructions with [`__builtin_prefetch`](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)[^4] as shown on [@lst:MemPrefetch2].

Listing: Memory Prefetching: baseline version.

~~~~ {#lst:MemPrefetch1 .cpp}
for (int i = 0; i < N; ++i) {
  int j = calcNextIndex();
  // ...
  doSomeExtensiveComputation();
  // ...
  x = arr[j]; // this load misses in L3 cache a lot
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing: Memory Prefetching: using built-in prefetch hints.

~~~~ {#lst:MemPrefetch2 .cpp}
for (int i = 0; i < N; ++i) {
  int j = calcNextIndex();
  __builtin_prefetch(a + j, 0, 1); // well before the load
  // ...
  doSomeExtensiveComputation();
  // ...
  x = arr[j];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For prefetch hints to take effect, be sure to insert it well ahead of time so that by the time the loaded value will be used in other calculations, it will be already in the cache. Also, do not insert it too early since it may pollute the cache with the data that is not used for some time. In order to estimate the prefetch window, use the method described in [@sec:timed_lbr]. [^5]

The most common scenario where engineers use explicit memory prefetching is to get the data required for the next iteration of the loop. However, linear function prefetching can also be very helpful, e.g., when you know the address of the data ahead of time but request the data with some delay (prefetch window).

Explicit memory prefetching is not portable, meaning that if it gives performance gains on one platform, it doesn't guarantee similar speedups on another platform. Even worse, when used badly, it can worsen the performance of caches. When using the wrong size of a memory block or requesting prefetches too often, it can force other useful data to be evicted from the caches.

While software prefetching gives programmer control and flexibility, it's not always easy to get it right. Consider a situation when we want to insert a prefetch instruction into the piece of code that has average IPC=2, and every DRAM access takes 100 cycles. To have the best effect, we would need to insert prefetching instruction 200 instructions before the load. It is not always possible, especially if the load address is computed right before the load itself. The pointer chasing problem can be a good example when explicit prefetching is helpless. [@PrefetchSlides]

Finally, an explicit prefetch instruction increases code size and adds pressure on the CPU Front-End. The prefetch instruction is just like any other instruction: it consumes CPU resources, and when using it wrong, it can pessimize the performance of a program.

[^3]: For this example, we define "big enough" to be more than this size of L3 cache inside a typical desktop CPU, which, at the time of writing, varies from 5 to 20 MB.
[^4]: GCC builtins - [https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html).
[^5]: Readers can also find an example of estimating the prefetch window in the article: [https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf#application-estimating-prefetch-window](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf#application-estimating-prefetch-window).
