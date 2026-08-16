"""Generate the primary navbar from the nav tree scraped off the official site.

Reads navtree.json (produced by navextract.py from scrape/index.php.html) and
writes src/_nav.html, which build.py injects into the layout at {{NAV}}.

The official menu goes 8 levels deep via cascading hover flyouts. This flattens
it to the house rule: the navbar carries two levels, anything deeper becomes a
link to a page that holds the rest.
"""
import json, re, codecs, os

TREE = 'navtree.json'
OUT = 'src/_nav.html'

# pages already built by hand keep their existing filenames
OVERRIDE = {
    # the hub covers the introduction — one page, not two
    'ayurveda.php': 'ayurveda.html',
    'index.php': 'index.html',
}

# Nodes whose href is a dead '#' or a coming-soon stub get their filename
# derived from their path. These are the ones we've authored by hand, keyed by
# their trail through the menu so they keep their existing URLs.
PATH_OVERRIDE = {
    'Indian Medicine>Ayurveda': 'ayurveda.html',
    'Indian Medicine>Ayurveda>List of Ayurveda Colleges': 'ayurveda-colleges.html',
    # 'ayurveda-syllabus.html' is taken by the real Old Syllabus page
    # (ayurveda-syllabus.php), so the hub gets its own name
    'Indian Medicine>Ayurveda>Curriculum & Syllabus': 'ayurveda-curriculum.html',
    'Indian Medicine>Ayurveda>Academic Calendar': 'ayurveda-calendar.html',
    'Indian Medicine>Ayurveda>Library': 'ayurveda-library.html',
}

# Top-level menus folded in as columns of another menu. Thirteen items plus the
# brand needs ~2090px of bar; these three are small, low-traffic and read
# naturally as services, so they move under Others.
MERGE_INTO = {
    'Vigilance Corner': 'Others',
    'RTI': 'Others',
    'Results': 'Others',
}

# id(node) -> output filename, filled by assign_paths()
PATHS = {}
# nodes whose filename came from PATH_OVERRIDE — an explicit pin that later
# rules (the Introduction merge) must not overwrite
PINNED = set()

# PDFs mirrored into assets/pdf/ (the rest still resolve to the origin)
LOCAL_PDFS = {
    'Attachment 0SPUR scheme_1320.pdf',
    'NCISM Schemes for financial assistance Brochure (4).pdf',
    'Textbook Quality Assessment Scale.pdf',
    'Ayush Module Internship Electives for MBBS.pdf',
    'SoP for access NCISM certificate from DigiLocker.pdf',
}

ORIGIN = 'https://ncismindia.org/'
ACCENTS = ['var(--saffron)', 'var(--teal)', 'var(--leaf)', 'var(--gold)']


def slug(name):
    """ayurveda-syllabus.php -> ayurveda-syllabus.html"""
    n = re.sub(r'\.php$', '', name, flags=re.I)
    n = n.replace('%20', ' ').strip()
    n = re.sub(r'[^A-Za-z0-9]+', '-', n).strip('-').lower()
    return (n or 'page') + '.html'


def resolve(href):
    """Map an official href onto this build's URL space."""
    if not href or href.strip() in ('#', ''):
        return '#'
    h = href.strip()
    if h.startswith('http'):
        return h
    if h.lower().endswith('.pdf'):
        base = h.split('/')[-1]
        if base in LOCAL_PDFS:
            return 'assets/pdf/' + base
        from urllib.parse import quote
        return ORIGIN + quote(h)
    if 'coming-soon' in h:
        return 'coming-soon.html'
    if h in OVERRIDE:
        return OVERRIDE[h]
    return slug(h)


def load_tree(path=TREE):
    """Read the scraped menu and apply the top-level merges.

    Both gen_nav and gen_pages must see the same shape, or filenames and
    breadcrumbs drift apart — so every consumer loads through here.
    """
    tree = json.load(open(path, encoding='utf-8'))
    by_label = {m['label']: m for m in tree}
    out = []
    for m in tree:
        target = MERGE_INTO.get(m['label'])
        if target and target in by_label:
            by_label[target].setdefault('children', []).append(m)
            continue
        out.append(m)
    return out


def assign_paths(tree):
    """Give every node a unique output filename.

    A node with a real .php href keeps that name (two nodes legitimately
    sharing an href share a page). A node with a dead '#' or a coming-soon
    stub is named from its whole trail, so Ayurveda's "Curriculum & Syllabus"
    and Unani's don't collide on one file.
    """
    PATHS.clear()
    taken = set()

    def real(href):
        h = (href or '').strip()
        return (h and h != '#' and not h.startswith('http')
                and not h.lower().endswith('.pdf') and 'coming-soon' not in h)

    def walk(nodes, trail):
        for n in nodes:
            path_key = '>'.join([t['label'] for t in trail] + [n['label']])
            href = (n.get('href') or '').strip()
            if path_key in PATH_OVERRIDE:
                name = PATH_OVERRIDE[path_key]
                PINNED.add(id(n))
            elif href in OVERRIDE:
                name = OVERRIDE[href]
            elif real(href):
                name = slug(href)
            else:
                # derived: nearest ancestor + label is enough to disambiguate
                # in practice; widen the trail only if that name is taken
                parts = [t['label'] for t in trail[1:]] + [n['label']]
                for take in range(min(2, len(parts)), len(parts) + 1):
                    cand = slug('-'.join(parts[-take:]))
                    if len(cand) > 65:
                        cand = cand[:60].rstrip('-') + '.html'
                    if cand not in taken:
                        break
                name = cand
                base = name[:-5]
                i = 2
                while name in taken:
                    name = '%s-%d.html' % (base, i)
                    i += 1
            taken.add(name)
            PATHS[id(n)] = name
            walk(kids(n), trail + (n,))

    walk(tree, ())
    return PATHS


