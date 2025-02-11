#!/usr/bin/python3
import sys
import datetime
import re
import os
import html

DEBUG=False

def debug(*args):
    if DEBUG:
        print(*args)


COMMENT_CHARACTERS = ';#'

def read_indented_data_from_fn(filename):
    return read_indented_data_from_file(open(filename))

def read_indented_data_from_file(infile):
    return read_indented_data_from_lines(infile.readlines())

def read_indented_data_from_lines(lines):
    lines = [line.rstrip() for line in lines]
    # get rid of blanks and commented lines:
    lines = [html.escape(line) for line in lines
             if line.lstrip() and line.lstrip()[0] not in COMMENT_CHARACTERS]
    return parse_indented_data(lines)

def get_indent_and_label(s):
    i = 0
    while s.startswith(indent_string):
        i += 1
        s = s[len(indent_string):]
    if s.startswith(indent_separator):
        s = s[len(indent_separator):]
    return i, s


indent_string = None
indent_separator = ''


def set_indent_string_and_separator(indstring, indsep):
    global indent_string, indent_separator
    indent_string = indstring
    indent_separator = indsep


def guess_indent_string(lines):
    # check for org-mode outline format:
    if lines[0][0] == '*':
        debug('org-mode')
        return '*', ' '
    # must be spaces or tabs, with no separator:
    for line in lines:
        if line.lstrip() != line:
            break
    guess = line[:-len(line.lstrip())]
    if guess:
        return guess, ''
    # default to four spaces:
    return '    ', ''

def parse_indented_data(lines):
    "This parses a forest, and returns a forest (a list of trees)"
    global indent_string, indent_separator
    if indent_string is None:
        indent_string, indent_separator = guess_indent_string(lines)
    debug('indent string is "%s"' % indent_string)
    pos = 0
    children = []
    ll = len(lines)
    # now we split each line into a (numeric) indent and a label:
    indented_lines = [get_indent_and_label(line) for line in lines]
    debug(indented_lines)
    outer_indent = indented_lines[0][0]
    while pos < ll:
        child, pos = parse_indented_data_inner(indented_lines, pos, outer_indent)
        children.append(child)
    return children

def parse_indented_data_inner(indented_lines, pos, level):
    "From the top, call with level = outermost level# repeatedly"
    ind, label = indented_lines[pos]
    if not ind == level:
        debug('expected level %d, got %d, "%s"' % (level, ind, label))
        print('ERROR')
    children = []
    ll = len(indented_lines)
    pos += 1
    while pos < ll and indented_lines[pos][0] > level:
        if indented_lines[pos][0] == level + 1:
            child, pos = parse_indented_data_inner(indented_lines, pos, level + 1)
            children.append(child)
    if children:
        return [label, children], pos
    else:
        return label, pos

def main(args):
    print(read_indented_data_from_file(sys.stdin))

if __name__ == '__main__':
    main(sys.argv[1:])

# TODO:
# __ option to print tree as JSON
# __ option to Python pretty-print tree
