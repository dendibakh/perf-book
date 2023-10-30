---
typora-root-url: ..\..\img
---

## Replace Branches with Lookup

Frequently branches can be avoided by using lookup tables. An example of code when such transformation might be profitable is shown in [@lst:LookupBranches1]. Function `mapToBucket` maps values into corresponding buckets. For uniformly distributed values of `v`, we will have an equal probability for `v` to fall into any of the buckets. In the generated assembly for the baseline version, we will likely see many branches, which could have high misprediction rates. Hopefully, it's possible to rewrite the function `mapToBucket` using a single array lookup, as shown in [@lst:LookupBranches2].

Listing: Replacing branches: baseline version.

~~~~ {#lst:LookupBranches1 .cpp}
int mapToBucket(unsigned v) {
  if (v >= 0  && v < 10) return 0;
  if (v >= 10 && v < 20) return 1;
  if (v >= 20 && v < 30) return 2;
  if (v >= 30 && v < 40) return 3;
  if (v >= 40 && v < 50) return 4;
  return -1;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing: Replacing branches: lookup version.

~~~~ {#lst:LookupBranches2 .cpp}
int buckets[256] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    ... };

int mapToBucket(unsigned v) {
  if (v < (sizeof (buckets) / sizeof (int)))
    return buckets[v];
  return -1;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The assembly code of the `mapToBucket` function from [@lst:LookupBranches2] should be using only one branch instead of many. A typical hot path through this function will execute the untaken branch and one load instruction. Since we expect most of the input values to fall into the range covered by the `buckets` array, the branch that guards out-of-bounds access will be well-predicted by CPU. Also, the `buckets` array is relatively small, so we can expect it to reside in CPU caches, which should allow for fast accesses to it.[@LemireBranchless]

If we have a need to map a bigger range of values, allocating a very large array is not practical. In this case, we might use interval map data structures that accomplish that goal using much less memory but logarithmic lookup complexity. Readers can find existing implementations of interval map container in [Boost](https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html)[^2] and [LLVM](https://llvm.org/doxygen/IntervalMap_8h_source.html) [^3].

[^2]: C++ Boost `interval_map` - [https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html](https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html)
[^3]: LLVM's `IntervalMap` - [https://llvm.org/doxygen/IntervalMap_8h_source.html](https://llvm.org/doxygen/IntervalMap_8h_source.html)
