## Low Latency Tuning Techniques {#sec:LowLatency}

So far we have discussed a variety of software optimizations that aim at improving overall performance of an application. In this section, we will discuss additional tuning techniques used in low-latency systems, such as real-time processing and high-frequency trading (HFT). In such an environment, the primary optimization goal is to make a certain portion of a program to run as fast as possible. When you work in the HFT industry, every microsecond and nanosecond count as it has a direct impact on profits. Usually, the low-latency portion implements a critical loop of a real-time of an HFT system, such as moving a robotic arm or sending an order to the exchange. Optimizing latency of a critical path is sometimes done at the expense of other portions of a program. And some techniques even sacrifice the overall throughput of a system.

When developers optimize for latency, they avoid any unnecessary cost they need to pay on a hot path. That usually involves system calls, memory allocation, I/O, and anything else that has non-deterministic latency. To reach the lowest possible latency, the hot path needs to have all the resources ready and available for it ahead of time. 

One relatively simple technique is to precompute some of the operations you would do on the hot path. That comes with a cost of using more memory which will be unavailable to other processes in the system but it may save you some precious cycles on a critical path. However, keep in mind that sometimes it is faster to compute the thing than to fetch the result from memory.

Since this a book about low-level CPU performance, we will skip talking about higher-level techniques similar to the one we just mentioned. Instead, we will discuss how to avoid page faults, cache misses, TLB shootdowns, and core throttling on a critical path.

### Avoid Minor Page Faults

While the term contains the word "minor", there's nothing minor about the impact of minor page faults on runtime latency. Recall that when a user code allocates memory, OS only commits to provide a page, but it doesn't immediately execute on the committment by giving us a zeroed physical page. Instead, it will wait until the first time the user code will access it and only then the OS fulfills its duties. The very first access to a newly allocated page triggers a minor page fault, a HW interrupt that is handled by the OS. Latency impact of minor faults can range from just under a microsecond up to several microseconds, especially if you're using a Linux kernel with 5-level page tables instead of 4-level page tables.

How do you detect runtime minor page faults in your application? One simple way is by using the `top` utility (add the `-H` option for a thread-level view). Add the `vMn` field to the default selection of display columns to view the number of minor page faults occurring per display refresh interval. Another way involves attaching to the running process with `perf stat -e page-faults`. 

[TODO]: add dump of `top -H`

In the HFT world, anything more than `0` is a problem. But for low latency applications in other business domains, a constant occurrence in the range of 100-1000 faults per second should prompt further investigation. Investigating the root cause of runtime minor page faults can be as simple as firing up `perf record -e page-faults` and then `perf report` to locate offending source code lines.

To avoid page fault penalties during runtime, you should pre-fault all the memory for the application at startup time. A toy example might look something like this:

```cpp
char *mem = malloc(size);
int pageSize = sysconf(_SC_PAGESIZE)
for (int i = 0; i < size; i += pageSize)
  mem[i] = 0;
```

First, this sample code allocates `size` amount of memory on the heap as usual. However, immediately after that, it steps by and touches each page of newly allocated memory to ensure each one is brought into RAM.

Another reason for a minor page fault is when the accessed page was swapped out to disk and is not currently stored in RAM. This can be prevented by *locking* pages in RAM. Let's take a look at a more comprehensive approach of tuning the glibc allocator in conjunction with `mlock/mlockall` syscalls:

```cpp
#include <malloc.h>
#include <sys/mman.h>

mallopt(M_MMAP_MAX, 0);
mallopt(M_TRIM_THRESHOLD, -1);
mallopt(M_ARENA_MAX, 1);

mlockall(MCL_CURRENT | MCL_FUTURE);

char *mem = malloc(size);
for (int i = 0; i < size; i += sysconf(_SC_PAGESIZE))
    mem[i] = 0;
//...
free(mem);
```

In the code above, we tune three glibc malloc settings: `M_MMAP_MAX`, `M_TRIM_THRESHOLD`, and `M_ARENA_MAX`.

- Setting `M_MMAP_MAX` to `0` disables underlying `mmap` syscall usage for large allocations – this is necessary because the `mlockall` can be undone by library usage of `munmap` when it attempts to release `mmap`-ed segments back to the OS, defeating the purpose of our efforts.
- Setting `M_TRIM_THRESHOLD` to `-1` prevents glibc from returning memory to the OS after calls to `free`. As indicated before, this option has no effect on `mmap`-ed segments.
- Finally, setting `M_ARENA_MAX` to `1` prevents glibc from allocating multiple arenas via `mmap` to accommodate multiple cores. Keep in mind, the latter hinders the glibc allocator's multithreaded scalability feature.

Combined, these settings force glibc into heap allocations which will not release memory back to the OS until the application ends. As a result, the heap will remain the same size after the final call to `free(mem)` in the code above. Any subsequent runtime calls to `malloc` or `new` simply will reuse space in this pre-allocated/pre-faulted heap area if it is sufficiently sized at initialization.

More importantly, all that heap memory that was pre-faulted in the `for`-loop will persist in RAM due to the previous `mlockall` call – the option `MCL_CURRENT` locks all pages which are currently mapped, while `MCL_FUTURE` locks all pages that will become mapped in the future. An added benefit of using `mlockall` this way is that any thread spawned by this process will have its stack pre-faulted and locked, as well. For the finer control of page locking, developers should use `mlock` system call which gives you the option to choose which pages should persist in RAM. A downside of this technique is that it reduces the amount of memory available to other processes running on the system.

