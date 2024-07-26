# Introduction {#sec:chapter1}

[TODO][FIX_BEFORE_REVIEW]: update the intro. It is the most important part of the book. :)

They say, "performance is king". It was true a decade ago, and it certainly is now. According to [@Domo2017], in 2017, the world has been creating 2.5 quintillions[^1] bytes of data every day, and as predicted in [@Statista2018], this number is growing 25% per year. In our increasingly data-centric world, the growth of information exchange fuels the need for both faster software (SW) and faster hardware (HW). The rapid growth of generated data requires not only more computing power but also faster storage and network systems. 

Software programmers have had an "easy ride" for decades, thanks to Moore’s law. It used to be the case that some SW vendors preferred to wait for a new generation of HW to speed up their application and did not spend human resources on making improvements in their code. By looking at Figure @fig:50YearsProcessorTrend, we can see that single-threaded performance growth is slowing down. Single-threaded performance is a performance of a single HW thread inside a CPU core when measured in isolation.

![50 Years of Microprocessor Trend Data. *© Image by K. Rupp via karlrupp.net*. Original data up to the year 2010 collected and plotted by M. Horowitz, F. Labonte, O. Shacham, K. Olukotun, L. Hammond, and C. Batten. New plot and data collected for 2010-2021 by K. Rupp.](../../img/intro/50-years-processor-trend.png){#fig:50YearsProcessorTrend width=100%}

When it's no longer the case that each HW generation provides a significant performance boost, we must start paying more attention to how fast our code runs. When seeking ways to improve performance, developers should not rely on HW. Instead, they should start optimizing the code of their applications.

> “Software today is massively inefficient; it’s become prime time again for software programmers to get really good at optimization.” - Marc Andreessen, the US entrepreneur and investor (a16z Podcast, 2020)

Reaching high-level performance is challenging and usually requires substantial efforts, but hopefully, this book will give you the tools to help you achieve it.

[^1]: Quintillion is a thousand raised to the power of six (10^18^).
[^2]: From the late 1990s to the late 2000s where personal computers where dominating the market of computing devices.
