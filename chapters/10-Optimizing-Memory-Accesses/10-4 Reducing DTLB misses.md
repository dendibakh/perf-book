---
typora-root-url: ..\..\img
---

## Reducing DTLB misses {#sec:secDTLB}

As described earlier in the book, TLB is a fast but finite per-core cache for virtual-to-physical address translations of memory addresses. Without it, every memory access by an application would require a time-consuming page walk of the kernel page table to calculate the correct physical address for each referenced virtual address. In section [@sec:FeTLB] we discussed how large pages can be used for code. Now we will see how they can be used for data.

Any algorithm that does random accesses into a large memory region will likely suffer from DTLB misses. Examples of such applications are: binary search in a big array, accessing large hash tables, histogram-like algorithms, etc. Usage of large pages has potential for speeding up such applications.

On x86 platforms, the default page size is 4KB. Consider an application that actively references hundreds of MBs of memory. First, it will need to allocate many small pages which is expensive. Second, it will be touching many 4KB-sized pages, each of which will contend for a limited set of TLB entries. For instance, using large 2MB pages, 20MB of memory can be mapped with just ten pages, whereas with 4KB pages, you will need 5120 pages. This means fewer TLB entries are needed, in turn reducing the number of TLB misses. Besides 2MB huge pages, x86-based chips from AMD and Intel also support 1GB gigantic pages, which are only available for data, not for instructions.

As we just learned, one way to reduce the number of ITLB misses is to use the larger page size. Thankfully, TLB is capable of caching entries for 2MB and 1GB pages as well. If an application employed 2MB pages instead of the default 4KB pages, it would reduce the pressure on TLB. It may not always be a factor of 512 since the number of 2MB entries is much less. For example, in Intel's Skylake core families, L1 ITLB has 128 entries for 4KB pages and only 8 per thread for 2MB pages. L1 DTLB has 64 entries for 4KB pages and 32 entries for 2MB pages. Likewise, using 1GB pages instead of 2MB pages reduces TLB pressure even more. 

Utilizing huge pages typically leads to fewer page walks, and the penalty for walking the kernel page table in the event of a TLB miss is reduced since the table itself is more compact. Both Windows and Linux allow applications to establish large-page memory regions. Instructions on how to enable huge pages for Windows and Linux can be found in appendix C. On Linux, there are two ways of using large pages in an application: Explicit and Transparent Huge Pages.

I STOPPED HERE

### Explicit Hugepages.

Explicit hugepages are available as a part of the system memory, exposed as a huge page file system (`hugetlbfs`). Applications can access it using system calls, e.g., `mmap`. Huge pages can be reserved at boot time or at run time. Reserving at boot time increases the possibility of success because the memory has not yet been significantly fragmented. Explicitly preallocated pages reside in a reserved chunk of memory and cannot be swapped out under memory pressure. Also, this memory space cannot be used for other purposes, so users should be careful and reserve only the number of pages they need.

I STOPPED HERE

There is an option to dynamically allocate memory on top of large pages with [libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs)[^23] library that overrides `malloc` calls used in existing dynamically linked binary executables. It doesn't require modifying the code or even relink the binary; end-users just need to configure several environment variables. It can use both explicitly reserved huge pages as well as transparent ones. See `libhugetlbfs` [how-to documentation](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO)[^24] for more details.

For more fine-grained control over accesses to large pages from the code (i.e., not affecting every memory allocation), developers have the following alternatives:

* `mmap` using the `MAP_HUGETLB` flag ([exampe code](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/map_hugetlb.c)[^25]).
* `mmap` using a file from a mounted `hugetlbfs` filesystem ([exampe code](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-mmap.c)[^26]).
* `shmget` using the `SHM_HUGETLB` flag ([exampe code](https://elixir.bootlin.com/linux/latest/source/tools/testing/selftests/vm/hugepage-shm.c)[^27]).

**[TODO]: Add examples with malloc + jemalloc.**

### Transparent Hugepages.

Linux also offers Transparent Hugepage Support (THP), which manages large pages[^21] automatically and is transparent for applications. Under Linux, you can enable THP, which dynamically switches to huge pages when large blocks of memory are needed. The THP feature has two modes of operation: system-wide and per-process. When THP is enabled system-wide, the kernel tries to assign huge pages to any process when it is possible to allocate such, so huge pages do not need to be reserved manually. If THP is enabled per-process, the kernel only assigns huge pages to individual processes' memory areas attributed to the `madvise` system call. You can check if THP enabled in the system with:\

```bash
$ cat /sys/kernel/mm/transparent_hugepage/enabled
always [madvise] never
```

If the values are `always` (system-wide) or `madvise` (per-process), then THP is available for your application. With the `madvise` option, THP is enabled only inside memory regions attributed with `MADV_HUGEPAGE` via `madvise` system call. Complete specification for every option can be found in Linux kernel [documentation](https://www.kernel.org/doc/Documentation/vm/transhuge.txt)[^28] regarding THP.

### Explicit vs. Transparent Hugepages.

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
