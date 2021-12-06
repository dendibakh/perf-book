---
typora-root-url: ..\..\img
---

## Optimizing for ITLB {#sec:FeTLB}

Another important area of tuning FE efficiency is virtual-to-physical address translation of memory addresses. Primarily those translations are served by TLB (see [@sec:uarch]), which caches most recently used memory page translations in dedicated entries. When TLB cannot serve translation request, a time-consuming page walk of the kernel page table takes place to calculate the correct physical address for each referenced virtual address. When TMA points to a high [ITLB Overhead](https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/reference/cpu-metrics-reference/front-end-bound/itlb-overhead.html) [^11], the advice in this section may become handy. 

ITLB pressure can be reduced by mapping the portions of the performance-critical code of an application onto large pages. This requires relinking the binary to align text segments at the proper page boundary in preparation for large page mapping (see [guide](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO)[^12] to libhugetlbfs). For general discussion on large pages, see [@sec:secDTLB].

Besides from employing large pages, standard techniques for optimizing I-cache performance can be used for improving ITLB performance; namely, reordering functions so that hot functions are more collocated, reducing the size of hot regions via [LTO/IPO](https://en.wikipedia.org/wiki/Interprocedural_optimization) [^10], using profile-guided optimization, and less aggressive inlining.

[^10]: Interprocedural optimizations - [https://en.wikipedia.org/wiki/Interprocedural_optimization](https://en.wikipedia.org/wiki/Interprocedural_optimization).
[^11]: ITLB Overhead - [https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/reference/cpu-metrics-reference/front-end-bound/itlb-overhead.html](https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/reference/cpu-metrics-reference/front-end-bound/itlb-overhead.html)
[^12]: libhugetlbfs guide - [https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO).
