## Cache-Friendly Data Structures {#sec:secCacheFriendly}

Writing cache-friendly algorithms and data structures is one of the key items in the recipe for a well-performing application. The key pillars of cache-friendly code are the principles of temporal and spatial locality that we introduced in [@sec:MemHierar]. The goal here is to have a predictable memory access pattern and store data efficiently.

The cache line is the smallest unit of data that can be transferred between the cache and the main memory. When designing cache-friendly code, it's helpful to think not only of individual variables and their locations in memory but also of cache lines.

Next, we will discuss several techniques to make data structures more cache-friendly.

### Access Data Sequentially

The best way to exploit the spatial locality of the caches is to make sequential memory accesses. By doing so, we enable the hardware prefetching mechanism (see [@sec:HwPrefetch]) to recognize the memory access pattern and bring in the next chunk of data ahead of time. An example of Row-major versus Column-Major traversal is shown in [@lst:CacheFriend]. Notice, that there is only one tiny change in the code (swapped `col` and `row` subscripts), but it has a large impact on performance.

The code on the left is not cache-friendly because it skips the `NCOLS` elements on every iteration of the inner loop. This results in a very inefficient use of caches: we aren't making full use of the entire prefetched cache line before it gets evicted. In contrast, the code on the right accesses elements of the matrix in the order in which they are laid out in memory. This guarantees that the cache line will be fully used before it gets evicted. Row-major traversal exploits spatial locality and is cache-friendly. Figure @fig:ColRowMajor illustrates the difference between the two traversal patterns.

Listing: Cache-friendly memory accesses.

