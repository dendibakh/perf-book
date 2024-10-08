## Compiler Intrinsics {#sec:secIntrinsics}

There are types of applications that have hotspots worth tuning heavily. However, compilers do not always do what we want in terms of generated code in those hot places. For example, a program does some computation in a loop which the compiler vectorizes in a suboptimal way. It usually involves some tricky or specialized algorithms, for which we can come up with a better sequence of instructions. It can be very hard or even impossible to make the compiler generate the desired assembly code using standard constructs of the C and C++ languages.

Hopefully, it's possible to force the compiler to generate particular assembly instructions without writing in low-level assembly language. To achieve that, one can use compiler intrinsics, which in turn are translated into specific assembly instructions. Intrinsics provide the same benefit as using inline assembly, but also they improve code readability and allow compiler type checking and further optimization, e.g., peephole transformations and instruction scheduling. An example in [@lst:Intrinsics] shows how the horizontal sum of elements in an array (see [@lst:VectIllegal]) can be coded via compiler intrinsics.

Listing: Summing elements of an array with compiler Intrinsics.
		
~~~~ {#lst:Intrinsics .cpp .numberLines}
#include <immintrin.h>

float calcSum(float* a, unsigned N) {  
  __m128 sum = _mm_setzero_ps();      // init sum with zeros
  unsigned i = 0;
  for (; i + 3 < N; i += 4) {
    __m128 vec = _mm_loadu_ps(a + i); // load 4 floats from array
    sum = _mm_add_ps(sum, vec);       // accumulate vec into sum
  }

  // Horizontal sum of the 128-bit vector
  __m128 shuf = _mm_movehdup_ps(sum); // broadcast elements 3,1 to 2,0
  sum = _mm_add_ps(sum, shuf);        // partial sums [0+1] and [2+3]
  shuf = _mm_movehl_ps(shuf, sum);    // high half -> low half
  sum = _mm_add_ss(sum, shuf);        // result in the lower element
  float result = _mm_cvtss_f32(sum);  // nop (compiler eliminates it)

  // Process any remaining elements
  for (; i < N; i++)
      result += a[i];
  return result;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When compiling [@lst:VectIllegal] for the SSE target, compilers would generate mostly identical assembly code as for [@lst:Intrinsics]. We show this example just for illustration purposes. Obviously, there is no need to use intrinsics if the compiler can generate the same machine code. You should use intrinsics only when compiler fails to generate the desired code. When you leverage compiler auto-vectorization, it will insert all necessary runtime checks. For instance, it will ensure that there are enough elements to feed the vector execution units (see [@lst:Intrinsics], line 6). Also, the compiler will generate a scalar version of the loop to process the remainder (line 19). When you use intrinsics, you have to take care of safety aspects yourself.

When writing code using non-portable platform-specific intrinsics, developers should also provide a fallback option for other architectures. A list of all available intrinsics for the Intel platform can be found in this [reference](https://software.intel.com/sites/landingpage/IntrinsicsGuide/)[^11]. For ARM, you can find such a list here: [https://developer.arm.com/architectures/instruction-sets/intrinsics/](https://developer.arm.com/architectures/instruction-sets/intrinsics/).

### Wrapper Libraries for Intrinsics {#sec:secIntrinsicLibraries}

The write-once, target-many model of ISPC is appealing. However, we may wish for tighter integration into C++ programs, for example, interoperability with templates, or avoiding a separate build step and using the same compiler. Conversely, intrinsics offer more control, but at a higher development cost.

We can combine the advantages of both and avoid these drawbacks using a so-called embedded domain-specific language, where the vector operations are expressed as normal C++ functions. You can think of these functions as 'portable intrinsics', for example, `Add` or `LoadU`. Even compiling your code multiple times, once per instruction set, can be done within a normal C++ library by using the preprocessor to 'repeat' your code with different compiler settings, but within unique namespaces. One example of this is the previously mentioned Highway library,[^12] which only requires the C++11 standard.

Like ISPC, Highway also supports detecting the best available instruction sets, grouped into 'clusters' which on x86 correspond to Intel Core (S-SSE3), Nehalem (SSE4.2), Haswell (AVX2), Skylake (AVX-512), or Icelake/Zen4 (AVX-512 with extensions). It then calls your code from the corresponding namespace.
Unlike intrinsics, the code remains readable (without prefixes/suffixes on each function) and portable.

Listing: Highway version of summing elements of an array.

~~~~ {#lst:HWY_code .cpp}
#include <hwy/highway.h>

float calcSum(const float* HWY_RESTRICT array, size_t count) {
  const ScalableTag<float> d;  // type descriptor; no actual data
  auto sum = Zero(d);
  size_t i = 0;
  for (; i + Lanes(d) <= count; i += Lanes(d)) {
    sum = Add(sum, LoadU(d, array + i));
  }
  sum = Add(sum, MaskedLoad(FirstN(d, count - i), d, array + i));
  return ReduceSum(d, sum);
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice the explicit handling of remainders after the loop processes multiples of the vector sizes `Lanes(d)`. Although this is more verbose, it makes visible what is actually happening, and allows optimizations such as overlapping the last vector instead of relying on `MaskedLoad`, or even skipping the remainder entirely when the `count` is known to be a multiple of the vector size.

Highway supports over 200 operations, which can be grouped into the following categories:

\begin{multicols}{2}
\begin{itemize}
\tightlist
\item Initialization
\item Getting/setting lanes
\item Getting/setting blocks
\item Printing
\item Tuples
\item Arithmetic
\item Logical
\item Masks
\item Comparisons
\item Memory
\item Cache control
\item Type conversion
\item Combine
\item Swizzle/permute
\item Swizzling within 128-bit blocks
\item Reductions
\item Crypto
\end{itemize}
\end{multicols}

For the full list of operations, see its documentation [^13] and [FAQ](https://github.com/google/highway/blob/master/g3doc/faq.md). Highway is not the only library of this kind. Other libraries include nsimd, SIMDe, VCL, and xsimd. Note that a C++ standardization effort starting with the Vc library resulted in std::experimental::simd, but this provides a very limited set of operations and as of this writing is not supported on all the major compilers.

[^11]: Intel Intrinsics Guide - [https://software.intel.com/sites/landingpage/IntrinsicsGuide/](https://software.intel.com/sites/landingpage/IntrinsicsGuide/).
[^12]: Highway library: [https://github.com/google/highway](https://github.com/google/highway)
[^13]: Highway Quick Reference - [https://github.com/google/highway/blob/master/g3doc/quick_reference.md](https://github.com/google/highway/blob/master/g3doc/quick_reference.md)
