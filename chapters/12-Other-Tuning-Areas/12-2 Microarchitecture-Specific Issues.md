### Microarchitecture-Specific Performance Issues {#sec:UarchSpecificIssues}

In this section we will discuss some common microarchitecture-specific issues that can be attributed to majority of modern processors. Note that the impact of a particular problem can be more/less pronounced on one platform than another.

#### Memory Order Violations {.unlisted .unnumbered}

\hfill \break

We introduced the concept of memory ordering in [@sec:uarchLSU]. Memory reordering is a crucial aspect of modern CPUs, as it allows to execute memory requests in parallel and out-of-order. The key element in load/store reordering is memory disambiguation, which predicts if it is safe to let loads go ahead of earlier stores. Since the memory disambiguation is speculative, it can lead to performance issues if not handled properly.

Consider an example in [@lst:MemOrderViolation], on the left. This code snippet calculates a histogram of an 8-bit grayscale image, i.e., calculate how many times a certain color appears in the image. Besides countless other places, this code can be found in Otsu's thresholding algorithm[^1] that is used to convert a grayscale image to a binary image. Since the input image is 8-bit grayscale, there are only 256 different colors.

For each pixel on an image, you need to read the current histogram count of the color of the pixel, increment it and store it back. This is a classic read-modify-write dependency through the memory. Imagine we have the following consequtive pixels in the image: `0xFF 0xFF 0x00 0xFF 0xFF ...` and so on. The loaded value of the histogram count for pixel 1 comes from the result of the previous iteration. But the histogram count for pixel 2 comes from memory; it is independent and can be reordered. But then again, the histogram count for pixel 3 is dependent on the result of processing pixel 1, and so on. 

Listing: Memory Order Violation Example.

