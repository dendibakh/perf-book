import os, sys
import argparse
import subprocess
import shlex
from shlex import quote
from shlex import split
import natsort 

parser = argparse.ArgumentParser(description='Compare multiple EMON outputs and generate an Excel file')
parser.add_argument("-ch", type=int, help="chapter to export", default="99")
parser.add_argument("-v", help="verbose", action="store_true", default=False)
args = parser.parse_args()

chapterNum = args.ch
verbose = args.v
chapterStr = os.path.join('chapters', str(chapterNum) + '-')
print(chapterStr)

def run_cmd(cmd):
	process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
	output = process.stdout.read()
	return output.decode('utf-8')

def get_list_of_files(path, extension):
    list_of_files = []
    for root, dirs, files in os.walk(path):
        if (chapterNum != 99) and (chapterStr not in root):
            continue        
        for file in files:
            if file.endswith("." + extension):
                list_of_files.append(shlex.quote(os.path.join(root, file)))
    return list_of_files

file_list = natsort.natsorted(get_list_of_files(os.path.join('.', 'chapters'), 'md'))
if verbose:
    for file in file_list:
        print(file)

default_pandoc_cmd = 'pandoc -N --file-scope --pdf-engine=xelatex --listings --include-in-header header.tex --include-before-body cover.tex --filter pandoc-fignos --filter pandoc-tablenos --filter pandoc-crossref --natbib -o book.tex metadata.txt '
files_string = " ".join(file_list)
files_string += " footer.tex"

if verbose:
    print (default_pandoc_cmd + files_string)
run_cmd(default_pandoc_cmd + files_string)