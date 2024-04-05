## Core Count Scaling Case Study

[TODO:] redo the scaling study

Figure @fig:MT_Scaling shows performance scaling of the `h264dec` benchmark from [Starbench parallel benchmark suite](https://www.aes.tu-berlin.de/menue/research/projects/completed_projects/starbench_parallel_benchmark_suite/). I tested it on Intel Core i5-8259U, which has 4 cores/8 threads. Notice that after using 4 threads, performance doesn't scale much. Likely, getting a CPU with more cores won't improve performance. [^7]

<div id="fig:MT_charts">
![Performance scaling with different number of threads.](../../img/mt-perf/scaling.png){#fig:MT_Scaling width=45%}
![Overhead of using different number of threads.](../../img/mt-perf/cycles.png){#fig:MT_cycles width=45%}

Performance scaling and overhead of h264dec benchmark on Intel Core i5-8259U.
</div>