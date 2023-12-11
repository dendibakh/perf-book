---
typora-root-url: ..\..\img
---

## Chapter Summary {.unlisted .unnumbered}

Summary of CPU Front-End optimizations is presented in Table {@tbl:CPU_FE_OPT}.

--------------------------------------------------------------------------
Transform  How transformed?  Why helps?    Works best for        Done by
---------  ----------------  ------------  --------------------  ---------
Basic      maintain          not taken     any code, especially  compiler
block      fall through      branches are  with a lot of 
placement  hot code          cheaper;      branches
                             better cache
                             utilization

Basic      shift the hot     better cache  hot loops             compiler
block      code using NOPS   utilization 
alignment

Function   split cold        better cache  functions with        compiler
splitting  blocks of code    utilization   complex CFG when 
           and place them                  there are big blocks 
           in separate                     of cold code between 
           functions                       hot parts

Function   group hot         better cache  many small            linker
reorder    functions         utilization   hot functions
           together
--------------------------------------------------------------------------

Table: Summary of CPU Front-End optimizations. {#tbl:CPU_FE_OPT}

* Code layout improvements are often underestimated and end up being omitted and forgotten. CPU Front-End performance issues like I-cache and ITLB misses represent a large portion of wasted cycles, especially for applications with large codebases. But even small- and medium-sized applications can benefit from optimizing the machine code layout.
* It is usually not the first thing developers turn their attention to when trying to improve the performance of their application. They prefer to start with low hanging fruits like loop unrolling and vectorization. However, knowing that you might get an extra 5-10\% just from better machine code layout is still useful.
* It is usually the best option to use LTO, PGO, BOLT, and other tools if you can come up with a set of typical use cases for your application. For large applications, it is the only practical way to improve machine code layout.

\sectionbreak
