---
typora-root-url: ..\..\img
---

# Part1. Performance analysis on a modern CPU {.unnumbered}

# Measuring Performance {#sec:secMeasPerf}

The first step on the path to understanding an application's performance is knowing how to measure it. Some people attribute performance as one of the features of the application[^15]. But unlike other features, performance is not a boolean property: applications always have some level of performance. This is why it's impossible to answer "yes" or "no" to the question of whether an application has the performance. 

Performance problems are usually harder to track down and reproduce than most functional issues[^10]. Every run of the benchmark is different from each other.  For example, when unpacking a zip-file, we get the same result over and over again, which means this operation is reproducible[^16]. However, it's impossible to reproduce exactly the same performance profile of this operation.

Anyone ever concerned with performance evaluations likely knows how hard it is to conduct fair performance measurements and draw accurate conclusions from it. Performance measurements sometimes can be very much unexpected. Changing a seemingly unrelated part of the source code can surprise us with a significant impact on program performance. This phenomenon is called measurement bias. Because of the presence of error in measurements, performance analysis requires statistical methods to process them. This topic deserves a whole book just by itself. There are many corner cases and a huge amount of research done in this field. We will not go all the way down this rabbit hole. Instead, we will just focus on high-level ideas and directions to follow.

Conducting fair performance experiments is an essential step towards getting accurate and meaningful results. Designing performance tests and configuring the environment are both important components in the process of evaluating performance. This chapter will give a brief introduction to why modern systems yield noisy performance measurements and what you can do about it. We will touch on the importance of measuring performance in real production deployments. 

Not a single long-living product exists without ever having performance regressions. This is especially important for large projects with lots of contributors where changes are coming at a very fast pace. This chapter devotes a few pages discussing the automated process of tracking performance changes in Continuous Integration and Continuous Delivery (CI/CD) systems. We also present general guidance on how to properly collect and analyze performance measurements when developers implement changes in their source codebase.

The end of the chapter describes SW and HW timers that can be used by developers in time-based measurements and common pitfalls when designing and writing a good microbenchmark.

[^10]: Sometimes, we have to deal with non-deterministic and hard to reproduce bugs, but it's not that often.
[^15]: Blog post by Nelson Elhage "Reflections on software performance": [https://blog.nelhage.com/post/reflections-on-performance/](https://blog.nelhage.com/post/reflections-on-performance/).
[^16]: Assuming no data races.
