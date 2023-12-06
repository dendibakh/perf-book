#### Summary {.unlisted .unnumbered}

TMA is great for identifying CPU performance bottlenecks in code. Ideally, when we run it on an application, we would like to see the Retiring metric at 100%.  This would mean that this application fully saturates the CPU. It is possible to achieve results close to this on a toy program. However, real-world applications are far from getting there. Figure @fig:TMA_metrics_SPEC2006 shows top-level TMA metrics for [SPEC CPU2006](http://spec.org/cpu2006/)[^13] benchmark for Skylake CPU generation. Keep in mind that the numbers are likely to change for other CPU generations as architects constantly try to improve the CPU design. The numbers are also likely to change for other instruction set architectures (ISA) and compiler versions.

![Top Level TMA metrics for SPEC CPU2006. *© Image by Ahmad Yasin, [http://cs.haifa.ac.il/~yosi/PARC/yasin.pdf](http://cs.haifa.ac.il/~yosi/PARC/yasin.pdf).*](../../img/pmu-features/TMAM_metrics_SPEC2006.png){#fig:TMA_metrics_SPEC2006 width=90%}

Using TMA on a code that has major performance flaws is not recommended because it will likely steer you in the wrong direction, and instead of fixing real high-level performance problems, you will be tuning bad code, which is just a waste of time. Similarly, make sure the environment doesn’t get in the way of profiling. For example, if you drop filesystem cache and run the benchmark under TMA, it will likely show that your application is Memory Bound, which in fact, may be false when filesystem cache is warmed up.

Workload characterization provided by TMA can increase the scope of potential optimizations beyond source code. For example, if an application is memory bound and all possible ways to speed it up on the software level have been exhausted, it may be possible to improve performance by upgrading the memory subsystem with faster memory chips. This illustrates how using TMA to diagnose performance bottlenecks can ensure you do not prematurely spend money on upgrading hardware.

At the time of this writing, the first level of TMA metrics is also available on AMD processors.

[^13]: SPEC CPU 2006 - [http://spec.org/cpu2006/](http://spec.org/cpu2006/).