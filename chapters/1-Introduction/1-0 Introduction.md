# Introduction {#sec:chapter1}

Performance is king: this was true a decade ago, and it certainly is now. According to [@Domo2017], in 2017, the world has been creating 2.5 quintillion[^1] bytes of data every day. [@Statista2024] predicts 400 quintillion bytes per day in 2024. In our increasingly data-centric world, the growth of information exchange requires both faster software and faster hardware.

Software programmers have had an "easy ride" for decades, thanks to Moore’s law. Software vendors could rely on new generations of hardware to speed up their software products, even if they did not spend human resources on making improvements. By looking at Figure @fig:50YearsProcessorTrend, we can see that single-threaded[^2] performance growth is slowing down. From 1990 to 2000, single-threaded performance on SPECint benchmarks increased by a factor of approximately 25 to 30, driven largely by higher CPU frequencies and improved microarchitecture.

![50 Years of Microprocessor Trend Data. *© Image by K. Rupp via karlrupp.net*. Original data up to the year 2010 was collected and plotted by M. Horowitz, F. Labonte, O. Shacham, K. Olukotun, L. Hammond, and C. Batten. New plot and data collected for 2010-2021 by K. Rupp.](../../img/intro/50-years-processor-trend.png){#fig:50YearsProcessorTrend width=100%}

Single-threaded CPU performance growth was more modest from 2000 to 2010 (a factor between four and five). Clock speeds topped out around 4GHz due to power consumption, heat dissipation challenges, limitations in voltage scaling (Dennard Scaling[^3]), and other fundamental problems. Architectural advancements continued: better branch prediction, deeper pipelines, larger caches, prefetching, and more efficient execution units.

From 2010 to 2020, single-threaded performance grew only by a factor between two and three. Multicore processors entered the mainstream during this decade, as did simultaneous multithreading. 

Transistor counts continue to increase in modern processors. Apple's M1 shipped in 2020 with 16 billion transistors. M2 made use of 20, M3 included 25, and 2024's M4 employs 28 billion transistors, a fifty percent increase over four years. The growth in transistor count enables manufacturers to add more cores to a processor. Intel's Sierra Forest dies are expected to boast a formidable 288 cores each. This is very impressive. Unfortunately, it doesn't always translate into better performance. Very often, application performance doesn't scale with extra CPU cores.

As it's no longer the case that each hardware generation provides a significant performance boost, we must start paying more attention to our code's efficiency. When seeking ways to improve performance, developers should not rely on hardware. Instead, they should start optimizing the code of their applications.

> “Software today is massively inefficient; it’s become prime time again for software programmers to get really good at optimization.” - Marc Andreessen, the US entrepreneur and investor (a16z Podcast)

[^1]: A quintillion is a thousand raised to the power of six (10^18^).
[^2]: Single-threaded performance is the performance of a single hardware thread inside a CPU core when measured in isolation.
[^3]: Dennard Scaling - [https://en.wikipedia.org/wiki/Dennard_scaling](https://en.wikipedia.org/wiki/Dennard_scaling)
