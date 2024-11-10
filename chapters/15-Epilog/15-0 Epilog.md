\phantomsection
# Epilog {.unnumbered}

\markboth{Epilog}{Epilog}

Thanks for reading through the whole book. I hope you enjoyed it and found it useful. I would be even happier if the book would help you solve a real-world problem. In such a case, I would consider it a success and proof that my efforts were not wasted. Before you continue with your endeavors, let me briefly highlight the essential points of the book and give you final recommendations:

* Modern software is massively inefficient. There are significant optimization opportunities to reduce carbon emissions and make a better user experience. People hate using slow software, especially when their productivity goes down because of it. Not all fast software is world-class, but all world-class software is fast. Performance is _the_ killer feature.
* Single-threaded CPU performance is not increasing as rapidly as it used to a few decades ago. When it's no longer the case that each hardware generation provides a significant performance boost, developers should start optimizing the code of their software.
* For many years performance engineering was a nerdy niche. But now it is mainstream as software vendors have realized the impact that their poorly optimized software has on their bottom line. Performance tuning is more critical than it has been for the last 40 years. It will be one of the key drivers for performance gains in the near future.
* The importance of low-level performance tuning should not be underestimated, even if it's just a 1% improvement. The cumulative effect of these small improvements is what makes a difference.
* There is a famous quote by Donald Knuth: "Premature optimization is the root of all evil".[@Knuth1974StructuredPW] The opposite is often true as well. Postponed performance engineering work may be too late and cause as much evil as premature optimization. Do not neglect performance aspects when designing your future products. Save your project by integrating automated performance benchmarking into your CI/CD pipeline. *Measure early, measure often.*
* Knowledge of the CPU microarchitecture is required to reach peak performance. However, your mental model can never be as accurate as the actual microarchitecture design of a CPU. So don't solely rely on your intuition when you make a specific change in your code. Predicting the performance of a particular piece of code is nearly impossible. *Always measure!*
* When measuring performance, understand the underlying technical reasons for the performance results you observe. Always measure one level deeper and collect as many metrics as possible to support your conclusions.
* Performance engineering is hard because there are no predetermined steps you should follow, no algorithm. Engineers need to tackle problems from different angles. Know performance analysis methods and tools (both hardware and software) available to you. I strongly suggest embracing the Top-down Microarchitecture Analysis (TMA) methodology. It will help you steer your work in the right direction. 
* When you identify the performance-limiting factor of your application, you are more than halfway through. Based on my experience, the fix is often easier than finding the root cause of the problem.
In Part 2 we covered some essential optimizations for every type of CPU performance bottleneck: how to optimize memory accesses and computations, how to get rid of branch mispredictions, how to improve machine code layout, and several others. Use chapters from Part 2 as a reference to see what options are available when your application has one of these problems.
* Processors from different vendors are not created equal. They differ in terms of instruction set architecture (ISA) supported and microarchitectural implementation. Reaching peak performance on a given platform requires utilizing the latest ISA extensions, avoiding common microarchitecture-specific issues, and tuning your code according to the strengths of a particular CPU microarchitecture.
* Multithreaded programs add one more dimension of complexity to performance tuning. They introduce new types of bottlenecks and require additional tools and methods to analyze and optimize. Examining how an application scales with the number of threads is an effective way to identify bottlenecks in multithreaded programs.

I hope you now have a better understanding of low-level performance optimizations. Of course, this book doesn't cover every possible scenario you may encounter in your daily job. My goal was to give you a starting point and to show you potential options and strategies for dealing with performance analysis and tuning on modern CPUs. I wish you experience the joy of discovering performance bottlenecks in your application and the satisfaction of fixing them.

**Happy performance tuning!**

[TODO]: link
I will post errata and other information about the book on my blog .

If you haven't solved the `perf-ninja` exercises yet, I encourage you to take the time to do so. They will help you to solidify your knowledge and prepare you for real-world performance engineering challenges.

P.S. If you enjoyed reading this book, make sure to pass it on to your friends and colleagues. I would appreciate your help in spreading the word about the book by endorsing it on social media platforms.
