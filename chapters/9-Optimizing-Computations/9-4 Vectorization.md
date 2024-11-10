## Vectorization {#sec:Vectorization}

On modern processors, the use of SIMD instructions can result in a great speedup over regular un-vectorized (scalar) code. When doing performance analysis, one of the top priorities of the software engineer is to ensure that the hot parts of the code are vectorized. This section guides engineers toward discovering vectorization opportunities. For a recap of the SIMD capabilities of modern CPUs, readers can take a look at [@sec:SIMD].

Vectorization often happens automatically without any user intervention; this is called compiler *autovectorization*. In such a situation, a compiler automatically recognizes the opportunity to produce SIMD machine code from the source code. 

Autovectorization is very convenient because modern compilers can automatically generate fast SIMD code for a wide variety of programs. However, in some cases, autovectorization does not succeed without intervention by the software engineer. Modern compilers have extensions that allow power users to control the autovectorization process and make sure that certain parts of the code are vectorized efficiently. We will provide several examples of using compiler autovectorization hints.

In this section, we will discuss how to harness compiler autovectorization, especially inner loop vectorization because it is the most common type of autovectorization. The other two types (outer loop vectorization, and Superword-Level Parallelism vectorization) are not discussed in this book.

### Compiler Autovectorization

Multiple hurdles can prevent autovectorization, some of which are inherent to the semantics of programming languages. For example, the compiler must assume that loop indices may overflow, and this can prevent certain loop transformations. Another example is the assumption that the C programming language makes: pointers in the program may point to overlapping memory regions, which can make the analysis of the program very difficult. 

Another major hurdle is the design of the processor itself. In some cases, processors don’t have efficient vector instructions for certain operations. For example, predicated (bitmask-controlled) load and store operations are not available on most processors. Despite all of the challenges, you can work around many of them and enable autovectorization. Later in this section, we provide guidance on how to work with the compiler and ensure that the hot code is vectorized by the compiler.

The vectorizer is usually structured in three phases: legality-check, profitability-check, and transformation itself:

* **Legality-check**: in this phase, the compiler checks if it is legal to transform the loop (or another type of code region) into using vectors. The legality phase collects a list of requirements that need to happen for the vectorization of the loop to be legal. The loop vectorizer checks that the iterations of the loop are consecutive, which means that the loop progresses linearly. The vectorizer also ensures that all of the memory and arithmetic operations in the loop can be widened into consecutive operations. That the control flow of the loop is uniform across all lanes and that the memory access patterns are uniform. The compiler has to check or ensure that the generated code won’t touch memory that it is not supposed to and that the order of operations will be preserved. The compiler needs to analyze the possible range of pointers, and if it has some missing information, it has to assume that the transformation is illegal.

* **Profitability-check**: next, the vectorizer checks if a transformation is profitable. It compares different vectorization widths and figures out which one would be the fastest to execute. The vectorizer uses a cost model to predict the cost of different operations, such as scalar add or vector load. It needs to take into account the added instructions that shuffle data into registers, predict register pressure, and estimate the cost of the loop guards that ensure that preconditions that allow vectorizations are met. The algorithm for checking profitability is simple: 1) add up the cost of all of the operations in the code, 2) compare the costs of each version of the code, and 3) divide the cost by the expected execution count. For example, if the scalar code costs 8 cycles, and the vectorized code costs 12 cycles but performs 4 loop iterations at once, then the vectorized version of the loop is probably faster.

* **Transformation**: finally, after the vectorizer figures out that the transformation is legal and profitable, it transforms the code. This process also includes the insertion of guards that enable vectorization. For example, most loops use an unknown iteration count, so the compiler has to generate a scalar version of the loop (remainder), in addition to the vectorized version of the loop, to handle the last few iterations. The compiler also has to check if pointers don’t overlap, etc. All of these transformations are done using information that is collected during the legality check phase.

### Discovering Vectorization Opportunities. {#sec:DiscoverVectOpptnt}

