# perf-book

This is a repository with source files of the book "Performance Analysis and Tuning on Modern CPU" by Denis Bakhvalov, et al.

# Requirements

You need to install:

 * Python3. Install natsort module: `pip install natsort`.
 * [pandoc](https://pandoc.org/installing.html) - install [version 2.9](https://github.com/jgm/pandoc/releases/tag/2.9.2.1).
 * install pandoc filters: `pip install pandoc-fignos pandoc-tablenos`
 * install `pandoc-crossref`. This one requires manual installation. I just downloaded the binary from [here](https://github.com/lierdakil/pandoc-crossref/releases/tag/v0.3.6.4) and copied it to the same place where `pandoc-fignos` is.
 * [MiKTeX](https://miktex.org/download) - check `Yes` for automatic packets installation

# Building a book (pdf)

Run:
```bash
# Linux bash & Mac
python.exe export_book.py && pdflatex book.tex && bibtex book && pdflatex book.tex && pdflatex book.tex

# Windows Powershell
function Run-Block-With-Error($block) {
    $ErrorActionPreference="Stop"
    Invoke-Command -ScriptBlock $block
}
Run-Block-With-Error {python.exe export_book.py; pdflatex book.tex; bibtex book; pdflatex book.tex; pdflatex book.tex}
```

First compilation may be slow due to installation of required packets.

## License

[Creative Commons Zero v1.0 Universal](LICENSE)
