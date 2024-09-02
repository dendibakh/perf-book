

## Automated Detection of Performance Regressions

We just discussed why you should monitor performance in production. On the other hand, it is still beneficial to set up continuous "in-house" testing to catch performance problems early. However, keep in mind that not every performance regression can be caught in a lab.

Software vendors constantly seek ways to accelerate the pace of delivering their products to the market. May companies deploy newly written code every couple of months or weeks. Unfortunately, software products don't get better performance with each new release. Performance defects tend to leak into production software at an alarming rate [@UnderstandingPerfRegress]. A large number of code changes pose a challenge to thoroughly analyze their performance impact.

Performance regressions are defects that make software run slower compared to the previous versions. Catching performance regressions (or improvements) requires detecting which commit(s) has changed the performance of the program. From database systems to search engines to compilers, performance regressions are commonly experienced by almost all large-scale software systems during their continuous evolution and deployment life cycle. It may be impossible to entirely avoid performance regressions during software development, but with proper testing and diagnostic tools, the likelihood of such defects silently leaking into production code can be reduced significantly.

It is useful to track performance of your application with charts, like the one shown in Figure @fig:PerfRegress. Using such a chart you can see historical trends and find moments where performance improved or dropped. Typically, you will have a separate line for each performance test you're tracking. Do not include too many benchmarks on a single chart as it will become very noisy.

Let's consider some potential solutions for detecting performance regressions. The first option that comes to mind is: having humans look at the graphs. For the chart in Figure @fig:PerfRegress, humans will likely catch performance regression that happened on August 7th, but it's not obvious that they will detect later smaller regressions. People tend to lose focus quickly and can miss regressions, especially on a busy chart. In addition to that, it is a time-consuming and boring job that must be performed daily. It shouldn't be surprising that we want to move away from that option very quickly.

There is another interesting performance drop on August 3rd. Developer will also likely catch it, however, most of us would be tempted to dismiss it since performance recovered the next day. But are we sure that it was merely a glitch in measurements? What if this was a real regression that was compensated by an optimization on August 4th? If we could fix the regression *and* keep the optimization, we would have performance score around 4500. Do not dismiss such cases. One way to proceed here would be to repeat the measurements for the dates Aug 02 - Aug 04 and inspect code changes during that period.

![Performance graph (higher better) for an application showing a big drop in performance on August 5th and smaller ones later.](../../img/measurements/PerfRegressions.png){#fig:PerfRegress width=100%}

The second option is to have a threshold, say, 2%. Every code modification that has performance within that threshold is considered noise and everything above the threshold is considered a regression. It is somewhat better than the first option but still has its own drawbacks. Fluctuations in performance tests are inevitable: sometimes, even a harmless code change can trigger performance variation in a benchmark.[^3] Choosing the right value for the threshold is extremely hard and does not guarantee a low rate of false-positive as well as false-negative alarms. Setting the threshold too low might lead to analyzing a bunch of small regressions that were not caused by the change in source code but due to some random noise. Setting the threshold too high might lead to filtering out real performance regressions. 

Small regressions can pile up slowly into a bigger regression, which can be left unnoticed. Going back to Figure @fig:PerfRegress, notice a downward trend that lasted from Aug 11 to Aug 21. The period started with the score of 3000 and ended up with 2600. That is roughly 15% regression over 10 days, or 1.5% per day on average. If we set a 2% threshold all regressions will be filtered out. But as we can see, the accumulated regression is much bigger than the threshold. 

Nevertheless, this option works reasonably well for some projects, especially if the level of noise in the benchmark is very low. Also, you can adjust the threshold for each test. An example of a CI system where each test requires setting explicit threshold values for alerting a regression is [LUCI](https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md),[^2] which is a part of the Chromium project.

An option that we recommend is to use statistical approach. An algorithm to identify performance regressions that recently became popular is called "Change Point Detection" (see [@ChangePointAnalysis]). It utilizes historical data and identifies points in time where performance has changed. A CI system that uses such approach can automatically display change points on the chart and open a new ticket in the bug tracker system. Many performance monitoring systems embraced Change Point Detection algorithm, including several open-source projects. Search the web to find the one that better suits your needs.

A typical CI performance tracking system should automate the following actions:

1. Set up a system under test.
2. Run a benchmark suite.
3. Report the results.
4. Determine if performance has changed.
5. Alert on unexpected changes in performance.
6. Visualize the results for a human to analyze.

Another desireable feature of a CI performance tracking system is to allow developers submit performance evaluation jobs for their patches before they commit them to the codebase. This greatly simplifies developer's job and facilitates quicker turnaround of experiments. Performance impact of a code change is frequently included in the list of check-in criterias. 

If, for some reason, a performance regression has slipped into the codebase, it is very important to detect it promptly. First, because fewer changes were merged since it happened. This allows us to have a person responsible for the regression look into the problem before they move to another task. Also, it is a lot easier for a developer to approach the regression since all the details are still fresh in their head as opposed to several weeks after that.

Lastly, the CI system should alert, not just on software performance regressions, but on unexpected performance improvements, too. For example, someone may check in a seemingly innocuous commit which, nonetheless, improves performance by 10% in the automated tracking harness. Your initial instinct may be to celebrate this fortuitous performance boost and proceed with your day. However, while this commit may have passed all functional tests in your CI pipeline, chances are that this unexpected improvement uncovered a gap in functional testing which only manifested itself in the performance regression results. For instance, the change caused the application to skip some part of work, which was not covered by functional tests. This scenario occurs often enough that it warrants explicit mention: treat the automated performance regression harness as part of a holistic software testing framework.

To wrap it up, we highly recommend setting up an automated statistical performance tracking system. Try using different algorithms and see which works best for your application. It will certainly take time, but it will be a solid investment in the future performance health of your project.

[^2]: LUCI - [https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md](https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md)
[^3]: The following article shows that changing the order of the functions or removing dead functions can cause variations in performance: [https://easyperf.net/blog/2018/01/18/Code_alignment_issues](https://easyperf.net/blog/2018/01/18/Code_alignment_issues)