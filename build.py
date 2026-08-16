import re, base64, os, mimetypes, glob, codecs, datetime

STAMP = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def inline_resources(html):
    fonts = codecs.open('assets/fonts/fonts.css', encoding='utf-8').read()
    html = html.replace('/*__FONTS__*/', fonts)

    def inline(m):
        attr, path = m.group(1), m.group(2)
        if path.startswith(('data:', 'http')):
            return m.group(0)
        if not os.path.exists(path):
            print('  !! missing:', path)
            return m.group(0)
        mime = mimetypes.guess_type(path)[0] or 'image/jpeg'
        b64 = base64.b64encode(open(path, 'rb').read()).decode()
        print(f'  inlined {path} ({os.path.getsize(path)/1024:.0f} KB)')
        return f'{attr}="data:{mime};base64,{b64}"'

    html = re.sub(r'(src)="([^"]+\.(?:png|jpg|jpeg|gif|svg|webp))"', inline, html)
    return html

def build():
    layout = codecs.open('src/_layout.html', encoding='utf-8').read()

    # primary navbar is generated from the scraped official menu — see gen_nav.py
    nav = codecs.open('src/_nav.html', encoding='utf-8').read()
    layout = layout.replace('{{NAV}}', nav)

    pages = glob.glob('src/*.html')
    for page in pages:
        # partials (_layout, _nav, ...) are ingredients, not pages
        if os.path.basename(page).startswith('_'):
            continue
            
        page_name = os.path.basename(page)
        content = codecs.open(page, encoding='utf-8').read()
        
        # Inject content into layout
        full_html = layout.replace('{{CONTENT}}', content)
        
        # Inline external CSS (style.css)
        if '<link rel="stylesheet" href="src/style.css">' in full_html:
            css_content = codecs.open('src/style.css', encoding='utf-8').read()
            full_html = full_html.replace('<link rel="stylesheet" href="src/style.css">', f'<style>\n{css_content}\n</style>')
        
        # Inline images and fonts
        full_html = inline_resources(full_html)
        
        # Wrap as standard document. A page's own <title> wins over the
        # layout's, otherwise every page ships with the same tab label.
        own = re.search(r'<title>(.*?)</title>', content, re.S)
        fallback = re.search(r'<title>(.*?)</title>', full_html, re.S)
        title_match = own or fallback
        title = title_match.group(1).strip() if title_match else 'NCISM'
        body = re.sub(r'<title>.*?</title>\s*', '', full_html, flags=re.S)

        doc = (
            '<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="color-scheme" content="light dark">\n'
            # these pages are multi-MB single files, so browsers cache them hard
            # and a rebuild can silently keep showing the old markup
            '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">\n'
            '<meta http-equiv="Pragma" content="no-cache">\n'
            '<meta http-equiv="Expires" content="0">\n'
            f'<meta name="build" content="{STAMP}">\n'
            f'<meta name="description" content="{title}">\n'
            f'<title>{title}</title>\n'
            '</head>\n<body>\n'
            f'<!-- build {STAMP} -->\n'
            f'{body}\n'
            f'<script>console.info("NCISM build {STAMP}");</script>\n'
            '</body>\n</html>\n'
        )
        
        out_path = page_name
        codecs.open(out_path, 'w', encoding='utf-8').write(doc)
        print(f'Built {out_path}: {os.path.getsize(out_path)/1024:.0f} KB')

if __name__ == '__main__':
    build()
