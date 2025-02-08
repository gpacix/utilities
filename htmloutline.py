#!/usr/bin/env python3

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

BRANCH_DIV = '<div class="branch" onclick="toggleSubtree(this)">%s</div>' #  expanded
SUBTREE_DIV_START = '<div class="subtree">' #  style="block"
SUBTREE_DIV_END = '</div>'
LABEL_DIV = '<div class="label">%s</div>'

def emit_html(tree, level=0):
    output = []
    # if no children:
    #   output this tree's root label
    # else:
    #   output this tree's root label, wrapped in a branch div
    #   output the children wrapped in a subtree div
    label = get_label(tree)
    if DEBUG:
        label = ('[%d]' % level) + label
    debug('label is', label)
    pad = ('  ' * level)
    if not has_children(tree):
        debug('no children')
        output.append(pad + LABEL_DIV % label)
    else:
        debug('has children')
        output.append(pad + BRANCH_DIV % label)
        output.append(pad + SUBTREE_DIV_START)
        children = get_children(tree)
        for child in children:
            debug('this child is', child)
            output += emit_html(child, level + 1)
        output.append(pad + SUBTREE_DIV_END)
        
    return output


def main(args):
    data = example_data
    if not is_tree(data):
        print('not a tree!')
        sys.exit(1)
    output = emit_html(data)
    debug(output)
    print(HEADER)
    print('\n'.join(output))
    print(FOOTER)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
