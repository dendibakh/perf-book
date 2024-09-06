## Why care about performance?

In addition to the slowing trend of hardware single-threaded performance growth, there are a couple of other business reasons to care about performance. During the PC era,[^12] the costs of slow software were paid by the users, as inefficient software was running on user computers. With the advent of SaaS (software as a service) and cloud computing, the costs of slow software are put back on the software providers, not their users. If you're a SaaS company like Meta or Netflix,[^4] it doesn't matter if you run your service on-premise hardware or you use the public cloud, you pay for the electricity your servers consume. Inefficient software cuts right into your margins and market evaluation. According to Synergy Research Group,[^5] worldwide spending on cloud services topped $100 billion in 2020, and according to Gartner,[^6] it will surpass $675 billion in 2024.

For many years performance engineering was a nerdy niche, but now it's becoming mainstream. Many companies have already realized the importance of performance engineering and are willing to pay well for this work.

It is fairly easy to reach performance level 4 in Table @tbl:PlentyOfRoom. In fact, you don't need this book to get there. Write your program in one of the native programming languages, distribute work among multiple threads, pick a good optimizing compiler and you'll get there. Unfortunately, this will only put you halfway to the desired efficiency target.

The methodologies in this book focus on squeezing out the last bit of performance from your application. Such transformations can be attributed along rows 6 and 7 in Table @tbl:PlentyOfRoom. The types of improvements that will be discussed are usually not big and often do not exceed 10%. However, do not underestimate the importance of a 10% speedup. SQLite is commonplace today not because its developers one day made it 50% faster, but because they meticulously made hundreds of 0.1% improvements over the years. The cumulative effect of these small improvements is what makes the difference.

The impact of small improvements is very relevant for large distributed applications running in the cloud. According to [@HennessyGoogleIO], in the year 2018, Google spent roughly the same amount of money on actual computing servers that run the cloud as it spent on power and cooling infrastructure. Energy efficiency is a very important problem, which can be improved by optimizing software.

>  "At such [Google] scale, understanding performance characteristics becomes critical---even small improvements in performance or utilization can translate into immense cost savings." [@GoogleProfiling]

