## Why Software Is Slow?

If all the software in the world would magically start utilizing all available hardware resources efficiently, then this book would not exist. We would not need any changes on the software side and would rely on what existing processors have to offer. But you already know that the reality is different, right? The reality is that modern software is *massively* inefficient. A regular server system in a public cloud, typically runs poorly optimized code, consuming more power than it could have consumed, which increases carbon emissions and contributes to other environmental issues.

The authors of paper [@Leisersoneaam9744] provide an excellent example that illustrates the performance gap between "default" and highly-optimized software. Table @tbl:PlentyOfRoom summarizes speedups from performance engineering a program that multiplies two 4096-by-4096 matrices. The end result of applying several optimizations is a program that runs over 60,000 times faster. The reason for providing this example is not to pick on Python or Java (which are great languages), but rather to break beliefs that software has "good enough" performance by default. Majority of programs are within rows 1-5. The potential of source-code-level improvements is significant.

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

So, let's talk about what prevent systems from achieving optimal performance by default. Here are some of the most important factors:

1. **CPU limitations**: it's so tempting to ask: "*Why doesn't HW solve all our problems?*" Modern CPUs execute instructions at incredible speed and are getting better with every generation. But still, they cannot do much if instructions that are used to perform the job are not optimal or even redundant. Processors cannot magically transform suboptimal code into something that performs better. For example, if we implement a sorting routine using BubbleSort algorithm, a CPU will not make any attempts to recognize it and use better alternatives, for example, QuickSort. It will blindly execute whatever it was told to do.
2. **Compiler limitations**: "*But isn't it what compilers are supposed to do? Why don't compilers solve all our problems?*" Indeed, compilers are amazingly smart nowadays, but can still generate suboptimal code. Compilers are great at eliminating redundant work, but when it comes to making more complex decisions like vectorization, etc., they may not generate the best possible code. Performance experts often can come up with a clever way to vectorize a loop, which would be extremely hard for a traditional compiler. When compilers have to make a decision to perform a code transformation, they rely on complex cost models and heuristics, which may not work for every possible scenario. For example, there is no binary "yes" or "no" answer to the question of whether a compiler should always inline a function into the place where it's called. It usually depends on many factors which a compiler should take into account. Additionally, compilers cannot perform optimizations unless they are certain it is safe to do so, and it does not affect the correctness of the resulting machine code. It may be very difficult for compiler developers to ensure that a particular optimization will generate correct code under all possible circumstances, so they often have to be conservative and refrain from doing some optimizations. Finally, compilers generally do not attempt "heroic" optimizations, like transforming data structures used by a program.
3. **Algorithmic complexity analysis limitations**: some developers are overly obsessed with algorithmic complexity analysis, which leads them to choose a popular algorithm with the optimal algorithmic complexity, even though it may not be the most efficient for a given problem. Considering two sorting algorithms, InsertionSort and QuickSort, the latter clearly wins in terms of Big O notation for the average case: InsertionSort is O(N^2^) while QuickSort is only O(N log N). Yet for relatively small sizes of `N` (up to 50 elements), InsertionSort outperforms QuickSort. Complexity analysis cannot account for all the branch prediction and caching effects of various algorithms, so people just encapsulate them in an implicit constant `C`, which sometimes can make drastic impact on performance. Blindly trusting Big O notation without testing on the target workload could lead developers down an incorrect path. So, the best-known algorithm for a certain problem is not necessarily the most performant in practice for every possible input. 

[TODO][FIX_BEFORE_REVIEW]: include discussion on "Clean code, horrible performance"?

Limitations described above leave the room for tuning the performance of our SW to reach its full potential. 

## Why Care about Performance?

In addition to the slowing trend of hardware single-threaded performance growth, there are a couple of other business reasons to care about performance. During the PC era,[^3] the costs of slow software were paid by the users, as inefficient software was running on user computers. With the advent of SaaS (software as a service) and cloud computing, the costs of slow software are put back on the software providers, not their users. If you're a SaaS company like Meta or Netflix,[^4] it doesn't matter if you run your service on-premise hardware or you use public cloud, you pay for the electricity your servers consume. Inefficient software cuts right into your margins and market evaluation. According to Synergy Research Group,[^5] worldwide spending on cloud services topped $100 billion in 2020, and according to Gartner,[^6] it will surpass $675 billion in 2024.

For many years performance engineering was a nerdy niche, but now it's becoming mainstream. Many companies have already realized the importance of performance engineering and are willing to pay well for this work.

It is fairly easy to reach performance level 4 in Table @tbl:PlentyOfRoom. In fact, you don't need this book to get there. Write your program in one of the native programming languages, distribute work among multiple threads, pick a good optimizing compiler and you'll get there. Unfortunately, this will only put you halfway to the desired efficiency target.

The methodologies in this book focus on squeezing out the last bit of performance from your application. Such transformations can be attributed along rows 6 and 7 in Table @tbl:PlentyOfRoom. The types of improvements that will be discussed are usually not big and often do not exceed 10%. However, do not underestimate the importance of a 10% speedup. SQLite is commonplace today not because its developers sat one day and decided to make it 50% faster. But because they meticulously made hundreds of 0.1% improvements over the years. The cumulative effect of these small improvements is what makes the difference.

The impact of small improvements is very relevant for large distributed applications running in the cloud. According to [@HennessyGoogleIO], in the year 2018, Google spent roughly the same amount of money on actual computing servers that run the cloud as it spent on power and cooling infrastructure. Energy efficiency is a very important problem, which can be improved by optimizing software.

>  "At such [Google] scale, understanding performance characteristics becomes critical – even small improvements in performance or utilization can translate into immense cost savings." [@GoogleProfiling]

[^3]: From the late 1990s to the late 2000s where personal computers where dominating the market of computing devices.
[^4]: In 2024, Meta uses mostly on-premise cloud, while Netflix uses AWS public cloud.
[^5]: Worldwide spending on cloud services in 2020 - [https://www.srgresearch.com/articles/2020-the-year-that-cloud-service-revenues-finally-dwarfed-enterprise-spending-on-data-centers](https://www.srgresearch.com/articles/2020-the-year-that-cloud-service-revenues-finally-dwarfed-enterprise-spending-on-data-centers)
[^6]: Worldwide spending on cloud services in 2024 - [https://www.gartner.com/en/newsroom/press-releases/2024-05-20-gartner-forecasts-worldwide-public-cloud-end-user-spending-to-surpass-675-billion-in-2024](https://www.gartner.com/en/newsroom/press-releases/2024-05-20-gartner-forecasts-worldwide-public-cloud-end-user-spending-to-surpass-675-billion-in-2024)