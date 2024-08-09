## Compiler Optimization Reports {#sec:compilerOptReports}

Nowadays, software development relies very much on compilers to do performance optimizations. Compilers play a critical role in speeding up software. The majority of developers leave the job of optimizing code to compilers, interfering only when they see an opportunity to improve something compilers cannot accomplish. Fair to say, this is a good default strategy. But it doesn't work well when you're looking for the best performance possible. What if the compiler failed to perform a critical optimization like vectorizing a loop? How you would know about this? Luckily, all major compilers provide optimization reports which we will discuss now.

Suppose you want to know if a critical loop was unrolled or not. If it was unrolled, what is the unroll factor? There is a hard way to know this: by studying generated assembly instructions. Unfortunately, not all people are comfortable reading assembly language. This can be especially difficult if the function is big, it calls other functions or has many loops that were also vectorized, or if the compiler created multiple versions of the same loop. Most compilers, including GCC, Clang, Intel compiler, and MSVC[^9] provide optimization reports to check what optimizations were done for a particular piece of code.

Let's take a look at [@lst:optReport], which shows an example of a loop that is not vectorized by `clang 16.0`.

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

To emit an optimization report in the Clang compiler, you need to use [-Rpass*](https://llvm.org/docs/Vectorizers.html#diagnostics) flags:

```bash
$ clang -O3 -Rpass-analysis=.* -Rpass=.* -Rpass-missed=.* a.c -c
a.c:5:3: remark: loop not vectorized [-Rpass-missed=loop-vectorize]
  for (unsigned i = 1; i < N; i++) {
  ^
a.c:5:3: remark: unrolled loop by a factor of 8 with run-time trip count [-Rpass=loop-unroll]
  for (unsigned i = 1; i < N; i++) {
  ^
```

By checking the optimization report above, we could see that the loop was not vectorized, but it was unrolled instead. It's not always easy for a developer to recognize the existence of a loop-carry dependency in the loop on line 6 in [@lst:optReport]. The value that is loaded by `c[i-1]` depends on the store from the previous iteration (see operations \circled{2} and \circled{3} in Figure @fig:VectorDep). The dependency can be revealed by manually unrolling the first few iterations of the loop:

```cpp
// iteration 1
  a[1] = c[0];
  c[1] = b[1]; // writing the value to c[1]
// iteration 2
  a[2] = c[1]; // reading the value of c[1]
  c[2] = b[2];
...
```

![Visualizing the order of operations in [@lst:optReport].](../../img/perf-analysis/VectorDep.png){#fig:VectorDep width=40%}

If we were to vectorize the code in [@lst:optReport], it would result in the wrong values written in the array `a`. Assuming a CPU SIMD unit can process four floats at a time, we would get the code that can be expressed with the following pseudocode:

```cpp
// iteration 1
  a[1..4] = c[0..3]; // oops!, a[2..4] get wrong values
  c[1..4] = b[1..4]; 
...
```

The code in [@lst:optReport] cannot be vectorized because the order of operations inside the loop matters. This example can be fixed by swapping lines 6 and 7 as shown in [@lst:optReport2]. This does not change the semantics of the code, so it's a perfectly legal change. Alternatively, the code can be improved by splitting the loop into two separate loops. Doing this would double the loop overhead, but this drawback would be outweighed by the performance improvement gained through vectorization.

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

In the optimization report, we can now see that the loop was vectorized successfully:

```bash
$ clang -O3 -Rpass-analysis=.* -Rpass=.* -Rpass-missed=.* a.c -c
a.cpp:5:3: remark: vectorized loop (vectorization width: 8, interleaved count: 4) [-Rpass=loop-vectorize]
  for (unsigned i = 1; i < N; i++) {
  ^
```

This was just one example of using optimization reports; we will provide more examples in [@sec:DiscoverVectOpptnt], where we discuss how to discover vectorization opportunities. Compiler optimization reports can help you find missed optimization opportunities, and understand why those opportunities were missed. In addition, compiler optimization reports are useful for testing a hypothesis. Compilers often decide whether a certain transformation will be beneficial based on their cost model analysis. But compilers don't always make the optimal choice. Once you detect a key missing optimization in the report, you can attempt to rectify it by changing the source code or by providing hints to the compiler in the form of, say, a `#pragma`, an attribute, a compiler built-in, etc. As always, verify your hypothesis by measuring it in a practical environment.

Compiler reports can be quite large, and a separate report is generated for each source-code file. Sometimes, finding relevant records in the output file can become a challenge. We should mention that initially these reports were explicitly designed for use by compiler writers to improve optimization passes. Over the years, several tools have been developed to make optimization reports more accessible and actionable by application developers. Most notably, [opt-viewer](https://github.com/llvm/llvm-project/tree/main/llvm/tools/opt-viewer)[^7] and [optview2](https://github.com/OfekShilon/optview2).[^8] Also, the [Compiler Explorer](https://godbolt.org/) website has the "Optimization Output" tool for LLVM-based compilers that reports performed transformations when you hover your mouse over the corresponding line of source code. All of these tools help visualize successful and failed code transformations by LLVM-based compilers.

In the Link-Time Optimization (LTO)[^5] mode, some optimizations are made during the linking stage. To emit compiler reports from both the compilation and linking stages, you should pass dedicated options to both the compiler and the linker. See the LLVM "Remarks" [guide](https://llvm.org/docs/Remarks.html)[^6] for more information. 

A slightly different way of reporting missing optimizations is taken by the Intel® [ISPC](https://ispc.github.io/ispc.html)[^3] compiler (discussed in [@sec:ISPC]). It issues warnings for code constructs that compile to relatively inefficient code. Either way, compiler optimization reports should be one of the key tools in your toolbox. They are a fast way to check what optimizations were done for a particular hotspot and see if some important ones failed. I have found many improvement opportunities thanks to compiler optimization reports.

[^1]: Using compiler optimization pragmas - [https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts](https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts)
[^3]: ISPC - [https://ispc.github.io/ispc.html](https://ispc.github.io/ispc.html)
[^5]: Link-Time Optimizations, also called InterProcedural Optimizations (IPO). Read more here: [https://en.wikipedia.org/wiki/Interprocedural_optimization](https://en.wikipedia.org/wiki/Interprocedural_optimization)
[^6]: LLVM compiler remarks - [https://llvm.org/docs/Remarks.html](https://llvm.org/docs/Remarks.html)
[^7]: opt-viewer - [https://github.com/llvm/llvm-project/tree/main/llvm/tools/opt-viewer](https://github.com/llvm/llvm-project/tree/main/llvm/tools/opt-viewer)
[^8]: optview2 - [https://github.com/OfekShilon/optview2](https://github.com/OfekShilon/optview2)
[^9]: At the time of writing (2024), MSVC provides only vectorization reports.
