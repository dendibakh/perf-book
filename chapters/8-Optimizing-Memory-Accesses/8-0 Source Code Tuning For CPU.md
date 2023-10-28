---
typora-root-url: ..\..\img
---

# Part2. Source Code Tuning {.unnumbered}

\markright{Part2. Source Code Tuning}

Welcome to the second part of this book where we will discuss various techniques for low-level source code optimization, aka *tuning*. In the first part, we learned how to find performance bottlenecks in the code, which is only half of the developer's job. Another half is to fix the problem.

Modern CPU is a very complicated device, and it's nearly impossible to predict how fast certain pieces of code will run. SW and HW performance depends on many factors, and the number of moving parts is too big for a human mind to overlook. Hopefully, observing how your code runs from a CPU perspective is possible thanks to all the performance monitoring capabilities we discussed in the first part of the book. We will extensively rely on methods and tools we learned about earlier in the book to guide our performance engineering process.

At a very high level, software optimizations can be divided into five categories.

* **Algorithmic optimizations**. Idea: analyze algorithms and data structures used in the program, and see if you can find better ones. Example: use quicksort instead of bubblesort.
* **Parallelizing computations**. Idea: if an algorithm is highly parallelizable, make the program threaded, or consider running it on a GPU. The goal is to do multiple things at the same time. Concurency is already used in all the layers of the HW and SW stacks. Examples: distribute the work across several threads, balance load between many servers in the data center, use async IO to avoid blocking while waiting for IO operations, keep multiple concurent network connections to overlap the request latency.
* **Eliminating redundant work**. Idea: don't do work that you don't need or have already done. Examples: leverage using more RAM to reduce the amount of CPU and IO you have to use (caching, memoization, look-up tables, compression), move loop invariant computations outside of the loop, pass a C++ object by reference to get rid of excessive copies caused by passing by value.
* **Batching**. Idea: aggregate multiple similar operations and do them in one go, thus reducing the overhead of repeating the action multiple times. Examples: send large TCP packets instead of many small ones, allocate large block of memory rather than allocating space for hundreds of tiny objects.
* **Ordering**. Idea: reorder the sequence of operations in an algorithm. Examples: change the data layout to allow sequential memory accesses, sort an array of C++ polymorphic objects based on their types to allow better prediction of virtual function calls, group hot functions together and place them closer to each other in a binary.

Many optimizations that we will discuss later in the book, fall under multiple categories. For example, we can say that vectorization is a combination of parallelizing and batching; loop blocking (tiling) is a manifestation of batching and eliminating redundant work.

To make the picture complete, let us also list other maybe obvious but still quite reasonable ways to speed up things:

* **Rewrite the code in another language**. If a program is written using interpreted languages (python, javascript, etc.), rewrite its performance-critical portion in a language with less overhead, e.g. C++, Rust, Go, etc.
* **Tune compiler options**. Check that you use at least these three compiler flags: `-O3` (enables machine-independent optimizations), `-march` (enables optimizations for particular CPU architecture), `-flto` (enables inter-procedural optimizations). But don't stop here, there are many other options that affect performance. We will look at some of those in the future chapters. One may consider mining the best set of options for an application, commercial products that automate this process are available.
* **Optimize third-party SW packages**. Vast majority of software projects leverage layers of proprietary and open-source code. This includes OS, libraries, and frameworks. You can also seek improvements by replacing, modifying, or reconfiguring one of those pieces.
* **Buy faster hardware**. Obviously, it's a business decision that comes with an associated cost, but sometimes it's the only way to improve performance when other options are already exhausted. It is much easier to justify the purchase when you identify performance bottlenecks in your application and communicate that clearly to the upper management. For example, once you find that memory bandwidth is limiting performance of your multithreaded program, you may suggest buying server motherboards and processors with more memory channels and DIMM slots.

### Algorithmic optimizations {.unlisted .unnumbered}

Standard algorithms and data structures don't always work well for performance-critical workloads. For example, a linked list is pretty much deprecated in favor of "flat" data structures. Traditionally, every new node of a linked list is dynamically allocated. Besides potentially invoking many costly memory allocations, this will likely result in a situation where all the elements of the list are scattered in memory. Traversing such a data structure is not cache-friendly. Even though algorithmic complexity is still O(N), in practice, the timings will be much worse than of a plain array. Some data structures, like binary trees, have natural linked-list-like representation, so it might be tempting to implement them in a pointer chasing manner. However, more efficient "flat" versions of those data structures exist, see `boost::flat_map`, `boost::flat_set`.

