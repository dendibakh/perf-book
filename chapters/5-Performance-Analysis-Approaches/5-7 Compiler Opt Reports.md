---
typora-root-url: ..\..\img
---

## Compiler Optimization Reports {#sec:compilerOptReports}

Nowadays, software development relies very much on compilers to do performance optimizations. Compilers play a very important role in speeding up our software. Usually, developers leave this job to compilers, interfering only when they see an opportunity to improve something compilers cannot accomplish. Fair to say, this is a good default strategy. For better interaction, compilers provide optimization reports which developers can use for performance analysis.

Sometimes you want to know if some function was inlined or loop was vectorized, unrolled, etc. If it was unrolled, what is the unroll factor? There is a hard way to know this: by studying generated assembly instructions. Unfortunately, not all people are comfortable at reading assembly language. This can be especially hard if the function is big, it calls other functions or has many loops that were also vectorized, or if the compiler created multiple versions of the same loop. Fortunately, most compilers, including `GCC`, `ICC`, and `Clang`, provide optimization reports to check what optimizations were done for a particular piece of code. Another example of a hint from a compiler can be Intel® [ISPC](https://ispc.github.io/ispc.html)[^3] compiler (see more in [@sec:ISPC]), which issues a number of performance warnings for code constructs that compile to relatively inefficient code.

[@lst:optReport] shows an example of the loop that is not vectorized by `clang 6.0`.

Listing: a.c

~~~~ {#lst:optReport .cpp .numberLines}
void foo(float* __restrict__ a, 
         float* __restrict__ b, 
         float* __restrict__ c,
         unsigned N) {
  for (unsigned i = 1; i < N; i++) {
    a[i] = c[i-1]; // value is carried over from previous iteration
    c[i] = b[i];
  }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To emit an optimization report in clang, you need to use [-Rpass*](https://llvm.org/docs/Vectorizers.html#diagnostics) flags:

```bash
$ clang -O3 -Rpass-analysis=.* -Rpass=.* -Rpass-missed=.* a.c -c
a.c:5:3: remark: loop not vectorized [-Rpass-missed=loop-vectorize]
  for (unsigned i = 1; i < N; i++) {
  ^
a.c:5:3: remark: unrolled loop by a factor of 4 with run-time trip count [-Rpass=loop-unroll]
  for (unsigned i = 1; i < N; i++) {
  ^
```

By checking the optimization report above, we could see that the loop was not vectorized, but it was unrolled instead. It's not always easy for a developer to recognize the existence of vector dependency in the loop on line 5 in [@lst:optReport]. The value that is loaded by `c[i-1]` depends on the store from the previous iteration (see operations #2 and #3 in Figure @fig:VectorDep). The dependency can be revealed by manually unrolling a few first iterations of the loop:

```cpp
// iteration 1
  a[1] = c[0];
  c[1] = b[1]; // writing the value to c[1]
// iteration 2
  a[2] = c[1]; // reading the value of c[1]
  c[2] = b[2];
...
```

![Visualizing the order of operations in [@lst:optReport].](/2/VectorDep.png){#fig:VectorDep width=50%}

If we were to vectorize the code in [@lst:optReport], it would result in the wrong values written in the array `a`. Assuming a CPU SIMD unit can process four floats at a time, we would get the code that can be expressed with the following pseudocode:

```cpp
// iteration 1
  a[1..4] = c[0..3]; // oops, a[2..4] get the wrong values
  c[1..4] = b[1..4]; 
...
```

The code in [@lst:optReport] cannot be vectorized because the order of operations inside the loop matter. This example can be fixed[^2] by swapping lines 6 and 7 without changing the semantics of the function, as shown in [@lst:optReport2]. For more information on discovering vectorization opportunities and examples using compiler optimization reports, see [@sec:Vectorization].

Listing: a.c

~~~~ {#lst:optReport2 .cpp .numberLines}
void foo(float* __restrict__ a, 
         float* __restrict__ b, 
         float* __restrict__ c,
         unsigned N) {
  for (unsigned i = 1; i < N; i++) {
    c[i] = b[i];
    a[i] = c[i-1];
  }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the optimization report, we can see that the loop was now vectorized:

```bash
$ clang -O3 -Rpass-analysis=.* -Rpass=.* -Rpass-missed=.* a.c -c
a.cpp:5:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]
  for (unsigned i = 1; i < N; i++) {
  ^
```

Compiler reports are generated per source file, which can be quite big. A user can simply search the source lines of interest in the output. [Compiler Explorer](https://godbolt.org/)[^4] website has the "Optimization Output" tool for LLVM-based compilers that reports performed transformations when you hover your mouse over the corresponding line of source code. 

In LTO[^5] mode, some optimizations are made during the linking stage. To emit compiler reports from both compilation and linking stages, one should pass dedicated options to both the compiler and the linker. See LLVM "Remarks" [guide](https://llvm.org/docs/Remarks.html)[^6] for more information. 

Compiler optimization reports not only help in finding missed optimization opportunities and explain why that happened but also are useful for testing hypotheses. The compiler often decides whether a certain transformation will be beneficial based on its cost model analysis. But it doesn't always make the optimal choice, which we can be tuned further. One can detect missing optimization in a report and provide a hint to a compiler by using `#pragma`, attributes, compiler built-ins, etc. See an example of using such hints on [easyperf blog](https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts)[^1]. As always, verify your hypothesis by measuring it in a practical environment.

\personal{Compiler optimization reports could be one of the key items in your toolbox. It is a fast way to check what optimizations were done for a particular hotspot and see if some important ones failed. I have found many improvement opportunities by using opt reports.}

[^1]: Using compiler optimization pragmas - [https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts](https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts).
[^2]: Alternatively, the code can be improved by splitting the loop into two separate loops.
[^3]: ISPC - [https://ispc.github.io/ispc.html](https://ispc.github.io/ispc.html).
[^4]: Compiler Explorer - [https://godbolt.org/](https://godbolt.org/).
[^5]: Link-Time optimizations, also called InterProcedural Optimizations (IPO). Read more here: [https://en.wikipedia.org/wiki/Interprocedural_optimization](https://en.wikipedia.org/wiki/Interprocedural_optimization).
[^6]: LLVM compiler remarks - [https://llvm.org/docs/Remarks.html](https://llvm.org/docs/Remarks.html).
