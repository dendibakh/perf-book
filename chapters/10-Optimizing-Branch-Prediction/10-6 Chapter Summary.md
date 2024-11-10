## Chapter Summary {.unlisted .unnumbered}

\markright{Summary}

* Modern processors are very good at predicting branch outcomes. So, I recommend paying attention to branch mispredictions only when the TMA points to a high `Bad Speculation` metric.
* When branch outcome patterns become hard for the CPU branch predictor to follow, the performance of the application may suffer. In this case, the branchless version of an algorithm can be more performant. In this chapter, I showed how branches could be replaced with lookup tables, arithmetic, and selection.
* Branchless algorithms are not universally beneficial. Always measure to find out what works better in your specific case.
* There are indirect ways to reduce the branch misprediction rate by reducing the dynamic number of branch instructions in a program. This approach helps because it alleviates the pressure on branch predictor structures. Examples of such techniques include loop unrolling/vectorization, replacing branches with bitwise operations, and using SIMD instructions.

\sectionbreak
