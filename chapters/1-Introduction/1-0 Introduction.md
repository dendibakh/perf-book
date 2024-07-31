# Introduction {#sec:chapter1}

They say, "Performance is king". It was true a decade ago, and it certainly is now. According to [@Domo2017], in 2017, the world has been creating 2.5 quintillion[^1] bytes of data every day, and as predicted in [@Statista2018], it will reach 400 quintillion bytes per day in 2024. In our increasingly data-centric world, the growth of information exchange fuels the need for both faster software (SW) and faster hardware (HW).

Software programmers have had an "easy ride" for decades, thanks to Moore’s law. It used to be the case that some SW vendors preferred to wait for a new generation of HW to speed up their software products and did not spend human resources on making improvements in the code. By looking at Figure @fig:50YearsProcessorTrend, we can see that single-threaded[^2] performance growth is slowing down.

![50 Years of Microprocessor Trend Data. *© Image by K. Rupp via karlrupp.net*. Original data up to the year 2010 was collected and plotted by M. Horowitz, F. Labonte, O. Shacham, K. Olukotun, L. Hammond, and C. Batten. New plot and data collected for 2010-2021 by K. Rupp.](../../img/intro/50-years-processor-trend.png){#fig:50YearsProcessorTrend width=100%}

The original interpretation of Moore's law is still standing, though, as transistor count in modern processors maintains its trajectory. For instance, the number of transistors in Apple chips grew from 16 billion in M1 to 20 billion in M2, to 25 billion in M3, to 28 billion in M4 in a span of roughly four years. The growth in transistor count enables manufacturers to add more cores to a processor. As of 2024, you can buy a high-end server processor that will have more than 100 logical cores on a single CPU socket. This is very impressive, unfortunately, it doesn't always translate into better performance. Very often, application performance doesn't scale with extra CPU cores.

When it's no longer the case that each HW generation provides a significant performance boost, we must start paying more attention to how fast our code runs. When seeking ways to improve performance, developers should not rely on HW. Instead, they should start optimizing the code of their applications.

> “Software today is massively inefficient; it’s become prime time again for software programmers to get really good at optimization.” - Marc Andreessen, the US entrepreneur and investor (a16z Podcast)

[^1]: A quintillion is a thousand raised to the power of six (10^18^).
[^2]: Single-threaded performance is the performance of a single HW thread inside a CPU core when measured in isolation.
