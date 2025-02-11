#!/usr/bin/env python3
import sys
import indented

DEBUG = False

def debug(*args):
    if DEBUG:
        print(*args)

# tree = label | [ label ] | [ label, [ tree tree tree ]]

example_data = ['Outline',
        [
            ['Level 2a', []],
            ['Level 2b', [
                'Level 3a of 2b', 'Level 3b of 2b']],
            'Level 2c']]


HEADER = '''<!DOCTYPE html>
<html>
<head>
<title>TITLE</title>
<script>
function toggleSubtree(element) {
  element.classList.toggle("expanded");
  const subtree = element.nextElementSibling;
  subtree.style.display = subtree.style.display === "block" ? "none" : "block";
}
</script>

<style>
  .branch {
    cursor: pointer;
    font-family: sans-serif;
  }
  .subtree {
    display: none;
    margin-left: 20px; /* Indentation */
    font-family: sans-serif;
  }
  .branch::before { /* Add a "+" icon */
      content: "▹ ";
  }
  .branch.expanded::before { /* Change to "-" when expanded */
      content: "▿ ";
  }
  .label::before { /* Add space */
      content: "   ";
  }
  .level-1 { font-size: 150%; }
  .level-2 { font-size: 130%; }
  .level-3 { font-size: 110%; }
  .level-rest { font-size: 100%; }
</style>
</head>
<body>

<h1>TITLE</h1>
'''

FOOTER = '''
</body>
</html>
'''


def join_alternate(separators, strings):
    "Join strings using first the first separator, then the second, then the first; always pair them"
    if (len(strings) % 2) == 0:
        strings.append('')
    r = strings.pop(0)
    next, after = separators[:2]
    while strings:
        r += next
        next, after = after, next
        r += strings.pop(0)
    return r

def markdown_faces(s):
    if '*' not in s:
        return s
    r = s[:]
    if '**' in r:
        r = join_alternate(['<b>', '</b>'], r.split('**'))
    if '*' in r:
        r = join_alternate(['<i>', '</i>'], r.split('*'))
    return r

def markdown_link(s):
    if '](' not in s:
        return s
    # may still not have a link in it:
    parts = s.split('](', maxsplit=1)
    if not ('[' in parts[0] and ')' in parts[1]):
        return s
    # work backwards from the end:
    before, linktext = parts[0].rsplit('[', maxsplit=1)
    linkurl, after = parts[1].split(')', maxsplit=1)
    return '%s<a href="%s">%s</a>%s' % (before, linkurl, linktext, after)

def markdown_links(s):
    olds = ''
    while not s == olds:
        olds = s[:]
        s = markdown_link(olds)
    return s


def markdown(s):
    return markdown_faces(markdown_links(s))

def is_tree(t):
    if type(t) == type(''):
        return True
    if type(t) != type([]):
        return False
    if len(t) == 0:
        return False
    if len(t) > 2:
        return False
    if type(t[0]) != type(''):
        return False
    if len(t) > 1:
        for child in t[1]:
            if not is_tree(child):
                print("NOT A TREE!", child)
                return False
    return True

def is_forest(maybe_forest):
    for t in maybe_forest:
        if not is_tree(t):
            return False
    return True

def get_label(tree):
    if type(tree) == type(''):
        return tree
    return tree[0]

def has_children(tree):
    if type(tree) == type(''):
        return False
    return len(tree) > 1 and len(tree[1]) > 0

def get_children(tree):
    if type(tree) == type(''):
        return []
    return tree[1]

BRANCH_DIV = '<div class="branch level-%s%s" onclick="toggleSubtree(this)">%s</div>'  # expanded
SUBTREE_DIV_START = '<div class="subtree"%s>'  # style="display:block"
SUBTREE_DIV_END = '</div>'
LABEL_DIV = '<div class="label level-%s">%s</div>'

def emit_html(tree, expand_to_level, level=0):
    output = []
    # if no children:
    #   output this tree's root label
    # else:
    #   output this tree's root label, wrapped in a branch div
    #   output the children wrapped in a subtree div
    label = get_label(tree)
    debug('emit_html looking at label:', label)
    if DEBUG:
        label = ('[%d]' % level) + label
    debug('label is', label)
    label = markdown(label)
    pad = ('  ' * level)
    level_string = str(level+1)
    if not has_children(tree):
        debug('no children')
        output.append(pad + LABEL_DIV % (level_string, label))
    else:
        debug('has children')
        branch_expansion, subtree_expansion = '', ''
        if (level+1) <= settings['expand_to_level']:
            branch_expansion = ' expanded'
            subtree_expansion = ' style="display:block"'
        output.append(pad + BRANCH_DIV % (level_string, branch_expansion, label))
        output.append(pad + SUBTREE_DIV_START % subtree_expansion)
        children = get_children(tree)
        for child in children:
            debug('this child is', child)
            output += emit_html(child, expand_to_level, level + 1)
        output.append(pad + SUBTREE_DIV_END)

    return output

settings = { 'title': 'Outline',
             'expand_to_level': 1000000,
             'wrapper': True,
             'use_example_data': False }

def parse_args(args, settings):
    while args:
        a = args.pop(0)
        if a == '--example':
            settings['use_example_data'] = True
        elif a in ['--expand', '-x']:
            levelstring = args.pop(0)
            if levelstring == 'all':
                levelstring = '1000000'
            elif levelstring == 'none':
                levelstring = '0'
            settings['expand_to_level'] = int(levelstring)
        elif a in ['--no-wrapper', '-w']:
            settings['wrapper'] = False
        elif a in ['--title', '-t']:
            settings['title'] = args.pop(0)
        else:
            print('WARNING: ignoring unknown argument "%s"' % a, file=sys.stderr)

def main(args):
    parse_args(args, settings)
    if settings['use_example_data']:
        data = example_data
    else:
        data = indented.read_indented_data_from_file(sys.stdin)

    debug(data)
    if not is_tree(data) and not is_forest(data):
        print('ERROR: not a tree or a forest!')
        sys.exit(1)
    if not is_forest(data):
        # if it's just a tree, make it a forest:
        data = [ data ]
    output = []
    for tree in data:
        output += emit_html(tree, settings['expand_to_level'])
    if settings['wrapper']:
        print(HEADER.replace("TITLE", settings['title']))
    print('\n'.join(output))
    if settings['wrapper']:
        print(FOOTER)

if __name__ == '__main__':
    main(sys.argv[1:])

# TODO:
# ++ option to skip header and footer
# ++ add level-1, level-2, etc. classes to labels
# ++ option to start with everything expanded (maybe use onLoad()?)
# ++ option to start with top n levels expanded
# ++ option to speicfy the title/h1
# __ option to specify (input) indent string and separator
# __ option for indent to be a regexp (count them? or just how wide entire string is?)
# __ add ability to have leaves: just text that gets hidden or shown, not an outline line
# __ add option for different comment character (currently just ";")
# __ possibly add middle-of-the-line comments
# __ make sure we deal with blank lines correctly
# __ add option for auto-numbering the labels
# __ add anchors for the labels
# __ add url targets for the labels
# ++ make it understand limited markdown: bold, italics
# ++ make it understand markdown links
# __ make it understand more markdown: maybe some other stuff
# __ add JavaScript to do org-mode type things: expand/contract, tab through 1-level, all levels, all text
# __ think about how someone could *edit* an outline in HTML, via the browser
# __ generate an outline live, from a file or API call
