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

Another option to utilize explicit SW prefetching on x86 platforms is to use compiler intrinsics `_mm_prefetch` intrinsic. See Intel Intrinsics Guide for more details. In any case, compiler will compile it down to machine instruction: `PREFETCH` for x86 and `pld` for ARM. For some platforms compiler can skip inserting an instruction, so it is a good idea to check the generated machine code.

There are situations when SW memory prefetching is not possible. For example, when traversing a linked list, prefetching window is tiny and it is not possible to hide the latency of pointer chaising.

In [@lst:MemPrefetch2] we saw an example of prefetching for the next iteration, but also you may frequently encounter a need to prefetch for 2, 4, 8, and sometimes even more iterations. The code in [@lst:MemPrefetch3] is one of those cases, when it could be beneficial. If the graph is very sparse and has a lot of verticies, it is very likely that accesses to `this->out_neighbors` and `this->in_neighbors` vectors will miss in caches a lot.

This code is different from the previous example as there are no extensive computations on every iteration, so the penalty of cache misses likely dominates the latency of each iteration. But we can leverage the fact that we know all the elements that will be accessed in the future. The elements of vector `el` are accessed sequentially and thus are likely to be timely brought to the L1 cache by the HW prefetcher. Our goal here is to overlap the latency of a cache miss with executing enough iterations to completely hide it.

As a general rule, for prefetch hints to be effective, they must be inserted well ahead of time so that by the time the loaded value will be used in other calculations, it will be already in the cache. However, it also shouldn't be inserted too early since it may pollute the cache with the data that is not used for a long time. Notice, in [@lst:MemPrefetch3], `lookAhead` is a template parameter, which allows to try different values and see which gives the best performance. More advanced users can try to estimate the prefetching window using the method described in [@sec:timed_lbr], example of using such method can be found on easyperf blog. [^5]

Listing: Example of a SW prefetching for the next 8 iterations.

~~~~ {#lst:MemPrefetch3 .cpp}
template <int lookAhead = 8>
void Graph::update(const std::vector<Edge>& el) {
  for(int i = 0; i + lookAhead < el.size(); i++) {
    VertexID v = el[i].from;
    VertexID u = el[i].to;
    this->out_neighbors[u].push_back(v);
    this->in_neighbors[v].push_back(u);

    // prefetch elements for future iterations
    VertexID v_next = el[i + lookAhead].from;
    VertexID u_next = el[i + lookAhead].to;
    __builtin_prefetch(this->out_neighbors.data() + v_next);
    __builtin_prefetch(this->in_neighbors.data()  + u_next);
  }
  // process the remainder of the vector `el` ...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SW memory prefetching is most frequently used in the loops, but also one can insert those hints into the parent function, again, all depends on the available prefetching window.

This technique is a powerful weapon, however, it should be used with extreme care as it is not easy to get it right. First of all, explicit memory prefetching is not portable, meaning that if it gives performance gains on one platform, it doesn't guarantee similar speedups on another platform. It is very implemetation-specific and platforms are not required to honor those hints. In such a case it will likely degrade performance. My recomendation would be to verify that the impact is positive with all available tools. Not only check the performance numbers, but also make sure that the number of cache misses (L3 in particular) went down. Once the change is committed into the code base, monitor performance on all the platforms that you run your application on, as it could be very sensitive to changes in the surrounding code. Consider dropping the idea if the benefits do not overweight the potential maintanance burden.

For some complicated scenarios, make sure that the code actually prefetches the right memory locations. It can get tricky, when a current iteration of a loop depends on the previous iteration, e.g there is `continue` statement or changing the next element to process guarded by an `if` condition. In this case, my recommendation is to instrument the code to test the accuracy of your prefetching hints. Because when used badly, it can worsen the performance of caches by evicting other useful data.

Finally, explicit prefetching increases code size and adds pressure on the CPU Front-End. A prefetch hint is just a fake load that goes into the memory subsystem, but does not have a destination register. And just like any other instruction it consumes CPU resources. Apply it with extreme care, because when used wrong, it can pessimize the performance of a program.

[^4]: GCC builtins - [https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html).
[^5]: "Precise timing of machine code with Linux perf" - [https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf#application-estimating-prefetch-window](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf#application-estimating-prefetch-window).
