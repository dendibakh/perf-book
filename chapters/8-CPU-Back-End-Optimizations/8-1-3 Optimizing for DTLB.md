---
typora-root-url: ..\..\img
---

### Optimizing For DTLB {#sec:secDTLB}

As described in [@sec:uarch], the TLB is a fast but finite per-core cache for virtual-to-physical address translations of memory addresses. Without it, every memory access by an application would require a time-consuming page walk of the kernel page table to calculate the correct physical address for each referenced virtual address. 

TLB hierarchy typically consists of L1 ITLB (instructions), L1 DTLB (data), and L2 STLB (unified cache for instructions and data). A miss in the L1 (first level) ITLBs results in a very small penalty that can usually be hidden by the Out of Order (OOO) execution. A miss in the STLB results in the page walker being invoked. This penalty can be noticeable in the runtime because, during this process, the CPU is stalled [@IntelBlueprint]. Assuming the default page size in Linux kernel is `4KB`, modern L1 level TLB caches can keep only up to a few hundred most recently used page-table entries, which covers address space of `~1MB`, while L2 STLB can hold up to a few thousand page-table entries. Exact numbers for a specific processor can be found at [https://ark.intel.com](https://ark.intel.com).

On Linux and Windows systems, applications are loaded into memory into 4KB pages, which is the default on most systems. Allocating many small pages is expensive. If an application actively references tens or hundreds of GBs of memory, that would require many 4KB-sized pages, each of which will contend for a limited set of TLB entries. Using large 2MB pages, 20MB of memory can be mapped with just ten pages, whereas with 4KB pages, 5120 pages are required. This means fewer TLB entries are needed, in turn reducing the number of TLB misses. Both Windows and Linux allow applications to establish large-page memory regions. HugeTLB subsystem support depends on the architecture, while AMD64 and Intel 64 architecture support both 2 MB (huge) and 1 GB (gigantic) pages.

As we just learned, one way to reduce the number of ITLB misses is to use the larger page size. Thankfully, TLB is capable of caching entries for 2MB and 1GB pages as well. If the aforementioned application employed 2MB pages instead of the default 4KB pages, it would reduce TLB pressure by a factor of 512. Likewise, if it updated from using 2MB pages to 1GB pages, it would reduce TLB pressure by yet another factor of 512. That is quite an improvement! Using a larger page size may be beneficial for some applications because less space is used in the cache for storing translations, allowing more space to be available for the application code. Huge pages typically lead to fewer page walks, and the penalty for walking the kernel page table in the event of a TLB miss is reduced since the table itself is more compact.

Large pages can be used for code, data, or both. Large pages for data are good to try if your workload has a large heap. Large memory applications such as relational database systems (e.g., MySQL, PostgreSQL, Oracle, etc.) and Java applications configured with large heap regions frequently benefit from using large pages. One example of using huge pages for optimizing runtimes is presented in [@IntelBlueprint], showing how this feature improves performance and reduces ITLB misses (up to 50%) in three applications in three environments. However, as it is with many other features, large pages are not for every application. An application that wants to allocate only one byte of data would be better off using a 4k page rather than a huge one; that way, memory is used more efficiently. 

On Linux OS, there are two ways of using large pages in an application: Explicit and Transparent Huge Pages.

#### Explicit Hugepages.

Are available as a part of the system memory, exposed as a huge page file system (`hugetlbfs`), applications can access it using system calls, e.g., `mmap`. One can check Huge Pages appropriately configured on the system through `cat /proc/meminfo` and look at `HugePages_Total` entries. Huge pages can be reserved at boot time or at run time. Reserving at boot time increases the possibility of success because the memory has not yet been significantly fragmented. Exact instructions for reserving huge pages can be found in [Red Hat Performance Tuning Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/performance_tuning_guide/sect-red_hat_enterprise_linux-performance_tuning_guide-memory-configuring-huge-pages#sect-Red_Hat_Enterprise_Linux-Performance_tuning_guide-Memory-Configuring-huge-pages-at-run-time) [^22].

There is an option to dynamically allocate memory on top of large pages with [libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs)[^23] library that overrides `malloc` calls used in existing dynamically linked binary executables. It doesn't require modifying the code or even relink the binary; end-users just need to configure several environment variables. It can use both explicitly reserved huge pages as well as transparent ones. See `libhugetlbfs` [how-to documentation](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO)[^24] for more details.

For more fine-grained control over accesses to large pages from the code (i.e., not affecting every memory allocation), developers have the following alternatives:

* `mmap` using the `MAP_HUGETLB` flag ([exampe code](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/map_hugetlb.c)[^25]).
* `mmap` using a file from a mounted `hugetlbfs` filesystem ([exampe code](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-mmap.c)[^26]).
* `shmget` using the `SHM_HUGETLB` flag ([exampe code](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-shm.c)[^27]).

#### Transparent Hugepages.

Linux also offers Transparent Hugepage Support (THP), which manages large pages[^21] automatically and is transparent for applications. Under Linux, you can enable THP, which dynamically switches to huge pages when large blocks of memory are needed. The THP feature has two modes of operation: system-wide and per-process. When THP is enabled system-wide, the kernel tries to assign huge pages to any process when it is possible to allocate such, so huge pages do not need to be reserved manually. If THP is enabled per-process, the kernel only assigns huge pages to individual processes' memory areas attributed to the `madvise` system call. You can check if THP enabled in the system with:\

```bash
$ cat /sys/kernel/mm/transparent_hugepage/enabled
always [madvise] never
```

If the values are `always` (system-wide) or `madvise` (per-process), then THP is available for your application. With the `madvise` option, THP is enabled only inside memory regions attributed with `MADV_HUGEPAGE` via `madvise` system call. Complete specification for every option can be found in Linux kernel [documentation](https://www.kernel.org/doc/Documentation/vm/transhuge.txt)[^28] regarding THP.

#### Explicit vs. Transparent Hugepages.

Whilst Explicit Huge Pages (EHP) are reserved in virtual memory upfront, THPs are not. In the background, the kernel attempts to allocate a THP, and if it fails, it will default to the standard 4k page. This all happens transparently to the user. The allocation process can potentially involve a number of kernel processes responsible for making space in the virtual memory for a future THP (which may include swapping memory to the disk, fragmentation, or compacting pages[^20]). Background maintenance of transparent huge pages incurs non-deterministic latency overhead from the kernel as it manages the inevitable fragmentation and swapping issues. EHP is not subject to memory fragmentation and cannot be swapped to the disk. 

Secondly, EHP is available for use on all segments of an application, including text segments (i.e., benefits both DTLB *and* ITLB), while THP is only available for dynamically allocated memory regions.

One advantage of THP is that less OS configuration effort is required than with EHP, which enables faster experiments.

[^20]: E.g., compacting 4KB pages into 2MB, breaking 2MB pages back into 4KB, etc.
[^21]: Note that the THP feature only supports 2MB pages.
[^22]: Red Hat Performance Tuning Guide - [https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/performance_tuning_guide/sect-red_hat_enterprise_linux-performance_tuning_guide-memory-configuring-huge-pages#sect-Red_Hat_Enterprise_Linux-Performance_tuning_guide-Memory-Configuring-huge-pages-at-run-tim](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/performance_tuning_guide/sect-red_hat_enterprise_linux-performance_tuning_guide-memory-configuring-huge-pages#sect-Red_Hat_Enterprise_Linux-Performance_tuning_guide-Memory-Configuring-huge-pages-at-run-time).
[^23]: libhugetlbfs - [https://github.com/libhugetlbfs/libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs).
[^24]: libhugetlbfs "how-to" page - [https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO).
[^25]: MAP_HUGETLB example - [https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/map_hugetlb.c](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/map_hugetlb.c).
[^26]: Mounted `hugetlbfs` filesystem - [https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-mmap.c](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-mmap.c).
[^27]: SHM_HUGETLB example - [https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-shm.c](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-shm.c).
[^28]: Linux kernel THP documentation - [https://www.kernel.org/doc/Documentation/vm/transhuge.txt](https://www.kernel.org/doc/Documentation/vm/transhuge.txt)
