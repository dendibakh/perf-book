## Why Is Software Slow?

If all the software in the world utilized all available hardware resources efficiently, then this book would not exist. We would not need any changes on the software side and would rely on what existing processors have to offer. But you already know that the reality is different, right? The reality is that modern software is *massively* inefficient. A regular server system in a public cloud typically runs poorly optimized code, consuming more power than it could have consumed (increasing carbon emissions and contributing to other environmental issues). If we could make all software run two times faster, we would potentially reduce the carbon footprint of computing by a factor of two.

The authors of the paper [@Leisersoneaam9744] provide an excellent example that illustrates the performance gap between "default" and highly optimized software. Table @tbl:PlentyOfRoom summarizes speedups from performance engineering a program that multiplies two 4096-by-4096 matrices. The end result of applying several optimizations is a program that runs over 60,000 times faster. The reason for providing this example is not to pick on Python or Java (which are great languages), but rather to break beliefs that software has "good enough" performance by default. The majority of programs are within rows 1--5. The potential for source-code-level improvements is significant.

-------------------------------------------------------------
Version   Implementation                 Absolute    Relative 
                                         speedup     speedup

-------   ----------------------------   --------    --------
   1         Python                         1            —

   2          Java                         11          10.8

   3           C                           47           4.4

   4      Parallel loops                   366          7.8

   5      Parallel divide and conquer     6,727        18.4
            
   6       plus vectorization            23,224         3.5
           
   7       plus AVX intrinsics           62,806         2.7

--------------------------------------------------------------

Table: Speedups from performance engineering a program that multiplies two 4096-by-4096 matrices running on a dual-socket Intel Xeon E5-2666 v3 system with a total of 60 GB of memory. From [@Leisersoneaam9744]. {#tbl:PlentyOfRoom}

So, let's talk about what prevents systems from achieving optimal performance by default. Here are some of the most important factors:

1. **CPU limitations**: It's so tempting to ask: "*Why doesn't hardware solve all our problems?*" Modern CPUs execute instructions incredibly quickly, and are getting better with every generation. But still, they cannot do much if instructions that are used to perform the job are not optimal or even redundant. Processors cannot magically transform suboptimal code into something that performs better. For example, if we implement a bubble sort, a CPU will not make any attempts to recognize it and use better alternatives (e.g. quicksort). It will blindly execute whatever it was told to do.
2. **Compiler limitations**: "*But isn't that what compilers are supposed to do? Why don't compilers solve all our problems?*" Indeed, compilers are amazingly smart nowadays, but can still generate suboptimal code. Compilers are great at eliminating redundant work, but when it comes to making more complex decisions like vectorization, they may not generate the best possible code. Performance experts often can come up with clever ways to vectorize loops beyond the capabilities of compilers. When compilers have to make a decision whether to perform a code transformation or not, they rely on complex cost models and heuristics, which may not work for every possible scenario. For example, there is no binary "yes" or "no" answer to the question of whether a compiler should always inline a function into the place where it's called. It usually depends on many factors which a compiler should take into account. Additionally, compilers cannot perform optimizations unless they are certain it is safe to do so. It may be very difficult for a compiler to prove that an optimization is correct under all possible circumstances, disallowing some transformations. Finally, compilers generally do not attempt "heroic" optimizations, like transforming data structures used by a program.
3. **Algorithmic complexity analysis limitations**: Some developers are overly obsessed with algorithmic complexity analysis, which leads them to choose a popular algorithm with the optimal algorithmic complexity, even though it may not be the most efficient for a given problem. Considering two sorting algorithms, insertion sort and quicksort, the latter clearly wins in terms of Big O notation for the average case: insertion sort is O(N^2^) while quickSort is only O(N log N). Yet for relatively small sizes of `N` (up to 50 elements), insertion sort outperforms quickSort. Complexity analysis cannot account for all the low-level performance effects of various algorithms, so people just encapsulate them in an implicit constant `C`, which sometimes can make a large impact on performance. Only counting comparisons and swaps that are used for sorting, ignores cache misses and branch mispredictions, which, today, are actually very costly. Blindly trusting Big O notation without testing on the target workload could lead developers down an incorrect path. So, the best-known algorithm for a certain problem is not necessarily the most performant in practice for every possible input.

In addition to the limitations described above, there are overheads created by programming paradigms. Coding practices that prioritize code clarity, readability, and maintainability can reduce performance. Highly generalized and reusable code can introduce unnecessary copies, runtime checks, function calls, memory allocations, etc. For instance, polymorphism in object-oriented programming is usually implemented using virtual functions, which introduce a performance overhead.[^1]

All the factors mentioned above assess a "performance tax" on the software. There are very often substantial opportunities for tuning the performance of our software to reach its full potential.

[^1]: I do not dismiss design patterns and clean code principles, but I encourage a more nuanced approach where performance is also a key consideration in the development process.
