# Preface {.unnumbered .unlisted}

## About The Author {.unlisted .unnumbered}

Denis Bakhvalov is a performance engineer at Intel, where he works on optimizing production applications and benchmarks. Before that, he was a part of the Intel compiler team, that develops C++ compilers for a variety of different architectures. Denis started his career as a software developer in 2008, working on a large C++ enterprise financial application. Before joining Intel, he worked for three years at Nokia, where he was writing embedded software.

Performance engineering and compilers were always among his primary interests. In 2016 Denis started `easyperf.net` blog where he writes about low-level performance optimizations, C/C++ compilers, and CPU microarchitecture. Away from work, Denis enjoys soccer, chess, and traveling.

Contacts:

* Email: dendibakh@gmail.com
* X (formerly Twitter): [\@dendibakh](https://x.com/dendibakh)
* LinkedIn: [\@dendibakh](https://www.linkedin.com/in/dendibakh/)

## From The Author {.unlisted .unnumbered}

I started this book with a simple goal: educate software developers to better understand their applications' performance. I know how difficult the topic of low-level performance engineering might be for a beginner or even for an experienced developer. I remember the days when I was starting with performance analysis. I was looking at unfamiliar metrics trying to match data that didn't match, and I was baffled. It took me years until it finally "clicked", and all pieces of the puzzle came together... even though sometimes I still struggle with the same problems.

When I was taking my first steps in performance engineering, the only good sources of information on the topic were software developer manuals, which are not what mainstream developers like to read. Frankly, I wish I had this book when I was trying to learn low-level performance analysis. In 2016 I started sharing things that I learned on my blog, and received some positive feedback from my readers. Some of them suggested I aggregate this information into a book. This book is their fault.

Many people have asked me why I decided to self-publish. In fact, I initially tried to pitch it to several reputable publishers, but they didn't see the financial benefits of making such a book. However, I really wanted to write it, so I decided to do it anyway. In the end, it turned out quite well, so I decided to self-publish the second edition too.

The first edition was released in November 2020. It was well-received by the community, however, readers gave me a lot of constructive criticism. The most popular feedback was to include exercises for experimentation. Some readers complained that it was too focused on Intel CPUs and didn't cover other architectures like AMD and ARM. Other readers suggested that I should cover system performance, not just CPU performance. The second edition expands in all these and many other directions. It came out to be twice as big as the first book.

Specifically, I want to highlight the exercises that I added to the second edition of the book. I created a supplementary online course "Performance Ninja" with more than twenty lab assignments. I recommend you use these small puzzles to practice optimization techniques and check your understanding of the material. I consider it the best part that differentiates this book from others. I hope it will make your learning process more entertaining. More details about the online course can be found in [@sec:chapter1Exercises].

I know firsthand that low-level performance optimization is not easy. I tried to explain everything as clearly as possible, but the topic is very complex. It requires experimentation and practice to fully understand the material. I encourage you to take your time, read through the chapters, and experiment with examples provided in the online course.

During my career, I never shied away from software optimization tasks. I always got a dopamine hit whenever I managed to make my program run faster. The excitement of discovering something and feeling proud left me even more curious and craving for more. My initial performance work was very unstructured. Now it is my profession, yet I still feel very happy when I make software run faster. I hope you also experience the joy of discovering performance issues, and the satisfaction of fixing them.

I sincerely hope that this book will help you learn low-level performance analysis. If you make your application faster as a result, I will consider my mission accomplished.

You will find that I use "we" instead of "I" in some places in the book. This is because I received a lot of help from other people. The full list of contributors can be found at the end of the book in the "Acknowledgements" section.

The PDF version of this book and the "Performance Ninja" online course are available for free. This is my way to give back to the community.

## Target Audience {.unlisted .unnumbered}

If you're working with performance-critical applications, this book is right for you. It is primarily targeted at software developers in High-Performance Computing (HPC), AI, game development, data center applications (like those at Meta, Google, etc.), High-Frequency Trading (HFT), and other industries where the value of performance optimizations is well known and appreciated.

This book will also be useful for any developer who wants to understand the performance of their application better and know how it can be improved. You may just be enthusiastic about performance engineering and want to learn more about it. Or you may want to be the smartest engineer in the room; that's also fine. I hope that the material presented in this book will help you develop new skills that can be applied in your daily work and potentially move your career forward.

A minimal background in the C and C++ programming languages is necessary to understand the book's examples. The ability to read basic x86/ARM assembly is desirable, but not a strict requirement. I also expect familiarity with basic concepts of computer architecture and operating systems like "CPU", "memory", "process", "thread", "virtual" and "physical memory", "context switch", etc. If any of these terms are new to you, I suggest studying these prerequisites first.

I suggest you read the book chapter by chapter, starting from the beginning. If you consider yourself a beginner in performance analysis, I do not recommend skipping chapters. After you finish reading, you can use this book as a source of ideas whenever you face a performance issue and are unsure how to fix it. You can skim through the second part of the book to see which optimization techniques can be applied to your code.

I will post errata and other information about the book on my blog at the following URL:  [https://easyperf.net/blog/2024/11/11/Book-Updates-Errata](https://easyperf.net/blog/2024/11/11/Book-Updates-Errata).

\sectionbreak
