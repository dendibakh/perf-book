---
typora-root-url: ..\..\img
---

I STOPPED HERE

## Static Performance Analysis

Today we have extensive tooling for static code analysis. For C and C++ languages we have such well known tools like [Clang Static Analyzer](https://clang-analyzer.llvm.org/), [Klocwork](https://www.perforce.com/products/klocwork), [Cppcheck](http://cppcheck.sourceforge.net/) and others. They aim at checking the correctness and semantics of the code. Likewise, there are tools that try to address the performance aspect of code. Static performance analyzers don't execute or profile the program. Instead, they simulate the code as if it is executed on a real HW. Statically predicting performance is almost impossible, so there are many limitations to this type of analysis.

First, it is not possible to statically analyze C/C++ code for performance since we don't know the machine code to which it will be compiled. So, static performance analysis works on assembly code.

Second, static analysis tools simulate the workload instead of executing it. It is obviously very slow, so it's not possible to statically analyze the entire program. Instead, tools take some small assembly code snippet and try to predict how it will behave on real hardware. The user should pick specific assembly instructions (usually small loop) for analysis. So, the scope of static performance analysis is very narrow.

The output of static performance analyzers is fairly low-level and sometimes breaks execution down to CPU cycles. Usually, developers use it for fine-grained tuning of the critical code region where every cycle matters.

[TODO]: emphasize that you would rather use those tools for microarchitectural analysis
[TODO]: add uica.uops.info
[TODO]: introduce UICA 
[TODO]: UICA: example of finding dependency chains
[TODO]: UICA: example of perfect scheduling with FMAs

\personal{I use those tools whenever I need to explore some interesting CPU microarchitecture effect. Static and low-level dynamic analyzers (like likwid and uarch-bench) allow us to observe HW effects in practice while doing performance experiments. They are a great help for building up your mental model of how CPU works.}

### Static vs. Dynamic Analyzers {.unlisted .unnumbered}

**Static tools** don't run the actual code but try to simulate the execution, keeping as many microarchitectural details as they can. They are not capable of doing real measurements (execution time, performance counters) because they don't run the code. The upside here is that you don't need to have the real HW and can simulate the code for different CPU generations. Another benefit is that you don't need to worry about consistency of the results: static analyzers will always give you deterministic output because simulation (in comparison with the execution on real hardware) is not biased in any way. The downside of static tools is that they usually can't predict and simulate everything inside a modern CPU: they are based on some model that may have bugs and limitations. Examples of static performance analyzers are [UICA](https://uica.uops.info/)[^2] and [llvm-mca](https://llvm.org/docs/CommandGuide/llvm-mca.html)[^3].

**Dynamic tools** are based on running the code on the real HW and collecting all sorts of information about the execution. This is the only 100% reliable method of proving any performance hypothesis. As a downside, usually, you are required to have privileged access rights to collect low-level performance data like PMCs. It's not always easy to write a good benchmark and measure what you want to measure. Finally, you need to filter the noise and different kinds of side effects. Examples of dynamic microarchitectural performance analyzers are [nanoBench](https://github.com/andreas-abel/nanoBench)[^5], [uarch-bench](https://github.com/travisdowns/uarch-bench)[^4] and a few others. 

A bigger collection of tools both for static and dynamic microarchitectural performance analysis is available [here](https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture)[^7].

[^2]: UICA - [https://uica.uops.info/](https://uica.uops.info/)
[^3]: LLVM MCA - [https://llvm.org/docs/CommandGuide/llvm-mca.html](https://llvm.org/docs/CommandGuide/llvm-mca.html)
[^4]: uarch-bench - [https://github.com/travisdowns/uarch-bench](https://github.com/travisdowns/uarch-bench)
[^5]: nanoBench - [https://github.com/andreas-abel/nanoBench](https://github.com/andreas-abel/nanoBench)
[^7]: Collection of links for C++ performance tools - [https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture](https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture).
