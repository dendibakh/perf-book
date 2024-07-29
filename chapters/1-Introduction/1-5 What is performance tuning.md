## What Is Performance Tuning?

Locating a performance bottleneck is only half of the engineer’s job. The second half is to fix it properly. Sometimes changing one line in the program source code can yield a drastic performance boost. Performance analysis and tuning are all about how to find and fix this line. Missing such opportunities can be a big waste.

[TODO][FIX_BEFORE_REVIEW]: Talk about mechanical sympathy

[TODO][FIX_BEFORE_REVIEW]: Update that we are now in the beginning of a new era. PC -> mobile -> cloud -> AI?

In the PC era,[^3] developers usually were programming directly on top of the operating system, with possibly a few libraries in between. As the world moved to the cloud era, the SW stack got deeper and more complex. The top layer of the stack on which most developers are working has moved further away from the HW. Those additional layers abstract away the actual HW, which allows using new types of accelerators for emerging workloads. However, the negative side of such evolution is that developers of modern applications have less affinity to the actual HW on which their SW is running. 

Leftover:

According to [@Leisersoneaam9744], at least in the near term, a large portion of performance gains for most applications will originate from the SW stack. The other two sources of potential speedups in the future will be algorithms (especially for new problem domains like machine learning) and streamlined hardware design. Algorithms obviously play a big role in performance of an application, but we will not cover this topic in this book. We will not be discussing hardware design either since, most of the time, SW developers have to deal with existing HW.

> "During the post-Moore era, it will become ever more important to make code run fast and, in particular, to tailor it to the hardware on which it runs." [@Leisersoneaam9744]

Understanding why that happens and possible ways to fix it is critical for the future growth of a product. Not being able to do proper performance analysis and tuning leaves lots of performance and money on the table and can kill the product.

Broadly speaking, the SW stack includes many layers, e.g., firmware, BIOS, OS, libraries, and the source code of an application. But since most of the lower SW layers are not under our direct control, a major focus will be made on the source code. 

Another important piece of SW that we will touch on a lot is a compiler. It's possible to obtain attractive speedups by making the compiler generate the desired machine code through various hints. You will find many such examples throughout the book. Luckily, most of the time, you don't have to be a compiler expert to drive performance improvements in your application. Majority of optimizations can be done at a source code level without the need to dig down into compiler sources. Although, understanding how the compiler works and how you can force it to do what you want is always advantageous in performance-related work.

There is a famous quote: "Premature optimization is the root of all evil". But the opposite is often true as well. Postponed performance engineering work may be too late and cause as much evil as premature optimization. For developers working with performance-critical projects, it is crucial to know how underlying HW works. In such industries, it is a fail-from-the-start when a program is being developed without HW focus. Performance characteristics of a software must be a first-class-citizen along with correctness and security starting from day 1. ClickHouse DB is an example of a successful software product that was built around a small but very efficient kernel.
