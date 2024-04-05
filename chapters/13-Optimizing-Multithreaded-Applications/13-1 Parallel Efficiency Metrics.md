## Parallel Efficiency Metrics {#sec:secMT_metrics}

When dealing with multithreaded applications, engineers should be careful analyzing basic metrics like CPU utilization and IPC (see [@sec:secMetrics]). One of the threads might show high CPU utilization and high IPC, but it could turn out that the thread was just spinning on a lock. That's why, when evaluating the parallel efficiency of an application, it's recommended to use Effective CPU Utilization, which is based only on the Effective time.[^12]

### Effective CPU Utilization

This metric represents how efficiently the application utilized the CPUs available. It shows the percent of average CPU utilization by all logical CPUs on the system. CPU utilization metric is based only on the Effective time and does not include the overhead introduced by the parallel runtime system[^11] and Spin time. A CPU utilization of 100% means that your application keeps all the logical CPU cores busy for the entire time that it runs[@IntelCpuMetrics].

For a specified time interval T, Effective CPU Utilization can be calculated as
$$
\textrm{Effective CPU Utilization} = \frac{\sum_{i=1}^{\textrm{ThreadsCount}}\textrm{Effective Cpu Time(T,i)}}{\textrm{T}~\times~\textrm{ThreadsCount}}
$$

### Thread Count

Applications usually have a configurable number of threads, which allows them to run efficiently on platforms with a different number of cores. Obviously, running an application using a lower number of threads than is available on the system underutilizes its resources. On the other hand, running an excessive number of threads can cause a higher CPU time because some of the threads may be waiting on others to complete, or time may be wasted on context switches.

Besides actual worker threads, multithreaded applications usually have helper threads: main thread, input and output threads, etc. If those threads consume significant time, they require dedicated HW threads themselves. This is why it is important to know the total thread count and configure the number of worker threads properly.

To avoid a penalty for threads creation and destruction, engineers usually allocate a [pool of threads](https://en.wikipedia.org/wiki/Thread_pool)[^14] with multiple threads waiting for tasks to be allocated for concurrent execution by the supervising program. This is especially beneficial for executing short-lived tasks.

### Wait Time

Wait Time occurs when software threads are waiting due to APIs that block or cause synchronization. Wait Time is per-thread; therefore, the total Wait Time can exceed the application Elapsed Time[@IntelCpuMetrics].

A thread can be switched off from execution by the OS scheduler due to either synchronization or preemption. So, Wait Time can be further divided into Sync Wait Time and Preemption Wait Time. A large amount of Sync Wait Time likely indicates that the application has highly contended synchronization objects. We will explore how to find them in the following sections. Significant Preemption Wait Time can signal a thread [oversubscription](https://software.intel.com/en-us/vtune-help-thread-oversubscription)[^13] problem either because of a big number of application threads or a conflict with OS threads or other applications on the system. In this case, the developer should consider reducing the total number of threads or increasing task granularity for every worker thread.

### Spin Time

Spin time is Wait Time, during which the CPU is busy. This often occurs when a synchronization API causes the CPU to poll while the software thread is waiting [@IntelCpuMetrics]. In reality, the implementation of kernel synchronization primitives prefer to spin on a lock for some time to the alternative of doing an immediate thread context switch (which is expensive). Too much Spin Time, however, can reflect the lost opportunity for productive work. 

[^11]: Threading libraries and APIs like `pthread`, `OpenMP`, and `Intel TBB` have their own overhead for creating and managing threads.
[^12]: Performance analysis tools such as Intel VTune Profiler can distinguish profiling samples that were taken while the thread was spinning. They do that with the help of call stacks for every sample (see [@sec:secCollectCallStacks]).
[^13]: Thread oversubscription - [https://software.intel.com/en-us/vtune-help-thread-oversubscription](https://software.intel.com/en-us/vtune-help-thread-oversubscription).
[^14]: Thread pool - [https://en.wikipedia.org/wiki/Thread_pool](https://en.wikipedia.org/wiki/Thread_pool).
