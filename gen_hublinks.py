"""Refresh the child-link list on hand-authored hub pages.

Generated pages get their child list from gen_pages.py. Hand-authored pages
(the Ayurveda set) need the same list kept in sync when filenames change, so
this rewrites the block in place — idempotent, safe to run every build.
"""
import json, codecs, os, re
from gen_nav import assign_paths, page_of, kids, esc, resolve, load_tree

TREE = 'navtree.json'

# hand-authored page  ->  the menu path whose children it should list
HUBS = {
    'ayurveda-curriculum.html': ['Indian Medicine', 'Ayurveda', 'Curriculum & Syllabus'],
    'ayurveda-calendar.html':   ['Indian Medicine', 'Ayurveda', 'Academic Calendar'],
}

BLOCK = re.compile(r'[ \t]*<ul class="doc-list.*?</ul>\n?', re.S)


def find(tree, path):
    node, cur = None, tree
    for label in path:
        node = next(n for n in cur if n['label'] == label)
        cur = kids(node)
    return node


def render(node, indent='          '):
    rows = ['%s<ul class="doc-list js rv in" style="animation-delay:.22s">' % indent]
    for c in kids(node):
        href = resolve(c['href'])
        if not href.startswith('http') and not href.lower().endswith('.pdf'):
            href = page_of(c)
        n = len(kids(c))
        meta = ' <span class="pill">%d</span>' % n if n else ''
        rows.append('%s  <li><a class="doc" href="%s">%s%s</a></li>'
                    % (indent, href, esc(c['label']), meta))
    rows.append('%s</ul>' % indent)
    return '\n'.join(rows) + '\n'


def main():
    tree = load_tree()
    assign_paths(tree)
    for fname, path in HUBS.items():
        p = os.path.join('src', fname)
        if not os.path.exists(p):
            print('  skip (no file):', fname)
            continue
        node = find(tree, path)
        html = codecs.open(p, encoding='utf-8').read()
        block = render(node)
        if BLOCK.search(html):
            new = BLOCK.sub(block, html, count=1)
        else:
            # first insertion: sit it above the page's closing action row
            m = re.search(r'\n[ \t]*<div style="margin-top: 3rem;">', html)
            if not m:
                print('  skip (no anchor):', fname)
                continue
            new = html[:m.start()] + '\n' + block + html[m.start():]
        codecs.open(p, 'w', encoding='utf-8').write(new)
        print('  %-32s %d child links' % (fname, len(kids(node))))


if __name__ == '__main__':
    main()
