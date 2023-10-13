## SIMD Multiprocessors {#sec:SIMD}

Another variant of multiprocessing that is widely used for many workloads is referred to as Single Instruction Multiple Data (SIMD). As the name indicates, in SIMD processors, a single instruction operates on many data elements in a single cycle using many independent functional units. Operations on vectors and matrices lend themselves well to SIMD architectures as every element of a vector or matrix can be processed using the same instruction. SIMD architecture allows more efficient processing of a large amount of data and works best for data-parallel applications that involve vector operations.

Figure @fig:SIMD shows scalar and SIMD execution modes for the code listed in @lst:SIMD. In a traditional SISD (Single Instruction, Single Data) mode, addition operation is separately applied to each element of arrays `a` and `b`. However, in SIMD mode, addition is applied to multiple elements at the same time. If we target a CPU architecture which has execution units capable of performing operations on 256-bit vectors, we can process four double-precision elements with a single instruction. This leads to issuing 4x less instructions and can potentially gain a 4x speedup over four scalar computations. But in practice, performance benefits are not so straightforward for various reasons.

Listing: SIMD execution

~~~~ {#lst:SIMD .cpp}
double *a, *b, *c;
for (int i = 0; i < N; ++i) {
  c[i] = a[i] + b[i];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Example of scalar and SIMD operations.](../../img/uarch/SIMD.png){#fig:SIMD width=80%}

For a regular SISD instructions, processors utilize general-purpose registers. Similarly, for SIMD instructions, CPUs have a set of SIMD registers to keep the data loaded from memory and store the intermediate results of computations. In our example, two regions of 256 bits of contiguous data corresponding to arrays `a` and `b` will be loaded from memory and stored in two separate vector registers. Next, the element-wise addition will be done and result will be stored in a new 256-bit vector register. Finally, the result will be written from the vector register to a 256-bit memory region that corresponds to the array `c`. Note, the data elements can be either integers or floating-point numbers.

Most of the popular CPU architectures feature vector instructions, including x86, PowerPC, Arm, and RISC-V. In 1996 Intel released MMX, a SIMD instruction set, that was designed for multimedia applications. Following MMX, Intel introduced new instruction sets with added capabilities and increased vector size: SSE, AVX, AVX2, AVX-512. Arm has optionally supported the 128-bit NEON instruction set in various versions of its architecture. In version 8 (aarch64), this support was made mandatory, and new instructions were added.

As the new instruction sets became available, work began to make them usable to software engineers. The software changes required to exploit SIMD instructions are known as *code vectorization*. At first, SIMD instructions were programmed in assembly. Later, special compiler intrinsics were introduced, which are small high-level source code functions that provide 1-to-1 mapping to SIMD instructions. Today all of the major compilers support autovectorization for the popular processors, i.e. they can generate SIMD instructions straight from the high-level code written in C/C++, Java, Rust and other languages.

To allow a code to run on systems that support different vector lengths, Arm introduced the SVE instruction set. Its defining characteristic is the concept of *scalable vectors*: their length is unknown at compile time. With SVE, there is no need to port software to every possible vector length. Users don't have to recompile the source code of their applications to leverage wider vectors when they become available in newer CPU generations. Another example of scalable vectors is the RISC-V V extension (RVV), which was ratified in late 2021. Some implementations support quite wide (2048 bit) vectors, and up to eight can be grouped together to yield 16,384 bit vectors, which greatly reduces the number of instructions executed. At each loop iteration, user code typically does `ptr += number_of_lanes`, where `number_of_lanes` is not known at compile time. ARM SVE provides special instructions for such length-dependent operations while RVV allows to query/set the `number_of_lanes`.

Also, CPUs increasingly accelerate the matrix multiplications often used in machine learning. Intel's AMX extension, supported in Sapphire Rapids, multiplies 8-bit matrices of shape 16x64 and 64x16, accumulating into a 32-bit 16x16 matrix. By contrast, the unrelated but identically named AMX extension in Apple CPUs, as well as Arm's SME extension, compute outer products of a row and column, respectively stored in special 512-bit registers, or scalable vectors.

Initially SIMD was driven by multimedia applications and scientific computations but later found its use in many other domains. Over time, the set of operations supported in SIMD instruction sets has steadily increased. In addition to straightforward arithmetic as shown above, newer use cases of SIMD include:

- String processing: finding characters, validating UTF-8 [^1], parsing JSON [^2] and CSV [^3];
- Hashing [^4], random generation [^5], cryptography (AES);
- Columnar databases (bit packing, filtering, joins);
- Sorting built-in types (VQSort [^6], QuickSelect);
- Machine Learning and Artificial Inteligence (speeding up PyTorch, Tensorflow).

[^1]: UTF-8 validation: [https://github.com/rusticstuff/simdutf8](https://github.com/rusticstuff/simdutf8)
[^2]: Parsing JSON: [https://github.com/simdjson/simdjson](https://github.com/simdjson/simdjson).
[^3]: Parsing CSV: [https://github.com/geofflangdale/simdcsv](https://github.com/geofflangdale/simdcsv)
[^4]: SIMD hashing: [https://github.com/google/highwayhash](https://github.com/google/highwayhash)
[^5]: Random generation: [abseil library](https://github.com/abseil/abseil-cpp/blob/master/absl/random/internal/randen.h)
[^6]: Sorting: [VQSort](https://github.com/google/highway/tree/master/hwy/contrib/sort)
