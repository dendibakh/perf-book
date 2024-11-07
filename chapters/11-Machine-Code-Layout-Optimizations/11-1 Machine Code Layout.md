# Machine Code Layout Optimizations {#sec:secFEOpt}

The CPU Frontend (FE) is responsible for fetching and decoding instructions and delivering them to the out-of-order Backend (BE). As the newer processors get more execution "horsepower", the CPU FE needs to be as powerful to keep the machine balanced. If the FE cannot keep up with supplying instructions, the BE will be underutilized, and the overall performance will suffer. That's why the FE is designed to always run well ahead of the actual execution to smooth out any hiccups that may occur and always have instructions ready to be executed. For example, Intel Skylake, released in 2016, can fetch up to 16 instructions per cycle.

Most of the time, inefficiencies in the CPU FE can be described as a situation when the Backend is waiting for instructions to execute, but the Frontend is not able to provide them. As a result, CPU cycles are wasted without doing any actual useful work. Recall that modern CPUs can process multiple instructions every cycle, nowadays ranging from 4- to 9-wide. Situations when not all available slots are filled happen very often. This represents a source of inefficiency for applications in many domains, such as databases, compilers, web browsers, and many others.

The TMA methodology captures FE performance issues in the `Frontend Bound` metric. It represents the percentage of cycles when the CPU FE is not able to deliver instructions to the BE, while it could have accepted them. Most of the real-world applications experience a non-zero 'Frontend Bound' metric, meaning that some percentage of running time will be lost on suboptimal instruction fetching and decoding. Below 10\% is the norm. If you see the "Frontend Bound" metric being more than 20\%, it's worth spending time on it.

There could be many reasons why FE cannot deliver instructions to the execution units. Most of the time, it is due to suboptimal code layout, which leads to poor I-cache and ITLB utilization. Applications with a large codebase, e.g., millions of lines of code, are especially vulnerable to FE performance issues. In this chapter, we will take a look at some typical optimizations to improve machine code layout.

## Machine Code Layout

When a compiler translates source code into machine code, it generates a linear byte sequence. [@lst:MachineCodeLayout] shows an example of a binary layout for a small snippet of C++ code. Once the compiler finishes generating assembly instructions, it needs to encode them and lay them out in memory sequentially.

Listing: Example of machine code layout

~~~~ {#lst:MachineCodeLayout .cpp}
  C++ Code      │    Assembly Listing     │    Disassembled Machine Code
  ........      │    ................     │    ......................... 
if (a <= b)     │     ; a is in edi       │    401125 cmp esi, edi
  bar();        │     ; b is in esi       │    401128 jb 401131
else            │     cmp esi, edi        │    40112a call bar
  baz();        │     jb .label1          │    40112f jmp 401136
                │     call bar()          │    401131 call baz
                │     jmp .label2         │    401136 ...
                │   .label1:              │
                │     call baz()          │
                │   .label2:              │
                │     ...                 │
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The way code is placed in an object file is called *machine code layout*. Note that for the same program, it's possible to lay out the code in many different ways. For the code in [@lst:MachineCodeLayout], a compiler may decide to reverse the branch in such a way that a call to `baz` will come first. Also, bodies of the functions `bar` and `baz` can be placed in two different orders: we can place `bar` first in the executable image and then `baz` or reverse the order. This affects offsets at which instructions will be placed in memory, which in turn may affect the performance of the generated program as you will see later. In the following sections of this chapter, we will take a look at some typical optimizations for the machine code layout.
