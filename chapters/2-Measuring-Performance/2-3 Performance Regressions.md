---
typora-root-url: ..\..\img
---

## Automated Detection of Performance Regressions

It is becoming a trend that SW vendors try to increase the frequency of deployments. Companies constantly seek ways to accelerate the rate of delivering their products to the market. Unfortunately, this doesn't automatically imply that SW products become better with each new release. In particular, software performance defects tend to leak into production software at an alarming rate [@UnderstandingPerfRegress]. A large number of changes in software impose a challenge to analyze all of those results and historical data to detect performance regressions.

Software performance regressions are defects that are erroneously introduced into software as it evolves from one version to the next. Catching performance bugs and improvements means detecting which commits change the performance of the software (as measured by performance tests) in the presence of the noise from the testing infrastructure. From database systems to search engines to compilers, performance regressions are commonly experienced by almost all large-scale software systems during their continuous evolution and deployment life cycle. It may be impossible to entirely avoid performance regressions during software development, but with proper testing and diagnostic tools, the likelihood for such defects to silently leak into production code could be minimized.

The first option that comes to mind is: having humans to look at the graphs and compare results. It shouldn't be surprising that we want to move away from that option very quickly. People tend to lose focus quickly and can miss regressions, especially on a noisy chart, like the one shown in figure @fig:PerfRegress. Humans will likely catch performance regression that happened around August 5th, but it's not obvious that humans will detect later regressions. In addition to being error-prone, having humans in the loop is also a time consuming and boring job that must be performed daily.

![Performance trend graph for four tests with a small drop in performance on August 5th (the higher value, the better). *© Image from [@MongoDBChangePointDetection]*](../../img/measurements/PerfRegressions.png){#fig:PerfRegress width=90%}

The second option is to have a simple threshold. It is somewhat better than the first option but still has its own drawbacks. Fluctuations in performance tests are inevitable: sometimes, even a harmless code change[^3] can trigger performance variation in a benchmark. Choosing the right value for the threshold is extremely hard and does not guarantee a low rate of false-positive as well as false-negative alarms. Setting the threshold too low might lead to analyzing a bunch of small regressions that were not caused by the change in source code but due to some random noise. Setting the threshold too high might lead to filtering out real performance regressions. Small changes can pile up slowly into a bigger regression, which can be left unnoticed[^1]. By looking at the figure @fig:PerfRegress, we can make an observation that the threshold requires per test adjustment. The threshold that might work for the green (upper line) test will not necessarily work equally well for the purple (lower line) test since they have a different level of noise. An example of a CI system where each test requires setting explicit threshold values for alerting a regression is [LUCI](https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md)[^2], which is a part of the Chromium project.

One of the recent approaches to identify performance regressions was taken in [@MongoDBChangePointDetection]. MongoDB developers implemented change point analysis for identifying performance changes in the evolving code base of their database products. According to [@ChangePointAnalysis], change point analysis is the process of detecting distributional changes within time-ordered observations. MongoDB developers utilized an "E-Divisive means" algorithm that works by hierarchically selecting distributional change points that divide the time series into clusters. Their open-sourced CI system called [Evergreen](https://github.com/evergreen-ci/evergreen)[^4] incorporates this algorithm to display change points on the chart and opens Jira tickets. More details about this automated performance testing system can be found in [@Evergreen].

Another interesting approach is presented in [@AutoPerf]. The authors of this paper presented `AutoPerf`, which uses hardware performance counters (PMC, see [@sec:PMC]) to diagnose performance regressions in a modified program. First, it learns the distribution of the performance of a modified function based on its PMC profile data collected from the original program. Then, it detects deviations of performance as anomalies based on the PMC profile data collected from the modified program. `AutoPerf` showed that this design could effectively diagnose some of the most complex software performance bugs, like those hidden in parallel programs.

Regardless of the underlying algorithm of detecting performance regressions, a typical CI system should automate the following actions:

1. Setup a system under test.
2. Run a workload.
3. Report the results.
4. Decide if performance has changed.
5. Visualize the results.

CI system should support both automated and manual benchmarking, yield repeatable results, and open tickets for performance regressions that were found. It is very important to detect regressions promptly. First, because fewer changes were merged since a regression happened. This allows us to have a person responsible for regression to look into the problem before they move to another task. Also, it is a lot easier for a developer to approach the regression since all the details are still fresh in their head as opposed to several weeks after that.

[^1]: E.g., suppose you have a threshold of 2%. If you have two consecutive 1.5% regressions, they both will be filtered out. But throughout two days, performance regression will sum up to 3%, which is bigger than the threshold.
[^2]: LUCI - [https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md](https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md)
[^3]: The following article shows that changing the order of the functions or removing dead functions can cause variations in performance: [https://easyperf.net/blog/2018/01/18/Code_alignment_issues](https://easyperf.net/blog/2018/01/18/Code_alignment_issues).
[^4]: Evergreen - [https://github.com/evergreen-ci/evergreen](https://github.com/evergreen-ci/evergreen).
