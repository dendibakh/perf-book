# Preface {.unnumbered .unlisted}

## About The Author {.unlisted .unnumbered}

Denis Bakhvalov is a performance engineer at Intel, where he works on optimizing various widespread production applications and benchmarks. Before that, he was a part of the Intel compiler team, that develops C++ compilers for a variety of different architectures. Since 2008, Denis has also helped develop a large C++ desktop application and worked at Nokia, where he was writing embedded software.
Performance engineering and compilers were always among his primary interests. In 2016 Denis started his `easyperf.net` blog, where he writes about low-level performance optimizations, C/C++ compilers, and CPU microarchitecture. Denis is a big proponent of an active lifestyle: he plays soccer, tennis, and chess.

Contacts:

* Email: dendibakh@gmail.com
* X (formerly Twitter): [\@dendibakh](https://x.com/dendibakh)
* LinkedIn: [\@dendibakh](https://www.linkedin.com/in/dendibakh/)

## From The Author {.unlisted .unnumbered}

I started this book with a simple goal: educate software developers to better understand their applications' performance on modern hardware. I know how confusing this topic might be for a beginner or even for an experienced developer. This confusion mostly happens to developers who don't have prior experience with performance engineering. And that's fine since every expert was once a beginner. 

I remember the days when I was starting with performance analysis. I was staring at unfamiliar metrics trying to match the data that didn't match. And I was baffled. It took me years until it finally "clicked", and all pieces of the puzzle came together. At the time, the only good sources of information were software developer manuals, which are not what mainstream developers like to read. So I decided to write this book, which will hopefully make it easier for developers to learn performance analysis concepts.

Developers who consider themselves beginners in performance analysis can start from the beginning of the book and read sequentially, chapter by chapter. Chapters 2-4 give developers a minimal set of knowledge required by later chapters. Readers already familiar with these concepts may choose to skip those. Additionally, this book can be used as a reference or a checklist for optimizing SW applications. Developers can use chapters 7-11 as a source of ideas for tuning their code.

[TODO][FIX_BEFORE_REVIEW]: what has changed from the first edition?

[TODO][FIX_BEFORE_REVIEW]: add
\personal{While working at Intel, I hear the same story from time to time: when Intel clients experience slowness in their application, they immediately and unconsciously start blaming Intel for having slow CPUs. But when Intel sends one of our performance ninjas to work with them and help them improve their application, it is not unusual that they help speed it up by a factor of 2x, sometimes even 10x.}

## Target Audience {.unlisted .unnumbered}

This book will be primarily useful for software developers who work with performance-critical applications and do low-level optimizations. To name just a few areas: High-Performance Computing (HPC), Game Development, data-center applications (like Facebook, Google, etc.), and High-Frequency Trading. However, the scope of the book is not limited to the mentioned industries. This book will be useful for any developer who wants to understand the performance of their application better and know how it can be diagnosed and improved. The author hopes that the material presented in this book will help readers develop new skills that can be applied in their daily work.

Readers are expected to have a minimal background in C/C++ programming languages to understand the book's examples. The ability to read basic x86 assembly is desired but is not a strict requirement. The author also expects familiarity with basic concepts of computer architecture and operating systems like central processor, memory, process, thread, virtual and physical memory, context switch, etc. If any of the mentioned terms are new to you, I suggest studying this material first.

[TODO]: put a link to an errata webpage 

\sectionbreak