In addition to cloud costs, there is another factor at play: how people perceive slow software. Google reported that a 2% slower search caused [2% fewer searches](https://assets.en.oreilly.com/1/event/29/Keynote Presentation 2.pdf) per user.[^3] For Yahoo! 400 milliseconds faster page load caused [5-9% more traffic](https://www.slideshare.net/stoyan/dont-make-me-wait-or-building-highperformance-web-applications).[^8] In the game of big numbers, small improvements can make a significant impact. The slower a service works, the fewer people will use it. 

Outside cloud services, there are many other performance-critical industries where performance engineering does not need to be justified, such as Artificial Intelligence (AI), High-Performance Computing (HPC), High-Frequency Trading (HFT), game development, etc. Moreover, performance is not only required in highly specialized areas, it is also relevant for general-purpose applications and services. Many tools that we use every day simply would not exist if they failed to meet their performance requirements. For example, Visual C++ [IntelliSense](https://docs.microsoft.com/en-us/visualstudio/ide/visual-cpp-intellisense)[^2] features that are integrated into Microsoft Visual Studio IDE have very tight performance constraints. For the IntelliSense autocomplete feature to work, it must parse the entire source codebase in milliseconds.[^9] Nobody will use a source code editor if it takes several seconds to suggest autocomplete options. Such a feature has to be very responsive and provide valid continuations as the user types new code.

> "Not all fast software is world-class, but all world-class software is fast. Performance is _the_ killer feature." ---Tobi Lutke, CEO of Shopify.

I hope it goes without saying that people hate using slow software, especially when their productivity goes down because of it. Table 2 shows that most people consider a delay of 2 seconds or more to be a "long wait," and would switch to something else after 10 seconds of waiting (I think much sooner). If you want to keep users' attention, your application must react quickly. 

Application performance can drive your customers to a competitor's product. By emphasizing performance, you can give your product a competitive advantage.

Sometimes fast tools find applications for which they were not initially designed. For example, game engines like Unreal and Unity are used in architecture, 3D visualization, filmmaking, and other areas. Because game engines are so performant, they are a natural choice for applications that require 2D and 3D rendering, physics simulation, collision detection, sound, animation, etc.

-----------------------------------------------------------------------------
Interaction   Human Perception                                 Response Time
Class                           

------------- -----------------------------------------------  --------------
Fast          Minimally noticeable delay                       100ms--200ms

Interactive   Quick, but too slow to be described as Fast      300ms--500ms
                
Pause         Not quick but still feels responsive             500ms--1 sec
               
Wait          Not quick due to amount of work for scenario     1 sec--3 sec
               
Long Wait     No longer feels responsive                       2 sec--5 sec

Captive       Reserved for unavoidably long/complex scenarios  5 sec--10 sec
               
Long-running  User will probably switch away during operation  10 sec--30 sec

------------------------------------------------------------------------------

Table: Human-software interaction classes. *Source: Microsoft Windows Blogs*.[^11] {#tbl:WindowsResponsiveness}

> “Fast tools don’t just allow users to accomplish tasks faster; they allow users to accomplish entirely new types of tasks, in entirely new ways.” - Nelson Elhage wrote in his blog.[^1]

Before starting performance-related work, make sure you have a strong reason to do so. Optimization just for optimization’s sake is useless if it doesn’t add value to your product.[^10] Mindful performance engineering starts with clearly defined performance goals. Understand clearly what you are trying to achieve, and justify the work. Establish metrics that you will use to measure success.

Now that we've talked about the value of performance engineering, let's uncover what it consists of. When you're trying to improve the performance of a program, you need to find problems (performance analysis) and then improve them (tuning), a task very similar to a regular debugging activity. This is what we will discuss next.

[^12]: The late 1990s and early 2000s, a time dominated by personal computers.
[^4]: In 2024, Meta uses mostly on-premise cloud, while Netflix uses AWS public cloud.
[^5]: Worldwide spending on cloud services in 2020 - [https://www.srgresearch.com/articles/2020-the-year-that-cloud-service-revenues-finally-dwarfed-enterprise-spending-on-data-centers](https://www.srgresearch.com/articles/2020-the-year-that-cloud-service-revenues-finally-dwarfed-enterprise-spending-on-data-centers)
[^6]: Worldwide spending on cloud services in 2024 - [https://www.gartner.com/en/newsroom/press-releases/2024-05-20-gartner-forecasts-worldwide-public-cloud-end-user-spending-to-surpass-675-billion-in-2024](https://www.gartner.com/en/newsroom/press-releases/2024-05-20-gartner-forecasts-worldwide-public-cloud-end-user-spending-to-surpass-675-billion-in-2024)

[^1]: Reflections on software performance by N. Elhage - [https://blog.nelhage.com/post/reflections-on-performance/](https://blog.nelhage.com/post/reflections-on-performance/)
[^2]: Visual C++ IntelliSense - [https://docs.microsoft.com/en-us/visualstudio/ide/visual-cpp-intellisense](https://docs.microsoft.com/en-us/visualstudio/ide/visual-cpp-intellisense)
[^3]: Slides by Marissa Mayer - [https://assets.en.oreilly.com/1/event/29/Keynote Presentation 2.pdf](https://assets.en.oreilly.com/1/event/29/Keynote Presentation 2.pdf)
[^8]: Slides by Stoyan Stefanov - [https://www.slideshare.net/stoyan/dont-make-me-wait-or-building-highperformance-web-applications](https://www.slideshare.net/stoyan/dont-make-me-wait-or-building-highperformance-web-applications)
[^9]: In fact, it's not possible to parse the entire codebase in the order of milliseconds. Instead, IntelliSense only reconstructs the portions of AST that have been changed. Watch more details on how the Microsoft team achieves this in the video: [https://channel9.msdn.com/Blogs/Seth-Juarez/Anders-Hejlsberg-on-Modern-Compiler-Construction](https://channel9.msdn.com/Blogs/Seth-Juarez/Anders-Hejlsberg-on-Modern-Compiler-Construction)
[^10]: Unless you just want to practice performance optimizations, which is fine too.
[^11]: Microsoft Windows Blogs - [https://blogs.windows.com/windowsdeveloper/2023/05/26/delivering-delightful-performance-for-more-than-one-billion-users-worldwide/](https://blogs.windows.com/windowsdeveloper/2023/05/26/delivering-delightful-performance-for-more-than-one-billion-users-worldwide/)
