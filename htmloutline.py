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
<title>Outline</title>
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
</style>
</head>
<body>

<h1>Outline</h1>
'''

FOOTER = '''
</body>
</html>
'''


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

BRANCH_DIV = '<div class="branch%s" onclick="toggleSubtree(this)">%s</div>' #  expanded
SUBTREE_DIV_START = '<div class="subtree"%s>' #  style="display:block"
SUBTREE_DIV_END = '</div>'
LABEL_DIV = '<div class="label">%s</div>'

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
    pad = ('  ' * level)
    if not has_children(tree):
        debug('no children')
        output.append(pad + LABEL_DIV % label)
    else:
        debug('has children')
        branch_expansion, subtree_expansion = '', ''
        if (level+1) <= settings['expand_to_level']:
            branch_expansion = ' expanded'
            subtree_expansion = ' style="display:block"'
        output.append(pad + BRANCH_DIV % (branch_expansion, label))
        output.append(pad + SUBTREE_DIV_START % subtree_expansion)
        children = get_children(tree)
        for child in children:
            debug('this child is', child)
            output += emit_html(child, expand_to_level, level + 1)
        output.append(pad + SUBTREE_DIV_END)
        
    return output

settings = { 'expand_to_level': 1000000 }

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
        else:
            print('WARNING: ignoring unknown argument "%s"' % a, file=sys.stderr)

def main(args):
    parse_args(args, settings)
    if settings.get('use_example_data', False):
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
    print(HEADER)
    print('\n'.join(output))
    print(FOOTER)

if __name__ == '__main__':
    main(sys.argv[1:])

# TODO:
# __ option to skip header and footer
# __ add level-1, level-2, etc. classes to labels
# __ option to start with everything expanded (maybe use onLoad()?)
# __ option to start with top n levels expanded
# __ option to speicfy the title/h1
# __ option to specify indent string and separator
# __ option for indent to be a regexp (count them? or just how wide entire string is?)
# __ add ability to have leaves: just text that gets hidden or shown, not an outline line
# __ add option for different comment character (currently just ";")
# __ possibly add middle-of-the-line comments
# __ make sure we deal with blank lines correctly
# __ add option for auto-numbering the labels
# __ add anchors for the labels
# __ add url targets for the labels
# __ make it understand limited markdown: bold, italics, links, maybe some other stuff
# __ add JavaScript to do org-mode type things: expand/contract, tab through 1-level, all levels, all text
# __ think about how someone could *edit* an outline in HTML, via the browser
# __ generate an outline live, from a file or API call
