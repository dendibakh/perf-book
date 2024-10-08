## Replace Branches with Lookup

One way to avoid frequently mispredicted branches is to use lookup tables. An example of code when such transformation might be profitable is shown in [@lst:LookupBranches]. As usual, the original version is on the left while the improved version is on the right. Function `mapToBucket` maps values in the `[0-50)` range into corresponding five buckets, and returns `-1` for values that are out of this range. For uniformly distributed values of `v`, we will have an equal probability for `v` to fall into any of the buckets. In the generated assembly for the original version, we will likely see many branches, which could have high misprediction rates. Hopefully, it's possible to rewrite the function `mapToBucket` using a single array lookup, as shown on the right.

Listing: Replacing branches with lookup tables.

~~~~ {#lst:LookupBranches .cpp}
int8_t mapToBucket(unsigned v) {       int8_t buckets[50] = {
  if      (v < 10) return 0;             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  else if (v < 20) return 1;             1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  else if (v < 30) return 2;      =>     2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  else if (v < 40) return 3;             3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
  else if (v < 50) return 4;             4, 4, 4, 4, 4, 4, 4, 4, 4, 4 };
  return -1;
}                                      int8_t mapToBucket(unsigned v) {
                                         if (v < (sizeof(buckets) / sizeof(int8_t)))
                                           return buckets[v];
                                         return -1;
                                       }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the improved version of `mapToBucket` on the right, a compiler will likely generate a single branch instruction that guards against out-of-bounds access to the `buckets` array. A typical hot path through this function will execute the untaken branch and one load instruction. The branch will be well-predicted by the CPU branch predictor since we expect most of the input values to fall into the range covered by the `buckets` array. The lookup will also be fast since the `buckets` array is small and likely to be in the L1 D-cache.

If we need to map a bigger range of values, say `[0-1M)`, allocating a very large array is not practical. In this case, we might use interval map data structures that accomplish that goal using much less memory but logarithmic lookup complexity. Readers can find existing implementations of interval map container in [Boost](https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html)[^2] and [LLVM](https://llvm.org/doxygen/IntervalMap_8h_source.html)[^3].

[^2]: C++ Boost `interval_map` - [https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html](https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html)
[^3]: LLVM's `IntervalMap` - [https://llvm.org/doxygen/IntervalMap_8h_source.html](https://llvm.org/doxygen/IntervalMap_8h_source.html)
