## Questions and Exercises {.unlisted .unnumbered}

\markright{Questions and Exercises}

1. Which performance analysis approaches would you use in the following scenarios?
- scenario 1: the client support team reports a customer issue: after upgrading to a new version of the application, the performance of a certain operation drops by 10%.
- scenario 2: the client support team reports a customer issue: some transactions run 2x longer than others with no particular pattern.
- scenario 3: you're evaluating three different compression algorithms and you want to know what types of performance bottlenecks (memory latency, computations, branch mispredictions, etc) each of them has.
- scenario 4: there is a new shiny library that claims to be faster than the one you currently have integrated into your project; you've decided to compare their performance.
- scenario 5: you were asked to analyze the performance of some unfamiliar code, which involves a hot loop; you want to know how many iterations the loop is doing.
2. Run the application that you're working with daily. Practice doing performance analysis using the approaches we discussed in this chapter. Collect raw counts for various CPU performance events, find hotspots, collect roofline data, and generate and study the compiler optimization report for the hot function(s) in your program.