Discovering opportunities for improving vectorization should start by analyzing hot loops in the program and checking what optimizations were performed by the compiler. Checking compiler vectorization reports (see [@sec:compilerOptReports]) is the easiest way to know that. Modern compilers can report whether a certain loop was vectorized, and provide additional details, e.g., vectorization factor (VF). In the case when the compiler cannot vectorize a loop, it is also able to tell the reason why it failed. 

An alternative way to use compiler optimization reports is to check assembly output. It is best to analyze the output from a profiling tool that shows the correspondence between the source code and generated assembly instructions for a given loop. That way you only focus on the code that matters, i.e., the hot code. However, understanding assembly language is much more difficult than a high-level language like C++. It may take some time to figure out the semantics of the instructions generated by the compiler. However, this skill is highly rewarding and often provides valuable insights. 

Experienced developers can quickly tell whether the code was vectorized or not just by looking at instruction mnemonics and the register names used by those instructions. For example, in x86 ISA, vector instructions operate on packed data (thus have `P` in their name) and use `XMM`, `YMM`, or `ZMM` registers, e.g., `VMULPS XMM1, XMM2, XMM3` multiplies four single precision floats in `XMM2` and `XMM3` and saves the result in `XMM1`. But be careful, often people conclude from seeing the `XMM` register being used, that it is vector code---not necessarily. For instance, the `VMULSS` instruction will only multiply one single-precision floating-point value, not four.

Another indicator for potential vectorization opportunities is a high `Retiring` metric (above 80%). In [@sec:TMA], we said that the `Retiring` metric is a good indicator of well-performing code. The rationale behind it is that execution is not stalled and a CPU is retiring instructions at a high rate. However, sometimes it may hide the real performance problem, that is, inefficient computations. Perhaps a workload executes a lot of simple instructions that can be replaced by vector instructions. In such situations, high `Retiring` metric doesn't translate into high performance.

There are a few common cases that developers frequently run into when trying to accelerate vectorizable code. Below we present four typical scenarios and give general guidance on how to proceed in each case.

#### Vectorization Is Illegal.

In some cases, the code that iterates over elements of an array is simply not vectorizable. Optimization reports are very effective at explaining what went wrong and why the compiler can’t vectorize the code. [@lst:VectDep] shows an example of dependence inside a loop that prevents vectorization.[^31]

Listing: Vectorization: read-after-write dependence.

