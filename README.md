![Build PDF](https://github.com/dendibakh/perf-book/actions/workflows/build_pdf.yml/badge.svg)

# perf-book

This is a repository with source files of the book "Performance Analysis and Tuning on Modern CPU" by Denis Bakhvalov, et al.

**Second edition work in progress!** Planned changes are outlined in the google [document](https://docs.google.com/document/d/1tr2qRDe72VSBYypIANYjJLM_zCdPB6S9m4LmXsQb0vQ/edit?usp=sharing). The planned new table of contents is in [new_toc.md](new_toc.md).

My goal is to accumulate as much knowledge as possible from all the best experts in the industry. And of course, share that knowledge with you. Contributions are welcome.

# Contributing

There are many ways how you can help.
- You can author a section(s) on a topic you are an expert in. But let me know before you start.
- Small improvements are welcome without prior approval, just open a new PR.
- Feel free to propose ideas for new content.
- Reviewers with all backgrounds are needed.

Check out the [discussions](https://github.com/dendibakh/perf-book/discussions) page to start.

For examples on how to add images, table, code listings, etc, see [how-to.md](how-to.md).

# Building a book (pdf)

Requirements:

 * Python3. Install natsort module: `pip install natsort`.
 * [pandoc](https://pandoc.org/installing.html) - install [version 2.9](https://github.com/jgm/pandoc/releases/tag/2.9.2.1).
 * install pandoc filters: `pip install pandoc-fignos pandoc-tablenos`
 * install `pandoc-crossref`. This one requires manual installation. I just downloaded the binary from [here](https://github.com/lierdakil/pandoc-crossref/releases/tag/v0.3.6.4) and copied it to the same place where `pandoc-fignos` is.
 * [MiKTeX](https://miktex.org/download) - check `Yes` for automatic packets installation

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

As a result, `book.pdf` will be generated. The first compilation may be slow due to the installation of required packets.

## License

[Creative Commons Zero v1.0 Universal](LICENSE)