def page_of(node):
    """Where this node's page lives."""
    return PATHS.get(id(node)) or slug(node['label'])


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def is_pdf(href):
    return bool(href) and href.strip().lower().endswith('.pdf')


def is_ext(href):
    return bool(href) and href.strip().startswith('http') and 'ncismindia.org' not in href


def kids(n):
    return n.get('children') or []


# degree code under each system name — students look for these, not the system
DEGREE = {'Ayurveda': 'BAMS', 'Unani': 'BUMS', 'Siddha': 'BSMS', 'Sowa-Rigpa': 'BSRMS'}


def trim(label):
    """Drop context the column header already supplies."""
    # "List of Ayurveda Colleges" inside the Ayurveda column -> "Colleges"
    m = re.match(r'^List of\s+(.*?)\s+Colleges$', label, re.I)
    if m:
        return 'Colleges'
    return label


def link(node, indent, shorten=False):
    """One <a>. Deeper subtrees collapse to a single link to their hub page."""
    href = resolve(node['href'])
    mapped = PATHS.get(id(node))
    if mapped and (href in ('#', 'coming-soon.html') or not href.endswith('.html')
                   or href == slug(node['href'] or '')):
        if not href.startswith('http') and not href.lower().endswith('.pdf'):
            href = mapped
    label = esc(trim(node['label']) if shorten else node['label'])
    tag = ''
    if is_pdf(node['href']):
        tag = ' <span class="tag">PDF</span>'
    elif is_ext(node['href']):
        tag = ' <span class="tag">EXT</span>'
    # a node with children that we are flattening: point it at its own page
    if href == '#':
        href = page_of(node)
    ext = ' target="_blank" rel="noopener"' if is_ext(node['href']) else ''
    return '%s<a href="%s"%s>%s%s</a>' % (' ' * indent, href, ext, label, tag)


# menus that stay a single link in the bar regardless of what hangs off them
PLAIN = {'home'}
# a vertical list reads fine up to this many; past it, go to columns
FLAT_LIMIT = 10


def wants_mega(menu):
    """Mega panel when the menu has grandchildren or too many flat items."""
    if any(kids(c) for c in kids(menu)):
        return True
    return len(kids(menu)) > FLAT_LIMIT


def render_menu(menu, out, anchor_right=False):
    label = esc(menu['label'])
    children = kids(menu)

    # plain link in the bar — no children, or explicitly flattened
    if not children or menu['label'].strip().lower() in PLAIN:
        out.append('        <li><a href="%s" class="nav-btn">%s</a></li>'
                   % (page_of(menu) if menu['href'] in ('#','',None) else resolve(menu['href']), label))
        return

    mega = wants_mega(menu)
    cls = ' class="has-mega"' if mega else ''
    out.append('        <li%s><button class="nav-btn">%s <i>&#9660;</i></button>' % (cls, label))

    if not mega:
        out.append('          <div class="drop">')
        for c in children:
            out.append(link(c, 12))
        out.append('          </div>')
        out.append('        </li>')
        return

    cols = [c for c in children if kids(c)]
    flat = [c for c in children if not kids(c)]
    ncols = len(cols) + (1 if flat else 0)
    # the panel sizes itself off its column count instead of a fixed width
    # Right-of-centre menus anchor from their right edge so the panel opens
    # inward. Pure-CSS safety net: if the JS clamp never runs, these still
    # cannot run off the right of the viewport.
    anchor = ';left:auto;right:0' if anchor_right else ''
    out.append('          <div class="drop mega" style="--cols:%d%s">' % (ncols, anchor))
    for i, col in enumerate(cols):
        out.append('            <div class="mega-col" style="--c:%s">'
                   % ACCENTS[i % len(ACCENTS)])
        items = list(kids(col))
        hd = page_of(col)
        # "Ayurveda > Introduction" is a redundant step — for every system the
        # intro IS the system page, so the column header absorbs it
        intro = next((c for c in items if c['label'].strip().lower() == 'introduction'), None)
        if intro is not None:
            items.remove(intro)
            hd = resolve(intro['href'])
        if hd == '#':
            hd = page_of(col)
        out.append('              <a class="mega-hd" href="%s">' % hd)
        out.append('                <span class="nm">%s</span>' % esc(col['label']))
        deg = DEGREE.get(col['label'].strip())
        if deg:
            out.append('                <span class="dg">%s</span>' % deg)
        out.append('              </a>')
        for c in items:
            out.append(link(c, 14, shorten=True))
        out.append('            </div>')
    if flat:
        out.append('            <div class="mega-rail">')
        out.append('              <div class="rl">More</div>')
        for c in flat:
            out.append(link(c, 14))
        out.append('            </div>')
    out.append('          </div>')
    out.append('        </li>')


def build():
    tree = load_tree()
    assign_paths(tree)
    out = []
    visible = [m for m in tree if m['label'].lower() != 'logins']
    for i, menu in enumerate(visible):
        render_menu(menu, out, anchor_right=(i >= len(visible) * 0.4))

    # Logins keeps its right-aligned pill treatment
    logins = next((m for m in tree if m['label'].lower() == 'logins'), None)
    if logins:
        out.append('        <li><button class="nav-btn nav-login">Logins <i>&#9660;</i></button>')
        out.append('          <div class="drop" style="left:auto;right:0">')
        for c in kids(logins):
            out.append(link(c, 12))
        out.append('          </div>')
        out.append('        </li>')

    os.makedirs('src', exist_ok=True)
    codecs.open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')

    total = sum(1 for line in out if '<a ' in line)
    print('wrote %s — %d menus, %d links' % (OUT, len(tree), total))


if __name__ == '__main__':
    build()
