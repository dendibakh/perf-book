---
typora-root-url: ..\..\img
---

## Chapter Summary

Summary of CPU Front-End optimizations is presented in table {@tbl:CPU_FE_OPT}.

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
grouping   functions         utilization   hot functions
           together
--------------------------------------------------------------------------

Table: Summary of CPU Front-End optimizations. {#tbl:CPU_FE_OPT}

\personal{I think code layout improvements are often underestimated and end up being omitted and forgotten. I agree that you might want to start with low hanging fruits like loop unrolling and vectorization opportunities. But knowing that you might get an extra 5-10\% just from better laying out the machine code is still useful. It is usually the best option to use PGO if you can come up with a set of typical use cases for your application.}
