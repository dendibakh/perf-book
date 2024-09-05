# How-to

Here you will find a collection of how-to's for editing the book.

Hint: to save time for exporting the entire book, you can limit it to only a single chapter with `-ch` option:

``` bash
python.exe export_book.py -ch 1 && pdflatex book.tex && bibtex book && pdflatex book.tex && pdflatex book.tex
```

You can also insert LaTeX tags directly into the `*.md` files as shown below. They will not be translated by pandoc. Please try to avoid doing so. :)

```
\sectionbreak
```

## Images

### Simple image

```
![40 Years of Microprocessor Trend Data.](../img/1/40-years-processor-trend.png){#fig:40YearsProcessorTrend width=90%}
```
Reference it in the text with `@fig:40YearsProcessorTrend`.

### Two images side-by-side

```
<div id="fig:BBLayout">
![default layout](../../img/5/BBLayout_Default.jpg){#fig:BB_default width=30%}
![improved layout](../../img/5/BBLayout_Better.jpg){#fig:BB_better width=30%}

Two different layouts for the code snippet.
</div>
``` 
Reference it in the text with `@fig:BB_default`, `@fig:BB_better`, or `@fig:BBLayout`

## Table

```
--------------------------------------------------------------------------
Event  Umask Event Mask            Description
 Num.  Value Mnemonic              
------ ----- --------------------- ---------------------------------------
C0H     00H  INST_RETIRED.         Number of instructions retired. 
             ANY_P

C4H     00H  BR_INST_RETIRED.      Branch instructions retired.
             ALL_BRANCHES                  
--------------------------------------------------------------------------

Table: Example of encoding Skylake performance events. {#tbl:perf_count}
```
Reference it in the text with `{@tbl:perf_count}`.

## Paper/Book reference

To reference a book, first download its citation in BibTeX format, e.g.:

```
@Article{Mytkowicz09,
  author     = {Mytkowicz, Todd and Diwan, Amer and Hauswirth, Matthias and Sweeney, Peter F.},
  title      = {Producing Wrong Data without Doing Anything Obviously Wrong!},
  journal    = {SIGPLAN Not.},
  year       = {2009},
  volume     = {44},
  number     = {3},
  pages      = {265–276},
  month      = mar,
  issn       = {0362-1340},
  address    = {New York, NY, USA},
  doi        = {10.1145/1508284.1508275},
  issue_date = {February 2009},
  keywords   = {measurement, bias, performance},
  numpages   = {12},
  publisher  = {Association for Computing Machinery},
  url        = {https://doi.org/10.1145/1508284.1508275},
}
```
Reference the paper in the text with `[@Mytkowicz]`.

Not all fields in the citations are required, but get at least `title`, `organization`, `year`, `url`. 

## Code listings

```
Listing: a.c

~~~~ {#lst:optReport .cpp .numberLines}
void foo(float* __restrict__ a, 
         float* __restrict__ b, 
         float* __restrict__ c,
         unsigned N) {
  for (unsigned i = 1; i < N; i++) {
    a[i] = c[i-1]; // value is carried over from previous iteration
    c[i] = b[i];
  }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```
Reference the code listing in the text with `[@lst:optReport]`

You can also use a simpler version for tiny snippets or command line scripts:

```
```$ perf record -- ./ls```
```

## Footnotes

```
[^1]: Profiling(wikipedia) - [https://en.wikipedia.org/wiki/Profiling_(computer_programming)](https://en.wikipedia.org/wiki/Profiling_(computer_programming)).
```
Reference the footnote in the same `*.md` file with `[^1]`

## Section reference

To reference a section of the book from another chapter, first add a tag to the header of the section that you want to refer to, e.g.:

```
# Performance Analysis {#sec:sec1}
```
Reference the section in the text with `[@sec:sec1]`

## Math formulas

Below are two examples of math formulas: one simple and one more involved. You can check how they get rendered.

```
$$
IPC = \frac{INST\_RETIRED.ANY}{CPU\_CLK\_UNHALTED.THREAD}
$$

$$
\begin{aligned}
\textrm{Peak FLOPS} =& \textrm{ 8 (number of logical cores)}~\times~\frac{\textrm{256 (AVX bit width)}}{\textrm{32 bit (size of float)}} ~ \times ~ \\
& \textrm{ 2 (FMA)} \times ~ \textrm{3.8 GHz (Max Turbo Frequency)} \\
& = \textrm{486.4 GFLOPs}
\end{aligned}
$$
```

## Quotes

```
> "During the post-Moore era, it will become ever more important to make code run fast and, in particular, to tailor it to the hardware on which it runs." [@Leisersoneaam9744]
```
