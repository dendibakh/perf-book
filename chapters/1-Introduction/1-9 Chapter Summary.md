## Chapter Summary {.unlisted .unnumbered}

* Single-threaded CPU performance is not increasing as rapidly as it used to a few decades ago. When it's no longer the case that each hardware generation provides a significant performance boost, developers should start optimizing the code of their software.
* Modern software is massively inefficient. A regular server system in a public cloud, typically runs poorly optimized code, consuming more power than it could have consumed, which increases carbon emissions and contributes to other environmental issues.
* Certain limitations exist that prevent applications from reaching their full performance potential. CPUs cannot magically speed up slow algorithms. Compilers are far from generating optimal code for every program. BigO notation is not always a good indicator of performance as it doesn't account for hardware specifics.
* For many years performance engineering was a nerdy niche. But now it's becoming mainstream as software vendors realize the impact that their poorly optimized software has on their bottom line.
* People absolutely hate using slow software, especially when their productivity goes down because of it. Not all fast software is world-class, but all world-class software is fast. Performance is _the_ killer feature.
* Software tuning is becoming more important than it has been for the last 40 years and it will be one of the key drivers for performance gains in the near future. The importance of low-level performance tuning should not be underestimated, even if it's just a 1% improvement. The cumulative effect of these small improvements is what makes the difference.
* To squeeze the last bit of performance you need to have a good mental model of how modern CPUs work.
* Predicting the performance of a certain piece of code is nearly impossible since there are so many factors that affect the performance of modern platforms. When implementing software optimizations, developers should not rely on intuition but use careful performance analysis instead.

\sectionbreak
