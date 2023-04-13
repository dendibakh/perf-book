## Questions and Exercises {.unlisted .unnumbered}

1. Which approaches you would use in the following scenarios?
- scenario 1: client support team reports a customer issue: after upgrading to a new version of the application, performance of a certain operation drops by 10%.
- scenario 2: client support team reports a customer issue: some transactions take 2x longer time to finish than usual with no particular pattern.
- scenario 3: you're evaluating three different compression algorithms and you want to know what types of performance bottlenecks (memory latency/bandwidth, branch mispredictions, etc) each of them has.
- scenario 4: there is a new shiny library that claims to be faster than the one you currently have integrated in your project; you've decided to compare their performance.
- scenario 5: you were asked to analyze performance of an unfamiliar code; you want to know how frequently a certain branch is taken and how many iterations the loop is doing.
2. Run the application that you're working with on a daily basis. Practice doing performance analysis using approaches we discussed in this chapter. Collect raw counts for various CPU performance events, find hotspots, collect roofline data, generate and study the compiler optimization report fot the hot function(s) in your program.