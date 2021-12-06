---
typora-root-url: ..\..\img
---

## Analysis with Coz {#sec:COZ}

In [@sec:secAmdahl], we defined the challenge of identifying parts of code that affects the overall performance of a multithreaded program. Due to various reasons, optimizing one part of a multithreaded program might not always give visible results. [Coz](https://github.com/plasma-umass/coz)[^16] is a new kind of profiler that addresses this problem and fills the gaps left behind by traditional software profilers. It uses a novel technique called “causal profiling”, whereby experiments are conducted during the runtime of an application by virtually speeding up segments of code to predict the overall effect of certain optimizations. It accomplishes these “virtual speedups” by inserting pauses that slow down all other concurrently running code. [@CozPaper]

Example of applying Coz profiler to [C-Ray](https://openbenchmarking.org/test/pts/c-ray) benchmark from [Phoronix test suite](https://www.phoronix-test-suite.com/) is shown on @fig:CozProfile. According to the chart, if we improve the performance of line 540 in c-ray-mt.c by 20%, Coz expects a corresponding increase in application performance of C-Ray benchmark overall of about 17%. Once we reach ~45% improvement on that line, the impact on the application begins to level off by COZ’s estimation. For more details on this example, see the [article](https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers)[^17] on easyperf blog.

![Coz profile for [C-Ray](https://openbenchmarking.org/test/pts/c-ray) benchmark.](/5/CozProfile.png){#fig:CozProfile width=70%}

[^16]: COZ source code - [https://github.com/plasma-umass/coz](https://github.com/plasma-umass/coz).
[^17]: Blog article "COZ vs Sampling Profilers" - [https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers](https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers).
