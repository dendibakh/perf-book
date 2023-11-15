---
typora-root-url: ..\..\img
---

[TODO]: Describe how to measure code footprint

# Machine Code Layout Optimizations {#sec:secFEOpt}

The CPU Front-End (FE) is responsible for fetching and decoding instructions and delivering them to the out-of-order Back-End. As the newer processors get more execution "horsepower", CPU FE needs to be as powerful to keep the machine balanced. If the FE cannot keep up with supplying instructions, the BE will be underutilized, and the overall performance will suffer. That's why the FE is designed to always run well ahead of the actual execution to smooth out any hiccups that may occur and always have instructions ready to be executed. For example, Intel Skylake, released in 2016, can fetch up to 16 instructions per cycle.

Most of the time, inefficiencies in the CPU FE can be described as a situation when the Back-End is waiting for instructions to execute, but the FE is not able to provide them. As a result, CPU cycles are wasted without doing any actual useful work. Recall that modern CPUs can process multiple instructions every cycle, nowadays ranging from 4- to 8-wide. Situations when not all available slots are filled happen very often. This represents a source of inefficiency for applications in many domains, such as databases, compilers, web browsers, and many others. 

The TMA methodology captures FE performance issues in the `Front-End Bound` metric. It represents the percentage of cycles when the CPU FE is not able to deliver instructions to the BE, while it could have accepted them. Most of the real-world applications experience a non-zero 'Front-End Bound' metric, meaning that some percentage of running time will be lost on suboptimal instruction fetching and decoding. Below 10\% is the norm. If you see the "Front-End Bound" metric being more than 20\%, it's definitely worth to spend time on it.

There could be many reasons why FE cannot deliver instructions to the execution units. Most of the time, it is due to suboptimal code layout, whcih leads to the poor I-cache and ITLB utilization. Applications with a large codebase, e.g. millions lines of code, are especially vulnerable to FE performance issues. In this chapter, we will take a look at some typical optimizations to improve machine code layout and increase the overall performance of the program.

## Machine Code Layout

When a compiler translates a source code into machine code, it generates a serial byte sequence. For example, for the following C code:

```cpp
if (a <= b)
  bar();
else
  baz();
```

the compiler can generate machine code like this:

```asm
  ; a is in edi
  ; b is in esi
  cmp esi, edi
  jb .label1
  call bar()
  jmp .label2
.label1:
  call baz()
.label2:
  ...
```

Assembly instructions will be encoded and laid out in memory consequently:

```asm
401125 cmp esi, edi
401128 jb 401131
40112a call bar
40112f jmp 401136
401131 call baz
401136 ...
```

The way code is placed in a binary is called *machine code layout*. Note that for the same program, it's possible to lay out the code in many different ways. For example, compiler may decide to reverse the branch in such a way that in the layout, a call to `baz` will come first. Also, the bodies of the functions `bar` and `baz` can be placed in two different orders: we can place `bar` first in the binary and then `baz` or reverse the order. This affects offsets at which instructions will be placed in memory, which in turn may affect the performance of the generated binary as you will see later. In the next section of this chapter, we will take a look at some typical optimizations for the machine code layout.
