---
typora-root-url: ..\..\img
---

# Part2. Source Code Tuning For CPU {.unnumbered}

\markright{Part2. Source Code Tuning For CPU}

In part 2, we will take a look at how to use CPU monitoring features (see [@sec:sec4]) to find the places in the code which can be tuned for execution on a CPU. For performance-critical applications like large distributed cloud services, scientific HPC software, 'AAA' games, etc. it is very important to know how underlying HW works. It is a fail-from-the-start when the program is being developed without HW focus. 

Standard algorithms and data structures don't always work well for performance-critical workloads. For example, a linked list is pretty much deprecated in favor of 'flat' data structures. Traditionally every new node of the linked list is dynamically allocated. Besides invoking many costly[^7] memory allocations, this will likely result in a situation where all the elements of the list are scattered in memory. Traversing such a data structure requires random memory access for every element. Even though algorithmic complexity is still O(N), in practice, the timings will be much worse than of a plain array. Some data structures, like binary trees, have natural linked-list-like representation, so it might be tempting to implement them in a pointer chasing manner. However, more efficient "flat" versions of those data structures exist, see `boost::flat_map`, `boost::flat_set`.

Even though the algorithm you choose is best known for a particular problem, it might not work best for your particular case. For example, a binary search is optimal for finding an element in a sorted array. However, this algorithm usually suffers from branch mispredictions since every test of the element value has a 50% chance of being true. This is why on a small-sized (less than 20 elements) array of integers, linear search is usually better.

Performance engineering is an art. And like in any art, the set of possible scenarios is endless. This chapter tries to address optimizations specific to CPU microarchitecture without trying to cover all existing optimization opportunities one can imagine. Still, I think it is important to at least name some high-level ones:

* If a program is written using interpreted languages (python, javascript, etc.), rewrite its performance-critical portion in a language with less overhead.
* Analyze the algorithms and data structures used in the program, see if you can find better ones.
* Tune compiler options. Check that you use at least these three compiler flags: `-O3` (enables machine-independent optimizations), `-march` (enables optimizations for particular CPU generation), `-flto` (enables inter-procedural optimizations).
* If a problem is a highly parallelizable computation, make it threaded, or consider running it on a GPU.
* Use async IO to avoid blocking while waiting for IO operations.
* Leverage using more RAM to reduce the amount of CPU and IO you have to use (memoization, look-up tables, caching of data, compression, etc.)

## Data-Driven Optimizations {.unlisted .unnumbered}

One of the most important techniques for tuning is called "Data-Driven" optimization that is based on introspecting the data the program is working on. The approach is to focus on the layout of the data and how it is transformed throughout the program.[^3] A classic example of such an approach is Structure-Of-Array to Array-Of-Structures ([SOA-to-AOS](https://en.wikipedia.org/wiki/AoS_and_SoA)[^4]) transformation, which is shown on [@lst:AOStoSOA]. 

Listing: SOA to AOS transformation.

~~~~ {#lst:AOStoSOA .cpp}
struct S {
  int a[N];
  int b[N];
  int c[N];
  // many other fields
};

<=>
    
struct S {
  int a;
  int b;
  int c;
  // many other fields
};
S s[N];
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The answer to the question of which layout is better depends on how the code is accessing the data. If the program iterates over the data structure and only accesses field `b`, then SOA is better because all memory accesses will be sequential (spatial locality). However, if the program iterates over the data structure and does excessive operations on all the fields of the object (i.e. `a`, `b`, `c`), then AOS is better because it's likely that all the members of the structure will reside in the same cache line. It will additionally better utilize the memory bandwidth since fewer cache line reads will be required.

This class of optimizations is based on knowing the data on which the program operates, how it is laid out, and modifying the program accordingly.

\personal{In fact, we can say that all optimizations are data-driven in some sense. Even the transformations that we will look at in the next sections are based on some feedback we receive from the execution of the program: function call counts, profiling data, performance counters, etc. }

Another very important example of data-driven optimization is "Small Size optimization". Its idea is to preallocate some amount of memory for a container to avoid dynamic memory allocations. It is especially useful for small and medium-sized containers when the upper limit of elements can be well-predicted. This approach was successfully deployed across the whole LLVM infrastructure and provided significant performance benefits (search `SmallVector`, for example). The same concept is implemented in `boost::static_vector`.

Obviously, it's not a complete list of data-driven optimizations, but as was written earlier, there was no attempt to list them all. Readers can find some more examples on [easyperf blog](https://easyperf.net/blog/2019/11/27/data-driven-tuning-specialize-indirect-call)[^5].

Modern CPU is a very complicated device, and it's nearly impossible to predict how certain pieces of code will perform. Instruction execution by the CPU depends on many factors, and the number of moving parts is too big for a human mind to overlook. Hopefully, knowing how your code looks like from a CPU perspective is possible thanks to all the performance monitoring capabilities we discussed in [@sec:sec4].

Note that optimization that you implement might not be beneficial for every platform. For example, [loop blocking](https://en.wikipedia.org/wiki/Loop_nest_optimization)[^2] very much depends on the characteristics of the memory hierarchy in the system, especially L2 and L3 cache sizes. So, an algorithm tuned for CPU with particular sizes of L2 and L3 caches might not work well for CPUs with smaller caches[^6]. It is important to test the change on the platforms your application will be running on.

The next three chapters are organized in the most convenient way to be used with TMA (see [@sec:TMA]). The idea behind this classification is to offer some kind of checklist which engineers can use in order to effectively eliminate inefficiencies that TMA reveals. Again, this is not supposed to be a complete list of transformations one can come up with. However, this is an attempt to describe the typical ones.

[^2]: Loop nest optimizations - [https://en.wikipedia.org/wiki/Loop_nest_optimization](https://en.wikipedia.org/wiki/Loop_nest_optimization).
[^3]: Data-Driven optimizations - [https://en.wikipedia.org/wiki/Data-oriented_design](https://en.wikipedia.org/wiki/Data-oriented_design).
[^4]: AoS to SoA transformation - [https://en.wikipedia.org/wiki/AoS_and_SoA](https://en.wikipedia.org/wiki/AoS_and_SoA).
[^5]: Examples of data-driven tuning - [https://easyperf.net/blog/2019/11/27/data-driven-tuning-specialize-indirect-call](https://easyperf.net/blog/2019/11/27/data-driven-tuning-specialize-indirect-call) and [https://easyperf.net/blog/2019/11/22/data-driven-tuning-specialize-switch](https://easyperf.net/blog/2019/11/22/data-driven-tuning-specialize-switch).
[^6]: Alternatively, one can use cache-oblivious algorithms whose goal is to work reasonably well for any size of the cache. See [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm).
[^7]: By default, memory allocation involves an expensive system call (`malloc`), which can be especially costly in a multithreaded context.
