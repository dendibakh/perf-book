# Preface {.unnumbered .unlisted}

## About The Author {.unlisted .unnumbered}

Denis Bakhvalov is a performance engineer at Intel, where he works on optimizing various widespread production applications and benchmarks. Before that, he was a part of the Intel compiler team, that develops C++ compilers for a variety of different architectures. Denis started his career as a software developer in 2008, working on a large C++ enterprise financial application. Before joining Intel, he worked for three years at Nokia, where he was writing embedded software. 

Performance engineering and compilers were always among his primary interests. In 2016 Denis started his `easyperf.net` blog, where he writes about low-level performance optimizations, C/C++ compilers, and CPU microarchitecture. Denis is a big proponent of an active lifestyle: he plays soccer, tennis, and chess.

Contacts:

* Email: dendibakh@gmail.com
* X (formerly Twitter): [\@dendibakh](https://x.com/dendibakh)
* LinkedIn: [\@dendibakh](https://www.linkedin.com/in/dendibakh/)

## From The Author {.unlisted .unnumbered}

I started this book with a simple goal: educate software developers to better understand their applications' performance. I know how difficult the topic of low-level performance engineering might be for a beginner or even for an experienced developer. I remember the days when I was starting with performance analysis. I was looking at unfamiliar metrics trying to match the data that didn't match. And I was baffled. It took me years until it finally "clicked", and all pieces of the puzzle came together... even though sometimes I still struggle with the same problems.

When I was making my first steps in performance engineering, the only good source of information on the topic was software developer manuals, which are not what mainstream developers like to read. Frankly, I wish I had this book when I was trying to learn low-level performance analysis. In 2016 I started sharing things that I learned on my blog and received some positive feedback from my readers. Some of them suggested me to aggregate this information into a book. This book is their fault.

I published the first edition in November 2020. The book was well-received by the community, however, I also received a lot of constructive criticism. The most popular feedback was to include exercises for experimentation. Some readers complained that it was too focused on Intel CPUs and didn't cover other architectures like AMD, ARM-based CPUs, etc. Other readers suggested that I should cover system-level performance, not just CPU performance. The second edition expands in all these and many other directions. It came out to be twice as big as the first book.

Specifically, I want to highlight the exercises that I added to the second edition of the book. I created a supplementary online course "Performance Ninja", which has more than 20 lab assignments. You can use these small puzzles to practice optimization techniques and check your understanding of the material covered in this book. I consider it the best part that differentiates this book from others. I hope it will make your learning process more entertaining. More details about the online course can be found in [@sec:chapter1Exercises].

Low-level performance optimizations are not easy, I fully understand that. I tried to explain everything as clearly as possible, however the topic is very complex. No matter how hard I tried, I know that it requires a fair amount of experimentation and practice to fully understand the material. I encourage you to take your time, read through the chapters and experiment with examples provided in the online course.

I joined Intel in 2017, but even before that I never shied away from software optimization tasks. I always got a dopamine hit when I saw the running time of my program went from 10 seconds down to 5 seconds. That feeling of excitement of discovering something, feeling proud of yourself. It made me even more curious and craving for more. I've been doing it a lot more chaotic back then. Now I do it more professionally, however, I still feel very happy when I make the software run faster. I wish you too experience the joy of discovering performance issues in your application and the satisfaction of fixing them.

I sincerely hope that this book will help you learn low-level performance analysis, and, if you make your application faster as a result, I will consider my mission accomplished.

You will find that I use "we" instead of "I" in many places in the book. This is because I received a lot of help from other people. The PDF version of this book and the "Performance Ninja" online course are available for free. This is my way to give back to the community. The full list of contributors can be found at the end of the book in the "Acknowledgements" section.

## Target Audience {.unlisted .unnumbered}

If you're working with performance-critical applications, this book is right for you. It is primarily targeted at software developers in High-Performance Computing (HPC), game development, data-center applications (like Facebook, Google, etc.), High-Frequency Trading (HFT), and other industries where the value of performance optimizations is well-known and appreciated.

This book will also be useful for any developer who wants to understand the performance of their application better and to know how it can be diagnosed and improved. You may just be enthusiastic about performance engineering and want to learn more about it. Or you may want to be the smartest engineer in the room, that's also fine. I hope that the material presented in this book will help you develop new skills that can be applied in your daily work and potentially move your career forward.

Readers are expected to have a minimal background in C/C++ programming languages to understand the book's examples. The ability to read basic x86/ARM assembly is desired but is not a strict requirement. I also expect familiarity with basic concepts of computer architecture and operating systems like central processor, memory, process, thread, virtual and physical memory, context switch, etc. If any of the mentioned terms are new to you, I suggest studying this material first.

I suggest you read the book chapter by chapter, starting from the beginning. If you consider yourself a beginner in performance analysis, I do not recommend skipping chapters. After you finish reading, this book can be used as a reference or a checklist for optimizing software applications. The second part of the book can be a source of ideas for code optimizations.

[TODO]: put a link to an errata webpage 

\sectionbreak