~~~~ {#lst:VectDep .cpp}
void vectorDependence(int *A, int n) {
  for (int i = 1; i < n; i++)
    A[i] = A[i-1] * 2;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While some loops cannot be vectorized due to the hard limitations (such as read-after-write dependence), others could be vectorized when certain constraints are relaxed. For example, the code in [@lst:VectIllegal] cannot be autovectorized by the compiler, because it will change the order of floating-point operations and may lead to different rounding and a slightly different result. Floating-point addition is commutative, which means that you can swap the left-hand side and the right-hand side without changing the result: `(a + b == b + a)`. However, it is not associative, because rounding happens at different times: `((a + b) + c) != (a + (b + c))`.

Listing: Vectorization: floating-point arithmetic.

~~~~ {#lst:VectIllegal .cpp .numberLines}
// a.cpp
float calcSum(float* a, unsigned N) {
  float sum = 0.0f;
  for (unsigned i = 0; i < N; i++) {
    sum += a[i];
  }
  return sum;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you tell the compiler that you can tolerate a bit of variation in the final result, it  will autovectorize the code for you. Clang and GCC compilers have a flag, `-ffast-math`,[^29] that allows this kind of transformation even though the resulting program may give slightly different results:

```bash
$ clang++ -c a.cpp -O3 -march=core-avx2 -Rpass-analysis=.*
...
a.cpp:5:9: remark: loop not vectorized: cannot prove it is safe to reorder floating-point operations; allow reordering by specifying '#pragma clang loop vectorize(enable)' before the loop or by providing the compiler option '-ffast-math'. [-Rpass-analysis=loop-vectorize]
...
$ clang++ -c a.cpp -O3 -march=core-avx2 -ffast-math -Rpass=.*
...
a.cpp:4:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]
...
```

Unfortunately, this flag involves subtle and potentially dangerous behavior changes, including for Not-a-Number, signed zero, infinity, and subnormals. Because third-party code may not be ready for these effects, this flag should not be enabled across large sections of code without careful validation of the results, including for edge cases. Since Clang 18, you can limit the scope of transformations by using dedicated pragmas, e.g., `#pragma clang fp reassociate(on)`.[^4]

Let's look at another typical situation when a compiler may need support from a developer to perform vectorization. When compilers cannot prove that a loop operates on arrays with non-overlapping memory regions, they usually choose to be on the safe side. Given the code in [@lst:OverlappingMemRefions], compilers should account for the situation when the memory regions of arrays `a`, `b`, and `c` overlap.

Listing: a.c

~~~~ {#lst:OverlappingMemRefions .cpp .numberLines}
void foo(float* a, float* b, float* c, unsigned N) {
  for (unsigned i = 1; i < N; i++) {
    c[i] = b[i];
    a[i] = c[i-1];
  }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is the optimization report (enabled with `-fopt-info`) provided by GCC 10.2:

```bash
$ gcc -O3 -march=core-avx2 -fopt-info
a.cpp:2:26: optimized: loop vectorized using 32-byte vectors
a.cpp:2:26: optimized:  loop versioned for vectorization because of possible aliasing
```

GCC has recognized potential overlap between memory regions and created multiple versions of the loop. The compiler inserted runtime checks[^36] to detect if the memory regions overlap. Based on those checks, it dispatches between vectorized and scalar versions. In this case, vectorization comes with the cost of inserting potentially expensive runtime checks. If a developer knows that memory regions of arrays `a`, `b`, and `c` do not overlap, it can insert `#pragma GCC ivdep`[^37] right before the loop or use the `__restrict__  ` keyword as shown in [@sec:compilerOptReports]. Such compiler hints will eliminate the need for the GCC compiler to insert the runtime checks mentioned earlier.

Some dynamic tools, such as Intel Advisor, can detect if issues like cross-iteration dependence or access to arrays with overlapping memory regions occur in a loop. But be aware that such tools only provide a suggestion. Carelessly inserting compiler hints can cause real problems.

#### Vectorization Is Not Beneficial.

In some cases, the compiler can vectorize the loop but decide that doing so is not profitable. In the code presented in [@lst:VectNotProfit], the compiler could vectorize the memory access to array `A` but would need to split the access to array `B` into multiple scalar loads. The scatter/gather pattern is relatively expensive, and compilers that can simulate the cost of operations often decide to avoid vectorizing code with such patterns. 

Listing: Vectorization: not beneficial.

~~~~ {#lst:VectNotProfit .cpp .numberLines}
// a.cpp
void stridedLoads(int *A, int *B, int n) {
  for (int i = 0; i < n; i++)
    A[i] += B[i * 3];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is the compiler optimization report for the code in [@lst:VectNotProfit]: 

```bash
$ clang -c -O3 -march=core-avx2 a.cpp -Rpass-missed=loop-vectorize
a.cpp:3:3: remark: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]
  for (int i = 0; i < n; i++)
  ^
```

Users can force the Clang compiler to vectorize the loop by using the `#pragma` hint, as shown in [@lst:VectNotProfitOverriden]. However, keep in mind that whether vectorization is profitable largely depends on the runtime data, for example, the number of iterations of the loop. Compilers don't have this information available,[^1] so they often tend to be conservative. Though you can use such hints for performance experiments.

Listing: Vectorization: not beneficial.

~~~~ {#lst:VectNotProfitOverriden .cpp .numberLines}
// a.cpp
void stridedLoads(int *A, int *B, int n) {
#pragma clang loop vectorize(enable)
  for (int i = 0; i < n; i++)
    A[i] += B[i * 3];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Developers should be aware of the hidden cost of using vectorized code. Using AVX and especially AVX-512 vector instructions could lead to frequency downclocking or startup overhead, which on certain CPUs can also affect subsequent code for several microseconds. The vectorized portion of the code should be hot enough to justify using AVX-512.[^38] For example, sorting 80 KiB was found to be sufficient to amortize this overhead and make vectorization worthwhile.[^39]

#### Loop Vectorized but Scalar Version Used.

In some scenarios, the compiler successfully vectorizes the code, but it does not show up as being executed in the profiler. When inspecting the corresponding assembly of a loop, it is usually easy to find the vectorized version of the loop body because it uses vector registers, which are not commonly used in other parts of the program.

If the vector code is not executed, one possible reason for this is that the generated code assumes loop trip counts that are higher than what the program uses. For example, a compiler may decide to vectorize and unroll the loop in such a way as to process 64 elements per iteration. An input array may not have enough elements even for a single iteration of the loop. In this case, the scalar version (remainder) of the loop will be used instead. It is easy to detect these cases because the scalar loop would light up in the profiler, and the vectorized code would remain cold. 

The solution to this problem is to force the vectorizer to use a lower vectorization factor or unroll count, to reduce the number of elements that the loop processes. You can achieve that with the help of `#pragma` hints. For the Clang compiler, you can use `#pragma clang loop vectorize_width(N)` as shown in the article on the Easyperf blog.[^30]

#### Loop Vectorized in a Suboptimal Way.

When you see a loop being autovectorized and executed at runtime, there is a high chance that this part of the program already performs well. However, there are exceptions. There are situations when the scalar un-vectorized version of a loop performs better than the vectorized one. This could happen due to expensive vector operations like `gather/scatter` loads, masking, `inserting/extracting` elements, data shuffling, etc., if the compiler is required to use them to make vectorization happen. Performance engineers could also try to disable vectorization in different ways. For the Clang compiler, it can be done via compiler options `-fno-vectorize` and `-fno-slp-vectorize`, or with a hint specific to a particular loop, e.g., `#pragma clang loop vectorize(disable)`.

It is important to note that there is a range of problems where SIMD is important and where autovectorization just does not work and is not likely to work in the near future. One example can be found in [@Mula_Lemire_2019]. Another example is outer loop autovectorization, which is not currently attempted by compilers. Vectorizing floating-point code is problematic because reordering arithmetic floating-point operations results in different rounding and slightly different values.

There is one more subtle problem with autovectorization. As compilers evolve, optimizations that they make are changing. The successful autovectorization of code that was done in the previous compiler version may stop working in the next version, or vice versa. Also, during code maintenance or refactoring, the structure of the code may change, such that autovectorization suddenly starts failing. This may occur long after the original software was written, so it would be more expensive to fix or redo the implementation at this point.

#### Languages with Explicit Vectorization. {#sec:ISPC}

Vectorization can also be achieved by rewriting parts of a program in a programming language that is dedicated to parallel computing. Those languages use special constructs and knowledge of the program's data to compile the code efficiently into parallel programs. Originally such languages were mainly used to offload work to specific processing units such as graphics processing units (GPU), digital signal processors (DSP), or field-programmable gate arrays (FPGAs). However, some of those programming models can also target your CPU (such as OpenCL and OpenMP).

One such parallel language is Intel® Implicit SPMD Program Compiler [(ISPC)](https://ispc.github.io/),[^33] which I will briefly cover in this section. The ISPC language is based on the C programming language and uses the LLVM compiler infrastructure to generate optimized code for many different architectures. The key feature of ISPC is the "close to the metal" programming model and performance portability across SIMD architectures. It requires a shift from the traditional thinking of writing programs but gives programmers more control over CPU resource utilization.

Another advantage of ISPC is its interoperability and ease of use. ISPC compiler generates standard object files that can be linked with the code generated by conventional C/C++ compilers. ISPC code can be easily plugged into any native project since functions written with ISPC can be called as if it was C code.

[@lst:ISPC_code] shows an ISPC version of a function that I presented earlier in [@lst:VectIllegal]. ISPC considers that the program will run in parallel instances, based on the target instruction set. For example, when using SSE with `float`s, it can compute 4 operations in parallel. Each program instance would operate on vector values of `i` being `(0,1,2,3)`, then `(4,5,6,7)`, and so on, effectively computing 4 sums at a time. As you can see, a few keywords not typical for C and C++ are used:

* The `export` keyword means that the function can be called from a C-compatible language.

* The `uniform` keyword means that a variable is shared between program instances.

* The `varying` keyword means that each program instance has its own local copy of the variable.

* The `foreach` is the same as a classic `for` loop except that it will distribute the work across the different program instances. 

Listing: ISPC version of summing elements of an array.

~~~~ {#lst:ISPC_code .cpp}
export uniform float calcSum(const uniform float array[], 
                             uniform ptrdiff_t count)
{
    varying float sum = 0;
    foreach (i = 0 ... count)
        sum += array[i];
    return reduce_add(sum);
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the function `calcSum` must return a single value (a `uniform` variable) and our `sum` variable is `varying`, we then need to *gather* the values of each program instance using the `reduce_add` function. ISPC also takes care of generating peeled and remainder loops as needed to take into account the data that is not correctly aligned or that is not a multiple of the vector width. 

**"Close to the metal" programming model**: one of the problems with traditional C and C++ languages is that the compiler doesn't always vectorize critical parts of code. ISPC helps to resolve this problem by assuming every operation is SIMD by default. For example, the ISPC statement `sum += array[i]` is implicitly considered as a SIMD operation that makes multiple additions in parallel. ISPC is not an autovectorizing compiler, and it does not automatically discover vectorization opportunities. Since the ISPC language is very similar to C and C++, it is more readable than intrinsics (see [@sec:secIntrinsics]) as it allows you to focus on the algorithm rather than the low-level instructions. Also, it has reportedly matched [@ISPC_Paper] or beaten[^34] hand-written intrinsics code in terms of performance.

**Performance portability**: ISPC can automatically detect features of your CPU to fully utilize all the resources available. Programmers can write ISPC code once and compile to many vector instruction sets, such as SSE4, AVX2, and ARM NEON.

[^1]: Besides Profile Guided Optimizations (see [@sec:secPGO]).
[^2]: For example, compiler optimization reports, see [@sec:compilerOptReports].
[^29]: The compiler flag `-Ofast` enables `-ffast-math` as well as the `-O3` compilation mode.
[^30]: Using Clang's optimization pragmas - [https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts](https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts)
[^31]: It is easy to spot a read-after-write dependency once you unroll a couple of iterations of the loop. See the example in [@sec:compilerOptReports].
[^33]: ISPC compiler: [https://ispc.github.io/](https://ispc.github.io/).
[^34]: Some parts of the Unreal Engine that used SIMD intrinsics were rewritten using ISPC, which gave speedups: [https://software.intel.com/content/www/us/en/develop/articles/unreal-engines-new-chaos-physics-system-screams-with-in-depth-intel-cpu-optimizations.html](https://software.intel.com/content/www/us/en/develop/articles/unreal-engines-new-chaos-physics-system-screams-with-in-depth-intel-cpu-optimizations.html).
[^36]: See the example on the Easyperf blog: [https://easyperf.net/blog/2017/11/03/Multiversioning_by_DD](https://easyperf.net/blog/2017/11/03/Multiversioning_by_DD).
[^37]: It is a GCC-specific pragma. For other compilers, check the corresponding manuals.
[^38]: For more details read this blog post: [https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html](https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html).
[^39]: Study of AVX-512 downclocking: in [VQSort readme](https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md#study-of-avx-512-downclocking)
[^4]: LLVM extensions to specify floating-point flags - [https://clang.llvm.org/docs/LanguageExtensions.html#extensions-to-specify-floating-point-flags](https://clang.llvm.org/docs/LanguageExtensions.html#extensions-to-specify-floating-point-flags)