When selecting an algorithm for a problem at hand, you might quickly pick the most popular option and move on... even though it could not be the best for your particular case. For example, you need to find an element in a sorted array. The first option that most developers consider is binary search, right? It is very well-known and is optimal in terms of algorithmic complexity, O(logN). Will you change your decision if I say that the array holds 32-bit integer values and the size of an array is usually very small (less than 20 elements)? In the end, measurements should guide your decision, but binary search suffers from branch mispredictions since every test of the element value has a 50% chance of being true. This is why on a small-sized array, linear scan is usually faster even though it has worse algorithmic complexity.

### Data-Driven Optimizations {.unlisted .unnumbered}

One of the most important techniques for tuning is called "Data-Driven" optimization that is based on introspecting the data that the program is working on. The approach is to focus on the layout of the data and how it is transformed throughout the program. A classic example of such an approach is Array-Of-Structures to Structure-Of-Array transformation, which is shown in [@lst:AOStoSOA]. 

Listing: SOA to AOS transformation.

~~~~ {#lst:AOStoSOA .cpp}
struct S {
  int a;
  int b;
  int c;
  // other fields
};
S s[N];    // AOS

<=>
    
struct S { // SOA
  int a[N];
  int b[N];
  int c[N];
  // other fields  
};
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The answer to the question of which layout is better depends on how the code is accessing the data. If the program iterates over the data structure and only accesses field `b`, then SOA is better because all memory accesses will be sequential. However, if a program iterates over the data structure and does *extensive* operations on all the fields of the object, then AOS may give better memory bandwidth utilization and in some cases, better performance. In the AOS scenario, members of the struct are likely to reside in the same cache line, and thus require fewer cache line reads and use less cache space. But more often, we see SOA gives better performance as it allows other important transformations, for example vectorization.

The main idea in Data-Driven Development (DDD), is to study how a program accesses data (how it is laid out in memory, observe access patterns), then modify the program accordingly (change the data layout, change the access patterns).

\personal{In fact, we can say that all optimizations are data-driven in a sense. Even the transformations that we will look at in the next sections are based on some feedback we receive from the execution of the program: function call counts, branch taken or not taken, performance counters, etc. }

Another wide-spread example of DDD is "Small Size optimization". Its idea is to statically preallocate some amount of memory to avoid dynamic memory allocations. It is especially useful for small and medium-sized containers when the upper limit of elements can be well-predicted. Modern C++ STL implementations of `std::string` keep the first 15-20 characters in the buffer allocated on the stack and only allocate memory on the heap for longer strings. Another instances of this approach can be found in LLVM's `SmallVector` and Boost's `static_vector`.

### Low-Level Optimizations {.unlisted .unnumbered}

Performance engineering is an art. And like in any art, the set of possible scenarios is endless. It's impossible to cover all various optimizations one can imagine. The upcoming several chapters primarily address optimizations specific to modern CPU architectures. 

Before we jump into particular source code tuning techinques, there are a few caution notes to make. First, avoid tuning bad code. If a piece of code has a high-level performance inefficiency, you shouldn't apply machine-specific optimizations to it. Always focus on fixing the major problem first. Only once you're sure that the algorithms and data structures are optimal for the problem you're trying to solve, try applying low-level improvements.

Second, remember that an optimization that you implement might not be beneficial for every platform. For example, Loop Blocking depends on characteristics of the memory hierarchy in a system, especially L2 and L3 cache sizes. So, an algorithm tuned for a CPU with particular sizes of L2 and L3 caches might not work well for CPUs with smaller caches. It is important to test the change on the platforms your application will be running on.

The next four chapters are organized according to the TMA classification (see [@sec:TMA]):

* Chapter 8. Optimizing Memory Accesses - `TMA:MemoryBound` category
* Chapter 9. Optimizing Computations - `TMA:CoreBound` category
* Chapter 10. Optimizing Branch Prediction - `TMA:BadSpeculation` category
* Chapter 11. Machine Code Layout Optimizations - `TMA:FrontEndBound` category

The idea behind this classification is to offer a checklist for developers when they are using TMA methodology in their performance engineering work. Whenever TMA attributes a performance bottleneck to one of the categories mentioned above, feel free to consult one of the corresponding chapters to learn about your options.

Chapter 14 covers other optimization areas that do not belong to any of the categories above. Chapter 15 addresses some common problems in optimizing multithreaded applications.