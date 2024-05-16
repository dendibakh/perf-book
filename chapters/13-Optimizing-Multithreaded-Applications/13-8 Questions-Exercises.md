## Questions and Exercises {.unlisted .unnumbered}

[TODO]: update

1. Solve `perf-ninja::false_sharing` lab assignment.
2. Run the application that you're working with on a daily basis. Is it multithreaded? If not, pick up some multithreaded benchmark. Calculate parallel efficiency metrics. Run the scaling study. Look at the timeline diagram, are there any scheduling issues? Identify the hot locks and which code paths lead to those locks. Can you improve locking? Check if the application performance suffers from true/false sharing.
3. Bonus question: what are the benefits of multithreaded vs. multiprocessed applications?