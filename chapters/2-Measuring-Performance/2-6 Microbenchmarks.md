---
typora-root-url: ..\..\img
---

## Microbenchmarks

Microbenchmarks are small self-contained programs that people write to quickly test a hypothesis. Usually, microbenchmarks are used to choose the best implementation of a certain relatively small algorithm or functionality. Nearly all modern languages have benchmarking frameworks. In C++, one can use the Google [benchmark](https://github.com/google/benchmark)[^3] library, C# has [BenchmarkDotNet](https://github.com/dotnet/BenchmarkDotNet)[^4] library, Julia has the [BenchmarkTools](https://github.com/JuliaCI/BenchmarkTools.jl)[^5] package, Java has [JMH](http://openjdk.java.net/projects/code-tools/jmh/etc)[^6] (Java Microbenchmark Harness), etc.

When writing microbenchmarks, it's very important to ensure that the scenario you want to test is actually executed by your microbenchmark at runtime. Optimizing compilers can eliminate important code that could render the experiment useless, or even worse, drive you to the wrong conclusion. In the example below, modern compilers are likely to eliminate the whole loop:

```cpp
// foo DOES NOT benchmark string creation
void foo() {
  for (int i = 0; i < 1000; i++)
    std::string s("hi");
}
```

A simple way to test this is to check the performance profile of the benchmark and see if the intended code stands out as the hotspot. Sometimes abnormal timings can be spotted instantly, so use common sense while analyzing and comparing benchmark runs. One of the popular ways to keep the compiler from optimizing away important code is to use [`DoNotOptimize`](https://github.com/google/benchmark/blob/c078337494086f9372a46b4ed31a3ae7b3f1a6a2/include/benchmark/benchmark.h#L307)-like[^7] helper functions, which do the necessary inline assembly magic under the hood:

```cpp
// foo benchmarks string creation
void foo() {
  for (int i = 0; i < 1000; i++) {
    std::string s("hi");
    DoNotOptimize(s);
  }
}
```

If written well, microbenchmarks can be a good source of performance data. They are often used for comparing the performance of different implementations of a critical function. What defines a good benchmark is whether it tests performance in realistic conditions in which functionality will be used. If a benchmark uses synthetic input that is different from what will be given in practice, then the benchmark will likely mislead you and will drive you to the wrong conclusions. Besides that, when a benchmark runs on a system free from other demanding processes, it has all resources available to it, including DRAM and cache space. Such a benchmark will likely champion the faster version of the function even if it consumes more memory than the other version. However, the outcome can be the opposite if there are neighbor processes that consume a significant part of DRAM, which causes memory regions that belong to the benchmark process to be swapped to the disk. 

For the same reason, be careful when concluding results obtained from unit-testing a function. Modern unit-testing frameworks, e.g. GoogleTest, provide the duration of each test. However, this information cannot substitute a carefully written benchmark that tests the function in practical conditions using realistic input (see more in [@fogOptimizeCpp, chapter 16.2]). It is not always possible to replicate the exact input and environment as it will be in practice, but it is something developers should take into account when writing a good benchmark.

[^3]: Google benchmark library - [https://github.com/google/benchmark](https://github.com/google/benchmark)
[^4]: BenchmarkDotNet - [https://github.com/dotnet/BenchmarkDotNet](https://github.com/dotnet/BenchmarkDotNet)
[^5]: Julia BenchmarkTools - [https://github.com/JuliaCI/BenchmarkTools.jl](https://github.com/JuliaCI/BenchmarkTools.jl)
[^6]: Java Microbenchmark Harness - [http://openjdk.java.net/projects/code-tools/jmh/etc](http://openjdk.java.net/projects/code-tools/jmh/etc)
[^7]: For JMH, this is known as the `Blackhole.consume()`.