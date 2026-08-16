"""Create a page for every navbar destination that doesn't have one yet.

Each generated page carries its real title, its breadcrumb trail through the
official menu, and a link to the source page on ncismindia.org. Pages already
authored by hand are never overwritten.
"""
import json, os, codecs, re
from gen_nav import resolve, slug, kids, esc, ORIGIN, assign_paths, page_of, PATHS, load_tree

TREE = 'navtree.json'
# fingerprint identifying a page this script wrote (safe to overwrite)
MARKER = 'Content is being migrated'
OUTDIR = 'src'

# section label -> the rail tag shown down the left margin
RAIL = {
    'About NCISM': 'The Commission',
    'Indian Medicine': 'Systems',
    'Registration': 'Registration',
    'Information Desk': 'Information',
    'E-learning': 'E-learning',
    'Examinations': 'Examinations',
    'Rating': 'Rating',
    'Others': 'Services',
    'Vigilance Corner': 'Vigilance',
    'RTI': 'RTI',
    'Results': 'Results',
}

TEMPLATE = """<title>{title} &middot; NCISM</title>

<div class="band">
  <div class="wrap">
    <div class="rail js rv in">
      <div class="no">{num}</div>
      <div class="tag">{rail}</div>
    </div>
    <div class="body-col">
      <nav class="crumb js rv in" aria-label="Breadcrumb">
{crumbs}
      </nav>
      <div class="hd js rv in" style="animation-delay:.12s">
        <h2>{heading}</h2>
        <p>{lede}</p>
      </div>
{extra}
      <div class="pg-foot js rv in" style="animation-delay:.24s">
        <a href="{back}" class="btn btn-fill">&larr; {backlabel}</a>
        <a href="{source}" class="btn" target="_blank" rel="noopener">Official page &nearr;</a>
      </div>
    </div>
  </div>
</div>
"""


def collect(nodes, trail=(), acc=None):
    acc = acc if acc is not None else []
    for n in nodes:
        acc.append((trail, n))
        collect(kids(n), trail + (n,), acc)
    return acc


def child_list(node):
    """If this page is a hub, render its children as a link list."""
    ch = kids(node)
    if not ch:
        return ''
    rows = []
    rows.append('      <ul class="doc-list js rv in" style="animation-delay:.18s">')
    for c in ch:
        href = resolve(c['href'])
        if not href.startswith('http') and not href.lower().endswith('.pdf'):
            href = page_of(c)
        pdf = ' <span class="pill">PDF</span>' if c['href'] and c['href'].lower().endswith('.pdf') else ''
        rows.append('        <li><a class="doc" href="%s">%s%s</a></li>' % (href, esc(c['label']), pdf))
    rows.append('      </ul>')
    return '\n'.join(rows)


def main():
    tree = load_tree()
    assign_paths(tree)
    items = collect(tree)

    # Several menu paths can legitimately share one file — a system and its
    # "Introduction" are the same page. Generate from the richest node, so the
    # hub keeps its child list instead of being overwritten by a bare leaf.
    best = {}
    for trail, node in items:
        key = page_of(node)
        prev = best.get(key)
        if prev is None or len(kids(node)) > len(kids(prev[1])):
            best[key] = (trail, node)
    items = list(best.values())

    made = skipped = 0
    for trail, node in items:
        href = node['href']
        target = resolve(href)
        if target.startswith('http'):
            continue                      # external — digialm logins, docs.google
        if href and href.strip() not in ('#', '') and not target.endswith('.html'):
            continue                      # pdf
        target = page_of(node)
        if not target.endswith('.html') or '/' in target or ':' in target:
            continue                      # not a safe local filename
        if target in ('index.html',):
            continue
        path = os.path.join(OUTDIR, target)
        if os.path.exists(path):
            # regenerate our own output, never touch a hand-authored page
            try:
                prior = codecs.open(path, encoding='utf-8').read()
            except OSError:
                prior = ''
            if MARKER not in prior:
                skipped += 1
                continue

        section = trail[0]['label'] if trail else node['label']
        parent = trail[-1] if trail else None
        back = page_of(parent) if parent else 'index.html'
        backlabel = 'Back to %s' % (parent['label'] if parent else 'Home')

        crumbs = ['        <a href="index.html">Home</a>']
        for t in trail:
            crumbs.append('        <a href="%s">%s</a>' % (page_of(t), esc(t['label'])))
        crumbs.append('        <span aria-current="page">%s</span>' % esc(node['label']))

        src = ORIGIN + (href if href and href.strip() not in ('#', '') else 'index.php')

        # "A.Y. 2024-25" alone is ambiguous across four systems and two menus,
        # so qualify the tab label with its parent and its top-level section
        # the system (Siddha/Unani/...) sits at trail depth 1 and is what
        # actually distinguishes "First Semester" from "First Semester"
        bits = [node['label']]
        if len(trail) > 1:
            bits.append(trail[1]['label'])
        if parent is not None:
            bits.append(parent['label'])
        bits.append(section)
        seen, uniq = set(), []
        for b in bits:
            if b not in seen:
                seen.add(b)
                uniq.append(b)
        bits = uniq
        page_title = esc(bits[0]) + (' &mdash; ' + ' &middot; '.join(esc(b) for b in bits[1:])
                                     if len(bits) > 1 else '')

        body = TEMPLATE.format(
            title=page_title,
            heading=esc(node['label']),
            num='%02d' % ((len(trail) or 1)),
            rail=esc(RAIL.get(section, 'NCISM')),
            crumbs='\n'.join(crumbs),
            lede='This section mirrors <strong>%s</strong> from the National Commission '
                 'for Indian System of Medicine. Content is being migrated; the official '
                 'page remains the authoritative source.' % esc(node['label']),
            extra=child_list(node),
            back=back,
            backlabel=esc(backlabel),
            source=esc(src),
        )
        codecs.open(path, 'w', encoding='utf-8').write(body)
        made += 1

    print('generated %d pages, skipped %d already present' % (made, skipped))


if __name__ == '__main__':
    main()