~~~~ {#lst:MemOrderViolation .cpp}
std::array<uint32_t, 256> hist;                    std::array<uint32_t, 256> hist1;
hist.fill(0);                                      std::array<uint32_t, 256> hist2;
for (int i = 0; i < width * height; ++i)     =>    hist1.fill(0);
  hist[image[i]]++;                                hist2.fill(0);
                                                   int i = 0;
                                                   for (; i + 1 < width * height; i += 2) {
                                                     hist1[image[i+0]]++;
                                                     hist2[image[i+1]]++;
                                                   }
                                                   // remainder
                                                   for (; i < width * height; ++i)
                                                     hist1[image[i]]++;
                                                   // combine partial histograms
                                                   for (int i = 0; i < hist1.size(); ++i)
                                                     hist1[i] += hist2[i];
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recall from [@sec:uarchLSU], the processor doesn't necessarily knows about a potential store-to-load forwarding, so it has to make a prediction. If it correctly predicts a memory order violation between two updates of color `0xFF`, then these accesses will be serialized. The performance will not be great, but it is the best we could hope for with the initial code. On the contrary, if the processor predicts that there is no memory order violation, it will speculatively let the two updates run in parallel. Later it will recognize the mistake, flush the pipeline, and re-execute the later of the two updates. This is very hurtful for performance.

Performance will greatly depend on the color patterns of the input image. Images with long sequences of pixels with the same color will have worse performance than images where colors don't repeat often. Performance of the initial version will be good as long as the distance between two pixels of the same color is long enough. The phrase "long enough" in this context is determined by the size of the out-of-order instruction window. Repeating read-modify-writes of the same color may trigger ordering violations if they occur within a few loop iterations of each other, but not if they occur more than a hundred of loop iterations apart.

A cure for the memory order violation problem is shown in [@lst:MemOrderViolation], on the right. As you can see, we duplicated the histogram and now alternate processing of pixels between two partial histograms. In the end, we combine the two partial histograms to get a final result. This new version with two partial histograms is still prone to potentially problematic patterns, such as `0xFF 0x00 0xFF 0x00 0xFF ...`. However, with this change, the worst-case scenario, e.g., `0xFF 0xFF 0xFF ...`  will run twice as fast as before. It may be beneficial to create four or eight partial histograms depending on the color pattern of input images. This exact code is featured in the [mem_order_violation_1](https://github.com/dendibakh/perf-ninja/tree/main/labs/memory_bound/mem_order_violation_1)[^2] lab assignment of Performance Ninja course, so feel free to experiment. On a small set of input images we observed from 10% to 50% speedup on various platforms. It is worth to mention that the version on the left consumes 1 KB of additional memory, which may not be huge in this case, but is something to watch out for.

#### Misaligned Memory Accesses {.unlisted .unnumbered}

\hfill \break

We already discussed how to align objects in {#sec:secMemAlign}. In most processors, the L1 cache is designed to be able to read data at any alignment. Generally, even if a load/store is misaligned but does not cross the cache line boundary, it won't have any performance penalty.

However, when a load or store crosses cache line boundary, such access requires two cache line reads (*split load/store*). It requires using a *split register*, which keeps the two parts and once both parts are fetched, they are combined into a single register. The number of split registers is limited. When executed sporadically, split accesses generally complete without any observable performance impact to overall execution. However, if that happens frequently, misaligned memory accesses will suffer delays.

[TODO]: example with split loads in matmul?

#### 4K Aliasing {.unlisted .unnumbered}

\hfill \break

just describe
https://richardstartin.github.io/posts/4k-aliasing
While unlikely to be a significant
problem, L1I Cache misses may result from set conflicts. Apple silicon uses 16KB
memory pages that may make this even more likely to occur, since independent
libraries tend to be aligned to page boundaries when they are loaded.

#### Cache Trashing {.unlisted .unnumbered}

\hfill \break

just describe
Avoid Cache Thrashing: Minimize cache conflicts by ensuring data structures do not excessively map to the same cache lines.
https://github.com/ibogosavljevic/hardware-efficiency/blob/main/cache-conflicts/cache_conflicts.c

#### Non-Temporal Loads and Stores {.unlisted .unnumbered}

\hfill \break

Caches naturally store data close to the processor under the assumption that the data in
the cache line will be used again in the near term. Data that benefits from caching is said
to have temporal locality. However, some algorithms stream (read and/or write) through
large quantities of data with little temporal reuse. In these cases, storing the data in the
cache is counterproductive because it floods (or "pollutes") the cache with unneeded
data, forcing out potentially useful data.
When using Non-Temporal Loads and Stores, the processor will optimize cache allocation
policies for particular cache lines to minimize pollution.
These special assembly instructions usually have "NT" suffix.

https://www.agner.org/optimize/optimizing_cpp.pdf#page=108&zoom=100,116,716

#### Store-to-Load Forwarding Delays {.unlisted .unnumbered}

\hfill \break

#### Minimize Moves Between Integer and Floating-Point Registers {.unlisted .unnumbered}

\hfill \break

DUP(general), FMOV(general), INS(general), MOV(from general), SCVTF(scalar), UCVTF(scalar)
Movement of data between integer and vector registers requires several cycles. Load
directly into vector registers
In most of the cases it is compiler's job to ensure, but in case you're writing compiler intrinsics or inline assembly routines, this advice may become handy.
When you need to load a `uint32_t` value from memory and then convert it to `float`, do not load the value in a general-purpose register (e.g. `EAX`) and then convert it to `XMM0`; load straight into `XMM0`.

Also, avoid mixing single and double precision values. For example:
```cpp
float circleLength(float r) {
    //return 2.0 * 3.14 * r; // 
    return 2.0f * 3.14f * r;
}
```

#### Slow Floating-Point Arithmetic {.unlisted .unnumbered}

\hfill \break

#### AVX-SSE Transitions {.unlisted .unnumbered}

\hfill \break

remove?
https://www.agner.org/optimize/microarchitecture.pdf#page=167&zoom=100,116,904

[^1]: Otsu's thresholding method - [https://en.wikipedia.org/wiki/Otsu%27s_method](https://en.wikipedia.org/wiki/Otsu%27s_method)
[^2]: Performance Ninja lab assignment: Memory Order Violation - [https://github.com/dendibakh/perf-ninja/tree/main/labs/memory_bound/mem_order_violation_1](https://github.com/dendibakh/perf-ninja/tree/main/labs/memory_bound/mem_order_violation_1)