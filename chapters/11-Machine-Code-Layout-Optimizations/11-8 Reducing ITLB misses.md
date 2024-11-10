## Reducing ITLB Misses {#sec:FeTLB}

Another important area of tuning Frontend efficiency is the virtual-to-physical address translation of memory addresses. Primarily those translations are served by the TLB (see [@sec:TLBs]), which caches the most recently used memory page translations in dedicated entries. When TLB cannot serve the translation request, a time-consuming page walk of the kernel page table takes place to calculate the correct physical address for each referenced virtual address. Whenever you see a high percentage of ITLB overhead in the TMA summary, the advice in this section may become handy. 

In general, relatively small applications are not susceptible to ITLB misses. For example, Golden Cove microarchitecture can cover memory space up to 1MB in its ITLB. If the machine code of your application fits in 1MB you should not be affected by ITLB misses. The problem starts to appear when frequently executed parts of an application are scattered around in memory. When many functions begin to frequently call each other, they start competing for the entries in the ITLB. One of the examples is the Clang compiler, which at the time of writing, has a code section of ~60MB. ITLB overhead running on a laptop with a mainstream Intel Coffee Lake processor is ~7%, which means that 7% of cycles are spent handling ITLB misses: doing demanded page walks and populating TLB entries.

Another set of large memory applications that frequently benefit from using huge pages include relational databases (e.g., MySQL, PostgreSQL, Oracle), managed runtimes (e.g., JavaScript V8, Java JVM), cloud services (e.g., web search), web tooling (e.g., node.js).

The general idea of reducing ITLB pressure is to map the portions of the performance-critical code of an application onto 2MB (huge) pages. Usually, the entire code section of an application gets remapped for simplicity. The key requirement for that transformation to happen is to have the code section aligned on a 2MB boundary. When on Linux, this can be achieved in two different ways: relinking the binary with an additional linker option or remapping the code sections at runtime. Both options are showcased on the Easyperf[^1] blog. To the best of my knowledge, it is not possible on Windows, so I will only show how to do it on Linux.

The first option can be achieved by linking the binary with the following options: `-Wl,-zcommon-page-size=2097152` `-Wl,-zmax-page-size=2097152`. These options instruct the linker to place the code section at the 2MB boundary in preparation for it to be placed on 2MB pages by the loader at startup. The downside of such placement is that the linker will be forced to insert up to 2MB of padded (wasted) bytes, bloating the binary even more. In the example with the Clang compiler, it increased the size of the binary from 111 MB to 114 MB. After relinking the binary, we set a special bit in the ELF binary header that determines if the text segment should be backed with huge pages by default. The simplest way to do it is using the `hugeedit` or `hugectl` utilities from [libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO)[^12] package. For example:

```bash
# Permanently set a special bit in the ELF binary header.
$ hugeedit --text /path/to/clang++
# Code section will be loaded using huge pages by default.
$ /path/to/clang++ a.cpp

# Overwrite default behavior at runtime.
$ hugectl --text /path/to/clang++ a.cpp
```

The second option is to remap the code section at runtime. This option does not require the code section to be aligned to a 2MB boundary and thus can work without recompiling the application. This is especially useful when you don’t have access to the source code. The idea behind this method is to allocate huge pages at the startup of the program and transfer the code section there. The reference implementation of that approach is implemented in the [iodlr](https://github.com/intel/iodlr)[^2] library. One option would be to call that functionality from your `main` function. Another option, which is simpler, is to build the dynamic library and preload it in the command line:

```bash
$ LD_PRELOAD=/usr/lib64/liblppreload.so clang++ a.cpp
```

While the first method only works with explicit huge pages, the second approach which uses `iodlr` works both with explicit and transparent huge pages. Instructions on how to enable huge pages for Windows and Linux can be found in Appendix B.

Mapping code sections onto huge pages can reduce the number of ITLB misses by up to 50% [@IntelBlueprint], which yields speedups of up to 10% for some applications. However, as it is with many other features, huge pages are not for every application. Small programs with an executable file of only a few KB in size would be better off using regular 4KB pages rather than 2MB huge pages; that way, memory is used more efficiently.

Besides employing huge pages, standard techniques for optimizing I-cache performance can be used to improve ITLB performance. Namely, reordering functions so that hot functions are collocated better, reducing the size of hot regions via Link-Time Optimizations (LTO/IPO), using Profile-Guided Optimizations (PGO) and BOLT, and less aggressive inlining.

BOLT provides the `-hugify` option to automatically use huge pages for hot code based on profile data. When this option is used, `llvm-bolt` will inject the code to put hot code on 2MB pages at runtime. The implementation leverages Linux Transparent Huge Pages (THP). The benefit of this approach is that only a small portion of the code is mapped to the huge pages and the number of required huge pages is minimized, and as a consequence, page fragmentation is reduced. 

[^1]: "Performance Benefits of Using Huge Pages for Code" - [https://easyperf.net/blog/2022/09/01/Utilizing-Huge-Pages-For-Code](https://easyperf.net/blog/2022/09/01/Utilizing-Huge-Pages-For-Code).
[^2]: iodlr library, Linux-only - [https://github.com/intel/iodlr](https://github.com/intel/iodlr).
[^12]: libhugetlbfs - [https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO).
