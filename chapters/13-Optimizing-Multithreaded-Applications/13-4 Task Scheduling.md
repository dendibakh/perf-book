## Task Scheduling

With the emergence of hybrid processors, task scheduling becomes very challenging. For example, recent Intel's Meteor Lake chips have three types of cores; all with different performance characteristics. As you will see in this section, it is very easy to pessimize the performance of a multithreaded application by using a suboptimal scheduling policy. Implementing a generic task scheduling policy is tricky because it greatly depends on the nature of the running tasks. Here are some examples:

* Compute-intensive lightly-threaded workloads (e.g., data compression) must be served only on P-cores.
* Background tasks (e.g., video calls) could be run on E-cores to save power.
* For bursty applications that demand high responsiveness (e.g., productivity software), a system should only use P-cores.
* Multithreaded programs with sustained performance demand (e.g., video rendering) should utilize both P- and E-cores.

For the most part, task schedulers in modern operating systems take care of these and many other corner cases. For example, Intel's Thread Director helps monitor and analyze performance data in real time to seamlessly place the right application thread on the right core. The general recommendation here is to let the OS do its job and not restrict it too much. The operating system knows how to schedule tasks to minimize contention,  maximize reuse of data in caches, and ultimately maximize performance. This will play a big role if you are developing cross-platform software that is intended to run on different hardware configurations.

Below I show a few typical pitfalls of task scheduling in asymmetric systems. I took the same system I used in the previous case study: 12th Gen Alderlake Intel(R) Core(TM) i7-1260P CPU, which has four P-cores and eight E-cores. For simplicity, I only enabled two P-cores and two E-cores; the rest of the cores were temporarily disabled. I also disabled SMT sibling threads on the two active P-cores. I wrote a simple OpenMP application, where each worker thread runs several bit manipulation operations on every 32-bit integer element of a large array. After a worker thread has finished processing, it hits a barrier and is forced to wait for other threads to finish their parts. After that, the main thread cleans up the array and the processing repeats. The program was compiled with GCC 13.2 and `-O3 -march=core-avx2`, which enables vectorization.

Figure @fig:OmpScheduling shows three strategies, which highlight common problems that we regularly see in practice. These screenshots were captured with Intel VTune. The bars on the timeline indicate CPU time, i.e., periods when a thread was running. For each software thread, there is one or two corresponding CPU cores. Using this view, we can see on which core each thread was running at any given time.

\begin{figure}[htbp]
\centering

\subfloat[Static partitioning with pinning threads to the cores:
\passthrough{\lstinline!\#pragma omp for schedule(static)!} with
\passthrough{\lstinline!OMP\_PROC\_BIND=true!}.]{\includegraphics[width=0.8\textwidth,height=\textheight]{../../img/mt-perf/OmpAffinity.png}\label{fig:OmpAffinity}}

\subfloat[Static partitioning, no thread affinity:
\passthrough{\lstinline!\#pragma omp for schedule(static)!}.]{\includegraphics[width=0.8\textwidth,height=\textheight]{../../img/mt-perf/OmpStatic.png}\label{fig:OmpStatic}}

\subfloat[Dynamic partitioning with 16 chunks:
\passthrough{\lstinline!\#pragma omp for schedule(dynamic, N/16)!}.]{\includegraphics[width=0.8\textwidth,height=\textheight]{../../img/mt-perf/OmpDynamic.png}\label{fig:OmpDynamic}}

\caption{Typical task scheduling pitfalls: core affinity blocks thread
migration, partitioning jobs with large granularity fails to maximize
CPU utilization.}

\label{fig:OmpScheduling}

\end{figure}

Our first example uses static partitioning, which divides the processing of our large array into four equal chunks (since we have four cores enabled). For each chunk, the OpenMP runtime will spawn a new thread. Also, we used `OMP_PROC_BIND=true`, which instructs OpenMP runtime to pin spawned threads to the CPU cores. Figure @fig:OmpAffinity demonstrates the effect: P-cores are much better at handling SIMD instructions than E-cores and they finish their jobs two times faster (see *Thread 1* and *Thread 2*). However, thread affinity does not allow *Thread 3* and *Thread 4* to migrate to P-cores, which are waiting at the barrier. That results in a high latency, which is limited by the speed of E-cores.

Our recommendation is to avoid pinning threads to cores. With unbalanced work, pinning might restrict the work stealing, leaving the long execution tail for E-cores. On macOS, it is not possible to pin threads to cores since the OS does not provide an API for that.

In the second example, we don't pin threads anymore, but the partitioning scheme remains the same. Figure @fig:OmpStatic illustrates the effect of this change. As in the previous scenario, *Thread 1* and *Thread 4* finished their jobs early, because they were using P-cores. *Thread 2* and *Thread 3* started running on E-cores, but once P-cores became available, they migrated. It solved the problem we had before, but now E-cores remain idle until the end of the processing.

Our second piece of advice is to avoid static partitioning on systems with asymmetric cores. Equal-sized chunks will likely be processed faster on P-cores than on E-cores which will introduce dynamic load imbalance.

In the final example, we switch to using dynamic partitioning. With dynamic partitioning, chunks are distributed to threads dynamically. Each thread processes a chunk of elements, then requests another chunk, until no chunks remain to be distributed. Figure @fig:OmpDynamic shows the result of using dynamic partitioning by dividing the array into 16 chunks. With this scheme, each task becomes more granular, which enables OpenMP runtime to balance the work even when P-cores run two times faster than E-cores. However, notice that there is still some idle time on E-cores. 

Performance can be slightly improved if we partition the work into 128 chunks instead of 16. But don't make the jobs too small, otherwise it will result in increased management overhead. The result summary of our experiments is shown in Table [@tbl:TaskSchedulingResults]. Partitioning the work into 128 chunks turns out to be the sweet spot for our example. Even though our example is very simple, lessons from it can be applied to production-grade multithreaded software.

------------------------------------------------------------------------------------------------
                               Affinity  Static   Dynamic,    Dynamic,   Dynamic,    Dynamic,
                                                  4 chunks   16 chunks  128 chunks   1024 chunks
----------------------------- ---------- ------- ---------- ----------- ----------- ------------
Avg latency of 10 runs, ms     864       567       570         541        517          560

------------------------------------------------------------------------------------------------

Table: Results of the task scheduling experiments. {#tbl:TaskSchedulingResults}
