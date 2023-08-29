---
typora-root-url: ..\..\img
---

## Static Performance Analysis

[TODO] introduce UICA, show example of finding dependency chains using it

Today we have extensive tooling for static code analysis. For C and C++ languages we have such well known tools like [Clang Static Analyzer](https://clang-analyzer.llvm.org/), [Klocwork](https://www.perforce.com/products/klocwork), [Cppcheck](http://cppcheck.sourceforge.net/) and others[^1]. They aim at checking the correctness and semantics of the code. Likewise, there are tools that try to address the performance aspect of the code. Static performance analyzers don't run the actual code. Instead, they simulate the code as if it is executed on a real HW. Statically predicting performance is almost impossible, so there are many limitations to this type of analysis.

First, it is not possible to statically analyze C/C++ code for performance since we don't know the machine code to which it will be compiled. So, static performance analysis works on assembly code.

Second, static analysis tools simulate the workload instead of executing it. It is obviously very slow, so it's not possible to statically analyze the entire program. Instead, tools take some assembly code snippet and try to predict how it will behave on real hardware. The user should pick specific assembly instructions (usually small loop) for analysis. So, the scope of static performance analysis is very narrow.

The output of the static analyzers is fairly low-level and sometimes breaks execution down to CPU cycles. Usually, developers use it for fine-grained tuning of the critical code region where every cycle matter.

### Static vs. Dynamic Analyzers

**Static tools** don't run the actual code but try to simulate the execution, keeping as many microarchitectural details as they can. They are not capable of doing real measurements (execution time, performance counters) because they don't run the code. The upside here is that you don't need to have the real HW and can simulate the code for different CPU generations. Another benefit is that you don't need to worry about consistency of the results: static analyzers will always give you stable output because simulation (in comparison with the execution on real hardware) is not biased in any way. The downside of static tools is that they usually can't predict and simulate everything inside a modern CPU: they are based on some model that may have bugs and limitations in it. Examples of static performance analyzers are [IACA](https://software.intel.com/en-us/articles/intel-architecture-code-analyzer)[^2] and [llvm-mca](https://llvm.org/docs/CommandGuide/llvm-mca.html)[^3].

**Dynamic tools** are based on running the code on the real HW and collecting all sorts of information about the execution. This is the only 100% reliable method of proving any performance hypothesis. As a downside, usually, you are required to have privileged access rights to collect low-level performance data like PMCs. It's not always easy to write a good benchmark and measure what you want to measure. Finally, you need to filter the noise and different kinds of side effects. Examples of dynamic performance analyzers are Linux perf, [likwid](https://github.com/RRZE-HPC/likwid)[^5]and [uarch-bench](https://github.com/travisdowns/uarch-bench)[^4]. Examples of usage and output for the tools mentioned above can be found on [easyperf blog](https://easyperf.net/blog/2018/04/03/Tools-for-microarchitectural-benchmarking) [^6].

A big collection of tools both for static and dynamic microarchitectural performance analysis is available [here](https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture)[^7].

\personal{I use those tools whenever I need to explore some interesting CPU microarchitecture effect. Static and low-level dynamic analyzers (like likwid and uarch-bench) allow us to observe HW effects in practice while doing performance experiments. They are a great help for building up your mental model of how CPU works.}

[^1]: Tools for static code analysis - [https://en.wikipedia.org/wiki/List_of_tools_for_static_code_analysis#C,_C++](https://en.wikipedia.org/wiki/List_of_tools_for_static_code_analysis#C,_C++).
[^2]: IACA - [https://software.intel.com/en-us/articles/intel-architecture-code-analyzer](https://software.intel.com/en-us/articles/intel-architecture-code-analyzer). In April 2019, the tools has reached its End Of Life and is no longer supported.
[^3]: LLVM MCA - [https://llvm.org/docs/CommandGuide/llvm-mca.html](https://llvm.org/docs/CommandGuide/llvm-mca.html)
[^4]: Uarch bench - [https://github.com/travisdowns/uarch-bench](https://github.com/travisdowns/uarch-bench)
[^5]: LIKWID - [https://github.com/RRZE-HPC/likwid](https://github.com/RRZE-HPC/likwid)
[^6]: An article about tools for microarchitectural benchmarking - [https://easyperf.net/blog/2018/04/03/Tools-for-microarchitectural-benchmarking](https://easyperf.net/blog/2018/04/03/Tools-for-microarchitectural-benchmarking)
[^7]: Collection of links for C++ performance tools - [https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture](https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture).
