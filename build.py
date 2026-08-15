import re, base64, os, mimetypes, glob, codecs

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
    
    pages = glob.glob('src/*.html')
    for page in pages:
        if '_layout' in page:
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
        
        # Wrap as standard document
        title_match = re.search(r'<title>(.*?)</title>', full_html, re.S)
        title = title_match.group(1).strip() if title_match else 'NCISM'
        body = re.sub(r'<title>.*?</title>\s*', '', full_html, count=1, flags=re.S)

        doc = (
            '<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="color-scheme" content="light dark">\n'
            f'<meta name="description" content="{title}">\n'
            f'<title>{title}</title>\n'
            '</head>\n<body>\n'
            f'{body}\n'
            '</body>\n</html>\n'
        )
        
        out_path = page_name
        codecs.open(out_path, 'w', encoding='utf-8').write(doc)
        print(f'Built {out_path}: {os.path.getsize(out_path)/1024:.0f} KB')

if __name__ == '__main__':
    build()
