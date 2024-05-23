## Chapter Summary {.unlisted .unnumbered}

* Applications that do not take advantage of modern multicore CPUs are lagging behind their competitors. Preparing software to scale well with a growing amount of CPU cores is very important for the future success of your application.
* When dealing with a single-threaded application, optimizing one portion of the program usually yields positive results on performance. However, this is not necessarily the case for multithreaded applications. This effect is widely known as Amdahl's law, which constitutes that the speedup of a parallel program is limited by its serial part.
* Threads communication can yield retrograde speedup as explained by Universal Scalability Law. This poses additional challenges for tuning multithreaded programs. 
* As we saw in our thread count case study, frequency throttling, memory bandwidth saturation, and other issues can lead to poor performance scaling.
* Task scheduling on hybrid processors is challenging. Watch out for suboptimal job scheduling and do not restrict the OS scheduler when it is not necessary.
* Optimizing performance of multithreaded applications also involves detecting and mitigating the effects of cache coherence, such as true sharing and false sharing.
* During the past years, new tools emerged that cover gaps in analyzing performance of multithreaded applications, that traditional profilers cannot cover. We introduced Coz and GAPP which have a unique set of features.

\sectionbreak