[TODO]: double-check this: Developers of applications for Windows should look into the following APIs: lock pages with `VirtualLock`, avoid immediate release of memory with `VirtualFree` with `MEM_DECOMMIT`, but not `MEM_RELEASE` flag.

These are just two example methods for preventing runtime minor faults. Some or all of these techniques may be already integrated into memory allocation libraries such as jemalloc, tcmalloc, or mimalloc. Check the documentation of your chosen library to see what is available.

### Cache Warming {#sec:CacheWarm}

Instruction and data caches, and the performance impact of each, were explained in [@sec:secFEOpt] and [@sec:secCacheFriendly], along with specific techniques to get the most benefit from each. However, in some application workloads, the portions of code that are most latency-sensitive are the least frequently executed. This results in the function blocks and associated data from aging out of the I-cache and D-cache after some time. Then, just when we need that critical piece of rarely executed code to execute, we take I-cache and D-cache miss penalties, which may exceed our target performance budget.

An example of such a workload might be a high-frequency trading application that continuously reads market data signals from the stock exchange and, once a favorable market signal is detected, sends a BUY order to the exchange. In the aforementioned workload, the code paths involved with reading the market data is most commonly executed, while the code paths for executing a BUY order is rarely executed. If we want our BUY order to reach the exchange as fast as possible and to take advantage of the favorable signal detected in the market data, then the last thing we want is to incur cache misses right at the moment we decide to execute that critical piece of code. This is where the technique of Cache Warming would be helpful.

Cache Warming involves periodically exercising the latency-sensitive code to keep it in the cache while ensuring it does not follow all the way through with any unwanted actions. Exercising the latency-sensitive code also "warms up" the D-cache by bringing latency-sensitive data into it. In fact, this technique is routinely employed for trading applications like the one described in a [CppCon 2018 lightning talk](https://www.youtube.com/watch?v=XzRxikGgaHI)[^4].

### Avoid TLB Shootdowns

We learned from earlier chapters that the TLB is a fast but finite per-core cache for virtual-to-physical memory address translations that reduces the need for time-consuming kernel page table walks. However, unlike the case with MESI-based protocols and per-core CPU caches (i.e., L1, L2, and LLC), the HW itself is incapable of maintaining core-to-core TLB coherency. Therefore, this task must be performed in software by the kernel. The kernel fulfills this role by means of Inter Processor Interrupts (IPI) called “TLB Shootdowns.”

TLB Shootdowns differ from wholesale TLB flushes, such as what occurs when a process is scheduled off a core to make way for a new process with an entirely different virtual address space. Instead, TLB Shootdowns involve more selective removal of TLB entries, such as via the INVLPG command on Intel CPUs. 

One of the most overlooked pitfalls to achieving low latency with multithreaded applications is the TLB Shootdown. Why? Because in a multithreaded application, process threads share the virtual address space. Therefore, the kernel must communicate specific types of updates to that shared address space among the TLBs of the cores on which any of the participating threads execute. For example, commonly used syscalls such as munmap (which we disabled from glibc allocator usage in the prior section on “Avoiding Minor Page Faults”), mprotect, and madvise effect the types of address space changes that the kernel must communicate among the constituent threads of a process.

Though a developer may avoid explicitly using these syscalls in his/her code, TLB Shootdowns may still erupt from external sources – e.g., allocator shared libraries or OS facilities. Not only will this type of IPI disrupt runtime application performance, but the magnitude of its impact grows with the number of threads involved since the interrupts are delivered in software.

How do you detect TLB Shootdowns in your multithreaded application? One simple way is to check the TLB row in /proc/interrupts. A useful method of detecting continuous TLB interrupts during runtime is to use the “watch” command while viewing this file. For example, you might run “watch -n5 -d ‘grep TLB /proc/interrupts’” – the “-n 5” option refreshes the view every 5 seconds while “-d” highlights the delta between each refresh output. 

Preventing TLB Shootdowns requires limiting the number of updates made to the shared process address space – e.g., avoiding runtime execution of the aforementioned list of syscalls. Also, disable kernel features which induce TLB Shootdowns as a consequence of its function, such as Transparent Huge Pages and Automatic NUMA Balancing – these features either relocate or alter permissions of pages in the process of operation, which require page table updates and, thus, TLB Shootdowns.

For more details on TLB Shootdowns, along with their detection and prevention, read https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/.

### Prevent Unintentional Core Throttling

C/C++ compilers are a wonderful feat of engineering. However, they sometimes generate surprising results that may lead you on a wild goose chase. A real-life example is an instance where the compiler optimizer emits heavy AVX instructions that you never intended. While less of an issue on more modern chips, many older generations of CPUs (which remain in active usage on-prem and in the cloud) exhibit heavy core throttling/downclocking when executing heavy AVX instructions. If your compiler produces these instructions without your explicit knowledge or consent, you may experience unexplained latency anomalies during application runtime.

For this specific case, if heavy AVX instruction usage is not desired, include “-mprefer-vector-width=###” to your compilation flags to pin the highest width instruction set to either 128 or 256. Again, if your entire server fleet runs on the latest chips then this is much less of a concern since the throttling impact of AVX instruction sets is negligible nowadays.



[MAYBE] Tradeoff Random RAM Access with Larger Footprint (on 2nd thought, this is more of a coding technique than a tuning technique)

[^4]: Cache Warming technique - [https://www.youtube.com/watch?v=XzRxikGgaHI](https://www.youtube.com/watch?v=XzRxikGgaHI).
