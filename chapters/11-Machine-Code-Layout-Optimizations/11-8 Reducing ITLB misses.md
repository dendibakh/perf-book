---
typora-root-url: ..\..\img
---

## Reducing ITLB Misses {#sec:FeTLB}

Another important area of tuning FE efficiency is virtual-to-physical address translation of memory addresses. Primarily those translations are served by TLB (see [@sec:TLBs]), which caches most recently used memory page translations in dedicated entries. When TLB cannot serve the translation request, a time-consuming page walk of the kernel page table takes place to calculate the correct physical address for each referenced virtual address. Whenever you see a high percentage of [ITLB Overhead](https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/reference/cpu-metrics-reference/front-end-bound/itlb-overhead.html) [^11] in the Top-Down summary, the advice in this section may become handy. 

In general, relatively small applications are not susceptible to ITLB misses. For example, Golden Cove microarchitecture can cover memory space up to 1MB in its ITLB. If machine code of your application fits in 1MB you should not be affected by ITLB misses. The problem start to appear when frequently executed parts of an application are scattered around the memory. When many functions begin to frequently call each other, they start competing for the entries in the ITLB. One of the examples is the Clang compiler, which at the time of writing, has 
a code section of ~60MB. ITLB overhead running on a laptop with a mainstream Intel CoffeeLake processor is ~7%, which means that 7% of cycles are wasted handling ITLB misses: doing demanding page walks and populating TLB entries.

Another set of large memory applications that frequently benefit from using huge pages include relational databases (e.g., MySQL, PostgreSQL, Oracle), managed runtimes (e.g. Javascript V8, Java JVM), cloud services (e.g. web search), web tooling (e.g. node.js). Mapping code sections onto the huge pages can reduce the number of ITLB misses by up to 50% [@IntelBlueprint], which yields speedups of up to 10% for some applications. However, as it is with many other features, huge pages are not for every application. Small programms with an executable file of only a few KB in size would be better off using regular 4KB pages rather than 2MB huge pages; that way, memory is used more efficiently.

The general idea of reducing ITLB pressure is by mapping the portions of the performance-critical code of an application onto 2MB (huge) pages. But usually, the entire code section of an application gets remapped for simplicity or if you don't know which functions are hot. The key requirement for that transformation to happen is to have code section aligned on 2MB boundary. When on Linux, this can be achieved in two different ways: relinking the binary with additional linker option or remapping the code sections at runtime. Both options are showcased on easyperf.net[^1] blog.

**TODO: how to do it on Windows?**

The first option can be achieved by linking the binary with `-Wl,-zcommon-page-size=2097152 -Wl,-zmax-page-size=2097152` options. These options instruct the linker to place the code section at the 2MB boundary in preparation for it to be placed on 2MB pages by the loader at startup. The downside of such placement is that linker will be forced to insert up to 2MB of padded (wasted) bytes, bloating the binary even more. In the example with Clang compiler, it increased the size of the binary from 111 MB to 114 MB. After relinking the binary, we  that determines if the text segment should be backed by default with huge pages. The simplest ways to do it is using the `hugeedit` or `hugectl` utilities from [libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO)[^12] package. For example:

```bash
# Permanently set a special bit in the ELF binary header.
$ hugeedit --text /path/to/clang++
# Code section will be loaded using huge pages by default.
$ /path/to/clang++ a.cpp

# Overwrite default behavior at runtime.
$ hugectl --text /path/to/clang++ a.cpp
```

The second option is to remap the code section at runtime. This option does not require the code section to be aligned to 2MB boundary, thus can work without recompiling the application. This is especially useful when you don’t have access to the source code. The idea behind this method is to allocate huge pages at the startup of the program and transfer all the code section there. The reference implementation of that approach is implemented in the [iodlr](https://github.com/intel/iodlr)[^2]. One option would be to call that functionality from your `main` function. Another option, which is simpler, to build the dynamic library and preload it in the command line:

```bash
$ LD_PRELOAD=/usr/lib64/liblppreload.so clang++ a.cpp
```

While the first method only works with explicit huge pages, the second approach which uses `iodlr` works both with explicit and transparent huge pages. Instructions on how to enable huge pages for Windows and Linux can be found in appendix C.

Besides from employing huge pages, standard techniques for optimizing I-cache performance can be used for improving ITLB performance. Namely, reordering functions so that hot functions are collocated better, reducing the size of hot regions via Link-Time Optimizations (LTO/IPO), using Profile-Guided Optimizations (PGO), and less aggressive inlining.

[^1]: "Performance Benefits of Using Huge Pages for Code" - [https://easyperf.net/blog/2022/09/01/Utilizing-Huge-Pages-For-Code](https://easyperf.net/blog/2022/09/01/Utilizing-Huge-Pages-For-Code).
[^2]: iodlr library - [https://github.com/intel/iodlr](https://github.com/intel/iodlr).
[^11]: ITLB Overhead - [https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/reference/cpu-metrics-reference/front-end-bound/itlb-overhead.html](https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/reference/cpu-metrics-reference/front-end-bound/itlb-overhead.html)
[^12]: libhugetlbfs - [https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO).
