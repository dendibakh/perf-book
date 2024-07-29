## Why Care about Performance?

Modern CPUs are getting more and more cores each year. As of the end of 2019, you can buy a high-end server processor which will have more than 100 logical cores. This is very impressive, but that doesn’t mean we don’t have to care about performance anymore. Very often, application performance might not get better with more CPU cores. Understanding why that happens and possible ways to fix it is critical for the future growth of a product. Not being able to do proper performance analysis and tuning leaves lots of performance and money on the table and can kill the product.

According to [@Leisersoneaam9744], at least in the near term, a large portion of performance gains for most applications will originate from the SW stack. Sadly, applications do not get optimal performance by default. The paper also provides an excellent example that illustrates the potential for performance improvements that could be done on a source code level. Speedups from performance engineering a program that multiplies two 4096-by-4096 matrices are summarized in Table @tbl:PlentyOfRoom. The end result of applying multiple optimizations is a program that runs over 60,000 times faster. The reason for providing this example is not to pick on Python or Java (which are great languages), but rather to break beliefs that software has "good enough" performance by default.

-----------------------------------------------
Version   Implementation   Absolute    Relative 
                           speedup     speedup

-------   --------------   --------    --------
   1         Python           1            —

   2          Java           11          10.8

   3           C             47           4.4

   4      Parallel loops     366          7.8

   5      Parallel divide   6,727        18.4
            and conquer

   6          plus         23,224         3.5
           vectorization

   7        plus AVX       62,806         2.7
           intrinsics

--------------------------------------------------------------

Table: Speedups from performance engineering a program that multiplies two 4096-by-4096 matrices running on a dual-socket Intel Xeon E5-2666 v3 system with a total of 60 GB of memory. From [@Leisersoneaam9744]. {#tbl:PlentyOfRoom}

Here are some of the most important factors that prevent systems from achieving optimal performance by default:

1. **CPU limitations**: it's so tempting to ask: "*Why doesn't HW solve all our problems?"* Modern CPUs execute instructions at incredible speed and are getting better with every generation. But still, they cannot do much if instructions that are used to perform the job are not optimal or even redundant. Processors cannot magically transform suboptimal code into something that performs better. For example, if we implement a sorting routine using BubbleSort algorithm, a CPU will not make any attempts to recognize it and use the better alternatives, for example, QuickSort. It will blindly execute whatever it was told to do.
2. **Compiler limitations**: *"But isn't it what compilers are supposed to do? Why don't compilers solve all our problems?"* Indeed, compilers are amazingly smart nowadays, but can still generate suboptimal code. Compilers are great at eliminating redundant work, but when it comes to making more complex decisions like function inlining, loop unrolling, etc., they may not generate the best possible code. For example, there is no binary "yes" or "no" answer to the question of whether a compiler should always inline a function into the place where it's called. It usually depends on many factors which a compiler should take into account. Often, compilers rely on complex cost models and heuristics, which may not work for every possible scenario. Additionally, compilers cannot perform optimizations unless they are certain it is safe to do so, and it does not affect the correctness of the resulting machine code. It may be very difficult for compiler developers to ensure that a particular optimization will generate correct code under all possible circumstances, so they often have to be conservative and refrain from doing some optimizations. Finally, compilers generally do not transform data structures used by the program, which are also crucial in terms of performance.
3. **Algorithmic complexity analysis limitations**: developers are frequently overly obsessed with complexity analysis of the algorithms, which leads them to choose the popular algorithm with the optimal algorithmic complexity, even though it may not be the most efficient for a given problem. Considering two sorting algorithms, InsertionSort and QuickSort, the latter clearly wins in terms of Big O notation for the average case: InsertionSort is O(N^2^) while QuickSort is only O(N log N). Yet for relatively small sizes of `N` (up to 50 elements), InsertionSort outperforms QuickSort. Complexity analysis cannot account for all the branch prediction and caching effects of various algorithms, so people just encapsulate them in an implicit constant `C`, which sometimes can make drastic impact on performance. Blindly trusting Big O notation without testing on the target workload could lead developers down an incorrect path. So, the best-known algorithm for a certain problem is not necessarily the most performant in practice for every possible input. 

[TODO][FIX_BEFORE_REVIEW]: include discussion on "Clean code, horrible performance"?

Limitations described above leave the room for tuning the performance of our SW to reach its full potential. Broadly speaking, the SW stack includes many layers, e.g., firmware, BIOS, OS, libraries, and the source code of an application. But since most of the lower SW layers are not under our direct control, a major focus will be made on the source code. 

Another important piece of SW that we will touch on a lot is a compiler. It's possible to obtain attractive speedups by making the compiler generate the desired machine code through various hints. You will find many such examples throughout the book. Luckily, most of the time, you don't have to be a compiler expert to drive performance improvements in your application. Majority of optimizations can be done at a source code level without the need to dig down into compiler sources. Although, understanding how the compiler works and how you can force it to do what you want is always advantageous in performance-related work.

According to [@Leisersoneaam9744], the other two sources of potential speedups in the future will be algorithms (especially for new problem domains like machine learning) and streamlined hardware design. Algorithms obviously play a big role in performance of an application, but we will not cover this topic in this book. We will not be discussing hardware design either since, most of the time, SW developers have to deal with existing HW.

> "During the post-Moore era, it will become ever more important to make code run fast and, in particular, to tailor it to the hardware on which it runs." [@Leisersoneaam9744]

The methodologies in this book focus on squeezing out the last bit of performance from your application. Such transformations can be attributed along rows 6 and 7 in Table @tbl:PlentyOfRoom. The types of improvements that will be discussed are usually not big and often do not exceed 10%. However, do not underestimate the importance of a 10% speedup. SQLite is commonplace today not because its developers sat one day and decided to make it 50% faster. But because they meticulously made hundreds of 0.1% improvements over the years. The cumulative effect of these small improvements is what makes the difference.

The impact of small improvements is very relevant for large distributed applications running in the cloud. According to [@HennessyGoogleIO], in the year 2018, Google spent roughly the same amount of money on actual computing servers that run the cloud as it spent on power and cooling infrastructure. Energy efficiency is a very important problem, which can be improved by optimizing SW.

>  "At such scale, understanding performance characteristics becomes critical – even small improvements in performance or utilization can translate into immense cost savings." [@GoogleProfiling]

With the advent of cloud computing, the costs of slow software are put back on the owners of that software, not on their users. Because now, owners are paying cloud bills, not the users. 
[TODO][FIX_BEFORE_REVIEW]: include stats about cloud spending.

For many years performance engineering was a nerdy niche, but now it's becoming mainstream. Many companies have already realized the importance of performance engineering and are willing to pay well for this work.

There is a famous quote: "Premature optimization is the root of all evil". But the opposite is often true as well. Postponed performance engineering work may be too late and cause as much evil as premature optimization. For developers working with performance-critical projects, it is crucial to know how underlying HW works. In such industries, it is a fail-from-the-start when a program is being developed without HW focus. Performance characteristics of a software must be a first-class-citizen along with correctness and security starting from day 1. ClickHouse DB is an example of a successful software product that was built around a small but very efficient kernel.