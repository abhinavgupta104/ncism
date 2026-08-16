"""Extract the full primary-nav tree (with hrefs) from the scraped NCISM homepage."""
import codecs, json, re, sys
from html.parser import HTMLParser

SRC = 'scrape/index.php.html'


class NavParser(HTMLParser):
    """Walks ul/li/a nesting and rebuilds the menu as a tree."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0            # nesting depth inside the target <ul>
        self.active = False       # inside ul.navbar-nav.custom-nav?
        self.root = []
        self.stack = []           # stack of child-lists
        self.li_stack = []        # stack of current li dicts
        self.cur_a = None         # li whose <a> text we are collecting
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '')

        if tag == 'ul':
            if not self.active and 'navbar-nav' in cls and 'custom-nav' in cls:
                self.active = True
                self.depth = 1
                self.stack = [self.root]
                return
            if self.active:
                self.depth += 1
                # nested ul -> children of the most recent li
                if self.li_stack:
                    self.stack.append(self.li_stack[-1].setdefault('children', []))
                else:
                    self.stack.append(self.root)
            return

        if not self.active:
            return

        if tag == 'li':
            node = {'label': '', 'href': None}
            self.stack[-1].append(node)
            self.li_stack.append(node)
            return

        if tag == 'a' and self.li_stack:
            node = self.li_stack[-1]
            if node['href'] is None:
                node['href'] = a.get('href', '')
                self.cur_a = node

    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag == 'ul':
            self.depth -= 1
            if self.depth <= 0:
                self.active = False
            elif len(self.stack) > 1:
                self.stack.pop()
            return
        if tag == 'li' and self.li_stack:
            self.li_stack.pop()
            return
        if tag == 'a':
            self.cur_a = None

    def handle_data(self, data):
        if self.cur_a is not None:
            self.cur_a['label'] += data


def clean(node):
    node['label'] = re.sub(r'\s+', ' ', node.get('label', '')).strip()
    for c in node.get('children', []):
        clean(c)
    return node


def classify(href):
    if not href:
        return 'EMPTY'
    h = href.strip()
    if h in ('#', ''):
        return 'DEAD'
    if h.lower().endswith('.pdf'):
        return 'PDF'
    if h.startswith('http') and 'ncismindia.org' not in h:
        return 'EXTERNAL'
    if 'coming-soon' in h:
        return 'STUB'
    return 'PAGE'


def render(nodes, ind=0, out=None):
    out = out if out is not None else []
    for n in nodes:
        kind = classify(n['href'])
        out.append('%s%s  [%s] %s' % ('   ' * ind, n['label'] or '(no label)', kind, n['href'] or ''))
        render(n.get('children', []), ind + 1, out)
    return out


html = codecs.open(SRC, encoding='utf-8', errors='replace').read()
p = NavParser()
p.feed(html)
tree = [clean(n) for n in p.root]
tree = [n for n in tree if n['label'] or n.get('children')]

print('\n'.join(render(tree)))

# counts
tally, pdfs, ext = {}, [], []


def walk(nodes, trail=()):
    for n in nodes:
        k = classify(n['href'])
        tally[k] = tally.get(k, 0) + 1
        path = trail + (n['label'],)
        if k == 'PDF':
            pdfs.append((' > '.join(path), n['href']))
        if k == 'EXTERNAL':
            ext.append((' > '.join(path), n['href']))
        walk(n.get('children', []), path)


walk(tree)
print('\n===== TALLY =====')
for k, v in sorted(tally.items()):
    print(' %-9s %d' % (k, v))
print('\n===== PDFS (%d) =====' % len(pdfs))
for label, href in pdfs:
    print(' %s\n     %s' % (label, href))

json.dump(tree, open(sys.argv[1], 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('\nwrote', sys.argv[1])
