## Core Count Scaling Case Study

Core count scaling is perhaps the most valuable analysis you can perform on a multithreaded application. It shows how well the application can utilize modern multicore systems. As you will see, there is a ton of information you can learn along the way. Without further introduction, let's get started. In this case study, we will analyze the core count scaling of the following benchmarks, some of them should be already familiar to you from the previous chapters:

1. Blender 3.4 - an open-source 3D creation and modeling software project. This test is of Blender's Cycles performance with the BMW27 blend file. URL: [https://download.blender.org/release](https://download.blender.org/release). Command line: `./blender -b bmw27_cpu.blend -noaudio --enable-autoexec -o output.test -x 1 -F JPEG -f 1 -t N`, where `N` is the number of threads.
2. Clang 17 selfbuild - this test uses clang 17 to build clang 17 compiler from sources. URL: [https://www.llvm.org](https://www.llvm.org). Command line: `ninja -jN clang`, where `N` is the number of threads.
3. Zstandard v1.5.5, a fast lossless compression algorithm. URL: [https://github.com/facebook/zstd](https://github.com/facebook/zstd). A dataset used for compression: [http://wanos.co/assets/silesia.tar](http://wanos.co/assets/silesia.tar). Command line: `./zstd -TN -3 -f -- silesia.tar`, where `N` is the number of compression worker threads.
4. CloverLeaf 2018 - a Lagrangian-Eulerian hydrodynamics benchmark. All HW threads are used. This test uses clover_bm.in input file (Problem 5). URL: [http://uk-mac.github.io/CloverLeaf](http://uk-mac.github.io/CloverLeaf). Command line: `export OMP_NUM_THREADS=N; ./clover_leaf`, where `N` is the number of threads.
5. CPython 3.12, a reference implementation of the Python programming language. URL: [https://github.com/python/cpython](https://github.com/python/cpython). A simple multithreaded binary search script, which searches `10'000` random numbers in a sorted list of `1'000'000` elements. Command line: `./python3 binary_search.py N`, where `N` is the number of threads.

The benchmarks were executed on a machine with the configuration shown below:
* 12th Gen Alderlake Intel(R) Core(TM) i7-1260P CPU @ 2.10GHz (4.70GHz Turbo), 4P+8E cores, 18MB L3-cache
* 16 GB RAM, DDR4 @ 2400 MT/s
* Clang 15 compiler with the following options: `-O3 -march=core-avx2`
* 256GB NVMe PCIe M.2 SSD
* 64-bit Ubuntu 22.04.1 LTS (Jammy Jellyfish)

This is clearly not the top-of-the-line hardware setup, but rather a mainstream computer, not necessarily designed to handle media, developer, or HPC workloads. However, for our case study, it is excellent platform to demonstrate the various effects of core count scaling. Because of the limited resources, applications start to hit performance roadblocks even with a small number of threads. Keep in mind, that on better hardware, the scaling results will be different.

Our processor has four P-cores and eight E-cores. P-cores are SMT-enabled, which means the total number of threads on this platform is sixteen. By default, Linux scheduler will first try to use idle physical P-cores. The first four threads will utilize four threads on four idle P-cores. When they are fully utilized, it will start to schedule threads on E-cores. So, the next eight threads will be scheduled on eight E-cores. Finally, the remaining four threads will be scheduled on the 4 sibling SMT threads of P-cores. For our case study, we've also ran the benchmarks while affinitizing threads using the aformentioned scheme, except `Zstd` and `CPython`. Results came out very similar. Running without affinity does a better job of representing real world scenarios, however, thread affinity makes core count scaling analysis more clean, so we present the results when thread affinity is used.

The benchmarks do fixed amount of work. The number of retired instructions is almost identical regardless of the core count.In all of them, the largest portion of an algorithm is implemented using divide-and-conquer paradigm, where work is split into equal parts, and each part can be processed independently. In theory, this allows applications to scale well with the number of cores. However, in practice, the scaling is not perfect. 

Figure @fig:ScalabilityMainChart shows the thread count scalability of the selected benchmarks. The x-axis represents the number of threads, and the y-axis shows the speedup relative to the single-threaded execution. The speedup is calculated as the execution time of the single-threaded execution divided by the execution time of the multi-threaded execution. The higher the speedup, the better the application scales with the number of threads. 

![Thread Count Scalability chart for five selected benchmarks.](../../img/mt-perf/ScalabilityMainChart.png){#fig:ScalabilityMainChart width=100%}

As you can see, most of them are very far from the linear scaling, which is quite disappointing. The benchmark with the best scaling in this case study, Blender, achieves only 6x speedup while using 16x threads. CPython, for examples sees no core count scaling at all. Performance of Clang and Zstd suddenly degrades when the number of threads goes beyond 11. To understand this and other issues, let's dive into the details of each benchmark.

### Blender {.unlisted .unnumbered}

Blender is the only benchmark in our suite that continues to scale up to all 16 threads in the system. The reason for this is that the workload is highly parallelizable. The rendering process is divided into small tiles, and each tile can be rendered independently. However, even with this high level of parallelism, the scaling is only `6.1x speedup / 16 threads = 38%`. What are the reasons for this suboptimal scaling?

From [@sec:PerfMetricsCaseStudy], we know that Blender's performance is bounded by floating point computations. It has relatively high percentage of SIMD instructions as well. P-cores are much better at handling such instructions than E-cores. This is why we see the slope of the speedup curve decrease after 4 threads. After that, scaling continues at the same pace until 12 threads, where it starts to degrade again. This is the effect of using SMT sibling threads. Two active sibling SMT threads compete for the limited number of FP/SIMD execution units. To measure SMT scaling, we need to divide performance of two SMT threads (2T1C - two threads one core) by performance of a single P-core (1T1C), also `4T2C/2T2C`, `6T3C/3T3C`, and so on. For Blender, SMT scaling is around `1.3x` in all configurations. Obviously, this is not a perfect scaling, but still, using sibling SMT threads on P-cores provide performance boost for this workload.

There is another aspect of scaling degradation which we will talk about when discussing Clang's core count scaling.

### Clang {.unlisted .unnumbered}

While Blender uses multithreading to exploit parallelism, concurrency in C++ compilation is usually achieved with multiprocessing. Clang 17 has more than `2'500` translation units, and to compile each of them, a new process is spawned. Similar to Blender, we classify Clang compilation as massively parallel, yet they scale differently. We recommend you to revisit [@sec:PerfMetricsCaseStudy] for an overview of Clang compiler performance bottlenecks. In short, it has a large codebase, flat profile, many small functions, and "branchy" code. Its performance is affected by data cache and TLB misses, and branch mispredictions. It is largely affected by the same scaling issues as Blender: P-cores are more effective than E-cores, and P-core SMT scaling is about `1.1x`. But notice that scaling stops around 10 threads, and starts to degrade. Let's understand why that happens.

The problem is related to the frequency throttling. When multiple cores are utilized simultaneously, the processor generates more heat due to the increased workload on each core. To prevent overheating and maintain stability, CPUs often throttle down their clock speeds depending on how many cores are in use. Additionally, boosting all cores to their maximum turbo frequency simultaneously would require significantly more power, which might exceed the power delivery capabilities of the CPU. Our system doesn't posses advanced liquid cooling solution, and only has a single processor fan.

Figure @fig:FrequencyThrotlingClang shows the CPU frequency throttling on our platform while running Clang. Notice that sustained frequency starts to decline starting from a scenario when two P-cores are used simultaneously. By the time you start using all 16 threads, the frequency of P-cores is throttled down to `3.2GHz`, while E-cores operate at `2.6GHz`. We used Intel Vtune's platform view to visualize CPU frequency as shown in [@sec:IntelVtuneOverview]. 

![Frequency throttling while runnning Clang compilation on Intel(R) Core(TM) i7-1260P.](../../img/mt-perf/FrequencyThrotlingClang.png){#fig:FrequencyThrotlingClang width=100%}

Such frequency chart may be used as a first approximation to understand the throttling that occurs on your platform. However, it cannot be automatically applied to all the workloads. Applications that heavily use SIMD instructions typically operate on lower frequencies, so Blender, for example, may see slightly more frequency throttling than Clang.

To confirm that frequency throttling is one of the main reasons for performance degradation, we temporarily disabled Turbo Boost on our platform and redo the scaling study. When Turbo Boost is disabled, all cores operate on their base frequencies, which are `2.1Ghz` for P-cores and `1.5Ghz` for E-cores. The results are shown in Figure @fig:ScalabilityNoTurboChart. As you can see, thread count scaling almost doubles when and 16 threads are used and TurboBoost is disabled, for both Blender (`38%->69%`) and Clang (`21%->41%`). It gives us an intuition of what the thread count scaling would look like if frequency throttling would not exist. In fact, frequency throttling accounts for a large portion of nonrealized performance scaling in modern systems.

![Thread Count Scalability chart for Blender and Clang with disabled Turbo Boost. Frequency throttling is a major roadblock to achieve good thread count scaling.](../../img/mt-perf/ScalabilityNoTurboChart.png){#fig:ScalabilityNoTurboChart width=100%}

Going back to the main chart shown in Figure fig:ScalabilityMainChart, for the Clang workload, the tipping point of performance scaling is around 10 threads. This is the point where the frequency throttling starts to have a significant impact on performance. The benefit of adding additional threads is smaller than the penalty of running at a lower frequency.

### Zstandard {.unlisted .unnumbered}

The next on our list is Zstandard compression algorithm, or Zstd for short. When compressing data, Zstd divides the input into blocks, and each block can be compressed independently. This means that multiple threads can work on compressing different blocks simultaneously. However, as you will see, the dynamic interaction between Zstd worker threads is quite complicated.

First of all, performance of Zstd depends on the compression level. The higher the compression level, the more compact the result. Lower compression levels provide faster compression, while higher levels yield better compression ratios. In our case study, we used compression level 3, which is the default level since it provides a good trade-off between speed and compression ratio.

Here is the high level algorithm of Zstd compression:[^1]
* Input file is divided into a number of blocks, which size depends on the compression level. Each job is responsible for compressing a block of data. When Zstd receives some data to compress, it copies a small chunk into one of its internal buffers and posts a new compression job, which is picked up by one of the worker threads. The main thread fills all input buffers for all its workers and send them to work in order.
* Jobs are always started in order, but they can finish in any order. Compression speed can be variable, and depends on the data to compress. Some blocks are easier to compress than others.
* After a worker finishes compressing a block, it signals the main thread that the compressed data is ready to be flushed to the output file. The main thread is responsible for flushing the compressed data to the output file. Note that flushing must be done in order, which means that the second job is allowed to be flushed only after the first one is entirely flushed. The main thread can "partially flush" an ongoing job, i.e., it doesn't have to wait for a job to be completely finished before starting to flush it.

To visualize the work of Zstd algorithm on a timeline, we instrumented the Zstd source code with Vtune's ITT markers.[^2] The timeline of compressing Silesia corpus using 8 threads is shown in Figure @fig:ZstdTimeline. Using 8 worker threads is enough to observe thread interaction in Zstd while keeping the image less noisy than all 16 threads. The second half of the timeline was cut to make the image fit on the page.

[TODO]: prepare grayscale version of the image
[TODO]: cut the second half of the image if I don't talk much about it

![Timeline view of compressing Silesia corpus with Zstandard using 8 threads.](../../img/mt-perf/ZstdTimelineCut.png){#fig:ZstdTimeline width=100%}

On the image, we have the main thread at the bottom (PID 913273), and eight worker threads at the top. The worker threads are created at the beginning of the compression process and are reused for multiple compressing jobs. 

On the worker thread timeline (top 8 rows) we have the following markers:
* 'job0' - 'job25' bars indicate start and end of a job.
* 'ww' (short for "worker wait") bars indicate a period when a worker thread is waiting for a new job.
* Notches below job periods indicate that a thread has just finished compressing a portion of the input block and is signaling to the main thread that the data is available to be partially flushed.

On the main thread timeline (row 9, TID 913273) we have the following markers:
* 'p0' - 'p25' boxes indicate a period of preparing a new job. It starts when the main thread starts filling up the input buffer until it is full (but this new job is not necessarily posted on the worker queue immediately).
* 'fw' (short for "flush wait") markers indicate a period when the main thread waits for the produced data to start flushing it. During this time, the main thread is blocked.

With a quick glance at the image, we could tell that there are many `ww` periods, when worker threads are waiting. Let's progress throught the timeline and try to understand what's going on.

1. First, when worker threads are created, there is no work to do, so they are waiting for the main thread to post a new job. 
2. Then the main thread starts to fill up the input buffers for the worker threads. It has prepared jobs 0 to 7 (see bars `p0` - `p7`), which were picked up by worker threads immediately. Notice, the main thread also prepared job8 (`p8`), but it didn't posted it in the worker queue yet. This is because all workers are still busy.
3. After the main thread has finished `p8`, it flushed the data already produced by `job0`. Notice, that by this time, `job0` has already delivered five portions of compressed data (first five notches below `job0` bar). Now, the main thread enters its first `fw` period, and start to wait for more data from `job0`.
4. At the timestamp `45ms`, one more chunck of compressed data is produced by `job0`, and the main thread briefly wakes up to flush it, see \circled{1}. After that it goes to sleep again.
5. `Job3` is the first to finish, but there is a couple of milliseconds delay before TID 913309 picks up the new job, see \circled{2}. This happens because `job8` was not posted in the queue by the main thread. Luckily, the new portion of compressed data comes from `job0`, so the main thread wakes up, flushes it and notices that there are idle worker threads. So, it posts `job8` to the worker queue, and starts preparing the next job (`p9`).
6. The same thing happens with TID 913313 (see \circled{3}) and TID 913314 (see \circled{4}). But this time the delay is bigger. Interestingly, `job10` could have been picked up by either TID 913314 or TID 913312 since they were both idle the time `job10` was pushed to the job queue.
7. We should have expected that the main thread would start preparing `job11` immediately after `job10` was posted in the queue as it did before. But it didn't. This happens because there are no available input buffers. We will discuss it in more detail shortly.
8. Only when `job0` finishes, the main thread was able to aquire a new input buffer and start preparing `job11` (see  \circled{5}). 

As we just said, the reason for the 20-40ms delays between jobs is lack of input buffers, which are required to start preparing a new job. Zstd maintains a single memory pool, which allocates space for both input and output buffers. This memory pool is prone to fragmentation issues, as it has to provide contiguos blocks of memory. When a worker finished a job, the output buffer is waiting to be flushed, but it still occupies memory. And to start working on another job, it will require another pair of buffers. 

Limiting the capacity of the memory pool is a design decision to reduce memory consumption. In the worst case, there could be many "run-away" buffers, left by workers that have completed their jobs very fast, and move on to process the next job; meanwhile the flush queue is still blocked by one slow job. In such a scenario, the memory consumption would be very high, which is undesirable. However, the downside here is increased wait time between the jobs.

The Zstd algorithm is a good example of a complex interaction between threads. It is a good reminder that even if you have a parallelizable workload, performance of your application can be limited by the synchronization between threads and available resources.

### CloverLeaf {.unlisted .unnumbered}

  remeasure 9t - there was a bug in the script.
  [DONE] redo full scalability study with affinity
  [DONE] do HT scalability study
  [DONE] check profile 1T vs. 2T vs. 4T vs. 16T - prove that mem BW is saturated.
  Describe experiments with better memory speed.
  Why there is a drop from 4T -> 5T ? Are E-cores are slow or this is a beginning of thermal issue.

Interestingly, for CloverLeaf, TurboBoost doesn't provide any performance benefit when all 16 threads are used. That means that performance is the same regardless you enable Turbo or let the cores run on their base frequency. How is that possible? The reason is that having 16 active threads is enough to saturate two memory controllers. Since most of the time threads are just waiting for data, when you disable Turbo, they simply start to wait "slower". This is why performance is the same regardless of the frequency.

### CPython {.unlisted .unnumbered}

[TODO]:
Check clang SMT speedup on a single core.
[DONE] Build a frequency chart
[DONE] I see perf drop with many cores -- probably because the CPU cannot sustain frequency. Redo scaling studies with Turbo turned off. 
[DONE] Redo scaling studies with affinity - otherwise instructions on E-cores look very suspicious. And just to ensure no migration.
[TODO]: Find a candidate with almost perfect scaling. - maybe hard to do due to thermal issue on my platform.

https://realpython.com/python-parallel-processing/#use-an-alternative-runtime-environment-for-python

[^1]: Huge thanks to Yann Collet, the author of Zstd, for providing us with the information about the internal workings of Zstd. [TODO]: move to the acknowledgements section.
[^2]: VTune ITT instrumentation - [https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-1/instrumenting-your-application.html](https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-1/instrumenting-your-application.html)