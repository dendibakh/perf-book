


## SIMD Multiprocessors {#sec:SIMD}

[TODO]: put the chapter after ILP section.

Another variant of multiprocessing that is widely used for certain workloads is referred to as SIMD (Single Instruction, Multiple Data) multiprocessors, in contrast to the MIMD approach described in the previous section. As the name indicates, in SIMD processors, a single instruction typically operates on many data elements in a single cycle using many independent functional units. Scientific computations on vectors and matrices lend themselves well to SIMD architectures as every element of a vector or matrix needs to be processed using the same instruction. SIMD multiprocessors are used primarily for such special purpose tasks that are data-parallel and require only a limited set of functions and operations.

Figure @fig:SIMD shows scalar and SIMD execution modes for the code listed in @lst:SIMD. In a traditional SISD (Single Instruction, Single Data) mode, addition operation is separately applied to each element of array `a` and `b`. However, in SIMD mode, addition is applied to multiple elements at the same time. SIMD CPUs support execution units that are capable of performing different operations on vector elements. The data elements themselves can be either integers or floating-point numbers. SIMD architecture allows more efficient processing of a large amount of data and works best for data-parallel applications that involve vector operations.

Listing: SIMD execution

~~~~ {#lst:SIMD .cpp}
double *a, *b, *c;
for (int i = 0; i < N; ++i) {
  c[i] = a[i] + b[i];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Example of scalar and SIMD operations.](../../img/uarch/SIMD.png){#fig:SIMD width=80%}

Most of the popular CPU architectures feature vector instructions, including x86, PowerPC, Arm, and RISC-V. In 1996 Intel released a new instruction set, MMX, which was a SIMD instruction set that was designed for multimedia applications. Following MMX, Intel introduced new instruction sets with added capabilities and increased vector size: SSE, AVX, AVX2, AVX-512. Arm has optionally supported the 128-bit NEON instruction set in various versions of its architecture. In version 8 (aarch64), this support was made mandatory, and new instructions were added. To allow making use of wider vectors without having to port software to each vector length, Arm subsequently introduced the SVE instruction set. Its defining characteristic is the concept of "scalable" vectors: their length is unknown at compile time. SVE provides special instructions for length-dependent operations such as incrementing pointers.

Another example of scalable vectors is the RISC-V V extension, which was ratified in late 2021. Some implementations support quite wide (2048 bit) vectors, and up to eight can be grouped together to yield 16,384 bit vectors, which greatly reduces the number of instructions executed.

As the new instruction sets became available, work began to make them usable to software engineers. At first, SIMD instructions were programmed in assembly. Later, special compiler intrinsics were introduced. Today all of the major compilers support vectorization for the popular processors.

Over time, the set of operations supported in SIMD has steadily increased. In addition to straightforward arithmetic as shown above, newer use cases of SIMD include:

-   String processing: finding characters, validating UTF-8 [^1], parsing JSON [^2] and CSV [^3];
-   Hashing [^4], random generation [^5], cryptography (AES);
-   Columnar databases (bit packing, filtering, joins);
-   Sorting built-in types (VQSort [^6]), QuickSelect.

[^1]: UTF-8 validation: [https://github.com/rusticstuff/simdutf8](https://github.com/rusticstuff/simdutf8)
[^2]: Parsing JSON: [https://github.com/simdjson/simdjson](https://github.com/simdjson/simdjson).
[^3]: Parsing CSV: [https://github.com/geofflangdale/simdcsv](https://github.com/geofflangdale/simdcsv)
[^4]: SIMD hashing: [https://github.com/google/highwayhash](https://github.com/google/highwayhash)
[^5]: Random generation: [abseil library](https://github.com/abseil/abseil-cpp/blob/master/absl/random/internal/randen.h)
[^6]: Sorting: [VQSort](https://github.com/google/highway/tree/master/hwy/contrib/sort)
