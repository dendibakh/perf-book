### TMA Summary

TMA is great for identifying CPU performance bottlenecks. Ideally, when we run it on an application, we would like to see the Retiring metric at 100%. This would mean that this application fully saturates the CPU. It is possible to achieve results close to this on a toy program. However, real-world applications are far from getting there. 

Figure @fig:TMA_google shows top-level TMA metrics for Google's datacenter workloads along with several [SPEC CPU2006](http://spec.org/cpu2006/)[^13] benchmarks running on Intel's IvyBridge server processors. We can see that that most datacenter workloads have very small fraction in the `Retiring` bucket. This implies that most datacenter workloads spend time stalled on various bottlenecks. `BackendBound` is the primary source of performance issues. `FrontendBound` category represents a bigger problem for datacenter workloads than in SPEC2006 due to the fact that those applications typically have large codebases. Finally, some workloads suffer from branch mispredictions more than others, e.g. `search2` and `445.gobmk`.

![TMA breakdown of Google's datacenter workloads along with several SPEC CPU2006 benchmarks, *© Image from [@GoogleProfiling]*](../../img/pmu-features/TMA_google.jpg){#fig:TMA_google width=80%}

Keep in mind that the numbers are likely to change for other CPU generations as architects constantly try to improve the CPU design. The numbers are also likely to change for other instruction set architectures (ISA) and compiler versions.

A few final thoughts before we move on... Using TMA on a code that has major performance flaws is not recommended because it will likely steer you in the wrong direction, and instead of fixing real high-level performance problems, you will be tuning bad code, which is just a waste of time. Similarly, make sure the environment doesn’t get in the way of profiling. For example, if you drop filesystem cache and run the benchmark under TMA, it will likely show that your application is Memory Bound, which in fact, may be false when filesystem cache is warmed up.

Workload characterization provided by TMA can increase the scope of potential optimizations beyond source code. For example, if an application is bound by memory bandwidth and all possible ways to speed it up on the software level have been exhausted, it may be possible to improve performance by upgrading the memory subsystem with faster memory chips. This illustrates how using TMA to diagnose performance bottlenecks can support your decision to spend money on a new hardware.

[^13]: SPEC CPU 2006 - [http://spec.org/cpu2006/](http://spec.org/cpu2006/).