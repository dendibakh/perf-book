[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/dendibakh)](https://twitter.com/dendibakh)
![GitHub Repo stars](https://img.shields.io/github/stars/dendibakh/perf-book)

# "Performance Analysis and Tuning on Modern CPUs" by Denis Bakhvalov, et al.

## Building a book (pdf)

At the moment, building the PDF book only works on Windows and Linux. MacOS requires building some components (e.g. pandoc-crossref) from sources.

Requirements:

 * Python3. Install natsort module: `pip install natsort`.
 * [Pandoc](https://pandoc.org/installing.html). Install [version 2.9](https://github.com/jgm/pandoc/releases/tag/2.9.2.1)
 * `pandoc-fignos` and `pandoc-tablenos`. Run `pip install pandoc-fignos pandoc-tablenos`.
 * `pandoc-crossref`. This one requires manual installation. I just downloaded the binary from [here](https://github.com/lierdakil/pandoc-crossref/releases/tag/v0.3.6.4) and copied it to the same place where `pandoc-fignos` is.
 * [MiKTeX](https://miktex.org/download). Check `Yes` for automatic package installation.

Run:
```bash
# Linux bash and Windows cmd prompt
python export_book.py && pdflatex book.tex && bibtex book && pdflatex book.tex && pdflatex book.tex

# Windows powershell
function Run-Block-With-Error($block) {
    $ErrorActionPreference="Stop"
    Invoke-Command -ScriptBlock $block
}
Run-Block-With-Error {python.exe export_book.py; pdflatex book.tex; bibtex book; pdflatex book.tex; pdflatex book.tex}
```

As a result, `book.pdf` will be generated. The first compilation may be slow.

## License

[Creative Commons Zero v1.0 Universal](LICENSE)
