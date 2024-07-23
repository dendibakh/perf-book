# Acknowledgments {.unnumbered}

\setlength\intextsep{0pt}

[TODO]: make round pictures

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/MarkDawson.jpg}
\end{wrapfigure} 
Mark E. Dawson, Jr. authored [@sec:LowLatency] "Low Latency Tuning Techniques" and [@sec:ContinuousProfiling] "Continuous Profiling". He has also contributed a lot to the first edition of the book. Mark is a recognized expert in the High-Frequency Trading industry, currently working at WH Trading. Mark also has a blog ([https://www.jabperf.com](https://www.jabperf.com)) where he writes about low-latency and other performance optimizations.

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/UniversityZaragoza2.jpg}
\end{wrapfigure} 
Agustín Navarro-Torres, Jesús Alastruey-Benedé, Pablo Ibáñez-Marín, Víctor Viñals-Yúfera from the University of Zaragoza authored [@sec:Sensitivity2LLC] "Case Study: Sensitivity to Last Level Cache Size". They are researchers in the field of computer science and has published multiple papers on topics related to performance engineering.

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/JanWassenberg.jpg}
\end{wrapfigure} 
Jan Wassenberg authored [@sec:secIntrinsicLibraries] "Wrapper Libraries for Intrinsics" and also proposed many improvements to [@sec:Vectorization] "Vectorization" and [@sec:SIMD] "SIMD Multiprocessors". Jan is a software engineer at Google DeepMind, where he leads development of Gemma.cpp.[^1] He also has authored
multiple research papers. His personal webpage is [https://wassenberg.dreamhosters.com](https://wassenberg.dreamhosters.com).

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/SwarupSahoo.jpg}
\end{wrapfigure} 
Swarup Sahoo helped me with writing about AMD PMU features in [@sec:PmuChapter], and authored [@sec:IntelVtuneOverview] about AMD uProf. Swarup is a senior developer at AMD, where he works on the uProf performance analysis tool for HPC (OpenMP, MPI) applications. Swarup's LinkedIn page can be found at [https://www.linkedin.com/in/swarupsahoo](https://www.linkedin.com/in/swarupsahoo).

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/AloisKraus.png}
\end{wrapfigure} 
Alois Kraus authored [@sec:ETW] "Event Tracing for Windows". He developed `ETWAnalyzer`, a command-line tool for analyzing ETW files with simple queries. He is employed by Siemens Healthineers where he studies performance of large software systems. Alois' personal webpage and blog: [https://aloiskraus.wordpress.com](https://aloiskraus.wordpress.com).

\vspace{-1cm} \hfill \break \vspace{0.5cm}
\newpage

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/MarcoCastorina.jpg}
\end{wrapfigure} 
Marco Castorina authored [@sec:Tracy] "Specialized and Hybrid profilers" that showcases performance profiling with Tracy. Marco currently works on the games graphics performance team at AMD, focusing on DX12. Also, he is the co-author of a book titled "Mastering Graphics Programming with Vulkan". Marco's personal web page is [https://marcocastorina.com](https://marcocastorina.com).

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/LallySingh.jpg}
\end{wrapfigure} 
Lally Singh has authored [@sec:MarkerAPI] about Marker APIs. [TODO]: Lally's bio

\hfill \break 
\hfill \break 
\hfill \break 
\hfill \break 

Huge thanks to Yann Collet, the author of Zstandard, for providing me with the information about the internal workings of Zstd for [@sec:ThreadCountScalingStudy].


Also, I would like to thank the whole performance community for countless blog articles and papers. I was able to learn a lot from reading blogs by Travis Downs, Daniel Lemire, Andi Kleen, Agner Fog, Bruce Dawson, Brendan Gregg, and many others. I stand on the shoulders of giants, and the success of this book should not be attributed only to myself. This book is my way to thank and give back to the whole community.

Last but not least, thanks to my family, who were patient enough to tolerate me missing weekend trips and evening walks. Without their support, I wouldn't have finished this book.

First edition acknowledgments:

* Huge thanks to Mark E. Dawson, Jr. for his help writing several sections of this book: "Optimizing For DTLB" ([@sec:secDTLB]), "Optimizing for ITLB" ([@sec:FeTLB]), "Cache Warming" ([@sec:CacheWarm]), System Tuning ([@sec:SysTune]), [@sec:secAmdahl] about performance scaling and overhead of multithreaded applications, [@sec:COZ] about using COZ profiler, [@sec:secEBPF] about eBPF, "Detecting Coherence Issues" ([@sec:TrueFalseSharing]). Mark was kind enough to share his expertise and feedback at different stages of this book's writing.
* Next, I want to thank Sridhar Lakshmanamurthy, who authored the major part of [@sec:uarch] about CPU microarchitecture. Sridhar has spent decades working at Intel, and he is a veteran of the semiconductor industry.
* Big thanks to Nadav Rotem, the original author of the vectorization framework in the LLVM compiler, who helped me write the [@sec:Vectorization] about vectorization.
* Clément Grégoire authored a [@sec:ISPC] about ISPC compiler. Clément has an extensive background in the game development industry. His comments and feedback helped address in the book some of the challenges in the game development industry.
* Reviewers: Dick Sites, Wojciech Muła, Thomas Dullien, Matt Fleming, Daniel Lemire, Ahmad Yasin, Michele Adduci, Clément Grégoire, Arun S. Kumar, Surya Narayanan, Alex Blewitt, Nadav Rotem, Alexander Yermolovich, Suchakrapani Datt Sharma, Renat Idrisov, Sean Heelan, Jumana Mundichipparakkal, Todd Lipcon, Rajiv Chauhan, Shay Morag, and others.

[^1]: Gemma.cpp, LLM inference on CPU - [https://github.com/google/gemma.cpp](https://github.com/google/gemma.cpp)