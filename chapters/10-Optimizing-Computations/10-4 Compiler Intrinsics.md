---
typora-root-url: ..\..\img
---

## Compiler Intrinsics {#sec:secIntrinsics}

There are types of applications that have hotspots worth tuning heavily. However, compilers do not always do what we want in terms of generated code in those hot places. For example, a program does some computation in a loop which the compiler vectorizes in a suboptimal way. It usually involves some tricky or specialized algorithms, for which we can come up with a better sequence of instructions. It can be very hard or even impossible to make the compiler generate the desired assembly code using standard constructs of the C and C++ languages.

Hopefully, it's possible to force the compiler to generate particular assembly instructions without writing in low-level assembly language. To achieve that, one can use compiler intrinsics, which in turn are translated into specific assembly instructions. Intrinsics provide the same benefit as using inline assembly, but also they improve code readability, allow compiler type checking, assist instruction scheduling, and help reduce debugging. Example in [@lst:Intrinsics] shows how the same loop in function `foo` can be coded via compiler intrinsics (function `bar`).

Listing: Compiler Intrinsics
		
~~~~ {#lst:Intrinsics .cpp .numberLines}
void foo(float *a, float *b, float *c, unsigned N) {
  for (unsigned i = 0; i < N; i++)
    c[i] = a[i] + b[i]; 
}

#include <xmmintrin.h>

void bar(float *a, float *b, float *c, unsigned N) {
  __m128 rA, rB, rC;
  for (int i = 0; i < N; i += 4){
    rA = _mm_load_ps(&a[i]);
    rB = _mm_load_ps(&b[i]);
    rC = _mm_add_ps(rA,rB);
    _mm_store_ps(&c[i], rC);
  } 
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both functions in [@lst:Intrinsics] generate similar assembly instructions. However, there are several caveats. First, when relying on auto-vectorization, the compiler will insert all necessary runtime checks. For instance, it will ensure that there are enough elements to feed the vector execution units. Secondly, function `foo` will have a fallback scalar version of the loop for processing the remainder of the loop. And finally, most vector intrinsics assume aligned data, so `movaps` (aligned load) is generated for `bar`, while `movups` (unaligned load) is generated for `foo`. Keeping that in mind, developers using compiler intrinsics have to take care of safety aspects themselves.

When writing code using non-portable platform-specific intrinsics, developers should also provide a fallback option for other architectures. A list of all available intrinsics for the Intel platform can be found in this [reference](https://software.intel.com/sites/landingpage/IntrinsicsGuide/)[^11].

### Use wrapper library for intrinsics

The write-once, target-many model of ISPC is appealing. However, we may wish for tighter integration into C++ programs, for example interoperability with templates, or avoiding a separate build step and using the same compiler. Conversely, intrinsics offer more control, but at a higher development cost.

We can combine the advantages of both and avoid these drawbacks using a so-called embedded domain-specific language, where the vector operations are expressed as normal C++ functions. You can think of these functions as 'portable intrinsics', for example `Add` or `LoadU`. Even compiling your code multiple times, once per instruction set, can be done within a normal C++ library by using the preprocessor to 'repeat' your code with different compiler settings, but within unique namespaces. One example of this is the previously mentioned Highway library[^12], which only requires the C++11 standard.

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

Notice the explicit handling of remainders after the loop processes multiples of the vector sizes `Lanes(d)`. Although this is more verbose, it makes visible what is actually happening, and allows optimizations such as overlapping the last vector instead of relying on `MaskedLoad`, or even skipping the remainder entirely when `count` is known to be a multiple of the vector size.

Highway supports over 200 operations. For the full list, see its documentation [^13] and [FAQ](https://github.com/google/highway/blob/master/g3doc/faq.md). You can also experiment with it in the online [Compiler Explorer](https://gcc.godbolt.org/z/zP7MYe9Yf).


[^11]: Intel Intrinsics Guide - [https://software.intel.com/sites/landingpage/IntrinsicsGuide/](https://software.intel.com/sites/landingpage/IntrinsicsGuide/).
[^12]: Highway library: [https://github.com/google/highway](https://github.com/google/highway)
[^13]: Highway Quick Reference - [https://github.com/google/highway/blob/master/g3doc/quick_reference.md](https://github.com/google/highway/blob/master/g3doc/quick_reference.md)