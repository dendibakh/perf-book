## Cache-Friendly Data Structures {#sec:secCacheFriendly}

[TODO]: Elaborate.

Writing cache-friendly algorithms and data structures, is one of the key items in the recipe for a well-performing application. The key pillar of cache-friendly code is the principles of temporal and spatial locality that we described in [@sec:MemHierar]. The goal here is to allow required data to be fetched from caches efficiently. When designing cache-friendly code, it's helpful to think in terms of cache lines, not only individual variables and their location in memory.

### Access Data Sequentially.

[TODO]: Elaborate

The best way to exploit the spatial locality of the caches is to make sequential memory accesses. By doing so, we allow the HW prefetcher (see [@sec:HwPrefetch]) to recognize the memory access pattern and bring in the next chunk of data ahead of time. An example of a C-code that does such cache-friendly accesses is shown on [@lst:CacheFriend]. The code is "cache-friendly" because it accesses the elements of the matrix in the order in which they are laid out in memory ([row-major traversal](https://en.wikipedia.org/wiki/Row-_and_column-major_order)[^6]). Swapping the order of indexes in the array (i.e., `matrix[column][row]`) will result in column-major order traversal of the matrix, which does not exploit spatial locality and hurts performance.

Listing: Cache-friendly memory accesses.

~~~~ {#lst:CacheFriend .cpp}
for (row = 0; row < NUMROWS; row++)
  for (column = 0; column < NUMCOLUMNS; column++)
    matrix[row][column] = row + column;
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The example presented in [@lst:CacheFriend] is classical, but usually, real-world applications are much more complicated than this. Sometimes you need to go an additional mile to write cache-friendly code. For instance, the standard implementation of binary search in a sorted large array does not exploit spatial locality since it tests elements in different locations that are far away from each other and do not share the same cache line. The most famous way of solving this problem is storing elements of the array using the Eytzinger layout [@EytzingerArray]. The idea of it is to maintain an implicit binary search tree packed into an array using the BFS-like layout, usually seen with binary heaps. If the code performs a large number of binary searches in the array, it may be beneficial to convert it to the Eytzinger layout.

### Use Appropriate Containers. 

[TODO]: Elaborate

There is a wide variety of ready-to-use containers in almost any language. But it's important to know their underlying storage and performance implications. A good step-by-step guide for choosing appropriate C++ containers can be found in [@fogOptimizeCpp, Chapter 9.7 Data structures, and container classes].

Additionally, choose the data storage, bearing in mind what the code will do with it. Consider a situation when there is a need to choose between storing objects in the array versus storing pointers to those objects while the object size is big. An array of pointers take less amount of memory. This will benefit operations that modify the array since an array of pointers requires less memory being transferred. However, a linear scan through an array will be faster when keeping the objects themselves since it is more cache-friendly and does not require indirect memory accesses.[^8]

### Packing the Data.

[TODO]: Cosmetics

[TODO]: include example of using data-type profiling (https://lwn.net/Articles/955709/). Find a good example for a case study.

Memory hierarchy utilization can be improved by making the data more compact. There are many ways to pack data. One of the classic examples is to use bitfields. An example of code when packing data might be profitable is shown on [@lst:PackingData1]. If we know that `a`, `b`, and `c` represent enum values which take a certain number of bits to encode, we can reduce the storage of the struct `S` (see [@lst:PackingData2]).

Listing: Packing Data: baseline struct.

~~~~ {#lst:PackingData1 .cpp}
struct S {
  unsigned a;
  unsigned b;
  unsigned c;
}; // S is `sizeof(unsigned int) * 3` bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing: Packing Data: packed struct.

~~~~ {#lst:PackingData2 .cpp}
struct S {
  unsigned a:4;
  unsigned b:2;
  unsigned c:2;
}; // S is only 1 byte
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This greatly reduces the amount of memory transferred back and forth and saves cache space. Keep in mind that this comes with the cost of accessing every packed element. Since the bits of `b` share the same machine word with `a` and `c`, compiler need to perform a `>>` (shift right) and `&` (AND) operation to load it. Similarly, `<<` (shift left) and `|` (OR) operations are needed to store the value back. Packing the data is beneficial in places where additional computation is cheaper than the delay caused by inefficient memory transfers.

Also, a programmer can reduce the memory usage by rearranging fields in a struct or class when it avoids padding added by a compiler (see example in [@lst:PackingData3]). The reason for a compiler to insert unused bytes of memory (pads) is to allow efficient storing and fetching of individual members of a struct. In the example, the size of `S1` can be reduced if its members are declared in the order of decreasing their sizes.

Listing: Avoid compiler padding.

~~~~ {#lst:PackingData3 .cpp}
struct S1 {
  bool b;
  int i;
  short s;
}; // S1 is `sizeof(int) * 3` bytes

struct S2 {
  int i;
  short s;  
  bool b;
}; // S2 is `sizeof(int) * 2` bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Aligning and Padding. {#sec:secMemAlign}

[TODO]: Cosmetics. Mention that vtune tracks it with the `Split Loads` metric.
https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-0/cpu-metrics-reference.html#SPLIT-LOADS

[TODO]: “Aligned” here means the memory address is a multiple of a specific size. For example, the low 5 bits of a 32 byte aligned memory address will be zero. A “misaligned” access crosses an alignment boundary

[TODO]: Update Agner Fog references. Or maybe just remove them?

[TODO]: Explain why misaligned loads can be a source of perf problems?
A “misaligned” access crosses an alignment boundary, forcing the load/store unit to make two L1D lookups to satisfy the request.

[TODO]: Accesses that cross a 4 KB boundary:
Accesses that cross a 4 KB boundary introduce more complications, because virtual to physical address translations are usually handled in 4 KB pages. Handling such an access would require accessing two TLB entries as well. TLBs must support multiple lookups per cycle.

[TODO]: Should I add images for better explanation?

Another technique to improve the utilization of the memory subsystem is to align the data. There could be a situation when an object of size 16 bytes occupies two cache lines, i.e., it starts on one cache line and ends in the next cache line. Fetching such an object requires two cache line reads, which could be avoided would the object be aligned properly. [@lst:AligningData] shows how memory objects can be aligned using C++11 `alignas` keyword.

Listing: Aligning data using the "alignas" keyword.

~~~~ {#lst:AligningData .cpp}
// Make an aligned array
alignas(16) int16_t a[N];

// Objects of struct S are aligned at cache line boundaries
#define CACHELINE_ALIGN alignas(64) 
struct CACHELINE_ALIGN S {
  //...
};
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A variable is accessed most efficiently if it is stored at a memory address, which is divisible by the size of the variable. For example, a double takes 8 bytes of storage space. It should, therefore, preferably be stored at an address divisible by 8. The size should always be a power of 2. Objects bigger than 16 bytes should be stored at an address divisible by 16. [@fogOptimizeCpp]

Alignment can cause holes of unused bytes, which potentially decreases memory bandwidth utilization. If, in the example above, struct `S` is only 40 bytes, the next object of `S` starts at the beginning of the next cache line, which leaves `64 - 40 = 24` unused bytes in every cache line which holds objects of struct `S`.

Sometimes padding data structure members is required to avoid edge cases like cache contentions [@fogOptimizeCpp, Chapter 9.10 Cache contentions] and false sharing (see [@sec:secFalseSharing]). For example, false sharing issues might occur in multithreaded applications when two threads, `A` and `B`, access different fields of the same structure. An example of code when such a situation might happen is shown on [@lst:PadFalseSharing1]. Because `a` and `b` members of struct `S` could potentially occupy the same cache line, cache coherency issues might significantly slow down the program. To resolve the problem, one can pad `S` such that members `a` and `b` do not share the same cache line as shown in [@lst:PadFalseSharing2].

Listing: Padding data: baseline version.

~~~~ {#lst:PadFalseSharing1 .cpp}
struct S {
  int a; // written by thread A
  int b; // written by thread B
};
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing: Padding data: improved version.

~~~~ {#lst:PadFalseSharing2 .cpp}
#define CACHELINE_ALIGN alignas(64) 
struct S {
  int a; // written by thread A
  CACHELINE_ALIGN int b; // written by thread B
};
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When it comes to dynamic allocations via `malloc`, it is guaranteed that the returned memory address satisfies the target platform's minimum alignment requirements. Some applications might benefit from a stricter alignment. For example, dynamically allocating 16 bytes with a 64 bytes alignment instead of the default 16 bytes alignment. To leverage this, users of POSIX systems can use [`memalign`](https://linux.die.net/man/3/memalign)[^13] API. Others can roll their own like described [here](https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/)[^14].

One of the most important areas for alignment considerations is the SIMD code. When relying on compiler auto-vectorization, the developer doesn't have to do anything special. However, when you write the code using compiler vector intrinsics (see [@sec:secIntrinsics]), it's pretty common that they require addresses divisible by 16, 32, or 64. Vector types provided by the compiler intrinsic header files are already annotated to ensure the appropriate alignment. [@fogOptimizeCpp]

```cpp
// ptr will be aligned by alignof(__m512) if using C++17
__m512 * ptr = new __m512[N];
```

[TODO]: Trim footnotes

[^5]: The same applies to memory deallocation.
[^6]: Row- and column-major order - [https://en.wikipedia.org/wiki/Row-_and_column-major_order](https://en.wikipedia.org/wiki/Row-_and_column-major_order).
[^8]: Blog article "Vector of Objects vs Vector of Pointers" by B. Filipek - [https://www.bfilipek.com/2014/05/vector-of-objects-vs-vector-of-pointers.html](https://www.bfilipek.com/2014/05/vector-of-objects-vs-vector-of-pointers.html).
[^13]: Linux manual page for `memalign` - [https://linux.die.net/man/3/memalign](https://linux.die.net/man/3/memalign).
[^14]: Generating aligned memory - [https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/](https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/).
