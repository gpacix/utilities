#!/usr/bin/env python3

# This file is in the public domain.

def make_tree(xs, separator='/', key=None, attribute=None, index=None, lowercase=True, uppercase=False):
    tree = {}
    for x in xs:
        #if opts['debug']: print('x:', x)
        if not x:
            continue
        t = tree
        if key:
            field = x[key]
        elif attribute:
            field = x.__getattribute__(attribute)
        elif index:
            field = x[index]
        else:
            field = x

        if lowercase:
            field = field.lower()
        elif uppercase:
            field = field.upper()
        path = field.split(separator)
        # if first path element is empty, skip it:
        if path and not path[0]:
            path = path[1:]
        for pe in path[:-1]:
            if pe not in t:
                t[pe] = {}
            t = t[pe]
        t[path[-1]] = x
    return tree

def print_tree(t, indent='* ', print_leaves=False, sort_keys=True):
    keys = t.keys()
    if sort_keys:
        keys = list(keys)
        keys.sort()
    for k in keys:
        print(indent + k)
        if k in t:
            if type(t[k]) == type({}):
                print_tree(t[k], '*' + indent, print_leaves, sort_keys)
            elif print_leaves:
                print(t[k])

opts = {}

def process_args(args):
    if '-?' in args or '--help' in args:
        print_help_and_exit()
    for arg in args:
        if arg in ['-l', '--leaves']:
            opts['leaves'] = True
        elif arg in ['-u', '--unsorted']:
            opts['sortem'] = False
        elif arg.startswith('-S'):
            sc = arg[2:] # may not actually be a single char
            if sc == '\\t':
                sc = '\t'
            if sc:
                opts['separator'] = sc
        elif arg.startswith('--separator='):
            sc = arg[12:] # may not actually be a single char
            if sc == '\\t':
                sc = '\t'
            if sc:
                opts['separator'] = sc
        elif arg in ['-k', '--keepcase']:
            opts['lowerit'] = False
            opts['upperit'] = False
        elif arg in ['--lowercase']:
            opts['lowerit'] = True
            opts['upperit'] = False
        elif arg in ['--uppercase']:
            opts['upperit'] = True
            opts['lowerit'] = False
        elif arg in ['-D', '--debug']:
            opts['debug'] = True
        else:
            print('unknown argument: ' + arg, file=sys.stderr)

def print_help_and_exit():
    print(sys.argv[0]+''':
   Read lines from standard input, interpret them as paths in a tree,
   and print the tree to standard output.

     -?, --help         print this help message
     -l, --leaves       print the leaves (original lines), not just the nodes (path elements)
     -u, --unsorted     do not sort the nodes before printing them
     -S, --separator=   use the string immediately after -S as the path-element separator,
                        instead of '/'.  -S'\\t' will specify TAB as the separator
     --lowercase        convert all path elements to lowercase (this is the default)
     --uppercase        convert all path elements to uppercase
     -k, --keepcase     do not convert the case of path elements (default is to lowercase them)
     -D, --debug        print debugging information

   treeify is also usable as a Python module, for even more flexibility.\n''',
          file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    import sys
    opts = { 'debug': False, 'leaves': False, 'sortem': True, 'lowerit': True, 'upperit': False, 'separator': '/' }
    process_args(sys.argv[1:])
    if opts['debug']: print('opts:', opts)
    t = make_tree([line.rstrip() for line in sys.stdin], separator=opts['separator'], lowercase=opts['lowerit'], uppercase=opts['upperit'])
    if opts['debug']: print('t:', t)
    print_tree(t, print_leaves=opts['leaves'], sort_keys=opts['sortem'])
