---
typora-root-url: ..\..\img
---

## Reducing DTLB misses {#sec:secDTLB}

As described earlier in the book, TLB is a fast but finite per-core cache for virtual-to-physical address translations of memory addresses. Without it, every memory access by an application would require a time-consuming page walk of the kernel page table to calculate the correct physical address for each referenced virtual address. In a system with a 5-level page table, it will require accessing at least 5 different memory locations to obtain an address translation. In section [@sec:FeTLB] we will discuss how huge pages can be used for code. Here we will see how they can be used for data.

Any algorithm that does random accesses into a large memory region will likely suffer from DTLB misses. Examples of such applications are: binary search in a big array, accessing a large hash table, traversing a graph. Usage of huge pages has potential for speeding up such applications.

On x86 platforms, the default page size is 4KB. Consider an application that actively references hundreds of MBs of memory. First, it will need to allocate many small pages which is expensive. Second, it will be touching many 4KB-sized pages, each of which will contend for a limited set of TLB entries. For instance, using huge 2MB pages, 20MB of memory can be mapped with just ten pages, whereas with 4KB pages, you will need 5120 pages. This means fewer TLB entries are needed, in turn reducing the number of TLB misses. It will not be a proportional reduction by a factor of 512 since the number of 2MB entries is much less. For example, in Intel's Skylake core families, L1 DTLB has 64 entries for 4KB pages and only 32 entries for 2MB pages. Besides 2MB huge pages, x86-based chips from AMD and Intel also support 1GB gigantic pages, which are only available for data, not for instructions. Using 1GB pages instead of 2MB pages reduces TLB pressure even more.

Utilizing huge pages typically leads to fewer page walks, and the penalty for walking the kernel page table in the event of a TLB miss is reduced since the table itself is more compact. Performance gains of utilizing huge pages can sometimes go as high as 30%, depending on how much TLB pressure an application is experiencing. Expecting 2x speedups would be asking too much, as it is quite rare that TLB misses are the primary bottleneck. The paper
[@Luo2015] presents the evaluation of using huge pages on the SPEC2006 benchmark suite. Results can be summarized as follows. Out of 29 benchmarks in the suite, 15 have a speedup within 1%, which can be discarded as noise. Six benchmarks have speedups in the range of 1%-4%. Four benchmarks have speedups in the range from 4% to 8%. Two benchmarks have speedups of 10%, and the two benchmarks that gain the most, enjoyed 22% and 27% speedups respectively.

Many real-world applications already take advantage of huge pages, for example KVM, MySQL, PostgreSQL, Java JVM, and others. Usually, those SW packages provide an option that enable that feature. Check documentation of the application to see if you can enable huge pages.

Both Windows and Linux allow applications to establish huge-page memory regions. Instructions on how to enable huge pages for Windows and Linux can be found in appendix C. On Linux, there are two ways of using huge pages in an application: Explicit and Transparent Huge Pages. Windows supports is not as rich a Linux and will be discussed later.

### Explicit Hugepages.

Explicit Huge Pages (EHP) are available as a part of the system memory, exposed as a huge page file system `hugetlbfs`. As the name implies, EHPs should be reserved either at boot time or at run time. See appendix C for instructions on how to do that. Reserving EHPs at boot time increases the possibility of successfull allocation because the memory has not yet been significantly fragmented. Explicitly preallocated pages reside in a reserved chunk of memory and cannot be swapped out under memory pressure. Also, this memory space cannot be used for other purposes, so users should be careful and reserve only the number of pages they need.

The simplest method of using EHP in an application is to call `mmap` with `MAP_HUGETLB` as shown in [@lst:ExplicitHugepages1]. In this code, pointer `ptr` will point to a 2MB region of memory that was explicitly reserved for EHPs. Notice, that allocation may fail due to the EHPs were not reserved in advance. Another less popular ways to use EHPs in user code are provided in appendix C. Also, developers can write their own arena-based allocators that tap into EHPs.

Listing: Mapping a memory region from explicitly allocated huge page.