~~~~ {#lst:CacheFriend .cpp}
// Column-major order                              // Row-major order
for (row = 0; row < NROWS; row++)                  for (row = 0; row < NROWS; row++)
  for (col = 0; col < NCOLS; col++)                  for (col = 0; col < NCOLS; col++)
    matrix[col][row] = row + col;          =>          matrix[row][col] = row + col;
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Column-major versus Row-major traversal.](../../img/memory-access-opts/ColumnRowMajor.png){#fig:ColRowMajor width=60%}

The example presented above is classical, but usually, real-world applications are much more complicated than this. Sometimes you need to go an additional mile to write cache-friendly code. If the data is not laid out in memory in a way that is optimal for the algorithm, it may require to rearrange the data first.

Consider a standard implementation of binary search in a large sorted array, where on each iteration, you access the middle element, compare it with the value you're searching for, and go either left or right. This algorithm does not exploit spatial locality since it tests elements in different locations that are far away from each other and do not share the same cache line. The most famous way of solving this problem is storing elements of the array using the Eytzinger layout [@EytzingerArray]. The idea is to maintain an implicit binary search tree packed into an array using the BFS-like layout, usually seen with binary heaps. If the code performs a large number of binary searches in the array, it may be beneficial to convert it to the Eytzinger layout. 

### Use Appropriate Containers. 

There is a wide variety of ready-to-use containers in almost any language. But it's important to know their underlying storage and performance implications. Keep in mind how the data will be accessed and manipulated. You should consider not only the time and space complexity of operations with a data structure but also the hardware effects associated with them.

By default, stay away from data structures that rely on pointers, e.g. linked lists or trees. When traversing elements, they require additional memory accesses to follow the pointers. If the maximum number of elements is relatively small and known at compile time, C++ `std::array` might be a better option than `std::vector`. If you need an associative container but don't need to store the elements in sorted order, `std::unordered_map` should be faster than `std::map`. A good step-by-step guide for choosing appropriate C++ containers can be found in [@fogOptimizeCpp, Section 9.7 Data structures, and container classes].

Sometimes, it's more efficient to store pointers to contained objects, instead of objects themselves. Consider a situation when you need to store many objects in an array while the size of each object is big. In addition, the objects are frequently shuffled, removed, and inserted. Storing objects in an array will require moving large chunks of memory every time the order of objects is changed, which is expensive. In this case, it's better to store pointers to objects in the array. This way, only the pointers are moved, which is much cheaper. However, this approach has its drawbacks. It requires additional memory for the pointers and introduces an additional level of indirection.

### Packing the Data

The utilization of data caches can be also improved by making data more compact. There are many ways to pack data. One of the classic examples is to use bitfields. An example of code when packing data might be profitable is shown in [@lst:DataPacking]. If we know that `a`, `b`, and `c` represent enum values that take a certain number of bits to encode, we can reduce the storage of the struct `S`.

Listing: Data Packing

~~~~ {#lst:DataPacking .cpp}
// S is 3 bytes                         // S is 1 byte
struct S {                              struct S {
  unsigned char a;                        unsigned char a:4;
  unsigned char b;                =>      unsigned char b:2;
  unsigned char c;                        unsigned char c:2;
};                                      };
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice the three times less space required to store an object of the packed version of `S`. This greatly reduces the amount of memory transferred back and forth and saves cache space. However, using bitfields comes with additional costs.[^15] Since the bits of `a`, `b`, and `c` are packed into a single byte, the compiler needs to perform additional bit manipulation operations to extract and insert them. For example, to load `b`, you need to shift the byte value right (`>>`) by 2 and do logical AND (`&`) with `0x3`. Similarly, shift left (`<<`) and logical OR (`|`) operations are needed to store the updated value back into the packed format. Data packing is beneficial in places where additional computation is cheaper than the delay caused by inefficient memory transfers.

Also, a programmer can reduce memory usage by rearranging fields in a struct or class when it avoids padding added by a compiler. Inserting unused bytes of memory (pads) enables efficient storing and fetching of individual members of a struct. In the example in [@lst:AvoidPadding], the size of `S` can be reduced if its members are declared in the order of decreasing size. Figure @fig:AvoidPadding illustrates the effect of rearranging the fields in struct `S`.

Listing: Avoid compiler padding.

~~~~ {#lst:AvoidPadding .cpp}
// S is `sizeof(int) * 3` bytes          // S is `sizeof(int) * 2` bytes
struct S {                               struct S {
  bool b;                                  int i;
  int i;                         =>        short s;
  short s;                                 bool b;
};                                       };

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Avoid compiler padding by rearranging the fields. Blank cells represent compiler padding.](../../img/memory-access-opts/AvoidPadding.png){#fig:AvoidPadding width=90%}

### Field Reordering

Reordering fields in a data structure can also be beneficial for another reason. Consider an example in [@lst:FieldReordering]. Suppose that the `Soldier` structure is used to track each one of the thousands of units on the battlefield in a game. The game has three phases: battle, movement, and trade. During the battle phase, the `attack`, `defense`, and `health` fields are used. During the movement phase, the `coords`, and `speed` fields are used. During the trade phase, only the `money` field is used.

The problem with the organization of the `Soldier` struct in the code on the left is that the fields are not grouped according to the phases of the game. For example, during the battle phase, the program needs to access two different cache lines to fetch the required fields. The fields `attack` and `defense` are very likely to reside on the same cache line, but the `health` field is always pushed to the next cache line. The same applies to the movement phase (`speed` and `coords` fields).

We can make the `Soldier` struct more cache-friendly by reordering the fields as shown in [@lst:FieldReordering] on the right. With that change, the fields that are accessed together are grouped together.

Listing: Field Reordering.

~~~~ {#lst:FieldReordering .cpp}
struct Soldier {                                 struct Soldier {
  2DCoords coords;   /*  8 bytes */                unsigned attack;  // 1. battle
  unsigned attack;                                 unsigned defense; // 1. battle
  unsigned defense;                     =>         unsigned health;  // 1. battle
  /* other fields */ /* 64 bytes */                2DCoords coords;  // 2. move
  unsigned speed;                                  unsigned speed;   // 2. move
  unsigned money;                                  // other fields
  unsigned health;                                 unsigned money;   // 3. trade
};                                                };
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Linux kernel 6.8, there is a new functionality in the `perf` tool that allows you to find data structure reordering opportunities. The `perf mem record` command can now be used to profile data structure access patterns. The `perf annotate --data-type` command will show you the data structure layout along with profiling samples attributed to each field of the data structure. Using this information you can identify fields that are accessed together.[^5]

Data-type profiling is very effective at finding opportunities to improve cache utilization. Recent Linux kernel history contains many examples of commits that reorder structures,[^1] pad fields,[^3], or pack[^2] them to improve performance.

### Other Data Structure Reorganization Techniques

To close the topic of cache-friendly data structures, we will briefly mention two other techniques that can be used to improve cache utilization: *structure splitting* and *pointer inlining*.

**Structure splitting**. Splitting a large structure into smaller ones can improve cache utilization. For example, if you have a structure that contains a large number of fields, but only a few of them are accessed together, you can split the structure into two or more smaller ones. This way, you can avoid loading unnecessary data into the cache. An example of structure splitting is shown in [@lst:StructureSplitting]. By splitting the `Point` structure into `PointCoords` and `PointInfo`, we can avoid loading the `PointInfo` data into caches when we only need `PointCoords`. This way, we can fit more points on a single cache line.

Listing: Structure Splitting.

~~~~ {#lst:StructureSplitting .cpp}
struct Point {                                struct PointCoords {
  int X;                                        int X;
  int Y;                                        int Y;
  int Z;                                        int Z;
  /*many other fields*/            =>         };
};                                            struct PointInfo {
std::vector<Point> points;                      /*many other fields*/
                                              };
                                              std::vector<PointCoords> pointCoords;
                                              std::vector<PointInfo> pointInfos;
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pointer inlining**. Inlining a pointer into a structure can improve cache utilization. For example, if you have a structure that contains a pointer to another structure, you can inline the pointer into the first structure. This way, you can avoid additional memory access to fetch the second structure. An example of pointer inlining is shown in [@lst:PointerInlining]. The `weight` parameter is used in many graph algorithms, and thus, it is frequently accessed. However, in the original version on the left, retrieving the edge weight requires additional memory access, which can result in a cache miss. By moving the `weight` parameter into the `GraphEdge` structure, we avoid such issues.

Listing: Moving the `weight` parameter into the parent structure.

~~~~ {#lst:PointerInlining .cpp}
struct GraphEdge {                            struct GraphEdge {
  unsigned int from;                            unsigned int from;
  unsigned int to;                              unsigned int to;
  GraphEdgeProperties* prop;                    float weight;
};                                 =>           GraphEdgeProperties* prop;
struct GraphEdgeProperties {                  };
  float weight;                               struct GraphEdgeProperties {
  std::string label;                            std::string label;
  // ...                                        // ...
};                                            };
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[^1]: Linux commit [54ff8ad69c6e93c0767451ae170b41c000e565dd](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=54ff8ad69c6e93c0767451ae170b41c000e565dd)
[^2]: Linux commit [e5598d6ae62626d261b046a2f19347c38681ff51](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e5598d6ae62626d261b046a2f19347c38681ff51)
[^3]: Linux commit [aee79d4e5271cee4ffa89ed830189929a6272eb8](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=aee79d4e5271cee4ffa89ed830189929a6272eb8)

[^5]: Linux `perf` data-type profiling - [https://lwn.net/Articles/955709/](https://lwn.net/Articles/955709/)

[^12]: aligned_alloc - [https://en.cppreference.com/w/c/memory/aligned_alloc](https://en.cppreference.com/w/c/memory/aligned_alloc)
[^13]: Linux manual page for `memalign` - [https://linux.die.net/man/3/memalign](https://linux.die.net/man/3/memalign)
[^14]: Generating aligned memory - [https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/](https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/)
[^15]: Also, you cannot take the address of a bitfield.
