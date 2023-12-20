## Measuring Code Footprint

[TODO]: write this section

1. Say why we need to measure code footprint

2. Large code footprint in itself doesn't necessary mean there is impact on performance. Say that it should be analyzed in conjunction with TMA. And be used as an additional data point.

3. estimating hot code footprint in non-ambiguous way is not trivial. Similar to mem footprint it quickly becomes very involved.
The question like: how many times the code needs to be executed what is hot code 

4. Start with high-level analysis of the `.text` segment. Say that it is not very accurate but it is a good starting point.

5. Not many tools can estimate hot code footprint at runtime.

6. Give example of `perf-tools` for 4 benchmarks: `clang`, `stockfish`, `blender`, `cloverleaf`.

- build clang with relocations, apply BOLT, check the perf difference rerun perf-tools
- collect blender

7. Mention code heatmap from BOLT.