~~~~ {#lst:ExplicitHugepages1 .cpp}
void ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
if (ptr == MAP_FAILED)
  throw std::bad_alloc{};                
...
munmap(ptr, size);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the past, there was an option to use the [libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs)[^1] library, which allowed to override `malloc` calls used in existing dynamically linked executables to allocate memory on top of EHPs. Unfortunately, this project is no longer maintained. It didn't require users to modify the code or to relink the binary. They could simply prepend the command line with `LD_PRELOAD=libhugetlbfs.so HUGETLB_MORECORE=yes <your app command line>` to make use of it. But luckily, there are other libraries that allow to use huge pages (not EHPs) with `malloc` as we will see shortly.

### Transparent Hugepages.

Linux also offers Transparent Hugepage Support (THP), which has two modes of operation: system-wide and per-process. When THP is enabled system-wide, the kernel manages huge pages automatically and it is transparent for applications. The OS kernel tries to assign huge pages to any process when large blocks of memory are needed and it is possible to allocate such, so huge pages do not need to be reserved manually. If THP is enabled per-process, the kernel only assigns huge pages to individual processes' memory areas attributed to the `madvise` system call. You can check if THP enabled in the system with:

```bash
$ cat /sys/kernel/mm/transparent_hugepage/enabled
always [madvise] never
```

If the values are `always` (system-wide) or `madvise` (per-process), then THP is available for your application. A detailed specification for every option can be found in the Linux kernel [documentation](https://www.kernel.org/doc/Documentation/vm/transhuge.txt)[^2] regarding THP. 

When THP is enabled system-wide, huge pages are used automatically for normal memory allocations, without an explicit request from applications. Basically, to observe the effect of huge pages on their application, a user just need to enable system-wide THPs with `echo "always" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled`. It will automatically lauches a daemon process named `khugepaged` which starts scanning application’s memory space to promote regular pages to huge pages. Though sometimes the kernel may fail to promote regular pages into huge pages in case it cannot find a contiguous 2MB chunk of memory.

[TODO]: on my system it looks like `khugepaged` doesn't do the work and a different behavior is in place: my application stalls on allocation failure and directly reclaim regular pages and promotes them into a THP immediately.

System-wide THPs mode is good for quick experiments to check if huge pages can improve performance. It works automatically, even for applications that are not aware of THPs, so developers don't have to change the code to see the benefit of huge pages for their application.

When hugepages are enabled system wide, applications may end up allocating much more memory resources. An application may mmap a large region but only touch 1 byte of it, in that case a 2M page might be allocated instead of a 4k page for no good. This is why it's possible to disable hugepages system-wide and to only have them inside MADV_HUGEPAGE madvise regions, which we will discuss next. Don't forget to disable system-wide THPs after you've finished your experiments as it may not benefit every application running on the system.

With the `madvise` (per-process) option, THP is enabled only inside memory regions attributed via `madvise` system call with `MADV_HUGEPAGE` flag. As shown in the [@lst:TransparentHugepages1], pointer `ptr` will point to a 2MB region of anonymous (transparent) memory region, which kernel allocates dynamically. The `mmap` call may fail in case the kernel could not find a contiguous 2MB chunk of memory.

Listing: Mapping a memory region to a transparent huge page.

~~~~ {#lst:TransparentHugepages1 .cpp}
void ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_PRIVATE | MAP_ANONYMOUS, -1 , 0);
if (ptr == MAP_FAILED)
  throw std::bad_alloc{};
madvise(ptr, size, MADV_HUGEPAGE);
// use the memory region `ptr`
munmap(ptr, size);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Developers can build custom THP allocators based on the code in [@lst:TransparentHugepages1]. But also, it's possible to use THPs inside `malloc` calls that their application is making. Many memory allocation libraries provide that feature by overriding the `libc`'s implementation of `malloc`. Here is an example of one of the most popular such libraries `jemalloc`. If you have access to the source code of the application, you can relink the binary with additional `-ljemalloc` option. This will dynamically link your application against the `jemalloc` library, which will handle all the `malloc` calls. Then use the following option to enable THPs for heap allocations:

```bash
$ MALLOC_CONF="thp:always" <your app command line>
```

If you don't have access to the source code, you can still make use of `jemalloc` by preloading the dynamic library:

```bash
$ LD_PRELOAD=/usr/local/libjemalloc.so.2 MALLOC_CONF="thp:always" <your app command line>
```

Windows only offers using huge pages in a way similar to the Linux THP per-process mode via WinAPI `VirtualAlloc` system call. See details in appendix C.

### Explicit vs. Transparent Hugepages.

Linux users can use huge pages in three different modes:
* Explicit Huge Pages
* System-wide Transparent Huge Pages
* Per-process Transparent Huge Pages

Let's compare those options. First, EHPs are reserved in virtual memory upfront, THPs are not. That makes it harder to ship SW packages that use EHPs, as they rely on specific configuration settings made by an administrator of a machine. Moreover, EHPs statically sit in memory, consuming precious DRAM space for no reason, when they are not used.

Second, system-wide Transparent Huge Pages are great for quick experiments. No changes in the user code are required to test the benefit of using huge pages in your application. However, it will not be wise to ship a SW package to the customers and ask them to enable system-wide THPs, as it may negatively affect other running programs on that system. Usually, developers identify allocations in the code that could benefit from huge pages and use `madvise` hints in these places (per-process mode).

Per-process THPs don't have either of the downsides mentioned above, but they have another one. Previously we discussed that THP allocation by the kernel happens transparently to the user. The allocation process can potentially involve a number of kernel processes responsible for making space in the virtual memory, which may include swapping memory to the disk, fragmentation, or promoting pages. Background maintenance of transparent huge pages incurs non-deterministic latency overhead from the kernel as it manages the inevitable fragmentation and swapping issues. EHPs are not subject to memory fragmentation and cannot be swapped to the disk, thus have much less latency overhead.

All in all, THPs are easier to use, but incur bigger allocation latency overhead. That is exactly the reason why THPs are not popular in High-Frequency Trading and other ultra low-latency industries, they prefer to use EHPs instead. On the other hand, virtual machine providers and databases tend to use per-process THPs since requiring additional system configuration can become a burden for their users.

[^1]: libhugetlbfs - [https://github.com/libhugetlbfs/libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs).
[^2]: Linux kernel THP documentation - [https://www.kernel.org/doc/Documentation/vm/transhuge.txt](https://www.kernel.org/doc/Documentation/vm/transhuge.txt)
