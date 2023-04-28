## Questions and Exercises {.unlisted .unnumbered}

1. Solve the following lab assignments using techniques we discussed in this chapter:
- `perf-ninja::function_inlining_1` 
- `perf-ninja::vectorization` 1 & 2
- `perf-ninja::dep_chains_1`
- `perf-ninja::compiler_intrinsics` 1 & 2
- `perf-ninja::loop_interchange` 1 & 2
- `perf-ninja::loop_tiling_1`
2. Describe the steps you will take to find out if an application is using all the opportunities for utilizing SIMD code?
3. Practice doing loop optimizations manually on a real code (but don't commit it). Make sure that all the tests are still passing.
4. You're working on an application that has very low IpCall (instructions per call) metric. What optimizations you will try to apply/force?