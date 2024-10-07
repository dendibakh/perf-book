import os, sys
import argparse
import subprocess
import shlex
from shlex import quote
from shlex import split
import natsort 
import re

parser = argparse.ArgumentParser(description='Export book to PDF')
parser.add_argument("-ch", type=int, help="Chapter to export", default="99")
parser.add_argument("-paperback", help="Export for paperback print", action="store_true", default=False)
parser.add_argument("-kindle", help="Export the kindle version", action="store_true", default=False)
parser.add_argument("-v", help="verbose", action="store_true", default=False)
args = parser.parse_args()

chapterNum = args.ch
verbose = args.v
chapterStr = os.path.join('chapters', str(chapterNum) + '-')
chapter17Str = os.path.join('chapters', '17-')
print(chapterStr)

def run_cmd(cmd):
	process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
	output = process.stdout.read()
	return output.decode('utf-8')

def get_list_of_files(path, extension):
    list_of_files = []
    for root, dirs, files in os.walk(path):
        if (chapterNum != 99) and (chapterStr not in root) and (chapter17Str not in root):
            continue        
        for file in files:
            if file.endswith("." + extension):
                list_of_files.append(shlex.quote(os.path.join(root, file)))
    return list_of_files

file_list = natsort.natsorted(get_list_of_files(os.path.join('.', 'chapters'), 'md'))
if verbose:
    for file in file_list:
        print(file)

pandoc_cmd = 'pandoc -N --file-scope --pdf-engine=xelatex --listings --include-in-header header.tex '
if args.paperback:
  pandoc_cmd = pandoc_cmd + "-V classoption=twoside "
  pandoc_cmd = pandoc_cmd + "-V geometry:paperwidth=169.90mm "
  pandoc_cmd = pandoc_cmd + "-V geometry:paperheight=244.10mm "
  pandoc_cmd = pandoc_cmd + "-V geometry:inner=2.6cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:outer=1.4cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:top=2cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:bottom=2cm "
  pandoc_cmd = pandoc_cmd + "-V fontsize:8pt "
elif args.kindle:
  pandoc_cmd = pandoc_cmd + "-V geometry:paperwidth=169.90mm "
  pandoc_cmd = pandoc_cmd + "-V geometry:paperheight=244.10mm "
  pandoc_cmd = pandoc_cmd + "-V geometry:left=1cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:right=1cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:top=1.5cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:bottom=1.5cm "
  pandoc_cmd = pandoc_cmd + "-V fontsize:12pt "
else:
  pandoc_cmd = pandoc_cmd + "--include-before-body cover.tex "
  pandoc_cmd = pandoc_cmd + "-V geometry:left=2cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:right=2cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:top=2cm "
  pandoc_cmd = pandoc_cmd + "-V geometry:bottom=2cm "
  pandoc_cmd = pandoc_cmd + "-V fontsize:10pt "

pandoc_cmd = pandoc_cmd + "--filter pandoc-fignos --filter pandoc-tablenos --filter pandoc-crossref --natbib -o book.tex metadata.txt "

files_string = " ".join(file_list)
files_string += " footer.tex"

if verbose:
    print (pandoc_cmd + files_string)
run_cmd(pandoc_cmd + files_string)

# post-processing

texFile = 'book.tex'
editTexFile = 'book_edit.tex'

with open(texFile, 'r') as f:
    lines = f.readlines()

with open(editTexFile, 'w') as g:
    chapterRefs = []
    prev = ""
    for line in lines:
        if "\\section{" in line:
            chapterLabelPattern = r"\\hypertarget\{(.*?)\}"
            match = re.search(chapterLabelPattern, prev)
            if match:
                chapterRefs.append("{" + match.group(1) + "}")
        prev = line

    startTableCPUFESummary = False
    startTableARMsChip = False
    startTablePerfMetrics = False
    addTabularnewlineTableCPUFESummary = False
    addTabularnewlineTableARMsChip = False
    addTabularnewlineTablePerfMetrics = False
    for line in lines:
        # change font size in listings for paperback
        if (args.paperback or args.kindle) and "basicstyle=\\ttfamily," in line:
            g.write(line.replace("basicstyle=\\ttfamily,", "basicstyle=\\lst@ifdisplaystyle\\footnotesize\\fi\\ttfamily,"))
        # workaround for citations and bibliography
        elif "\\usepackage[]{natbib}" in line:
            g.write(line.replace("\\usepackage[]{natbib}", ''))
        elif "\\bibliographystyle{plainnat}" in line:
            g.write(line.replace("\\bibliographystyle{plainnat}", '\\bibliographystyle{apalike-ejor}'))
        else:
            # Add \tabularnewline for the table in the CPU Front-End section
            if "\\caption{Summary of CPU Front-End optimizations" in line:
                startTableCPUFESummary = True
            if startTableCPUFESummary and "\\endhead" in line:
                addTabularnewlineTableCPUFESummary = True
            if addTabularnewlineTableCPUFESummary and "\\end{minipage}\\tabularnewline" in line:
                line = line.replace("\\end{minipage}\\tabularnewline", "\\end{minipage}\\tabularnewline\\tabularnewline")
            if addTabularnewlineTableCPUFESummary and "\\end{longtable}" in line:
                addTabularnewlineTableCPUFESummary = False
                startTableCPUFESummary = False

            if "\\caption{List of recent ARM ISAs along with their own and third-party" in line:
                startTableARMsChip = True
            if startTableARMsChip and "\\endhead" in line:
                addTabularnewlineTableARMsChip = True
            if addTabularnewlineTableARMsChip and "\\end{minipage}\\tabularnewline" in line:
                line = line.replace("\\end{minipage}\\tabularnewline", "\\end{minipage}\\tabularnewline\\tabularnewline")                
            if addTabularnewlineTableARMsChip and "\\end{longtable}" in line:
                addTabularnewlineTableARMsChip = False
                startTableARMsChip = False      

            if "\\caption{A list (not exhaustive) of performance metrics along with" in line:
                startTablePerfMetrics = True
            if startTablePerfMetrics and "\\endhead" in line:
                addTabularnewlineTablePerfMetrics = True
            if addTabularnewlineTablePerfMetrics and "\\end{minipage}\\tabularnewline" in line:
                line = line.replace("\\end{minipage}\\tabularnewline", "\\end{minipage}\\tabularnewline\\tabularnewline")                
            if addTabularnewlineTablePerfMetrics and "\\end{longtable}" in line:
                addTabularnewlineTablePerfMetrics = False
                startTablePerfMetrics = False      
                      
            
            # workaround for citations and bibliography
            if "\\citep" in line:
                line = line.replace("\\citep", '\\cite')

            # replace Section -> Chapter for top-level sections
            if "Section~\\ref{" in line:
                for chref in chapterRefs:
                    if chref in line:
                        line = line.replace("Section~\\ref" + chref, "Chapter~\\ref" + chref)
            g.write(line)

os.remove('book.tex')
os.rename('book_edit.tex', 'book.tex')

# now we don't have URLs. Compare with natbib to figure out the differences