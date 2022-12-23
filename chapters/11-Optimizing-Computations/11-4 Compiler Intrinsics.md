---
typora-root-url: ..\..\img
---

## Compiler Intrinsics {#sec:secIntrinsics}

There are types of applications that have very few hotspots that call for tuning them heavily. However, compilers do not always do what we want in terms of generated code in those hot places. For example, a program does some computation in a loop which the compiler vectorizes in a suboptimal way. It usually involves some tricky or specialized algorithms, for which we can come up with a better sequence of instructions. It can be very hard or even impossible to make the compiler generate the desired assembly code using standard constructs of the C and C++ languages.

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

[^11]: Intel Intrinsics Guide - [https://software.intel.com/sites/landingpage/IntrinsicsGuide/](https://software.intel.com/sites/landingpage/IntrinsicsGuide/).
