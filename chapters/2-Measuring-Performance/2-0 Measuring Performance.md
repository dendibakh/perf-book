\phantomsection
# Part 1. Performance Analysis on a Modern CPU {.unnumbered}

# Measuring Performance {#sec:secMeasPerf}

The first step to understand the performance of an application is to measure it. An application can be slow, fast, or anywhere in between. Performance problems are often harder to reproduce and root cause than most functional issues. Every run of a program is usually functionally the same but somewhat different from a performance standpoint. For example, when unpacking a zip file, we get the same result over and over again, which means this operation is reproducible. However, it's impossible to reproduce the same CPU cycle-by-cycle performance profile of this operation.

Anyone ever concerned with performance evaluations likely knows how hard it is sometimes to conduct fair performance measurements and draw accurate conclusions from them. Performance measurements can be very unexpected and counterintuitive. Changing a seemingly unrelated part of the source code can surprise us with a significant impact on the performance of the program. This phenomenon is called measurement bias. Because of the presence of an error in measurements, performance analysis requires statistical methods to process them. This chapter barely scratches the surface since this topic deserves a whole book just by itself. There are many corner cases and a huge amount of research done in this field. We only discuss high-level ideas and give basic directions to follow.

Conducting fair performance experiments is an essential step towards getting accurate and meaningful results. You need to ensure you're looking at the right problem, and are not debugging some unrelated issue. Designing performance tests and configuring the environment are both important components in the process of evaluating performance. 

In this chapter, we:

- Give a brief introduction to why modern systems yield noisy performance measurements and what you can do about it. 
- Explain why it is important to measure performance in production deployments.
- Provide general guidance on how to properly collect and analyze performance measurements. 
- Explore how to automatically detect performance regressions as you implement changes in your codebase.
- Describe software and hardware timers that can be used by developers in time-based measurements. 
- Discuss how to write a good microbenchmark and some common pitfalls you may encounter while doing it.
