## Parallel Efficiency Metrics {#sec:secMT_metrics}

Let's start by introducing a few metrics that are important for analyzing the performance of multithreaded applications. When dealing with multithreaded applications, engineers should be careful in analyzing basic metrics, for example, CPU utilization. One of the threads might show high CPU utilization, but it could turn out that the thread was just spinning in a busy-wait loop while waiting for a lock. That's why, when evaluating the parallel efficiency of an application, it's recommended to use *Effective CPU Utilization*, which is based only on the *Effective time*.

### Effective CPU Utilization {.unlisted .unnumbered}

This metric represents how efficiently an application utilizes the available CPUs. It shows the percent of average CPU utilization by all logical CPUs on the system. It is based only on the *Effective time* and does not include the overhead introduced by the parallel runtime system[^11] and Spin time. An *Effective CPU utilization* of 100% means that your application keeps all the logical CPU cores busy for the entire time that it runs.

For a specified time interval `T`, *Effective CPU Utilization* can be calculated as
$$
\textrm{Effective CPU Utilization} = \frac{\sum_{i=1}^{\textrm{ThreadCount}}\textrm{Effective Cpu Time(T,i)}}{\textrm{T}~\times~\textrm{ThreadCount}}
$$

### Thread Count {.unlisted .unnumbered}

Most parallel applications have a configurable number of threads, which allows them to run efficiently on platforms with a different number of cores. Running an application using a lower number of threads than is available on the system underutilizes its resources. On the other hand, running an excessive number of threads can cause *oversubscription*; some threads will be waiting for their turn to run.

Besides actual worker threads, multithreaded applications usually have other housekeeping threads: main thread, input/output threads, etc. If those threads consume significant time, they will take execution time away from worker threads, as they too require CPU cores to run. This is why it is important to know the total thread count and configure the number of worker threads properly.

To avoid a penalty for thread creation and destruction, engineers usually allocate a [pool of threads](https://en.wikipedia.org/wiki/Thread_pool)[^14] with multiple threads waiting for tasks to be allocated for concurrent execution by the supervising program. This is especially beneficial for executing short-lived tasks.

### Wait Time {.unlisted .unnumbered}

*Wait Time* occurs when software threads are waiting due to APIs that block or cause a context switch. Wait Time is per thread; therefore, the total *Wait Time* can exceed the application elapsed time.

A thread can be switched off from execution by the OS scheduler due to either synchronization or preemption. So, *Wait Time* can be further divided into *Sync Wait Time* and *Preemption Wait Time*. A large amount of *Sync Wait Time* likely indicates that the application has highly contended synchronization objects. We will explore how to find them in the following sections. Significant *Preemption Wait Time* can signal a thread oversubscription problem either because of a large number of application threads or a conflict with OS threads or other applications on the system. In this case, the developer should consider reducing the total number of threads or increasing task granularity for every worker thread.

### Spin Time {.unlisted .unnumbered}

*Spin time* is *Wait Time*, during which the CPU is busy. This often occurs when a synchronization API causes the CPU to poll while the software thread is waiting. In reality, the implementation of kernel synchronization primitives spins on a lock for some time instead of immediately yielding to another thread. Too much Spin Time, however, can reflect the lost opportunity for productive work. 

A list of other parallel efficiency metrics can be found on Intel's VTune [page](https://software.intel.com/en-us/vtune-help-cpu-metrics-reference).[^15]

[^11]: Threading libraries such as `pthread`, `OpenMP`, and `Intel TBB` incur additional overhead for creating and managing threads.
[^14]: Thread pool - [https://en.wikipedia.org/wiki/Thread_pool](https://en.wikipedia.org/wiki/Thread_pool)
[^15]: CPU metrics reference - [https://software.intel.com/en-us/vtune-help-cpu-metrics-reference](https://software.intel.com/en-us/vtune-help-cpu-metrics-reference)