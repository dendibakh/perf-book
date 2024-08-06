# Acknowledgments {.unnumbered}

\markboth{Acknowledgments}{Acknowledgments}

I write this section with profound gratitude to all the people mentioned below. I feel very humble to deliver to you all the knowledge these people have.

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\setlength\intextsep{0pt}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/MarkDawson_circle.png}
\end{wrapfigure} 
Mark E. Dawson, Jr. authored [@sec:LowLatency] "Low Latency Tuning Techniques" and [@sec:ContinuousProfiling] "Continuous Profiling". He has also contributed a lot to the first edition of the book. Mark is a recognized expert in the High-Frequency Trading industry, currently working at WH Trading. Mark also has a blog ([https://www.jabperf.com](https://www.jabperf.com)) where he writes about low-latency and other performance optimizations.

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/UniversityZaragoza_circle.png}
\end{wrapfigure} 
Agustín Navarro-Torres, Jesús Alastruey-Benedé, Pablo Ibáñez-Marín, Víctor Viñals-Yúfera from the University of Zaragoza authored [@sec:Sensitivity2LLC] "Case Study: Sensitivity to Last Level Cache Size". They are researchers in the field of computer science and has published multiple papers on topics related to performance engineering.

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/JanWassenberg_circle.png}
\end{wrapfigure} 
Jan Wassenberg authored [@sec:secIntrinsicLibraries] "Wrapper Libraries for Intrinsics" and also proposed many improvements to [@sec:Vectorization] "Vectorization" and [@sec:SIMD] "SIMD Multiprocessors". Jan is a software engineer at Google DeepMind, where he leads development of Gemma.cpp.[^1] He also has authored
multiple research papers. His personal webpage is [https://wassenberg.dreamhosters.com](https://wassenberg.dreamhosters.com).

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/SwarupSahoo_circle.png}
\end{wrapfigure} 
Swarup Sahoo helped me with writing about AMD PMU features in [@sec:PmuChapter], and authored [@sec:IntelVtuneOverview] about AMD uProf. Swarup is a senior developer at AMD, where he works on the uProf performance analysis tool for HPC (OpenMP, MPI) applications. Swarup's LinkedIn page can be found at [https://www.linkedin.com/in/swarupsahoo](https://www.linkedin.com/in/swarupsahoo).

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/AloisKraus_circle.png}
\end{wrapfigure} 
Alois Kraus authored [@sec:ETW] "Event Tracing for Windows". He developed `ETWAnalyzer`, a command-line tool for analyzing ETW files with simple queries. He is employed by Siemens Healthineers where he studies performance of large software systems. Alois' personal webpage and blog: [https://aloiskraus.wordpress.com](https://aloiskraus.wordpress.com).

\vspace{-1cm} \hfill \break \vspace{0.5cm}
\newpage

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/MarcoCastorina_circle.png}
\end{wrapfigure} 
Marco Castorina authored [@sec:Tracy] "Specialized and Hybrid profilers" that showcases performance profiling with Tracy. Marco currently works on the games graphics performance team at AMD, focusing on DX12. Also, he is the co-author of a book titled "Mastering Graphics Programming with Vulkan". Marco's personal web page is [https://marcocastorina.com](https://marcocastorina.com).

\vspace{-1cm} \hfill \break \vspace{0.5cm}

\begin{wrapfigure}{r}{2.5cm}
\includegraphics[width=2.5cm]{../../img/contributors/LallySingh_circle.png}
\end{wrapfigure} 
Lally Singh has authored [@sec:MarkerAPI] about Marker APIs. Lally is currently at Tesla, his prior work includes Datadog's performance team, Google's Search performance team, low latency trading systems, and embedded real-time control systems. Lally has a PhD in CS from Virginia Tech, focusing on scalability in distributed VR.

\hfill \break 

Jumana Mundichipparakkal from ARM, for helping me write about ARM PMU features in [@sec:PmuChapter], for your review and comments. And thanks for your support from the first edition of this book.

Yann Collet, the author of Zstandard, for providing me with the information about the internal workings of Zstd for [@sec:ThreadCountScalingStudy].

Ciaran McHale, for finding tons of grammar mistakes in my text.

Peter Veentjer, for multiple contributions to various places in the book.

Also, I would like to thank the whole performance community for countless blog articles and papers. I was able to learn a lot from reading blogs by Travis Downs, Daniel Lemire, Andi Kleen, Agner Fog, Bruce Dawson, Brendan Gregg, and many others. I stand on the shoulders of giants, and the success of this book should not be attributed only to myself. This book is my way to thank and give back to the whole community.

[TODO]: images created with excalidraw.com

[TODO]: cover desing by {ask permision}

[TODO]: technical reviewers and proofreaders: Amir Aupov, Charles-Francois Natali

[TODO]: ask for permission. I would like to thank my manager at Intel for giving me time slots to work on this book.

Last but not least, thanks to my family, who were patient enough to tolerate me missing weekend trips and evening walks. Without their support, I wouldn't have finished this book.

I should also mention contributors to the first edition of this book. Below I only list names and section titles. More detailed acknowledgements are available in the first edition.

* Mark E. Dawson, Jr. wrote sections [@sec:secDTLB] "Optimizing For DTLB", [@sec:FeTLB] "Optimizing for ITLB", [@sec:CacheWarm] "Cache Warming", [@sec:SysTune] "System Tuning", and a few other.
* Sridhar Lakshmanamurthy, authored a large part of [@sec:uarch] about CPU microarchitecture.
* Nadav Rotem helped write [@sec:Vectorization] about vectorization.
* Clément Grégoire authored [@sec:ISPC] about ISPC compiler.
* Reviewers: Dick Sites, Wojciech Muła, Thomas Dullien, Matt Fleming, Daniel Lemire, Ahmad Yasin, Michele Adduci, Clément Grégoire, Arun S. Kumar, Surya Narayanan, Alex Blewitt, Nadav Rotem, Alexander Yermolovich, Suchakrapani Datt Sharma, Renat Idrisov, Sean Heelan, Jumana Mundichipparakkal, Todd Lipcon, Rajiv Chauhan, Shay Morag, and others.

[^1]: Gemma.cpp, LLM inference on CPU - [https://github.com/google/gemma.cpp](https://github.com/google/gemma.cpp)