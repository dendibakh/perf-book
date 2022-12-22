---
typora-root-url: ..\..\img
---

## Basic block alignment

Sometimes performance can significantly change depending on the offset at which instructions are laid out in memory. Consider a simple function presented in [@lst:LoopAlignment].

Listing: Basic block alignment

~~~~ {#lst:LoopAlignment .cpp}
void benchmark_func(int* a) {
  for (int i = 0; i < 32; ++i)
    a[i] += 1;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A decent optimizing compiler might come up with machine code for Skylake architecture that may look like below:

```bash
00000000004046a0 <_Z14benchmark_funcPi>:
  4046a0:  mov    rax,0xffffffffffffff80
  4046a7:  vpcmpeqd ymm0,ymm0,ymm0
  4046ab:  nop    DWORD PTR [rax+rax*1+0x0]
  4046b0:  vmovdqu ymm1,YMMWORD PTR [rdi+rax*1+0x80] # loop begins
  4046b9:  vpsubd ymm1,ymm1,ymm0
  4046bd:  vmovdqu YMMWORD PTR [rdi+rax*1+0x80],ymm1
  4046c6:  add    rax,0x20
  4046ca:  jne    4046b0                             # loop ends
  4046cc:  vzeroupper 
  4046cf:  ret 
```

The code itself is pretty reasonable[^4] for Skylake architecture, but its layout is not perfect (see Figure @fig:Loop_default). Instructions that correspond to the loop are highlighted in yellow. As well as for data caches, instruction cache lines are usually 64 bytes long. On Figure @fig:LoopLayout thick boxes denote cache line borders. Notice that the loop spans multiple cache lines: it begins on the cache line `0x80 - 0xBF` and ends in the cache-line `0xC0 - 0xFF`. Those kinds of situations usually cause performance problems for the CPU Front-End, especially for the small loops like presented above.

To fix this, we can shift the loop instructions forward by 16 bytes using NOPs so that the whole loop will reside in one cache line. Figure @fig:Loop_better shows the effect of doing this with NOP instructions highlighted in blue. Note that since the benchmark runs nothing but this hot loop, it is pretty much guaranteed that both cache lines will remain in L1I-cache. The reason for the better performance of the layout @fig:Loop_better is not trivial to explain and will involve a fair amount of microarchitectural details[^1], which we will avoid in this book.

<div id="fig:LoopLayout">
![default layout](../../img/cpu_fe_opts/LoopAlignment_Default.png){#fig:Loop_default width=90%}

![improved layout](../../img/cpu_fe_opts/LoopAlignment_Better.png){#fig:Loop_better width=90%}

Two different alignments for the loop.
</div>

Even though CPU architects try hard to hide such kind of bottlenecks in their designs, there are still cases when code placement (alignment) can make a difference in performance. 

By default, the LLVM compiler recognizes loops and aligns them at 16B boundaries, as we saw in Figure @fig:Loop_default. To reach the desired code placement for our example, as shown in Figure @fig:Loop_better, one should use the `-mllvm -align-all-blocks` option[^6]. However, be careful with using this option, as it can easily degrade performance. Inserting NOPs that will be executed can add overhead to the program, especially if they stand on a critical path. NOPs do not require execution; however, they still require to be fetched from memory, decoded, and retired. The latter additionally consumes space in FE data structures and buffers for bookkeeping, similar to all other instructions.

In order to have fine-grained control over alignment, it is also possible to use [`ALIGN`](https://docs.oracle.com/cd/E26502_01/html/E28388/eoiyg.html)[^5] assembler directives. For experimental purposes, the developer can emit assembly listing and then insert the `ALIGN` directive:
```asm
; will place the .loop at the beginning of 256 bytes boundary
ALIGN 256
.loop
  dec rdi
  jnz rdi
```

[^1]: Interested readers can find more information in the article on easyperf blog [Code alignment issues](https://easyperf.net/blog/2018/01/18/Code_alignment_issues).
[^4]: Loop unrolling is disabled for illustrating the idea of the section.
[^5]: x86 assembler directives manual - [https://docs.oracle.com/cd/E26502_01/html/E28388/eoiyg.html](https://docs.oracle.com/cd/E26502_01/html/E28388/eoiyg.html). This example uses MASM. Otherwise, you will see the `.align` directive.
[^6]: For other available options to control code placement, one can take a look at the article on easyperf blog: [Code alignment options in llvm](https://easyperf.net/blog/2018/01/25/Code_alignment_options_in_llvm).
