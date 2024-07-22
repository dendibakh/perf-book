# Acknowledgments {.unnumbered}

\setlength\intextsep{0pt}

[TODO]: make round pictures

\begin{wrapfigure}{r}{3cm}
\includegraphics[width=3cm]{../../img/contributors/MarkDawson.jpg}
\end{wrapfigure} 
Mark E. Dawson, Jr. authored [@sec:LowLatency] "Low Latency Tuning Techniques" and [@sec:ContinuousProfiling] "Continuous Profiling". He has also contributed a lot to the first edition of the book. Mark is a recognized expert in the High-Frequency Trading industry, currently working at WH Trading. Mark also has a blog ([https://www.jabperf.com/](https://www.jabperf.com/)) where he writes about low-latency and other performance optimizations.

\hfill \break

\begin{wrapfigure}{r}{3cm}
\includegraphics[width=3cm]{../../img/contributors/SwarupSahoo.jpg}
\end{wrapfigure} 
Swarup Sahoo helped me with writing about AMD PMU features in [@sec:PmuChapter], and authored [@sec:IntelVtuneOverview] about AMD uProf. Swarup is a senior developer at AMD, where he works on the uProf performance analysis tool.

\hfill \break
\hfill \break
\hfill \break

\begin{wrapfigure}{r}{3cm}
\includegraphics[width=3cm]{../../img/contributors/UniversityZaragoza.jpg}
\end{wrapfigure} 
Agustín Navarro-Torres, Jesús Alastruey-Benedé, Pablo Ibáñez-Marín, Víctor Viñals-Yúfera from the University of Zaragoza authored [@sec:Sensitivity2LLC] "Case Study: Sensitivity to Last Level Cache Size". They are researchers in the field of computer science and has published multiple papers on topics related to performance engineering.

\hfill \break
\hfill \break

\begin{wrapfigure}{r}{3cm}
\includegraphics[width=3cm]{../../img/contributors/AloisKraus.png}
\end{wrapfigure} 
Alois Kraus authored [@sec:ETW] "Event Tracing for Windows".

\hfill \break

\begin{wrapfigure}{r}{3cm}
\includegraphics[width=3cm]{../../img/contributors/LallySingh.jpg}
\end{wrapfigure} 
Lally Singh

\hfill \break

Huge thanks to Yann Collet, the author of Zstd, for providing us with the information about the internal workings of Zstd for [@sec:ThreadCountScalingStudy].


Also, I would like to thank the whole performance community for countless blog articles and papers. I was able to learn a lot from reading blogs by Travis Downs, Daniel Lemire, Andi Kleen, Agner Fog, Bruce Dawson, Brendan Gregg, and many others. I stand on the shoulders of giants, and the success of this book should not be attributed only to myself. This book is my way to thank and give back to the whole community.

Last but not least, thanks to my family, who were patient enough to tolerate me missing weekend trips and evening walks. Without their support, I wouldn't have finished this book.

First edition acknowledgments:

* Huge thanks to Mark E. Dawson, Jr. for his help writing several sections of this book: "Optimizing For DTLB" ([@sec:secDTLB]), "Optimizing for ITLB" ([@sec:FeTLB]), "Cache Warming" ([@sec:CacheWarm]), System Tuning ([@sec:SysTune]), [@sec:secAmdahl] about performance scaling and overhead of multithreaded applications, [@sec:COZ] about using COZ profiler, [@sec:secEBPF] about eBPF, "Detecting Coherence Issues" ([@sec:TrueFalseSharing]). Mark was kind enough to share his expertise and feedback at different stages of this book's writing.
* Next, I want to thank Sridhar Lakshmanamurthy, who authored the major part of [@sec:uarch] about CPU microarchitecture. Sridhar has spent decades working at Intel, and he is a veteran of the semiconductor industry.
* Big thanks to Nadav Rotem, the original author of the vectorization framework in the LLVM compiler, who helped me write the [@sec:Vectorization] about vectorization.
* Clément Grégoire authored a [@sec:ISPC] about ISPC compiler. Clément has an extensive background in the game development industry. His comments and feedback helped address in the book some of the challenges in the game development industry.
* Reviewers: Dick Sites, Wojciech Muła, Thomas Dullien, Matt Fleming, Daniel Lemire, Ahmad Yasin, Michele Adduci, Clément Grégoire, Arun S. Kumar, Surya Narayanan, Alex Blewitt, Nadav Rotem, Alexander Yermolovich, Suchakrapani Datt Sharma, Renat Idrisov, Sean Heelan, Jumana Mundichipparakkal, Todd Lipcon, Rajiv Chauhan, Shay Morag, and others.
