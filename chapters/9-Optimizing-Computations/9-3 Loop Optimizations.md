---
typora-root-url: ..\..\img
---

## Loop Optimizations

Loops are the heart of nearly all high performance programs. Since loops represent a piece of code that is executed a large number of times, they are where the majority of the execution time is spent. Small changes in such a critical piece of code may have a high impact on the performance of a program. That's why it is so important to carefully analyze the performance of hot loops in a program and know possible ways to improve them.

To effectively optimize a loop, it is crucial to understand the performance bottleneck. Once you find a loop that is using most of the time, try to determine what limits its performance. Usually, it will be one or many of the following: memory latency, memory bandwidth, or compute capabilities of a machine. Roofline Performance Model ([@sec:roofline]) is a good starting point for assessing the performance of different loops against the HW theoretical maximums. Top-Down Microarchitecture Analysis ([@sec:TMA]) can be another good source of information about the bottlenecks.

In this section, we will take a look at the most well-known loop optimizations that address the types of bottlenecks mentioned above. We first discuss low-level optimizations that only move code around in a single loop. Such optimizations typically help make computations inside the loop more effective. Next, we will take a look at high-level optimizations that restructure loops, which often affects multiple loops. The second class of optimizations generally aims at improving memory accesses eliminating memory bandwidth and memory latency issues. Note, this is not a complete list of all known loop transformations. For more detailed information on each of the transformations discussed below, readers can refer to [@EngineeringACompilerBook].

Compilers can automatically recognize an opportunity to perform certain loop transformations. However, sometimes developer's interference is required to reach the desired outcome. In the second part of this section, we will share some thoughts on how to discover loop optimization opportunities. Understanding what transformations were performed on a given loop and what optimizations compiler failed to do is one of the keys to successful performance tuning. In the end, we will consider an alternative way of optimizing loops with polyhedral frameworks.

### Low-level optimizations.

First, we will consider simple loop optimizations that transform the code inside a single loop: Loop Invariant Code Motion, Loop Unrolling, Loop Strength Reduction, and Loop Unswitching. Such optimizations usually help improve the performance of a loop with high arithmetic intensity (see [@sec:roofline]), i.e., when a loop is bound by CPU compute capabilities. Generally, compilers are good at doing such transformations; however, there are still cases when a compiler might need a developer's support. We will talk about that in subsequent sections.

**Loop Invariant Code Motion (LICM)**. Expressions evaluated in a loop that never change are called loop invariants. Since their value doesn't change across loop iterations, we can move loop invariant expressions outside of the loop. We do so by storing the result in a temporary variable and use it inside the loop (see [@lst:LICM]). All decent compilers nowadays successfully perform LICM in majority of the cases.

Listing: Loop Invariant Code motion

