## SIMD Multiprocessors {#sec:SIMD}

Another technique to facilitate parallel processing is called Single Instruction Multiple Data (SIMD), which is used in nearly all high-performance processors. As the name indicates, in a SIMD processor, a single instruction operates on many data elements in a single cycle using many independent functional units. Operations on vectors and matrices lend themselves well to SIMD architectures as every element of a vector or matrix can be processed using the same instruction. A SIMD architecture enables more efficient processing of a large amount of data and works best for data-parallel applications that involve vector operations.

Figure @fig:SIMD shows scalar and SIMD execution modes for the code in @lst:SIMD. In a traditional Single Instruction Single Data (SISD) mode, also known as *scalar* mode, the addition operation is separately applied to each element of arrays `a` and `b`. However, in SIMD mode, addition is applied to multiple elements at the same time. If we target a CPU architecture that has execution units capable of performing operations on 256-bit vectors, we can process four double-precision elements with a single instruction. This leads to issuing 4x fewer instructions and can potentially gain a 4x speedup over four scalar computations.

Listing: SIMD execution

~~~~ {#lst:SIMD .cpp}
double *a, *b, *c;
for (int i = 0; i < N; ++i) {
  c[i] = a[i] + b[i];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Example of scalar and SIMD operations.](../../img/uarch/SIMD.png){#fig:SIMD width=80%}

For regular SISD instructions, processors utilize general-purpose registers. Similarly, for SIMD instructions, CPUs have a set of SIMD registers to keep the data loaded from memory and store the intermediate results of computations. In our example, two regions of 256 bits of contiguous data corresponding to arrays `a` and `b` will be loaded from memory and stored in two separate vector registers. Next, the element-wise addition will be done and the result will be stored in a new 256-bit vector register. Finally, the result will be written from the vector register to a 256-bit memory region corresponding to array `c`. Note, that the data elements can be either integers or floating-point numbers.

A vector execution unit is logically divided into *lanes*. In the context of SIMD, a lane refers to a distinct data pathway within the SIMD execution unit and processes one element of the vector. In our example, each lane processes 64-bit elements (double-precision), so there will be 4 lanes in a 256-bit register.

Most of the popular CPU architectures feature vector instructions, including x86, PowerPC, ARM, and RISC-V. In 1996 Intel released MMX, a SIMD instruction set, that was designed for multimedia applications. Following MMX, Intel introduced new instruction sets with added capabilities and increased vector size: SSE, AVX, AVX2, AVX-512. Arm has optionally supported the 128-bit NEON instruction set in various versions of its architecture. In version 8 (aarch64), this support was made mandatory, and new instructions were added.

As the new instruction sets became available, work began to make them usable to software engineers. The software changes required to exploit SIMD instructions are known as *code vectorization*. Initially, SIMD instructions were programmed in assembly. Later, special compiler intrinsics, which are small functions providing a one-to-one mapping to SIMD instructions, were introduced. Today all the major compilers support autovectorization for the popular processors, i.e., they can generate SIMD instructions straight from high-level code written in C/C++, Java, Rust and other languages.

To enable code to run on systems that support different vector lengths, Arm introduced the SVE instruction set. Its defining characteristic is the concept of *scalable vectors*: their length is unknown at compile time. With SVE, there is no need to port software to every possible vector length. Users don't have to recompile the source code of their applications to leverage wider vectors when they become available in newer CPU generations. Another example of scalable vectors is the RISC-V V extension (RVV), which was ratified in late 2021. Some implementations support quite wide (2048-bit) vectors, and up to eight can be grouped together to yield 16384-bit vectors, which greatly reduces the number of instructions executed. At each loop iteration, user code typically does `ptr += number_of_lanes`, where `number_of_lanes` is not known at compile time. ARM SVE provides special instructions for such length-dependent operations, while RVV enables a programmer to query/set the `number_of_lanes`.

Going back to the example in @lst:SIMD, if `N` equals 5, and we have a 256-bit vector, we cannot process all the elements in a single iteration. We can process the first four elements using a single SIMD instruction, but the 5th element needs to be processed individually. This is known as the *loop remainder*. Loop remainder is a portion of a loop that must process fewer elements than the vector width, requiring additional scalar code to handle the leftover elements. Scalable vector ISA extensions do not have this problem, as they can process any number of elements in a single instruction. Another solution to the loop remainder problem is to use *masking*, which allows selectively enable or disable SIMD lanes based on a condition.

Also, CPUs increasingly accelerate the matrix multiplications often used in machine learning. Intel's AMX extension, supported in server processors since 2023, multiplies 8-bit matrices of shape 16x64 and 64x16, accumulating into a 32-bit 16x16 matrix. By contrast, the unrelated but identically named AMX extension in Apple CPUs, as well as ARM's SME extension, computes outer products of a row and column, respectively stored in special 512-bit registers or scalable vectors.

Initially, SIMD was driven by multimedia applications and scientific computations, but later found uses in many other domains. Over time, the set of operations supported in SIMD instruction sets has steadily increased. In addition to straightforward arithmetic as shown in Figure @fig:SIMD, newer use cases of SIMD include:

- String processing: finding characters, validating UTF-8,[^1] parsing JSON[^2] and CSV;[^3]
- Hashing,[^4] random generation,[^5] cryptography(AES);
- Columnar databases (bit packing, filtering, joins);
- Sorting built-in types (VQSort,[^6] QuickSelect);
- Machine Learning and Artificial Intelligence (speeding up PyTorch, TensorFlow).

[^1]: UTF-8 validation - [https://github.com/rusticstuff/simdutf8](https://github.com/rusticstuff/simdutf8)
[^2]: Parsing JSON - [https://github.com/simdjson/simdjson](https://github.com/simdjson/simdjson).
[^3]: Parsing CSV - [https://github.com/geofflangdale/simdcsv](https://github.com/geofflangdale/simdcsv)
[^4]: SIMD hashing - [https://github.com/google/highwayhash](https://github.com/google/highwayhash)
[^5]: Random generation - [abseil library](https://github.com/abseil/abseil-cpp/blob/master/absl/random/internal/randen.h)
[^6]: Sorting - [VQSort](https://github.com/google/highway/tree/master/hwy/contrib/sort)
