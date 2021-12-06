import os, sys
import argparse
import subprocess
import shlex
from shlex import quote
from shlex import split
import natsort 

def run_cmd(cmd):
	process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
	output = process.stdout.read()
	return output.decode('utf-8')

def get_list_of_files(path, extension):
    list_of_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("." + extension):
                list_of_files.append(shlex.quote(os.path.join(root, file)))
    return list_of_files

file_list = natsort.natsorted(get_list_of_files(os.path.join('.', 'chapters'), 'md'))
for file in file_list:
    print(file)

default_pandoc_cmd = 'pandoc -N --file-scope --pdf-engine=xelatex --listings --include-in-header header.tex --include-before-body cover.tex --filter pandoc-fignos --filter pandoc-tablenos --filter pandoc-crossref --natbib -o book.tex metadata.txt '
files_string = " ".join(file_list)
files_string += " footer.tex"

#print (default_pandoc_cmd + files_string)
run_cmd(default_pandoc_cmd + files_string)