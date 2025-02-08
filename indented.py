#!/usr/bin/python3
import datetime
import re
import os
import html

def read_indented_data_from_fn(filename):
    return read_indented_data_from_file(open(filename))

def read_indented_data_from_file(infile):
    return read_indented_data_from_lines(infile.readlines())

def read_indented_data_from_lines(lines):
    lines = [line.rstrip() for line in lines]
    # get rid of blanks and commented lines: (; first non-blank is the comment character)
    lines = [html.escape(line) for line in lines if line.lstrip() and line.lstrip()[0] != ';']

    return parse_indented_data(lines)

def indent(s):
    for i in range(len(s)):
        if s[i] != ' ':
            return int(i/2)
    return int(len(s)/2)

def parse_indented_data(lines):
    pos = 0
    children = []
    ll = len(lines)
    while pos < ll:
        child, pos = parse_indented_data_inner(lines, pos, 0)
        children.append(child)
    return children

"From the top, call with level = 0 repeatedly"
def parse_indented_data_inner(lines, pos, level):
    myline = lines[pos]
    if not indent(myline) == level:
        print('ERROR')
    label = myline.lstrip()
    children = []
    ll = len(lines)
    pos += 1
    while pos < ll and indent(lines[pos]) > level:
        if indent(lines[pos]) == level + 1:
            child, pos = parse_indented_data_inner(lines, pos, level + 1)
            children.append(child)
    if children:
        return [label, children], pos
    else:
        return label, pos

def main(args):
    print(read_indented_data_from_file(sys.stdin))

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
