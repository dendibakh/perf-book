## Virtual Memory {#sec:VirtMem}

Virtual memory is the mechanism to share the physical memory attached to a CPU with all the processes executing on the CPU. Virtual memory provides a protection mechanism that prevents access to the memory allocated to a given process from other processes. Virtual memory also provides relocation, which is the ability to load a program anywhere in physical memory without changing the addresses in the program. 

In a CPU that supports virtual memory, programs use virtual addresses for their accesses. But while user code operates on virtual addresses, retrieving data from memory requires physical addresses. Also, to effectively manage the scarce physical memory, it is divided into pages. Thus, applications operate on a set of pages that an operating system has provided.

Address translation is required for accessing data as well as code (instructions). The mechanism for a system with a page size of 4KB is shown on Figure @fig:VirtualMem. The virtual address is split into two parts. The virtual page number (52 most significant bits) is used to index into the page table to produce a mapping between the virtual page number and the corresponding physical page. To offset within a 4KB page we need 12 bits; as already stated, the other 52 bits of a 64-bit pointer are used for the address of the page itself. Notice that the offset within a page (12 least significant bits) does not require translation, and it is used "as-is" to access the physical memory location.

![Virtual-to-physical address translation for 4KB pages.](../../img/uarch/VirtualMem.png){#fig:VirtualMem width=70%}

The page table can be either single level or nested. Figure @fig:L2PageTables shows one example of a 2-level page table. Notice how the address gets split into more pieces. The first thing to mention is that 16 most significant bits are not used. This can seem like a waste of bits, but even with the remaining 48 bits we can address 256 TB of total memory (2^48^). Some applications use those unused bits to keep metadata, also known as *pointer tagging*.

![Exmaple of a 2-level page table.](../../img/uarch/L2PageTables.png){#fig:L2PageTables width=70%}

A nested page table is a radix tree that keeps physical page addresses along with some metadata. To find a translation for such a 2-level page table, we first use bits 32..47 as an index into the Level-1 page table also known as *page table directory*. Every descriptor in the directory points to one of the 2^16^ blocks of Level-2 tables. Once we find the appropriate L2 block, we use bits 12..31 to find the physical page address. Concatenating it with the page offset (bits 0..11) gives us the physical address, which can be used to retrieve the data from the DRAM.

The exact format of the page table is dictated by the CPU for reasons we will discuss a few paragraphs later. Thus the variations of page table organization are limited by what a CPU supports. Nowadays it is common to see 4- and 5-level page tables. Modern CPUs support both 4-level page table with 48 bit pointers (256 TB of total memory) and 5-level page tables with 57 bit pointers (128 PB of total memory).

Breaking page table into multiple levels doesn't change the total addressable memory. However, a nested approach does not require storing the entire page table as a contiguous array and does not allocate blocks that have no descriptors. This saves memory space but adds overhead when traversing the page table.

Failure to provide a physical address mapping is called a *page fault*. It occurs if a requested page is invalid or is not currently in main memory. The two most common reasons are: 1) the OS committed to allocating a page but hasn't yet backed it with a physical page, and 2) an accessed page was swapped out to disk and is not currently stored in RAM.

### Translation Lookaside Buffer (TLB) {#sec:TLBs}

A search in a hierarchical page table could be expensive, requiring traversing through the hierarchy potentially making several indirect accesses. Such a traversal is usually called a *page walk*. To reduce the address translation time, CPUs support a hardware structure called a translation lookaside buffer (TLB) to cache the most recently used translations. Similar to regular caches, TLBs are often designed as a hierarchy of L1 ITLB (Instructions), L1 DTLB (Data), followed by a shared (instructions and data) L2 STLB. To lower memory access latency, TLB and cache lookups happen in parallel, because data caches operate on virtual addresses and do not require prior address translation

The TLB hierarchy keep translations for a relatively large memory space. Still, misses in the TLB can be very costly. To speed up handling of TLB misses, CPUs have a mechanism called a *HW page walker*. Such a unit can perform a page walk directly in HW by issuing the required instructions to traverse the page table, all without interrupting the kernel. This is the reason why the format of the page table is dictated by the CPU, to which OS’es have to comply. High-end processors have several HW page walkers that can handle multiple TLB misses simultaneously. However, even with all the acceleration offered by modern CPUs, TLB misses still cause performance bottlenecks for many applications.

### Huge Pages

Having a small page size makes it possible to manage the available memory more efficiently and reduce fragmentation. The drawback though is that it requires having more page table entries to cover the same memory region. Consider two page sizes: 4KB, which is a default on x86, and 2MB *huge page* size. For an application that operates on 10MB data, we need 2560 entries in first case, and just 5 entries if we would map the address space onto huge pages. Those are named *Huge Pages* on Linux, *Super Pages* on FreeBSD, and *Large Pages* on Windows, but they all mean the same thing. Through the rest of this book we will refer to them as Huge Pages.

An example of an address that points to data within a huge page is shown in Figure @fig:HugePageVirtualAddress. Just like with a default page size, the exact address format when using huge pages is dictated by the HW, but luckily we as programmers usually don't have to worry about it.

![Virtual address that points within a 2MB page.](../../img/uarch/HugePageVirtualAddress.png){#fig:HugePageVirtualAddress width=80%}

Using huge pages drastically reduces the pressure on the TLB hierarchy since fewer TLB entries are required. It greatly increases the chance of a TLB hit. We will discuss how to use huge pages to reduce the frequency of TLB misses in [@sec:secDTLB] and [@sec:FeTLB]. The downsides of using huge pages are memory fragmentation and, in some cases, non-deterministic page allocation latency because it is harder for the operating system to manage large blocks of memory and to ensure effective utilization of available memory. To satisfy a 2MB huge page allocation request at runtime, an OS needs to find a contiguous chunk of 2MB. If this cannot be found, the OS needs to reorganize the pages, resulting in a longer allocation latency.