~~~~ {#lst:LICM .cpp}
for (int i = 0; i < N; ++i)             for (int i = 0; i < N; ++i) {
  for (int j = 0; j < N; ++j)    =>       auto temp = c[i];
    a[j] = b[j] * c[i];                   for (int j = 0; j < N; ++j)
                                            a[j] = b[j] * temp;
                                        }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Loop Unrolling.** An induction variable is a variable in a loop, whose value is a function of the loop iteration number. For example, `v = f(i)`, where `i` is an iteration number. Modifying the induction variable on each iteration can be unnecessary and expensive. Instead, we can unroll a loop and perform multiple iterations for each increment of the induction variable (see [@lst:Unrol]).

Listing: Loop Unrolling

~~~~ {#lst:Unrol .cpp}
for (int i = 0; i < N; ++i)             for (int i = 0; i+1 < N; i+=2) {
  a[i] = b[i] * c[i];          =>         a[i]   = b[i]   * c[i];
                                          a[i+1] = b[i+1] * c[i+1];
                                        }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary benefit of loop unrolling is to perform more computations per iteration. At the end of each iteration, the index value must be incremented, tested, and the control is branched back to the top of the loop if it has more iterations to process. This work can be considered as loop "tax", which can be reduced. By unrolling the loop in [@lst:Unrol] by a factor of 2, we reduce the number of executed compare and branch instructions by half.

Loop unrolling is a well-known optimization; still, many people are confused about it and try to unroll the loops manually. I suggest that no developer should unroll any loop by hand. First, compilers are very good at doing this and usually do loop unrolling quite optimally. The second reason is that processors have an "embedded unroller" thanks to their out-of-order speculative execution engine (see [@sec:uarch]). While the processor is waiting for the load from the first iteration to finish, it may speculatively start executing the load from the second iteration assuming there are no loop-carry dependencies. This spans to multiple iterations ahead, effectively unrolling the loop in the instruction Reorder Buffer (ROB).

**Loop Strength Reduction (LSR)**. The idea of LSR is to replace expensive instructions with cheaper ones. Such transformation can be applied to all expressions that use an induction variable. Strength reduction is often applied to array indexing. Compilers perform LSR by analyzing how the value of a variable evolves across the loop iterations. In LLVM, it is known as Scalar Evolution (SCEV). In [@lst:LSR], it is relatively easy for a compiler to prove that the memory location `b[i*10]` is a linear function of the loop iteration number `i`, thus it can replace the expensive multiplication with a cheaper addition.

Listing: Loop Strength Reduction

~~~~ {#lst:LSR .cpp}
for (int i = 0; i < N; ++i)             int j = 0;
  a[i] = b[i * 10] * c[i];      =>      for (int i = 0; i < N; ++i) {
                                          a[i] = b[j] * c[i];
                                          j += 10;
                                        }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Loop Unswitching**. If a loop has a conditional statement inside and it is invariant, we can move it outside of the loop. We do so by duplicating the body of the loop and placing a version of it inside each of the `if` and `else` clauses of the conditional statement (see [@lst:Unswitch]). While the loop unswitching may double the amount of code written, each of these new loops may now be separately optimized.

Listing: Loop Unswitching

~~~~ {#lst:Unswitch .cpp}
for (i = 0; i < N; i++) {               if (c)
  a[i] += b[i];                           for (i = 0; i < N; i++) {
  if (c)                       =>           a[i] += b[i];
    b[i] = 0;                               b[i] = 0;
}                                         }
                                        else
                                          for (i = 0; i < N; i++) {
                                            a[i] += b[i];
                                          }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### High-level optimizations.

There is another class of loop transformations that change the structure of loops and often affect multiple nested loops. We will take a look at Loop Interchange, Loop Blocking (Tiling), and Loop Fusion and Distribution (Fission). This set of transformations aims at improving memory accesses and eliminating memory bandwidth and memory latency bottlenecks. From a compiler perspective, it is very difficult to prove legality of such transformations and justify their performance benefit. In that sense, developers are in a better position since they only have to care about the legality of the transformation in their particular piece of code, not about every possible scenario that may happen. Unfortunately, that also means that usually we have to do such transformations manually.

**Loop Interchange**. It is a process of exchanging the loop order of nested loops. The induction variable used in the inner loop switches to the outer loop, and vice versa. [@lst:Interchange] shows an example of interchanging nested loops for `i` and `j`. The main purpose of loop interchange is to perform sequential memory accesses to the elements of a multi-dimensional array. By following the order in which elements are laid out in memory, we can improve the spatial locality of memory accesses and make our code more cache-friendly. This transformation helps to eliminate memory bandwidth and memory latency bottlenecks.

Listing: Loop Interchange

~~~~ {#lst:Interchange .cpp}
for (i = 0; i < N; i++)                 for (j = 0; j < N; j++)
  for (j = 0; j < N; j++)          =>     for (i = 0; i < N; i++)
    a[j][i] += b[j][i] * c[j][i];           a[j][i] += b[j][i] * c[j][i];
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loop Interchange is only legal if loops are *perfectly nested*. A perfectly nested loop is one wherein all the statements are in the innermost loop. Interchanging imperfect loop nest is harder to do but still possible, check an example in the [Codee](https://www.codee.com/catalog/glossary-perfect-loop-nesting/)[^1] catalog.

**Loop Blocking (Tiling)**. The idea of this transformation is to split the multi-dimensional execution range into smaller chunks (blocks or tiles) so that each block will fit in the CPU caches. If an algorithm works with large multi-dimensional arrays and performs strided accesses to their elements, there is a high chance of poor cache utilization. Every such access may push the data that will be requested by future accesses out of the cache (cache eviction). By partitioning an algorithm in smaller multi-dimensional blocks, we ensure the data used in a loop stays in the cache until it is reused.

In the example shown in [@lst:blocking], an algorithm performs row-major traversal of elements of array `a` while doing column-major traversal of array `b`. The loop nest can be partitioned into smaller blocks in order to maximize the reuse of elements of the array `b`.

Listing: Loop Blocking

~~~~ {#lst:blocking .cpp}
// linear traversal                     // traverse in 8*8 blocks
for (int i = 0; i < N; i++)             for (int ii = 0; ii < N; ii+=8)
  for (int j = 0; j < N; j++)    =>      for (int jj = 0; jj < N; jj+=8)
    a[i][j] += b[j][i];                   for (int i = ii; i < ii+8; i++)
                                           for (int j = jj; j < jj+8; j++)
                                            a[i][j] += b[j][i];
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loop Blocking is a widely known method of optimizing GEneral Matrix Multiplication (GEMM) algorithms. It enhances the cache reuse of the memory accesses and improves both memory bandwidth and memory latency of an algorithm.

Typically, engineers optimize a tiled algorithm for the size of caches that are private to each CPU core (L1 or L2 for Intel and AMD, L1 for Apple). However, the sizes of private caches are changing from generation to generation, so hardcoding a block size presents its own set of challenges. As an alternative solution, one can use [cache-oblivious](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)[^2] algorithms whose goal is to work reasonably well for any size of the cache.

**Loop Fusion and Distribution (Fission)**. Separate loops can be fused together when they iterate over the same range and do not reference each other's data. An example of a Loop Fusion is shown in [@lst:fusion]. The opposite procedure is called Loop Distribution (Fission) when the loop is split into separate loops.

Listing: Loop Fusion and Distribution

~~~~ {#lst:fusion .cpp}
for (int i = 0; i < N; i++)             for (int i = 0; i < N; i++) {
  a[i].x = b[i].x;                        a[i].x = b[i].x;
                               =>         a[i].y = b[i].y;
for (int i = 0; i < N; i++)             }
  a[i].y = b[i].y;                      
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loop Fusion helps to reduce the loop overhead (similar to Loop Unrolling) since both loops can use the same induction variable. Also, loop fusion can help to improve the temporal locality of memory accesses. In [@lst:fusion], if both `x` and `y` members of a structure happen to reside on the same cache line, it is better to fuse the two loops since we can avoid loading the same cache line twice. This will reduce the cache footprint and improve memory bandwidth utilization.

However, loop fusion does not always improve performance. Sometimes it is better to split a loop into multiple passes, pre-filter the data, sort and reorganize it, etc. By distributing the large loop into multiple smaller ones, we limit the amount of data required for each iteration of the loop, effectively increasing the temporal locality of memory accesses. This helps in situations with a high cache contention, which typically happens in large loops. Loop distribution also reduces register pressure since, again, fewer operations are being done within each iteration of the loop. Also, breaking a big loop into multiple smaller ones will likely be beneficial for the performance of the CPU Front-End because of better instruction cache utilization. Finally, when distributed, each small loop can be further optimized separately by the compiler.

**Loop Unroll and Jam**. To perform this transformation, one needs to first unroll the outer loop, then jam (fuse) multiple inner loops together as shown in [@lst:unrolljam]. This transformation increases the ILP (Instruction-Level Parallelism) of the inner loop since more independent instructions are executed inside the inner loop. In the code example, inner loop is a reduction operation, which accumulates the deltas between elements of arrays `a` and `b`. When we unroll and jam the loop nest by a factor of 2, we effectively execute 2 iterations of the initial outer loop simultaneously. This is emphesized by having 2 independent accumulators, which breaks dependency chains over `diffs` in the initial variant.

Listing: Loop Unroll and Jam

~~~~ {#lst:unrolljam .cpp}
for (int i = 0; i < N; i++)           for (int i = 0; i+1 < N; i+=2)
  for (int j = 0; j < M; j++)           for (int j = 0; j < M; j++) {
    diffs += a[i][j] - b[i][j];   =>      diffs1 += a[i][j]   - b[i][j];
                                          diffs2 += a[i+1][j] - b[i+1][j];
                                        }
                                      diffs = diffs1 + diffs2;
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loop Unroll and Jam can be performed as long as there are no cross-iteration dependencies on the outer loops, in other words, two iterations of the inner loop can be executed in parallel. Also, this transformation makes sense if inner loop has memory accesses that are strided on the outer loop index (`i` in this case), otherwise other transformations likely apply better. Unroll and Jam is especially useful when the trip count of the inner loop is low, e.g. less than 4. By doing the transformation, we pack more independent operations into the inner loop, which increases the ILP.

Unroll and Jam transformation sometimes could be very useful for outer loop vectorization, which, at the time of writing, compilers cannot do automatically. In a situation when trip count of the inner loop is not visible to a compiler, it could still vectorize the original inner loop, hoping that it will execute enough iterations to hit the vectorized code (more on vectorization in the next section). But if the trip count is low, the program will use a slow scalar version of the loop. Once we do Unroll and Jam, we allow compiler to vectorize the code differently: now "glueing" the independent instructions in the inner loop together (aka SLP vectorization).

### Discovering loop optimization opportunities.

As we discussed at the beginning of this section, compilers will do the heavy-lifting part of optimizing your loops. You can count on them on making all the obvious improvements in the code of your loops, like eliminating unnecessary work, doing various peephole optimizations, etc. Sometimes a compiler is clever enough to generate the fast versions of the loops by default, and other times we have to do some rewriting ourselves to help the compiler. As we said earlier, from a compiler's perspective, doing loop transformations legally and automatically is very difficult. Often, compilers have to be conservative when they cannot prove the legality of a transformation. 

Consider a code in [@lst:Restrict]. A compiler cannot move the expression `strlen(a)` out of the loop body. So, the loop checks if we reached the end of the string on each iteration, which is obviously slow. The reason why a compiler cannot hoist the call is that there could be a situation when the memory regions of arrays `a` and `b` overlap. In this case, it would be illegal to move `strlen(a)` out of the loop body. If developers are sure that the memory regions do not overlap, they can declare both parameters of function `foo` with the `restrict` keyword, i.e., `char* __restrict__ a`.

Listing: Cannot move strlen out of the loop

~~~~ {#lst:Restrict .cpp}
void foo(char* a, char* b) {
  for (int i = 0; i < strlen(a); ++i)
    b[i] = (a[i] == 'x') ? 'y' : 'n';
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes compilers can inform us about failed transformations via compiler optimization remarks (see [@sec:compilerOptReports]). However, in this case, neither Clang 10 nor GCC 10 were able to explicitly tell that the expression `strlen(a)` was not hoisted out of the loop. The only way to find this out is to examine hot parts of the generated assembly code according to the profile of the application. Analyzing machine code requires the basic ability to read assembly language, but it is a highly rewarding activity.

It is a reasonable strategy to try to get the low-hanging fruits first. Developers could use compiler optimizations reports or examine the machine code of a loop to search for easy improvements. Sometimes, it's possible to adjust compiler transformations using user directives. For example, when we find out that the compiler unrolled our loop by a factor of 4, we may check if using a higher unrolling factor will improve performance. Most compilers support `#pragma unroll(8)`, which will instruct a compiler to use the unrolling factor specified by the user. There are other pragmas that control certain transformations, like loop vectorization, loop distribution, and others. For a complete list of user directives, we invite the user to check compiler's manual.

Next, developers should identify the bottlenecks in the loop and assess performance against the HW theoretical maximum. Start with the Roofline Performance Model ([@sec:roofline]), which will reveal the bottlenecks that developers should try to address. The performance of the loops is limited by one or many of the following factors: memory latency, memory bandwidth, or compute capabilities of a machine. Once the bottlenecks of the loop were identified, developers can try to apply one of the transformations we discussed earlier in this section.

Even though there are well-known optimization techniques for a particular set of computational problems, loop optimizations remain "black art" that comes with experience. We recommend you to rely on a compiler and complement it with manually transforming the code when necessary. Above all, keep the code as simple as possible and do not introduce unreasonably complicated changes if the performance benefits are negligible.

### Loop Optimization Frameworks

Over the years, researchers have developed techniques to determine the legality of loop transformations and to transform loops automatically. One such invention is the [polyhedral framework](https://en.wikipedia.org/wiki/Loop_optimization#The_polyhedral_or_constraint-based_framework)[^3]. [GRAPHITE](https://gcc.gnu.org/wiki/Graphite)[^4] was among the first set of polyhedral tools that were integrated into a production compiler. GRAPHITE performs a set of classical loop optimizations based on the polyhedral information, extracted from GIMPLE, GCC’s low-level intermediate representation. GRAPHITE has demonstrated the feasibility of the approach.

Later LLVM compiler developed its own polyhedral framework called [Polly](https://polly.llvm.org/)[^5]. Polly is a high-level loop and data-locality optimization infrastructure for LLVM. It uses an abstract mathematical representation based on integer polyhedral to analyze and optimize the memory access patterns of a program. Polly performs classical loop transformations, especially tiling and loop fusion, to improve data-locality. This framework has shown significant speedups on a number of well-known benchmarks [@Grosser2012PollyP]. Below is an example of how Polly can give an almost 30 times speedup of a GEneral Matrix-Multiply (GEMM) kernel from [Polybench 2.0](https://web.cse.ohio-state.edu/~pouchet.2/software/polybench/)[^6] benchmark suite:

```bash
$ clang -O3 gemm.c -o gemm.clang
$ time ./gemm.clang
real    0m6.574s
$ clang -O3 gemm.c -o gemm.polly -mllvm -polly
$ time ./gemm.polly
real    0m0.227s
```

Polly is a powerful framework for loop optimizations; however, it still misses out on some common and important situations[^7]. It is not enabled in the standard optimization pipeline in the LLVM infrastructure and requires that the user provide an explicit compiler option for using it (`-mllvm -polly`). Using polyhedral frameworks is a viable option when searching for a way to speed up your loops.

[^1]: Codee: perfect loop nesting - [https://www.codee.com/catalog/glossary-perfect-loop-nesting/]](https://www.codee.com/catalog/glossary-perfect-loop-nesting/)
[^2]: Cache-oblivious algorithm - [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)
[^3]: Polyhedral framework - [https://en.wikipedia.org/wiki/Loop_optimization#The_polyhedral_or_constraint-based_framework](https://en.wikipedia.org/wiki/Loop_optimization#The_polyhedral_or_constraint-based_framework).
[^4]: GRAPHITE polyhedral framework - [https://gcc.gnu.org/wiki/Graphite](https://gcc.gnu.org/wiki/Graphite).
[^5]: Polly - [https://polly.llvm.org/](https://polly.llvm.org/).
[^6]: Polybench - [https://web.cse.ohio-state.edu/~pouchet.2/software/polybench/](https://web.cse.ohio-state.edu/~pouchet.2/software/polybench/).
[^7]: Why not Polly? - [https://sites.google.com/site/parallelizationforllvm/why-not-polly](https://sites.google.com/site/parallelizationforllvm/why-not-polly).
