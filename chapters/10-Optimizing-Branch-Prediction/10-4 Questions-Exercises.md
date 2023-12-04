## Questions and Exercises {.unlisted .unnumbered}

1. Solve the following lab assignments using techniques we discussed in this chapter:
- `perf-ninja::branches_to_cmov_1`
- `perf-ninja::lookup_tables_1`
- `perf-ninja::virtual_call_mispredict`
- `perf-ninja::conditional_store_1`
2. Run the application that you're working with on a daily basis. Collect the TMA breakdown and check the `BadSpeculation` metric. Look at the code that is attributed with the most number of branch mispredictions. Is there a way to avoid branches using techniques we discussed in this chapter?

**Coding exercise**: write a microbenchmark that will experience 50% misprediction rate or get as close as possible. Your goal is to write a code in which half of all branch instructions are mispredicted. That is not as simple as you may think. Some hints and ideas:
- Branch misprediction rate is measured as `BR_MISP_RETIRED.ALL_BRANCHES / BR_INST_RETIRED.ALL_BRANCHES`.
- If you're coding in C++, you can use 1) google benchmark similar to perf-ninja, or 2) write a regular console program and collect CPU counters with Linux `perf`, or 3) integrate libpfm into the microbenchmark (see [@sec:MarkerAPI]).
- There is no need to invent some complicated algorithm. A simple approach would be to generate a pseudo-random number in the range `[0;100)` and check if it is less than 50. Random numbers can be pregenerated ahead of time.
- Keep in mind that modern CPUs can remember long (but still limited) sequences of branch outcomes.