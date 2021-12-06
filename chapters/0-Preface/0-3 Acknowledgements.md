---
typora-root-url: ..\..\img
---

## Acknowledgments {.unlisted .unnumbered}

Huge thanks to Mark E. Dawson, Jr. for his help writing several sections of this book: "Optimizing For DTLB" ([@sec:secDTLB]), "Optimizing for ITLB" ([@sec:FeTLB]), "Cache Warming" ([@sec:CacheWarm]), System Tuning ([@sec:SysTune]), [@sec:secAmdahl] about performance scaling and overhead of multithreaded applications, [@sec:COZ] about using COZ profiler, [@sec:secEBPF] about eBPF, "Detecting Coherence Issues" ([@sec:TrueFalseSharing]). Mark is a recognized expert in the High-Frequency Trading industry. Mark was kind enough to share his expertise and feedback at different stages of this book's writing.

Next, I want to thank Sridhar Lakshmanamurthy, who authored the major part of [@sec:uarch] about CPU microarchitecture. Sridhar has spent decades working at Intel, and he is a veteran of the semiconductor industry.

Big thanks to Nadav Rotem, the original author of the vectorization framework in the LLVM compiler, who helped me write the [@sec:Vectorization] about vectorization.

Clément Grégoire authored a [@sec:ISPC] about ISPC compiler. Clément has an extensive background in the game development industry. His comments and feedback helped address in the book some of the challenges in the game development industry.

This book wouldn't have come out of the draft without its reviewers: Dick Sites, Wojciech Muła, Thomas Dullien, Matt Fleming, Daniel Lemire, Ahmad Yasin, Michele Adduci, Clément Grégoire, Arun S. Kumar, Surya Narayanan, Alex Blewitt, Nadav Rotem, Alexander Yermolovich, Suchakrapani Datt Sharma, Renat Idrisov, Sean Heelan, Jumana Mundichipparakkal, Todd Lipcon, Rajiv Chauhan, Shay Morag, and others.

Also, I would like to thank the whole performance community for countless blog articles and papers. I was able to learn a lot from reading blogs by Travis Downs, Daniel Lemire, Andi Kleen, Agner Fog, Bruce Dawson, Brendan Gregg, and many others. I stand on the shoulders of giants, and the success of this book should not be attributed only to myself. This book is my way to thank and give back to the whole community.

Last but not least, thanks to my family, who were patient enough to tolerate me missing weekend trips and evening walks. Without their support, I wouldn't have finished this book.

\sectionbreak
