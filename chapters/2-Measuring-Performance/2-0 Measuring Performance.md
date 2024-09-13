\phantomsection
# Part 1. Performance Analysis on a Modern CPU {.unnumbered}

# Measuring Performance {#sec:secMeasPerf}

The first step to understanding the performance of an application is to measure it. Anyone ever concerned with performance evaluations likely knows how hard it is sometimes to conduct fair performance measurements and draw accurate conclusions from them. Performance measurements can be very unexpected and counterintuitive. Changing a seemingly unrelated part of the source code can surprise us with a significant impact on the performance of the program. For various reasons, measurements may consistently overestimate or underestimate the true performance, which leads to distorted results that do not accurately reflect reality. This phenomenon is called *measurement bias*.

Performance problems are often harder to reproduce and root cause than most functional issues. Every run of a program is usually functionally the same but somewhat different from a performance standpoint. For example, when unpacking a zip file, we get the same result over and over again, which means this operation is reproducible. However, it's impossible to reproduce the same CPU cycle-by-cycle performance profile of this operation.

Conducting fair performance experiments is an essential step towards getting accurate and meaningful results. You need to ensure you're looking at the right problem and are not debugging some unrelated issue. Designing performance tests and configuring the environment are both important components in the process of evaluating performance. 

Because of the measurement bias, performance evaluations often involve statistical methods, which deserve a whole book just for themselves. There are many corner cases and a huge amount of research done in this field. We will not dive into statistical methods for evaluating performance measurements. Instead, we only discuss high-level ideas and give basic directions to follow. We encourage you to research deeper on your own.

In this chapter, we:

- Give a brief introduction to why modern systems yield noisy performance measurements and what you can do about it. 
- Explain why it is important to measure performance in production deployments.
- Provide general guidance on how to properly collect and analyze performance measurements. 
- Explore how to automatically detect performance regressions as you implement changes in your codebase.
- Describe software and hardware timers that can be used by developers in time-based measurements. 
- Discuss how to write a good microbenchmark and some common pitfalls you may encounter while doing it.
